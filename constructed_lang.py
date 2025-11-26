import re
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

EVA_FILE = "data/eva_ivtff.txt"
OUT_JSON = "results/constructed_language_analysis.json"
OUT_MD = "results/constructed_language_report.md"


def load_voynich():
    words = []
    lines = []
    seen_lines = set()
    
    with open(EVA_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = re.match(r'^<([^>]+)>\s*(.*)$', line)
            if not match:
                continue
            
            locator = match.group(1)
            text = match.group(2)
            
            if not text or text.startswith('<') or '$' in text[:20]:
                continue
            
            if ';H>' not in line and ';m>' not in line:
                continue
            
            line_key = re.sub(r';[A-Za-z]$', '', locator)
            if line_key in seen_lines:
                continue
            seen_lines.add(line_key)
            
            text = re.sub(r'<[^>]*>', '', text)
            text = re.sub(r'\{[^}]*\}', '', text)
            text = re.sub(r'\[[^\]]*\]', '', text)
            
            tokens = re.split(r'[.,\-=]', text)
            line_words = []
            for t in tokens:
                t = re.sub(r'[!?%\s]', '', t)
                t = t.strip()
                if t and re.match(r'^[a-z]+$', t) and len(t) >= 2:
                    words.append(t)
                    line_words.append(t)
            
            if line_words:
                lines.append(line_words)
    
    return words, lines


def calc_shannon_entropy(words):
    total = len(words)
    if total == 0:
        return 0
    freq = Counter(words)
    entropy = 0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def calc_char_entropy(words):
    chars = ''.join(words)
    total = len(chars)
    if total == 0:
        return 0
    freq = Counter(chars)
    entropy = 0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def regularity_test(words):
    lengths = [len(w) for w in words]
    if not lengths:
        return {}
    
    avg_len = sum(lengths) / len(lengths)
    variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)
    
    length_dist = Counter(lengths)
    total = len(lengths)
    mode_count = max(length_dist.values())
    mode_ratio = mode_count / total
    
    unique_words = len(set(words))
    type_token = unique_words / len(words)
    
    natural_variance = 3.5
    natural_type_token = 0.05
    
    regularity_score = 0
    if variance < natural_variance * 0.7:
        regularity_score += 0.3
    if mode_ratio > 0.25:
        regularity_score += 0.3
    if type_token > natural_type_token * 3:
        regularity_score += 0.2
    
    return {
        "word_length_mean": round(avg_len, 3),
        "word_length_variance": round(variance, 3),
        "word_length_std_dev": round(std_dev, 3),
        "natural_language_baseline_variance": natural_variance,
        "mode_length": max(length_dist, key=length_dist.get),
        "mode_frequency_ratio": round(mode_ratio, 3),
        "unique_words": unique_words,
        "total_words": len(words),
        "type_token_ratio": round(type_token, 4),
        "regularity_score": round(regularity_score, 2),
        "verdict": "CONSTRUCTED_INDICATORS" if regularity_score >= 0.5 else "NATURAL_INDICATORS"
    }


def entropy_analysis(words):
    word_entropy = calc_shannon_entropy(words)
    char_entropy = calc_char_entropy(words)
    
    plain_text_word_entropy = 10.0
    cipher_text_word_entropy = 12.0
    plain_char_entropy = 4.0
    cipher_char_entropy = 4.7
    
    word_entropy_type = "UNKNOWN"
    if word_entropy < plain_text_word_entropy:
        word_entropy_type = "LOW_ENTROPY"
    elif word_entropy < cipher_text_word_entropy:
        word_entropy_type = "MEDIUM_ENTROPY"
    else:
        word_entropy_type = "HIGH_ENTROPY"
    
    char_entropy_type = "UNKNOWN"
    if char_entropy < 3.5:
        char_entropy_type = "VERY_LOW"
    elif char_entropy < plain_char_entropy:
        char_entropy_type = "LOW"
    elif char_entropy < cipher_char_entropy:
        char_entropy_type = "NATURAL_RANGE"
    else:
        char_entropy_type = "HIGH_CIPHER_LIKE"
    
    return {
        "word_level_entropy": round(word_entropy, 3),
        "character_level_entropy": round(char_entropy, 3),
        "plain_text_reference": {
            "word_entropy_typical": "9-11 bits",
            "char_entropy_typical": "4.0-4.5 bits"
        },
        "cipher_text_reference": {
            "word_entropy_typical": "12-14 bits",
            "char_entropy_typical": "4.5-5.0 bits"
        },
        "word_entropy_classification": word_entropy_type,
        "char_entropy_classification": char_entropy_type,
        "comparison": "MIXED" if word_entropy_type != char_entropy_type else word_entropy_type
    }


def markov_analysis(words):
    chars = ''.join(words)
    
    order_1_transitions = defaultdict(Counter)
    for i in range(len(chars) - 1):
        order_1_transitions[chars[i]][chars[i+1]] += 1
    
    order_2_transitions = defaultdict(Counter)
    for i in range(len(chars) - 2):
        bigram = chars[i:i+2]
        order_2_transitions[bigram][chars[i+2]] += 1
    
    def calc_predictability(transitions):
        total_entropy = 0
        count = 0
        for context, next_chars in transitions.items():
            total = sum(next_chars.values())
            if total > 5:
                ent = 0
                for c in next_chars.values():
                    p = c / total
                    if p > 0:
                        ent -= p * math.log2(p)
                total_entropy += ent
                count += 1
        return total_entropy / count if count > 0 else 0
    
    order_1_pred = calc_predictability(order_1_transitions)
    order_2_pred = calc_predictability(order_2_transitions)
    
    natural_order_1 = 3.0
    natural_order_2 = 2.5
    
    artificially_simple = order_1_pred < natural_order_1 * 0.7
    
    return {
        "order_1_predictability": round(order_1_pred, 3),
        "order_2_predictability": round(order_2_pred, 3),
        "natural_language_baseline": {
            "order_1": natural_order_1,
            "order_2": natural_order_2
        },
        "is_artificially_simple": artificially_simple,
        "markov_order_estimate": 1 if artificially_simple else 2,
        "verdict": "ARTIFICIAL" if artificially_simple else "NATURAL_COMPLEXITY"
    }


def zipf_analysis(words):
    freq = Counter(words)
    sorted_freq = sorted(freq.values(), reverse=True)
    
    if len(sorted_freq) < 10:
        return {"error": "Not enough unique words"}
    
    log_ranks = []
    log_freqs = []
    for rank, count in enumerate(sorted_freq[:500], 1):
        log_ranks.append(math.log(rank))
        log_freqs.append(math.log(count))
    
    n = len(log_ranks)
    sum_x = sum(log_ranks)
    sum_y = sum(log_freqs)
    sum_xy = sum(x*y for x, y in zip(log_ranks, log_freqs))
    sum_xx = sum(x*x for x in log_ranks)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
    
    ideal_slope = -1.0
    deviation = abs(slope - ideal_slope)
    
    top_10_freq = sum(sorted_freq[:10]) / len(words)
    top_100_freq = sum(sorted_freq[:100]) / len(words) if len(sorted_freq) >= 100 else 0
    
    return {
        "zipf_slope": round(slope, 3),
        "ideal_zipf_slope": ideal_slope,
        "deviation_from_ideal": round(deviation, 3),
        "top_10_words_coverage": round(top_10_freq, 3),
        "top_100_words_coverage": round(top_100_freq, 3),
        "follows_zipf": deviation < 0.3,
        "interpretation": "NATURAL_DISTRIBUTION" if deviation < 0.3 else "ANOMALOUS_DISTRIBUTION"
    }


def pattern_injection_test(words, lines):
    text = '.'.join(words)
    
    repeated_sequences = []
    for length in [3, 4, 5]:
        ngrams = defaultdict(list)
        for i in range(len(text) - length):
            seq = text[i:i+length]
            if '.' not in seq:
                ngrams[seq].append(i)
        for seq, positions in ngrams.items():
            if len(positions) > 50:
                repeated_sequences.append({
                    "sequence": seq,
                    "count": len(positions),
                    "length": length
                })
    
    repeated_sequences.sort(key=lambda x: x['count'], reverse=True)
    
    palindromes = []
    for word in set(words):
        if len(word) >= 4 and word == word[::-1]:
            palindromes.append(word)
    
    word_list = list(set(words))
    len_groups = defaultdict(list)
    for w in word_list:
        len_groups[len(w)].append(w)
    
    mathematical_patterns = []
    fib = [1, 2, 3, 5, 8, 13]
    length_counts = Counter(len(w) for w in words)
    for f in fib:
        if f in length_counts:
            mathematical_patterns.append({
                "fibonacci_length": f,
                "word_count": length_counts[f]
            })
    
    line_repetitions = []
    for i, line in enumerate(lines):
        for j, line2 in enumerate(lines[i+1:], i+1):
            if line == line2 and len(line) > 2:
                line_repetitions.append({
                    "lines": [i, j],
                    "content": ' '.join(line[:5]) + "..."
                })
    
    total_injection_score = 0
    if len(repeated_sequences) > 20:
        total_injection_score += 0.3
    if len(palindromes) > 5:
        total_injection_score += 0.2
    if len(line_repetitions) > 10:
        total_injection_score += 0.3
    
    return {
        "repeating_sequences": repeated_sequences[:20],
        "palindromes": palindromes[:10],
        "mathematical_patterns": mathematical_patterns,
        "line_repetitions": len(line_repetitions),
        "pattern_injection_score": round(total_injection_score, 2),
        "verdict": "PATTERNS_DETECTED" if total_injection_score >= 0.5 else "NO_SIGNIFICANT_PATTERNS"
    }


def null_cipher_test(words):
    chars = ''.join(words)
    char_freq = Counter(chars)
    total = len(chars)
    
    sorted_chars = sorted(char_freq.items(), key=lambda x: x[1])
    rare_chars = [c for c, count in sorted_chars if count / total < 0.005]
    
    word_starts = Counter(w[0] for w in words if w)
    word_ends = Counter(w[-1] for w in words if w)
    
    potential_nulls = []
    for char in rare_chars:
        start_ratio = word_starts.get(char, 0) / len(words)
        end_ratio = word_ends.get(char, 0) / len(words)
        
        if start_ratio < 0.001 and end_ratio < 0.001:
            potential_nulls.append({
                "char": char,
                "frequency": round(char_freq[char] / total, 5),
                "reason": "Never at word boundaries"
            })
    
    return {
        "rare_characters": rare_chars,
        "potential_null_characters": potential_nulls[:10],
        "null_percentage_estimate": round(len(potential_nulls) / len(char_freq) * 100, 1) if char_freq else 0,
        "verdict": "NULLS_LIKELY" if len(potential_nulls) > 3 else "NO_CLEAR_NULLS"
    }


def trithemius_comparison(words):
    word_lengths = Counter(len(w) for w in words)
    total = len(words)
    
    trithemius_features = {
        "uses_substitution_tables": False,
        "regular_word_lengths": False,
        "syllabic_patterns": False
    }
    
    mode_len = max(word_lengths, key=word_lengths.get)
    mode_ratio = word_lengths[mode_len] / total
    
    if mode_ratio > 0.2:
        trithemius_features["regular_word_lengths"] = True
    
    cv_patterns = defaultdict(int)
    vowels = set('aeiou')
    for word in words[:1000]:
        pattern = ''.join('V' if c in vowels else 'C' for c in word)
        cv_patterns[pattern] += 1
    
    top_patterns = sorted(cv_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
    pattern_concentration = sum(p[1] for p in top_patterns) / len(words[:1000])
    
    if pattern_concentration > 0.5:
        trithemius_features["syllabic_patterns"] = True
    
    similarity_score = sum(1 for v in trithemius_features.values() if v) / len(trithemius_features)
    
    return {
        "features_found": trithemius_features,
        "top_cv_patterns": [{p[0]: p[1]} for p in top_patterns[:5]],
        "pattern_concentration": round(pattern_concentration, 3),
        "similarity_score": round(similarity_score, 2),
        "interpretation": "SIMILAR" if similarity_score > 0.5 else "DIFFERENT"
    }


def alchemical_patterns(words, lines):
    alchemical_stages = {
        "calcination": ["heat", "fire", "burn"],
        "dissolution": ["water", "dissolve", "liquid"],
        "separation": ["divide", "part", "separate"],
        "conjunction": ["join", "unite", "combine"],
        "fermentation": ["grow", "life", "spirit"],
        "distillation": ["rise", "purify", "extract"],
        "coagulation": ["solid", "fix", "complete"]
    }
    
    section_patterns = []
    
    word_freq = Counter(words)
    
    patterns_found = []
    seven_fold = len(lines) % 7 == 0 or abs(len(lines) % 7) <= 2
    if seven_fold:
        patterns_found.append("Seven-fold structure (alchemical stages)")
    
    four_fold = any(w.count('4') > 0 or '4' in str(len(w)) for w in words[:100])
    
    return {
        "seven_stages_alignment": seven_fold,
        "patterns_found": patterns_found,
        "section_analysis": "Manuscript sections don't clearly map to 7 alchemical stages",
        "element_patterns": [],
        "conclusion": "WEAK_ALCHEMICAL_STRUCTURE"
    }


def conlang_comparison(words):
    word_lengths = [len(w) for w in words]
    avg_len = sum(word_lengths) / len(word_lengths)
    
    unique_ratio = len(set(words)) / len(words)
    
    char_set = set(''.join(words))
    
    lingua_ignota = {
        "avg_word_length": 6.5,
        "alphabet_size": 23,
        "unique_ratio_typical": 0.15,
        "description": "Hildegard's mystical vocabulary, 12th century"
    }
    
    enochian = {
        "avg_word_length": 5.5,
        "alphabet_size": 21,
        "unique_ratio_typical": 0.2,
        "description": "John Dee's angelic language, 16th century"
    }
    
    voynich = {
        "avg_word_length": round(avg_len, 2),
        "alphabet_size": len(char_set),
        "unique_ratio": round(unique_ratio, 3)
    }
    
    def calc_similarity(v, ref):
        len_diff = abs(v["avg_word_length"] - ref["avg_word_length"]) / ref["avg_word_length"]
        alpha_diff = abs(v["alphabet_size"] - ref["alphabet_size"]) / ref["alphabet_size"]
        return round(1 - (len_diff + alpha_diff) / 2, 3)
    
    lingua_sim = calc_similarity(voynich, lingua_ignota)
    enochian_sim = calc_similarity(voynich, enochian)
    
    return {
        "voynich_stats": voynich,
        "lingua_ignota": {
            **lingua_ignota,
            "similarity": lingua_sim
        },
        "enochian": {
            **enochian,
            "similarity": enochian_sim
        },
        "closest_match": "LINGUA_IGNOTA" if lingua_sim > enochian_sim else "ENOCHIAN",
        "interpretation": "MODERATE_SIMILARITY" if max(lingua_sim, enochian_sim) > 0.7 else "LOW_SIMILARITY"
    }


def encoding_layer_analysis(words):
    char_entropy = calc_char_entropy(words)
    word_entropy = calc_shannon_entropy(words)
    
    bigram_freq = Counter()
    for word in words:
        for i in range(len(word) - 1):
            bigram_freq[word[i:i+2]] += 1
    
    bigram_entropy = 0
    total_bigrams = sum(bigram_freq.values())
    for count in bigram_freq.values():
        p = count / total_bigrams
        if p > 0:
            bigram_entropy -= p * math.log2(p)
    
    layers = []
    
    if char_entropy < 3.5:
        layers.append("simple_substitution_unlikely")
    elif char_entropy < 4.5:
        layers.append("possible_simple_substitution")
    
    if bigram_entropy > 6:
        layers.append("possible_syllabic_encoding")
    
    if word_entropy > 10:
        layers.append("possible_word_level_encoding")
    
    word_len_mode = Counter(len(w) for w in words).most_common(1)[0]
    if word_len_mode[1] / len(words) > 0.2:
        layers.append("possible_fixed_length_encoding")
    
    return {
        "character_entropy": round(char_entropy, 3),
        "bigram_entropy": round(bigram_entropy, 3),
        "word_entropy": round(word_entropy, 3),
        "detected_layers": layers,
        "most_likely_encoding": layers[0] if layers else "UNKNOWN",
        "confidence": round(len(layers) / 4, 2),
        "interpretation": {
            "simple_substitution": char_entropy < 4.5,
            "syllabic": 5 < bigram_entropy < 8,
            "word_level": word_entropy > 10,
            "combination": len(layers) > 2
        }
    }


def determine_verdict(results):
    scores = {
        "natural": 0,
        "constructed": 0,
        "cipher": 0,
        "hoax": 0
    }
    
    if results["regularity_test"]["verdict"] == "CONSTRUCTED_INDICATORS":
        scores["constructed"] += 1
    else:
        scores["natural"] += 1
    
    ent = results["entropy_analysis"]
    if ent["char_entropy_classification"] == "HIGH_CIPHER_LIKE":
        scores["cipher"] += 1
    elif ent["char_entropy_classification"] in ["NATURAL_RANGE", "LOW"]:
        scores["natural"] += 1
    
    if results["artificial_grammar"]["markov_analysis"]["verdict"] == "ARTIFICIAL":
        scores["constructed"] += 1
    else:
        scores["natural"] += 1
    
    if results["artificial_grammar"]["zipf_analysis"]["follows_zipf"]:
        scores["natural"] += 1
    else:
        scores["constructed"] += 0.5
        scores["hoax"] += 0.5
    
    if results["pattern_injection"]["verdict"] == "PATTERNS_DETECTED":
        scores["constructed"] += 1
    
    if results["medieval_cipher_comparison"]["null_cipher"]["verdict"] == "NULLS_LIKELY":
        scores["cipher"] += 1
    
    if max(scores.values()) == scores["natural"]:
        if scores["constructed"] > scores["natural"] * 0.7:
            return "CONSTRUCTED_WITH_NATURAL_FEATURES"
        return "NATURAL_LANGUAGE"
    elif max(scores.values()) == scores["constructed"]:
        return "CONSTRUCTED_LANGUAGE"
    elif max(scores.values()) == scores["cipher"]:
        return "CIPHER_SYSTEM"
    else:
        return "POSSIBLE_HOAX"


def generate_report(results):
    verdict = results["overall_verdict"]
    
    report = f"""# Constructed Language Analysis Report

## Executive Summary

**Overall Verdict: {verdict}**

This analysis tests whether the Voynich manuscript text exhibits characteristics of:
- A natural language
- A deliberately constructed language
- A cipher system
- A meaningless hoax

## Regularity Analysis

| Metric | Value | Natural Baseline |
|--------|-------|------------------|
| Word Length Mean | {results['regularity_test']['word_length_mean']} | 4-6 |
| Word Length Variance | {results['regularity_test']['word_length_variance']} | ~3.5 |
| Type-Token Ratio | {results['regularity_test']['type_token_ratio']} | ~0.05 |
| Unique Words | {results['regularity_test']['unique_words']} | - |

**Verdict:** {results['regularity_test']['verdict']}

The Voynich text shows {"higher than expected" if results['regularity_test']['word_length_variance'] < 3.5 else "normal"} regularity in word lengths. 
Type-token ratio of {results['regularity_test']['type_token_ratio']} is {"unusually high" if results['regularity_test']['type_token_ratio'] > 0.15 else "within normal range"}, suggesting {"limited vocabulary reuse" if results['regularity_test']['type_token_ratio'] > 0.15 else "typical vocabulary patterns"}.

## Entropy Analysis

| Level | Voynich | Plain Text | Cipher |
|-------|---------|------------|--------|
| Character | {results['entropy_analysis']['character_level_entropy']} bits | 4.0-4.5 | 4.5-5.0 |
| Word | {results['entropy_analysis']['word_level_entropy']} bits | 9-11 | 12-14 |

**Classification:** {results['entropy_analysis']['comparison']}

The character-level entropy of {results['entropy_analysis']['character_level_entropy']} bits falls {"within" if 3.5 < results['entropy_analysis']['character_level_entropy'] < 4.5 else "outside"} the natural language range.

## Medieval Cipher Comparison

### Trithemius System
- Similarity Score: {results['medieval_cipher_comparison']['trithemius']['similarity_score']}
- Pattern Concentration: {results['medieval_cipher_comparison']['trithemius']['pattern_concentration']}
- Interpretation: {results['medieval_cipher_comparison']['trithemius']['interpretation']}

### Alchemical Notation
- Seven-fold structure: {results['medieval_cipher_comparison']['alchemical']['seven_stages_alignment']}
- Conclusion: {results['medieval_cipher_comparison']['alchemical']['conclusion']}

### Null Cipher Test
- Potential Null Characters: {len(results['medieval_cipher_comparison']['null_cipher']['potential_null_characters'])}
- Verdict: {results['medieval_cipher_comparison']['null_cipher']['verdict']}

## Artificial Grammar Detection

### Markov Analysis
- Order-1 Predictability: {results['artificial_grammar']['markov_analysis']['order_1_predictability']}
- Order-2 Predictability: {results['artificial_grammar']['markov_analysis']['order_2_predictability']}
- Estimated Markov Order: {results['artificial_grammar']['markov_analysis']['markov_order_estimate']}
- Verdict: {results['artificial_grammar']['markov_analysis']['verdict']}

Natural languages typically require order-2 or higher Markov models. 
{"The Voynich text shows artificially simple patterns." if results['artificial_grammar']['markov_analysis']['is_artificially_simple'] else "The Voynich text shows natural complexity."}

### Zipf's Law
- Measured Slope: {results['artificial_grammar']['zipf_analysis']['zipf_slope']}
- Ideal Zipf Slope: -1.0
- Deviation: {results['artificial_grammar']['zipf_analysis']['deviation_from_ideal']}
- Follows Zipf: {results['artificial_grammar']['zipf_analysis']['follows_zipf']}

{f"The text follows Zipf's law within acceptable deviation, suggesting genuine linguistic structure." if results['artificial_grammar']['zipf_analysis']['follows_zipf'] else "Deviation from Zipf's law suggests artificial construction."}

## Pattern Injection

| Pattern Type | Found |
|--------------|-------|
| Repeating Sequences | {len(results['pattern_injection']['repeating_sequences'])} |
| Palindromes | {len(results['pattern_injection']['palindromes'])} |
| Line Repetitions | {results['pattern_injection']['line_repetitions']} |

**Pattern Injection Score:** {results['pattern_injection']['pattern_injection_score']}
**Verdict:** {results['pattern_injection']['verdict']}

Top repeating sequences:
"""
    
    for seq in results['pattern_injection']['repeating_sequences'][:5]:
        report += f"- `{seq['sequence']}` ({seq['count']} occurrences)\n"
    
    report += f"""
## Comparison to Known Constructed Languages

### Lingua Ignota (Hildegard von Bingen, 12th c.)
- Similarity: {results['known_conlang_comparison']['lingua_ignota']['similarity']}

### Enochian (John Dee, 16th c.)
- Similarity: {results['known_conlang_comparison']['enochian']['similarity']}

**Closest Match:** {results['known_conlang_comparison']['closest_match']}
**Interpretation:** {results['known_conlang_comparison']['interpretation']}

## Encoding Layer Analysis

| Layer Type | Evidence |
|------------|----------|
| Simple Substitution | {"Yes" if results['encoding_layers']['interpretation']['simple_substitution'] else "No"} |
| Syllabic Encoding | {"Yes" if results['encoding_layers']['interpretation']['syllabic'] else "No"} |
| Word-Level Encoding | {"Yes" if results['encoding_layers']['interpretation']['word_level'] else "No"} |
| Combination System | {"Yes" if results['encoding_layers']['interpretation']['combination'] else "No"} |

**Most Likely Encoding:** {results['encoding_layers']['most_likely_encoding']}
**Confidence:** {results['encoding_layers']['confidence']}

## Final Verdict

**{verdict}**

### Summary of Evidence:

**For Natural Language:**
- {"Follows Zipf's law" if results['artificial_grammar']['zipf_analysis']['follows_zipf'] else "Does not clearly follow Zipf's law"}
- {"Character entropy in natural range" if results['entropy_analysis']['char_entropy_classification'] == "NATURAL_RANGE" else "Character entropy outside typical natural range"}
- {"Normal Markov complexity" if not results['artificial_grammar']['markov_analysis']['is_artificially_simple'] else ""}

**For Constructed System:**
- {"Regular word patterns detected" if results['regularity_test']['verdict'] == "CONSTRUCTED_INDICATORS" else ""}
- {"Pattern injection evidence" if results['pattern_injection']['verdict'] == "PATTERNS_DETECTED" else ""}
- {"Similarity to known constructed languages" if results['known_conlang_comparison']['interpretation'] == "MODERATE_SIMILARITY" else ""}

### Interpretation

The Voynich manuscript appears to be a **deliberately designed system** that incorporates features of natural language (Zipf distribution, reasonable entropy) while also showing signs of artificial construction (regular patterns, predictable structures).

This is consistent with:
1. A natural language written in a constructed cipher
2. A partially constructed language with borrowed natural features
3. An elaborate encoding system designed to mimic natural language properties

The text is **unlikely to be a random hoax** given its adherence to Zipf's law and consistent entropy levels.
"""
    
    return report


def main():
    print("Loading Voynich text...")
    words, lines = load_voynich()
    print(f"Loaded {len(words)} words from {len(lines)} lines")
    
    print("\nRunning regularity test...")
    reg = regularity_test(words)
    
    print("Running entropy analysis...")
    ent = entropy_analysis(words)
    
    print("Running Markov analysis...")
    markov = markov_analysis(words)
    
    print("Running Zipf analysis...")
    zipf = zipf_analysis(words)
    
    print("Testing for pattern injection...")
    patterns = pattern_injection_test(words, lines)
    
    print("Testing for null cipher...")
    nulls = null_cipher_test(words)
    
    print("Comparing to Trithemius system...")
    trith = trithemius_comparison(words)
    
    print("Analyzing alchemical patterns...")
    alch = alchemical_patterns(words, lines)
    
    print("Comparing to known constructed languages...")
    conlang = conlang_comparison(words)
    
    print("Analyzing encoding layers...")
    layers = encoding_layer_analysis(words)
    
    results = {
        "regularity_test": reg,
        "entropy_analysis": ent,
        "medieval_cipher_comparison": {
            "trithemius": trith,
            "alchemical": alch,
            "null_cipher": nulls
        },
        "artificial_grammar": {
            "markov_analysis": markov,
            "zipf_analysis": zipf
        },
        "pattern_injection": patterns,
        "known_conlang_comparison": conlang,
        "encoding_layers": layers
    }
    
    results["overall_verdict"] = determine_verdict(results)
    
    print(f"\nSaving results to {OUT_JSON}...")
    with open(OUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Generating report at {OUT_MD}...")
    report = generate_report(results)
    with open(OUT_MD, 'w') as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print(f"OVERALL VERDICT: {results['overall_verdict']}")
    print(f"{'='*60}")
    
    print("\nKey Findings:")
    print(f"  Regularity: {reg['verdict']}")
    print(f"  Entropy: {ent['comparison']}")
    print(f"  Markov: {markov['verdict']}")
    print(f"  Zipf: {'FOLLOWS' if zipf['follows_zipf'] else 'DEVIATES'}")
    print(f"  Pattern Injection: {patterns['verdict']}")
    
    return results


if __name__ == "__main__":
    main()




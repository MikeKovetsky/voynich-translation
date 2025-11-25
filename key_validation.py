import json
import re
from collections import Counter, defaultdict
import math

EVA_PHONETIC_MAP = {
    "o": "a", "k": "r", "y": "s", "t": "n", "e": "c", "l": "l", "m": "m",
    "a": "e", "i": "i", "d": "d", "c": "t", "q": "qu", "r": "i", "s": "b",
    "h": "h", "n": "n", "p": "p", "f": "f", "g": "g", "j": "j", "x": "x",
    "z": "z", "v": "v", "u": "u", "b": "b", "w": "w"
}

CLASTON_TO_EVA = {
    "o": "o", "a": "a", "s": "s", "f": "f", "i": "i", "n": "n",
    "9": "y", "8": "d", "h": "k", "k": "t", "e": "l", "y": "r",
    "c": "e", "4": "q", "g": "p", "p": "m", "1": "c", "2": "s"
}

PHONETIC_MAP = EVA_PHONETIC_MAP

LATIN_FREQS = {
    "i": 11.44, "e": 11.38, "a": 8.89, "t": 8.00, "s": 7.60, "n": 6.28,
    "r": 6.16, "u": 6.09, "o": 5.45, "m": 4.76, "c": 3.72, "l": 2.28,
    "d": 2.21, "p": 2.08, "b": 1.35, "q": 1.22, "v": 0.96, "f": 0.80,
    "g": 0.79, "h": 0.70, "x": 0.43, "y": 0.12, "z": 0.02
}

LATIN_BIGRAMS = {
    "qu": 1.8, "us": 1.5, "um": 1.4, "ae": 1.3, "is": 1.2, "it": 1.1,
    "es": 1.0, "er": 0.95, "nt": 0.9, "in": 0.85, "am": 0.8, "re": 0.75,
    "at": 0.7, "ti": 0.65, "em": 0.6, "et": 0.55, "te": 0.5, "or": 0.45,
    "st": 0.4, "ra": 0.38, "ta": 0.35, "de": 0.33, "en": 0.3, "ue": 0.28,
    "an": 0.25, "se": 0.22, "ar": 0.2, "al": 0.18, "ur": 0.16, "os": 0.15
}

LATIN_HERBAL = [
    "radix", "herba", "folium", "flos", "semen", "cortex", "succus",
    "oleum", "aqua", "bacca", "ramus", "fructus", "caulis", "stirps",
    "curat", "sanat", "valet", "prodest", "tollit", "solvit", "facit",
    "contra", "febris", "dolor", "ulcus", "tumor", "morbus",
    "calidus", "frigidus", "siccus", "humidus",
    "albus", "niger", "viridis", "rubeus"
]

def load_voynich_text():
    words = []
    try:
        with open("data/eva_ivtff.txt") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                if "\t" not in line:
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                text = parts[1]
                text = re.sub(r"\{[^}]*\}", "", text)
                text = re.sub(r"[!?=\-]", "", text)
                for word in text.split("."):
                    word = word.strip()
                    clean = re.sub(r"[^a-zA-Z]", "", word)
                    if clean and len(clean) >= 2:
                        words.append(clean.lower())
    except Exception as e:
        print(f"  Error loading: {e}")
    return words

def decode(word):
    result = []
    for ch in word:
        result.append(PHONETIC_MAP.get(ch, ch))
    return "".join(result)

def test_internal_consistency(words):
    results = {}
    key_chars = [("o", "a"), ("k", "r"), ("y", "s"), ("t", "n"), ("e", "c"),
                 ("l", "l"), ("m", "m"), ("a", "e"), ("i", "i"), ("d", "d"),
                 ("c", "t"), ("q", "qu"), ("r", "i"), ("s", "b")]
    
    for v_char, l_char in key_chars:
        words_starting = [w for w in words if w.startswith(v_char)]
        words_containing = [w for w in words if v_char in w]
        
        decoded_starting = [decode(w) for w in words_starting[:100]]
        
        valid_latin_starts = 0
        latin_start_examples = []
        for dec in decoded_starting[:50]:
            if dec.startswith(l_char):
                is_valid = any(
                    dec.startswith(lat[:min(3, len(lat))]) 
                    for lat in LATIN_HERBAL
                )
                if is_valid:
                    valid_latin_starts += 1
                    latin_start_examples.append(dec)
        
        char_positions = []
        for w in words[:500]:
            for i, ch in enumerate(w):
                if ch == v_char:
                    pos = "initial" if i == 0 else "medial" if i < len(w)-1 else "final"
                    char_positions.append(pos)
        
        pos_counts = Counter(char_positions)
        
        consistency = len(words_starting) / max(len(words_containing), 1)
        
        results[f"{v_char}_to_{l_char}"] = {
            "voynich_char": v_char,
            "latin_char": l_char,
            "words_starting": len(words_starting),
            "words_containing": len(words_containing),
            "position_distribution": dict(pos_counts),
            "valid_latin_starts": valid_latin_starts,
            "latin_examples": latin_start_examples[:10],
            "consistency_rate": round(consistency, 3)
        }
    
    return results

def test_anchor_words(words):
    anchors = {
        "oqo": {"expected": "aqua", "meaning": "water", "contexts": []},
        "daiin": {"expected": "deiin", "meaning": "of/from (de)", "contexts": []},
        "qokaiin": {"expected": "quareiin", "meaning": "herb (ablative)", "contexts": []},
        "oky": {"expected": "ars", "meaning": "Aries?", "contexts": []},
        "chol": {"expected": "tal", "meaning": "common word", "contexts": []},
        "shol": {"expected": "bal", "meaning": "common word", "contexts": []},
        "daiin": {"expected": "deiin", "meaning": "boundary word", "contexts": []},
    }
    
    text_str = " ".join(words)
    
    for anchor, info in anchors.items():
        count = words.count(anchor)
        info["occurrences"] = count
        info["decoded"] = decode(anchor)
        
        for i, w in enumerate(words):
            if w == anchor:
                ctx_start = max(0, i-3)
                ctx_end = min(len(words), i+4)
                ctx = words[ctx_start:ctx_end]
                decoded_ctx = [decode(x) for x in ctx]
                info["contexts"].append({
                    "voynich": " ".join(ctx),
                    "decoded": " ".join(decoded_ctx)
                })
                if len(info["contexts"]) >= 10:
                    break
        
        supporting = 0
        contradicting = 0
        
        if anchor == "o4o":
            for ctx in info["contexts"]:
                dec = ctx["decoded"]
                if any(herb in dec for herb in ["herb", "radi", "foli", "flor"]):
                    supporting += 1
                elif "num" in dec or "star" in dec:
                    contradicting += 1
        
        elif anchor == "8am":
            for ctx in info["contexts"]:
                dec = ctx["decoded"]
                if dec.count(" ") > 0:
                    supporting += 1
        
        info["supporting_contexts"] = supporting
        info["contradicting_contexts"] = contradicting
        info["confidence"] = supporting / max(supporting + contradicting, 1)
    
    return anchors

def test_frequency_distribution(words):
    decoded_words = [decode(w) for w in words]
    all_text = "".join(decoded_words).lower()
    
    total_chars = len(all_text)
    char_counts = Counter(all_text)
    
    decoded_freqs = {}
    for ch, count in char_counts.items():
        if ch.isalpha():
            decoded_freqs[ch] = round(count / total_chars * 100, 2)
    
    comparison = {}
    for ch in set(decoded_freqs.keys()) | set(LATIN_FREQS.keys()):
        if ch.isalpha():
            dec_f = decoded_freqs.get(ch, 0)
            lat_f = LATIN_FREQS.get(ch, 0)
            comparison[ch] = {
                "decoded": dec_f,
                "latin": lat_f,
                "difference": round(abs(dec_f - lat_f), 2)
            }
    
    dec_vals = [decoded_freqs.get(ch, 0) for ch in LATIN_FREQS.keys() if ch.isalpha()]
    lat_vals = [LATIN_FREQS.get(ch, 0) for ch in LATIN_FREQS.keys() if ch.isalpha()]
    
    n = len(dec_vals)
    if n > 0:
        mean_dec = sum(dec_vals) / n
        mean_lat = sum(lat_vals) / n
        
        num = sum((d - mean_dec) * (l - mean_lat) for d, l in zip(dec_vals, lat_vals))
        den_dec = math.sqrt(sum((d - mean_dec) ** 2 for d in dec_vals))
        den_lat = math.sqrt(sum((l - mean_lat) ** 2 for l in lat_vals))
        
        correlation = num / (den_dec * den_lat) if den_dec * den_lat > 0 else 0
    else:
        correlation = 0
    
    total_diff = sum(c["difference"] for c in comparison.values())
    avg_diff = total_diff / len(comparison) if comparison else 100
    
    return {
        "decoded_frequencies": decoded_freqs,
        "latin_frequencies": LATIN_FREQS,
        "comparison": comparison,
        "correlation": round(correlation, 3),
        "average_difference": round(avg_diff, 2),
        "total_chars_analyzed": total_chars
    }

def reverse_engineer_latin(words):
    reverse_map = {}
    for v, l in PHONETIC_MAP.items():
        if l not in reverse_map:
            reverse_map[l] = v
    
    def latin_to_voynich(latin_word):
        result = []
        i = 0
        while i < len(latin_word):
            if i < len(latin_word) - 1 and latin_word[i:i+2] == "qu":
                result.append("4")
                i += 2
            elif latin_word[i] in reverse_map:
                result.append(reverse_map[latin_word[i]])
            else:
                result.append(latin_word[i])
            i += 1
        return "".join(result)
    
    test_words = [
        ("radix", "root"),
        ("folium", "leaf"),
        ("curat", "cures"),
        ("herba", "herb"),
        ("aqua", "water"),
        ("flos", "flower"),
        ("contra", "against"),
        ("valet", "is effective"),
        ("dolor", "pain"),
        ("febris", "fever"),
    ]
    
    results = []
    word_set = set(words)
    
    for latin, meaning in test_words:
        predicted = latin_to_voynich(latin)
        
        found = predicted in word_set
        
        alternatives = []
        for w in word_set:
            if w.startswith(predicted[:3]) or decode(w).startswith(latin[:3]):
                alternatives.append({
                    "voynich": w,
                    "decoded": decode(w),
                    "similarity": round(sum(a == b for a, b in zip(decode(w), latin)) / max(len(decode(w)), len(latin)), 2)
                })
        
        alternatives = sorted(alternatives, key=lambda x: -x["similarity"])[:5]
        
        results.append({
            "latin": latin,
            "meaning": meaning,
            "predicted_voynich": predicted,
            "found_exact": found,
            "alternatives": alternatives,
            "best_match": alternatives[0] if alternatives else None
        })
    
    found_count = sum(1 for r in results if r["found_exact"])
    partial_count = sum(1 for r in results if r["best_match"] and r["best_match"]["similarity"] >= 0.5)
    
    return {
        "tests": results,
        "exact_matches": found_count,
        "partial_matches": partial_count,
        "success_rate": round((found_count + partial_count * 0.5) / len(results), 2)
    }

def test_alternative_mappings(words):
    alternatives = [
        ("k", "r", "l"),
        ("d", "d", "t"),
        ("q", "qu", "c"),
        ("r", "i", "e"),
        ("y", "s", "x"),
        ("a", "e", "a"),
    ]
    
    results = []
    
    for v_char, current, alt in alternatives:
        alt_map = PHONETIC_MAP.copy()
        alt_map[v_char] = alt
        
        def decode_alt(word):
            return "".join(alt_map.get(ch, ch) for ch in word)
        
        sample_words = [w for w in words if v_char in w][:100]
        
        current_latin_matches = 0
        alt_latin_matches = 0
        
        for w in sample_words:
            dec_current = decode(w)
            dec_alt = decode_alt(w)
            
            for lat in LATIN_HERBAL:
                if lat[:3] in dec_current:
                    current_latin_matches += 1
                    break
            
            for lat in LATIN_HERBAL:
                if lat[:3] in dec_alt:
                    alt_latin_matches += 1
                    break
        
        results.append({
            "voynich_char": v_char,
            "current_mapping": current,
            "alternative_mapping": alt,
            "words_tested": len(sample_words),
            "current_latin_matches": current_latin_matches,
            "alternative_latin_matches": alt_latin_matches,
            "current_better": current_latin_matches >= alt_latin_matches,
            "improvement_if_changed": alt_latin_matches - current_latin_matches
        })
    
    keep_current = sum(1 for r in results if r["current_better"])
    
    return {
        "alternatives_tested": results,
        "mappings_to_keep": keep_current,
        "mappings_to_change": len(results) - keep_current,
        "recommendation": "KEEP" if keep_current >= len(results) * 0.7 else "MODIFY"
    }

def calculate_bigrams(words):
    decoded_words = [decode(w) for w in words]
    
    bigram_counts = Counter()
    total_bigrams = 0
    
    for w in decoded_words:
        for i in range(len(w) - 1):
            bg = w[i:i+2].lower()
            if bg.isalpha():
                bigram_counts[bg] += 1
                total_bigrams += 1
    
    decoded_bigram_freqs = {}
    for bg, count in bigram_counts.most_common(50):
        decoded_bigram_freqs[bg] = round(count / total_bigrams * 100, 2)
    
    comparison = {}
    all_bigrams = set(decoded_bigram_freqs.keys()) | set(LATIN_BIGRAMS.keys())
    
    for bg in all_bigrams:
        dec_f = decoded_bigram_freqs.get(bg, 0)
        lat_f = LATIN_BIGRAMS.get(bg, 0)
        comparison[bg] = {
            "decoded": dec_f,
            "latin": lat_f,
            "difference": round(abs(dec_f - lat_f), 2)
        }
    
    common_latin = ["qu", "us", "um", "ae", "is", "it", "es", "er", "nt", "in"]
    matches = sum(1 for bg in common_latin if decoded_bigram_freqs.get(bg, 0) > 0.1)
    
    return {
        "decoded_bigrams": decoded_bigram_freqs,
        "latin_bigrams": LATIN_BIGRAMS,
        "comparison": dict(sorted(comparison.items(), key=lambda x: -max(x[1]["decoded"], x[1]["latin"]))[:20]),
        "common_latin_bigrams_found": matches,
        "bigram_match_rate": round(matches / len(common_latin), 2)
    }

def calculate_validation_score(consistency, anchors, freqs, reverse, alts, bigrams):
    consistency_score = sum(
        1 for k, v in consistency.items() 
        if v["consistency_rate"] > 0.1
    ) / len(consistency) if consistency else 0
    
    anchor_score = sum(
        a["confidence"] for a in anchors.values()
    ) / len(anchors) if anchors else 0
    
    freq_score = max(0, (freqs["correlation"] + 1) / 2)
    
    reverse_score = reverse["success_rate"]
    
    alt_score = alts["mappings_to_keep"] / len(alts["alternatives_tested"]) if alts["alternatives_tested"] else 0
    
    bigram_score = bigrams["bigram_match_rate"]
    
    weights = {
        "consistency": 0.15,
        "anchors": 0.20,
        "frequency": 0.25,
        "reverse": 0.15,
        "alternatives": 0.10,
        "bigrams": 0.15
    }
    
    overall = (
        consistency_score * weights["consistency"] +
        anchor_score * weights["anchors"] +
        freq_score * weights["frequency"] +
        reverse_score * weights["reverse"] +
        alt_score * weights["alternatives"] +
        bigram_score * weights["bigrams"]
    )
    
    return {
        "consistency_score": round(consistency_score, 3),
        "anchor_score": round(anchor_score, 3),
        "frequency_score": round(freq_score, 3),
        "reverse_score": round(reverse_score, 3),
        "alternative_score": round(alt_score, 3),
        "bigram_score": round(bigram_score, 3),
        "overall_score": round(overall, 3),
        "verdict": "KEEP" if overall >= 0.5 else "MODIFY" if overall >= 0.3 else "REJECT"
    }

def main():
    print("=== Track 28: Phonetic Key Validation ===\n")
    
    print("Loading Voynich text...")
    words = load_voynich_text()
    print(f"  Loaded {len(words)} words")
    
    print("\n1. Testing internal consistency...")
    consistency = test_internal_consistency(words)
    print(f"  Tested {len(consistency)} character mappings")
    
    print("\n2. Testing anchor words...")
    anchors = test_anchor_words(words)
    print(f"  Tested {len(anchors)} anchor words")
    
    print("\n3. Testing frequency distribution...")
    freqs = test_frequency_distribution(words)
    print(f"  Correlation with Latin: {freqs['correlation']}")
    print(f"  Average frequency difference: {freqs['average_difference']}%")
    
    print("\n4. Reverse engineering Latin words...")
    reverse = reverse_engineer_latin(words)
    print(f"  Exact matches: {reverse['exact_matches']}/10")
    print(f"  Partial matches: {reverse['partial_matches']}/10")
    
    print("\n5. Testing alternative mappings...")
    alts = test_alternative_mappings(words)
    print(f"  Mappings to keep: {alts['mappings_to_keep']}/{len(alts['alternatives_tested'])}")
    
    print("\n6. Calculating bigram statistics...")
    bigrams = calculate_bigrams(words)
    print(f"  Common Latin bigrams found: {bigrams['common_latin_bigrams_found']}/10")
    
    print("\n7. Calculating overall validation score...")
    score = calculate_validation_score(consistency, anchors, freqs, reverse, alts, bigrams)
    print(f"  Overall score: {score['overall_score']}")
    print(f"  Verdict: {score['verdict']}")
    
    results = {
        "internal_consistency": consistency,
        "anchor_word_validation": anchors,
        "frequency_comparison": freqs,
        "reverse_engineering": reverse,
        "alternative_mappings_tested": alts,
        "bigram_analysis": bigrams,
        "validation_scores": score,
        "overall_validation_score": score["overall_score"],
        "recommendation": score["verdict"]
    }
    
    with open("results/phonetic_key_validation.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved results/phonetic_key_validation.json")
    
    report = generate_report(results)
    with open("results/phonetic_key_report.md", "w") as f:
        f.write(report)
    print("Saved results/phonetic_key_report.md")

def generate_report(results):
    score = results["validation_scores"]
    freqs = results["frequency_comparison"]
    reverse = results["reverse_engineering"]
    alts = results["alternative_mappings_tested"]
    bigrams = results["bigram_analysis"]
    
    report = """# Phonetic Key Validation Report

## Executive Summary

| Metric | Score | Status |
|--------|-------|--------|
"""
    report += f"| Overall Validation | **{score['overall_score']:.1%}** | {score['verdict']} |\n"
    report += f"| Consistency | {score['consistency_score']:.1%} | {'✓' if score['consistency_score'] > 0.5 else '⚠'} |\n"
    report += f"| Anchor Words | {score['anchor_score']:.1%} | {'✓' if score['anchor_score'] > 0.5 else '⚠'} |\n"
    report += f"| Frequency Match | {score['frequency_score']:.1%} | {'✓' if score['frequency_score'] > 0.5 else '⚠'} |\n"
    report += f"| Reverse Engineering | {score['reverse_score']:.1%} | {'✓' if score['reverse_score'] > 0.3 else '⚠'} |\n"
    report += f"| Alternative Mappings | {score['alternative_score']:.1%} | {'✓' if score['alternative_score'] > 0.5 else '⚠'} |\n"
    report += f"| Bigram Match | {score['bigram_score']:.1%} | {'✓' if score['bigram_score'] > 0.3 else '⚠'} |\n"
    
    report += f"""
## Recommendation: **{score['verdict']}**

"""
    
    if score['verdict'] == "KEEP":
        report += "The phonetic key shows acceptable validation scores. Continue with current mapping.\n\n"
    elif score['verdict'] == "MODIFY":
        report += "The phonetic key shows mixed results. Consider modifying specific mappings.\n\n"
    else:
        report += "The phonetic key fails validation. Major revision needed.\n\n"
    
    report += """## 1. Internal Consistency Analysis

| Mapping | Words Starting | Words Containing | Valid Latin Starts |
|---------|----------------|------------------|-------------------|
"""
    for key, data in results["internal_consistency"].items():
        report += f"| {data['voynich_char']}→{data['latin_char']} | {data['words_starting']} | {data['words_containing']} | {data['valid_latin_starts']} |\n"
    
    report += """
## 2. Anchor Word Re-validation

| Anchor | Decoded | Expected | Occurrences | Supporting | Contradicting |
|--------|---------|----------|-------------|------------|---------------|
"""
    for anchor, data in results["anchor_word_validation"].items():
        report += f"| `{anchor}` | {data['decoded']} | {data['expected']} | {data['occurrences']} | {data['supporting_contexts']} | {data['contradicting_contexts']} |\n"
    
    report += f"""
## 3. Frequency Distribution

**Correlation with Latin:** {freqs['correlation']:.3f}
**Average Difference:** {freqs['average_difference']}%

### Top 10 Letter Frequencies

| Letter | Decoded % | Latin % | Difference |
|--------|-----------|---------|------------|
"""
    comparison = sorted(freqs['comparison'].items(), key=lambda x: -x[1]['latin'])[:10]
    for ch, data in comparison:
        report += f"| {ch} | {data['decoded']:.1f} | {data['latin']:.1f} | {data['difference']:.1f} |\n"
    
    report += f"""
## 4. Reverse Engineering Test

**Exact Matches:** {reverse['exact_matches']}/10
**Partial Matches:** {reverse['partial_matches']}/10
**Success Rate:** {reverse['success_rate']:.0%}

| Latin | Predicted | Found | Best Alternative |
|-------|-----------|-------|------------------|
"""
    for test in reverse['tests']:
        best = test['best_match']['voynich'] if test['best_match'] else "-"
        found = "✓" if test['found_exact'] else "✗"
        report += f"| {test['latin']} | `{test['predicted_voynich']}` | {found} | `{best}` |\n"
    
    report += f"""
## 5. Alternative Mapping Tests

| Current | Alternative | Current Matches | Alt Matches | Keep? |
|---------|-------------|-----------------|-------------|-------|
"""
    for alt in alts['alternatives_tested']:
        keep = "✓" if alt['current_better'] else "✗"
        report += f"| {alt['voynich_char']}→{alt['current_mapping']} | {alt['voynich_char']}→{alt['alternative_mapping']} | {alt['current_latin_matches']} | {alt['alternative_latin_matches']} | {keep} |\n"
    
    report += f"""
**Recommendation:** {alts['recommendation']}

## 6. Bigram Analysis

**Common Latin Bigrams Found:** {bigrams['common_latin_bigrams_found']}/10

### Top Decoded Bigrams

| Bigram | Decoded % | Latin % |
|--------|-----------|---------|
"""
    for bg, freq in list(bigrams['decoded_bigrams'].items())[:15]:
        lat = bigrams['latin_bigrams'].get(bg, 0)
        report += f"| {bg} | {freq:.2f} | {lat:.2f} |\n"
    
    report += f"""
## Critical Issues Identified

"""
    issues = []
    
    if freqs['correlation'] < 0.3:
        issues.append("⚠ **Low frequency correlation** - Decoded letter frequencies don't match Latin well")
    
    if reverse['exact_matches'] == 0:
        issues.append("⚠ **No exact reverse matches** - Can't find predicted Voynich forms for Latin words")
    
    if bigrams['bigram_match_rate'] < 0.3:
        issues.append("⚠ **Low bigram match** - Common Latin letter pairs are underrepresented")
    
    changes_suggested = [a for a in alts['alternatives_tested'] if not a['current_better']]
    if changes_suggested:
        for a in changes_suggested:
            issues.append(f"⚠ **Consider changing** {a['voynich_char']}→{a['current_mapping']} to {a['voynich_char']}→{a['alternative_mapping']}")
    
    if not issues:
        issues.append("✓ No critical issues identified")
    
    for issue in issues:
        report += f"{issue}\n\n"
    
    report += f"""
## Conclusion

The phonetic key validation produced an overall score of **{score['overall_score']:.1%}**.

"""
    if score['overall_score'] >= 0.5:
        report += """While the key shows reasonable statistical properties, the inability to produce 
readable Latin text suggests additional factors at play:
- The text may use heavy abbreviation
- Additional cipher layers may exist
- The underlying language may not be classical Latin

Further investigation recommended with focus on abbreviation patterns and word-by-word context analysis.
"""
    else:
        report += """The key validation failed to demonstrate sufficient statistical alignment with Latin.
Consider:
1. Re-examining the fundamental mapping assumptions
2. Testing alternative language hypotheses
3. Looking for additional encoding layers
"""
    
    return report

if __name__ == "__main__":
    main()

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

DATA_FILE = "data/eva_ivtff.txt"
RESULTS_DIR = Path("results")

HEBREW_GEMATRIA = {
    'alef': 1, 'bet': 2, 'gimel': 3, 'dalet': 4, 'he': 5,
    'vav': 6, 'zayin': 7, 'het': 8, 'tet': 9, 'yod': 10,
    'kaf': 20, 'lamed': 30, 'mem': 40, 'nun': 50, 'samekh': 60,
    'ayin': 70, 'pe': 80, 'tsade': 90, 'qof': 100, 'resh': 200,
    'shin': 300, 'tav': 400
}

EVA_TO_HEBREW = {
    'o': ('yod', 10), 'e': ('he', 5), 'h': ('vav', 6), 'a': ('mem', 40),
    'y': ('lamed', 30), 'c': ('alef', 1), 'l': ('resh', 200), 'd': ('bet', 2),
    'k': ('nun', 50), 's': ('shin', 300), 'i': ('tav', 400), 't': ('kaf', 20),
    'r': ('ayin', 70), 'n': ('nun', 50), 'p': ('het', 8), 'q': ('samekh', 60),
    'f': ('pe', 80), 'm': ('gimel', 3), 'g': ('zayin', 7), 'u': ('tsade', 90),
    'x': ('tet', 9)
}

SACRED_NUMBERS = {
    18: "chai (life)",
    26: "YHVH (God name)",
    36: "2x chai",
    72: "shem ha-meforash (72 names of God)",
    137: "kabbalah",
    216: "gevurah (strength) - 6^3",
    231: "gates of Sefer Yetzirah",
    314: "Shaddai",
    358: "Mashiach (Messiah)",
    248: "positive commandments",
    365: "negative commandments / days in year",
    400: "tav (end)",
    613: "total commandments"
}

HEBREW_ALPHABET = 'אבגדהוזחטיכלמנסעפצקרשת'
HEBREW_REVERSE = HEBREW_ALPHABET[::-1]

EVA_ALPHABET = 'oehaycdlksitrmnpqfgux'


def load_voynich_text():
    words = []
    lines = []
    paragraphs = defaultdict(list)
    
    with open(DATA_FILE, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            if not line.startswith('<f'):
                continue
            
            match = re.match(r'<(f\d+[rv]\d?)', line)
            if not match:
                continue
            folio = match.group(1)
            
            tab_pos = line.find('\t')
            if tab_pos == -1:
                continue
            text = line[tab_pos+1:].strip()
            text = re.sub(r'[<>{}!\[\]?\'"]', '', text)
            text = re.sub(r'@\w+', '', text)
            text = re.sub(r'\d+', '', text)
            
            line_words = [w for w in text.split('.') if w and len(w) > 0]
            clean_words = []
            for w in line_words:
                clean = ''.join(c for c in w.lower() if c in EVA_ALPHABET)
                if clean:
                    clean_words.append(clean)
            
            if clean_words:
                words.extend(clean_words)
                lines.append(clean_words)
                paragraphs[folio].append(clean_words)
    
    return words, lines, paragraphs


def calc_gematria(word):
    total = 0
    for char in word.lower():
        if char in EVA_TO_HEBREW:
            total += EVA_TO_HEBREW[char][1]
    return total


def gematria_analysis(words):
    word_values = {}
    for word in set(words):
        word_values[word] = calc_gematria(word)
    
    value_dist = Counter(word_values.values())
    
    sacred_found = {}
    for value, meaning in SACRED_NUMBERS.items():
        matching = [w for w, v in word_values.items() if v == value]
        if matching:
            sacred_found[value] = {
                "meaning": meaning,
                "count": len(matching),
                "words": matching[:20]
            }
    
    value_pairs = defaultdict(list)
    for w, v in word_values.items():
        if len(w) >= 3:
            value_pairs[v].append(w)
    related_words = {v: ws for v, ws in value_pairs.items() if len(ws) >= 3}
    
    return {
        "glyph_values": {k: v[1] for k, v in EVA_TO_HEBREW.items()},
        "value_distribution": dict(value_dist.most_common(30)),
        "sacred_numbers_found": sacred_found,
        "related_by_gematria": {k: v[:10] for k, v in list(related_words.items())[:20]},
        "sample_words": [{"word": w, "gematria": v} for w, v in list(word_values.items())[:30]]
    }


def build_atbash_map():
    atbash = {}
    for i, char in enumerate(EVA_ALPHABET):
        atbash[char] = EVA_ALPHABET[-(i+1)]
    return atbash


def build_albam_map():
    albam = {}
    half = len(EVA_ALPHABET) // 2
    for i in range(half):
        albam[EVA_ALPHABET[i]] = EVA_ALPHABET[i + half]
        albam[EVA_ALPHABET[i + half]] = EVA_ALPHABET[i]
    if len(EVA_ALPHABET) % 2 == 1:
        albam[EVA_ALPHABET[half]] = EVA_ALPHABET[half]
    return albam


def build_avgad_map():
    avgad = {}
    for i, char in enumerate(EVA_ALPHABET):
        avgad[char] = EVA_ALPHABET[(i + 1) % len(EVA_ALPHABET)]
    return avgad


def apply_temurah(word, mapping):
    return ''.join(mapping.get(c, c) for c in word)


def temurah_analysis(words):
    atbash = build_atbash_map()
    albam = build_albam_map()
    avgad = build_avgad_map()
    
    unique_words = set(words)
    
    atbash_results = []
    albam_results = []
    avgad_results = []
    
    for word in list(unique_words)[:500]:
        atbash_word = apply_temurah(word, atbash)
        if atbash_word in unique_words and atbash_word != word:
            atbash_results.append({"original": word, "atbash": atbash_word})
        
        albam_word = apply_temurah(word, albam)
        if albam_word in unique_words and albam_word != word:
            albam_results.append({"original": word, "albam": albam_word})
        
        avgad_word = apply_temurah(word, avgad)
        if avgad_word in unique_words and avgad_word != word:
            avgad_results.append({"original": word, "avgad": avgad_word})
    
    return {
        "atbash_mapping": atbash,
        "albam_mapping": albam,
        "avgad_mapping": avgad,
        "atbash_pairs": atbash_results[:20],
        "albam_pairs": albam_results[:20],
        "avgad_pairs": avgad_results[:20],
        "atbash_count": len(atbash_results),
        "albam_count": len(albam_results),
        "avgad_count": len(avgad_results)
    }


def notarikon_analysis(words, lines):
    initial_letters = [w[0] for w in words if w]
    final_letters = [w[-1] for w in words if w]
    
    initial_freq = Counter(initial_letters)
    final_freq = Counter(final_letters)
    
    three_letter = [w for w in words if len(w) == 3]
    three_letter_freq = Counter(three_letter)
    
    line_initials = []
    line_finals = []
    for line_words in lines:
        if line_words:
            initials = ''.join(w[0] for w in line_words if w)
            finals = ''.join(w[-1] for w in line_words if w)
            line_initials.append(initials)
            line_finals.append(finals)
    
    initial_bigrams = Counter()
    initial_trigrams = Counter()
    for init in line_initials:
        for i in range(len(init) - 1):
            initial_bigrams[init[i:i+2]] += 1
        for i in range(len(init) - 2):
            initial_trigrams[init[i:i+3]] += 1
    
    return {
        "initial_letter_frequency": dict(initial_freq.most_common(15)),
        "final_letter_frequency": dict(final_freq.most_common(15)),
        "three_letter_words": dict(three_letter_freq.most_common(30)),
        "three_letter_count": len(three_letter),
        "line_initial_patterns": {
            "sample": line_initials[:20],
            "common_bigrams": dict(initial_bigrams.most_common(20)),
            "common_trigrams": dict(initial_trigrams.most_common(20))
        },
        "abbreviation_candidates": [
            {"word": w, "count": c, "possible_expansion": f"{w[0]}-{w[1]}-{w[2]}"}
            for w, c in three_letter_freq.most_common(20)
        ]
    }


def structural_analysis(words, lines, paragraphs):
    line_word_counts = [len(line) for line in lines]
    line_count_freq = Counter(line_word_counts)
    
    para_word_counts = {}
    para_line_counts = {}
    for folio, para_lines in paragraphs.items():
        para_line_counts[folio] = len(para_lines)
        para_word_counts[folio] = sum(len(line) for line in para_lines)
    
    para_initials = {}
    for folio, para_lines in list(paragraphs.items())[:20]:
        initials = ''.join(line[0][0] if line and line[0] else '' for line in para_lines)
        para_initials[folio] = initials
    
    sacred_line_counts = {}
    for value, meaning in SACRED_NUMBERS.items():
        folios = [f for f, c in para_word_counts.items() if c == value]
        if folios:
            sacred_line_counts[value] = {"meaning": meaning, "folios": folios[:5]}
    
    return {
        "line_word_count_distribution": dict(line_count_freq.most_common(20)),
        "average_words_per_line": sum(line_word_counts) / len(line_word_counts) if line_word_counts else 0,
        "paragraph_word_counts": dict(list(para_word_counts.items())[:30]),
        "paragraph_line_counts": dict(list(para_line_counts.items())[:30]),
        "paragraph_initial_letters": para_initials,
        "sacred_number_paragraphs": sacred_line_counts,
        "total_lines": len(lines),
        "total_words": len(words)
    }


def sefer_yetzirah_patterns(words):
    three_letter = [w for w in words if len(w) == 3]
    root_freq = Counter(three_letter)
    
    letter_combinations = defaultdict(int)
    for word in three_letter:
        sorted_letters = ''.join(sorted(word))
        letter_combinations[sorted_letters] += 1
    
    permutation_groups = defaultdict(list)
    for word in three_letter:
        key = ''.join(sorted(word))
        if word not in permutation_groups[key]:
            permutation_groups[key].append(word)
    
    groups_with_multiple = {k: v for k, v in permutation_groups.items() if len(v) > 1}
    
    doubled_letters = [w for w in words if any(w.count(c) >= 2 for c in set(w))]
    doubled_freq = Counter(doubled_letters)
    
    return {
        "three_letter_roots": dict(root_freq.most_common(30)),
        "letter_combination_frequency": dict(Counter(letter_combinations.values()).most_common(10)),
        "permutation_groups": {k: v for k, v in list(groups_with_multiple.items())[:20]},
        "permutation_group_count": len(groups_with_multiple),
        "doubled_letter_words": dict(doubled_freq.most_common(20)),
        "231_gates_note": "Sefer Yetzirah speaks of 231 gates (letter pairs). Testing coverage..."
    }


def calc_overall_score(gematria, temurah, notarikon, structural, sefer):
    scores = []
    
    sacred_count = len(gematria.get("sacred_numbers_found", {}))
    sacred_score = min(sacred_count / 8, 1.0)
    scores.append(("sacred_numbers", sacred_score))
    
    temurah_pairs = (temurah.get("atbash_count", 0) + 
                    temurah.get("albam_count", 0) + 
                    temurah.get("avgad_count", 0))
    temurah_score = min(temurah_pairs / 30, 1.0)
    scores.append(("temurah_patterns", temurah_score))
    
    three_letter = notarikon.get("three_letter_count", 0)
    notarikon_score = min(three_letter / 500, 1.0)
    scores.append(("notarikon_candidates", notarikon_score))
    
    sacred_paras = len(structural.get("sacred_number_paragraphs", {}))
    structural_score = min(sacred_paras / 5, 1.0)
    scores.append(("structural_sacred", structural_score))
    
    perm_groups = sefer.get("permutation_group_count", 0)
    sefer_score = min(perm_groups / 50, 1.0)
    scores.append(("sefer_yetzirah_patterns", sefer_score))
    
    avg_score = sum(s[1] for s in scores) / len(scores)
    
    return {
        "component_scores": dict(scores),
        "overall_score": round(avg_score, 3),
        "interpretation": interpret_score(avg_score)
    }


def interpret_score(score):
    if score >= 0.7:
        return "STRONG Kabbalistic encoding likely"
    elif score >= 0.5:
        return "MODERATE Kabbalistic patterns detected"
    elif score >= 0.3:
        return "WEAK Kabbalistic indicators"
    else:
        return "NO significant Kabbalistic patterns"


def main():
    print("Loading Voynich text...")
    words, lines, paragraphs = load_voynich_text()
    print(f"Loaded {len(words)} words, {len(lines)} lines, {len(paragraphs)} folios")
    
    print("\n=== GEMATRIA ANALYSIS ===")
    gematria = gematria_analysis(words)
    print(f"Sacred numbers found: {len(gematria['sacred_numbers_found'])}")
    for value, data in gematria["sacred_numbers_found"].items():
        print(f"  {value} ({data['meaning']}): {data['count']} words")
    
    print("\n=== TEMURAH ANALYSIS ===")
    temurah = temurah_analysis(words)
    print(f"Atbash pairs: {temurah['atbash_count']}")
    print(f"Albam pairs: {temurah['albam_count']}")
    print(f"Avgad pairs: {temurah['avgad_count']}")
    
    print("\n=== NOTARIKON ANALYSIS ===")
    notarikon = notarikon_analysis(words, lines)
    print(f"Three-letter words (potential acronyms): {notarikon['three_letter_count']}")
    print(f"Top initial letters: {list(notarikon['initial_letter_frequency'].items())[:5]}")
    print(f"Top final letters: {list(notarikon['final_letter_frequency'].items())[:5]}")
    
    print("\n=== STRUCTURAL ANALYSIS ===")
    structural = structural_analysis(words, lines, paragraphs)
    print(f"Average words per line: {structural['average_words_per_line']:.2f}")
    print(f"Paragraphs with sacred word counts: {len(structural['sacred_number_paragraphs'])}")
    
    print("\n=== SEFER YETZIRAH PATTERNS ===")
    sefer = sefer_yetzirah_patterns(words)
    print(f"Permutation groups: {sefer['permutation_group_count']}")
    print(f"Sample groups: {list(sefer['permutation_groups'].items())[:3]}")
    
    print("\n=== OVERALL ASSESSMENT ===")
    assessment = calc_overall_score(gematria, temurah, notarikon, structural, sefer)
    print(f"Component scores:")
    for comp, score in assessment["component_scores"].items():
        print(f"  {comp}: {score:.3f}")
    print(f"\nOVERALL KABBALISTIC SCORE: {assessment['overall_score']}")
    print(f"VERDICT: {assessment['interpretation']}")
    
    results = {
        "gematria": gematria,
        "temurah": temurah,
        "notarikon": notarikon,
        "structural": structural,
        "sefer_yetzirah": sefer,
        "overall_assessment": assessment
    }
    
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "kabbalistic_analysis.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {RESULTS_DIR}/kabbalistic_analysis.json")
    return results


if __name__ == "__main__":
    main()

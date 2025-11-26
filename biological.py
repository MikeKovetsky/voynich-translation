#!/usr/bin/env python3
"""Track 66: Biological Section Exploration - analyze untouched human figure pages."""

import json
import re
from collections import defaultdict
from pathlib import Path

EVA_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/clean_dictionary.json"
OUTPUT_JSON = "results/biological_section.json"
OUTPUT_MD = "results/biological_section_report.md"

BIO_FOLIOS = [f"f{i}r" for i in range(75, 85)] + [f"f{i}v" for i in range(75, 85)]

BODY_PARTS = {
    "hand": {"hebrew": "yad", "italian": "mano", "skeletons": ["yd", "mn"]},
    "foot": {"hebrew": "regel", "italian": "piede", "skeletons": ["rgl", "pyd", "pd"]},
    "head": {"hebrew": "rosh", "italian": "testa", "skeletons": ["rsh", "tst"]},
    "heart": {"hebrew": "lev", "italian": "cuore", "skeletons": ["lv", "kr", "kwr"]},
    "blood": {"hebrew": "dam", "italian": "sangue", "skeletons": ["dm", "sng"]},
    "womb": {"hebrew": "rechem", "italian": "utero", "skeletons": ["rchm", "tr"]},
    "water": {"hebrew": "mayim", "italian": "acqua", "skeletons": ["mm", "mym", "kw", "akw"]},
    "belly": {"hebrew": "beten", "italian": "ventre", "skeletons": ["btn", "vntr"]},
    "skin": {"hebrew": "or", "italian": "pelle", "skeletons": ["wr", "pl"]},
    "eye": {"hebrew": "ayin", "italian": "occhio", "skeletons": ["yn", "kh"]},
    "breast": {"hebrew": "shad", "italian": "seno", "skeletons": ["shd", "sn"]},
    "navel": {"hebrew": "tabur", "italian": "ombelico", "skeletons": ["tbr", "mblk"]},
    "hip": {"hebrew": "yarekh", "italian": "fianco", "skeletons": ["yrk", "fnk"]},
    "arm": {"hebrew": "zeroa", "italian": "braccio", "skeletons": ["zr", "brch"]},
    "leg": {"hebrew": "shok", "italian": "gamba", "skeletons": ["shk", "gmb"]},
}

BATHING_VOCAB = {
    "bath": {"hebrew": "merchatz", "italian": "bagno", "skeletons": ["mrchtz", "bgn"]},
    "water": {"hebrew": "mayim", "italian": "acqua", "skeletons": ["mm", "mym", "kw"]},
    "wash": {"hebrew": "rachatz", "italian": "lavare", "skeletons": ["rchtz", "lvr"]},
    "clean": {"hebrew": "tahor", "italian": "pulito", "skeletons": ["thr", "plt"]},
    "mikveh": {"hebrew": "mikveh", "italian": "", "skeletons": ["mkv", "mkwh"]},
    "pool": {"hebrew": "breicha", "italian": "piscina", "skeletons": ["brk", "pscn"]},
    "pour": {"hebrew": "shafakh", "italian": "versare", "skeletons": ["shfk", "vrsr"]},
    "flow": {"hebrew": "nahar", "italian": "flusso", "skeletons": ["nhr", "fls"]},
    "tube": {"hebrew": "tzinor", "italian": "tubo", "skeletons": ["tznr", "tb"]},
    "vessel": {"hebrew": "keli", "italian": "vaso", "skeletons": ["kl", "vs"]},
}

HUMORAL_VOCAB = {
    "blood": {"hebrew": "dam", "italian": "sangue", "skeletons": ["dm", "sng"]},
    "phlegm": {"hebrew": "leichah", "italian": "flemma", "skeletons": ["lych", "flm"]},
    "bile": {"hebrew": "marah", "italian": "bile", "skeletons": ["mrh", "bl"]},
    "health": {"hebrew": "briut", "italian": "salute", "skeletons": ["bryt", "slt"]},
    "humor": {"hebrew": "lach", "italian": "umore", "skeletons": ["lch", "mr"]},
    "heat": {"hebrew": "chom", "italian": "calore", "skeletons": ["chm", "klr"]},
    "cold": {"hebrew": "kor", "italian": "freddo", "skeletons": ["kr", "frd"]},
    "wet": {"hebrew": "lach", "italian": "umido", "skeletons": ["lch", "md"]},
    "dry": {"hebrew": "yavesh", "italian": "secco", "skeletons": ["yvsh", "sk"]},
    "sick": {"hebrew": "choleh", "italian": "malato", "skeletons": ["chl", "mlt"]},
    "cure": {"hebrew": "refuah", "italian": "cura", "skeletons": ["rfh", "kr"]},
}


def load_dictionary():
    """Load clean dictionary."""
    if not Path(DICT_FILE).exists():
        raise FileNotFoundError(f"Dictionary not found: {DICT_FILE}")
    
    with open(DICT_FILE) as f:
        data = json.load(f)
    return data.get("entries", {})


def load_biological_text():
    """Load text from biological section folios."""
    folios = {}
    labels = {}
    paragraphs = {}
    
    with open(EVA_FILE) as f:
        content = f.read()
    
    for folio in BIO_FOLIOS:
        folio_pattern = rf"<{folio}\.[^>]+;H>\s+([^\n]+)"
        matches = re.findall(folio_pattern, content)
        
        lines = []
        folio_labels = []
        folio_paragraphs = []
        
        for match in matches:
            text = match.strip()
            text = re.sub(r"[<>!?\[\]{}]", "", text)
            text = re.sub(r"\s+", ".", text)
            
            if text:
                lines.append(text)
                words = [w for w in text.split(".") if w and len(w) > 1]
                
                if len(words) <= 3:
                    folio_labels.extend(words)
                else:
                    folio_paragraphs.extend(words)
        
        if lines:
            folios[folio] = lines
            labels[folio] = folio_labels
            paragraphs[folio] = folio_paragraphs
    
    return folios, labels, paragraphs


def extract_words(folios):
    """Extract all words from biological section."""
    all_words = []
    for folio, lines in folios.items():
        for line in lines:
            words = [w for w in line.split(".") if w and len(w) > 1]
            all_words.extend(words)
    return all_words


def apply_dictionary(words, dictionary):
    """Apply dictionary and calculate coverage."""
    translated = 0
    translations = {}
    untranslated = []
    
    for word in words:
        word_clean = word.lower()
        if word_clean in dictionary:
            translated += 1
            entry = dictionary[word_clean]
            translations[word_clean] = entry.get("meaning", "?")
        else:
            untranslated.append(word_clean)
    
    coverage = translated / len(words) if words else 0
    
    freq = defaultdict(int)
    for w in untranslated:
        freq[w] += 1
    top_untranslated = sorted(freq.items(), key=lambda x: -x[1])[:50]
    
    return {
        "total_words": len(words),
        "translated": translated,
        "coverage_rate": round(coverage, 3),
        "translations_found": translations,
        "top_untranslated": top_untranslated,
    }


def get_consonant_skeleton(word):
    """Extract consonant skeleton from word."""
    vowels = "aeiouy"
    return "".join(c for c in word.lower() if c not in vowels)


def search_vocabulary(words, vocab_dict, category):
    """Search for vocabulary matches in word list."""
    matches = []
    
    for word in words:
        word_clean = word.lower()
        skeleton = get_consonant_skeleton(word_clean)
        
        for term, data in vocab_dict.items():
            for skel in data.get("skeletons", []):
                if skeleton == skel or skeleton.startswith(skel) or skeleton.endswith(skel):
                    matches.append({
                        "voynich_word": word,
                        "skeleton": skeleton,
                        "matched_skeleton": skel,
                        "possible_term": term,
                        "hebrew": data.get("hebrew", ""),
                        "italian": data.get("italian", ""),
                    })
                    break
    
    deduped = {}
    for m in matches:
        key = (m["voynich_word"], m["possible_term"])
        if key not in deduped:
            deduped[key] = m
    
    return list(deduped.values())


def analyze_labels(labels):
    """Analyze labels near figures."""
    all_labels = []
    for folio, label_list in labels.items():
        for label in label_list:
            all_labels.append({"folio": folio, "label": label})
    
    freq = defaultdict(int)
    for item in all_labels:
        freq[item["label"]] += 1
    
    common = sorted(freq.items(), key=lambda x: -x[1])[:30]
    
    return {
        "total_labels": len(all_labels),
        "unique_labels": len(freq),
        "most_common": common,
        "label_list": all_labels[:100],
    }


def cross_reference_recipes():
    """Load recipe section words for comparison."""
    recipe_folios = [f"f{i}r" for i in range(103, 117)] + [f"f{i}v" for i in range(103, 117)]
    
    with open(EVA_FILE) as f:
        content = f.read()
    
    recipe_words = set()
    for folio in recipe_folios:
        pattern = rf"<{folio}\.[^>]+;H>\s+([^\n]+)"
        matches = re.findall(pattern, content)
        
        for match in matches:
            text = re.sub(r"[<>!?\[\]{}]", "", match)
            words = [w for w in re.split(r"[.\-=,\s]", text) if w and len(w) > 1]
            recipe_words.update(w.lower() for w in words)
    
    return recipe_words


def compare_with_recipes(bio_words, recipe_words):
    """Compare biological section with recipes."""
    bio_set = set(w.lower() for w in bio_words)
    
    overlap = bio_set & recipe_words
    bio_only = bio_set - recipe_words
    
    overlap_list = sorted(overlap)
    bio_only_list = sorted(bio_only)
    
    overlap_rate = len(overlap) / len(bio_set) if bio_set else 0
    
    return {
        "biological_unique_words": len(bio_set),
        "recipe_unique_words": len(recipe_words),
        "overlap_count": len(overlap),
        "overlap_rate": round(overlap_rate, 3),
        "shared_vocabulary": overlap_list[:100],
        "biological_only_sample": bio_only_list[:50],
    }


def suggest_new_vocabulary(untranslated, body_matches, bathing_matches, humoral_matches):
    """Suggest new vocabulary entries based on analysis."""
    suggestions = []
    
    all_matches = body_matches + bathing_matches + humoral_matches
    
    seen = set()
    for match in all_matches:
        word = match["voynich_word"]
        if word not in seen:
            seen.add(word)
            suggestions.append({
                "voynich": word,
                "suggested_meaning": match["possible_term"],
                "source_hebrew": match["hebrew"],
                "source_italian": match["italian"],
                "matched_skeleton": match["matched_skeleton"],
                "confidence": "low",
            })
    
    for word, count in untranslated[:30]:
        if word not in seen:
            skeleton = get_consonant_skeleton(word)
            suggestions.append({
                "voynich": word,
                "frequency": count,
                "skeleton": skeleton,
                "suggested_meaning": "?",
                "confidence": "needs_research",
            })
    
    return suggestions[:50]


def generate_report(results):
    """Generate markdown report."""
    lines = [
        "# Track 66: Biological Section Exploration",
        "",
        "## Purpose",
        "Explore the BIOLOGICAL section (f75r-f84v) - previously untouched by our analysis.",
        "This section shows nude female figures, bathing pools, and connecting tubes.",
        "",
        "## Section Overview",
        "",
        f"- **Folios analyzed**: {', '.join(results['folios_analyzed'])}",
        f"- **Total words**: {results['coverage']['total_words']}",
        f"- **Dictionary coverage**: {results['coverage']['coverage_rate']*100:.1f}%",
        "",
        "## Coverage Analysis",
        "",
        f"Applied our clean dictionary ({results['dictionary_size']} entries) to biological section:",
        "",
        f"- **Words translated**: {results['coverage']['translated']}",
        f"- **Coverage rate**: {results['coverage']['coverage_rate']*100:.1f}%",
        "",
    ]
    
    other_sections = [
        ("Botanical", 0.389),
        ("Recipes", 0.509),
    ]
    
    lines.extend([
        "### Comparison with Other Sections",
        "",
        "| Section | Coverage |",
        "|---------|----------|",
        f"| **Biological** | **{results['coverage']['coverage_rate']*100:.1f}%** |",
    ])
    for name, rate in other_sections:
        lines.append(f"| {name} (Track 59) | {rate*100:.1f}% |")
    
    lines.extend([
        "",
        "## Body Part Vocabulary Search",
        "",
        f"Found **{len(results['body_part_matches'])}** potential body part matches:",
        "",
    ])
    
    if results['body_part_matches']:
        lines.append("| Voynich | Possible Term | Hebrew | Italian |")
        lines.append("|---------|---------------|--------|---------|")
        for m in results['body_part_matches'][:15]:
            lines.append(f"| {m['voynich_word']} | {m['possible_term']} | {m['hebrew']} | {m['italian']} |")
    else:
        lines.append("*No strong body part vocabulary matches found.*")
    
    lines.extend([
        "",
        "## Bathing/Water Vocabulary Search",
        "",
        f"Found **{len(results['bathing_vocabulary'])}** potential bathing/water matches:",
        "",
    ])
    
    if results['bathing_vocabulary']:
        lines.append("| Voynich | Possible Term | Hebrew | Italian |")
        lines.append("|---------|---------------|--------|---------|")
        for m in results['bathing_vocabulary'][:15]:
            lines.append(f"| {m['voynich_word']} | {m['possible_term']} | {m['hebrew']} | {m['italian']} |")
    else:
        lines.append("*No strong bathing vocabulary matches found.*")
    
    lines.extend([
        "",
        "## Humoral/Medical Vocabulary Search",
        "",
        f"Found **{len(results['humoral_vocabulary'])}** potential humoral/medical matches:",
        "",
    ])
    
    if results['humoral_vocabulary']:
        lines.append("| Voynich | Possible Term | Hebrew | Italian |")
        lines.append("|---------|---------------|--------|---------|")
        for m in results['humoral_vocabulary'][:15]:
            lines.append(f"| {m['voynich_word']} | {m['possible_term']} | {m['hebrew']} | {m['italian']} |")
    
    lines.extend([
        "",
        "## Label Analysis",
        "",
        f"- **Total labels identified**: {results['labels_found']['total_labels']}",
        f"- **Unique labels**: {results['labels_found']['unique_labels']}",
        "",
        "### Most Common Labels",
        "",
        "| Label | Frequency |",
        "|-------|-----------|",
    ])
    
    for label, count in results['labels_found']['most_common'][:15]:
        lines.append(f"| {label} | {count} |")
    
    lines.extend([
        "",
        "## Cross-Reference with Recipes Section",
        "",
        f"- **Biological section unique words**: {results['cross_reference_recipes']['biological_unique_words']}",
        f"- **Recipe section unique words**: {results['cross_reference_recipes']['recipe_unique_words']}",
        f"- **Overlapping vocabulary**: {results['cross_reference_recipes']['overlap_count']}",
        f"- **Overlap rate**: {results['cross_reference_recipes']['overlap_rate']*100:.1f}%",
        "",
        "### Interpretation",
        "",
    ])
    
    overlap_rate = results['cross_reference_recipes']['overlap_rate']
    if overlap_rate > 0.5:
        lines.append("✅ **HIGH OVERLAP**: Biological and recipe sections share significant vocabulary.")
        lines.append("This suggests same author and possibly related content (medical treatments).")
    elif overlap_rate > 0.3:
        lines.append("⚠️ **MODERATE OVERLAP**: Some shared vocabulary, but sections have distinct content.")
    else:
        lines.append("❌ **LOW OVERLAP**: Sections use different vocabulary, possibly different topics or authors.")
    
    lines.extend([
        "",
        "### Shared Vocabulary Sample",
        "",
    ])
    
    shared = results['cross_reference_recipes']['shared_vocabulary'][:20]
    if shared:
        lines.append("| Word | Appears in Both Sections |")
        lines.append("|------|--------------------------|")
        for word in shared:
            lines.append(f"| {word} | ✓ |")
    
    lines.extend([
        "",
        "## New Vocabulary Candidates",
        "",
        "Based on consonant skeleton matching and frequency analysis:",
        "",
        "| Voynich | Suggested Meaning | Source | Confidence |",
        "|---------|-------------------|--------|------------|",
    ])
    
    for sug in results['new_vocabulary'][:20]:
        meaning = sug.get('suggested_meaning', '?')
        source = sug.get('source_hebrew', '') or sug.get('source_italian', '') or 'frequency'
        conf = sug.get('confidence', '?')
        lines.append(f"| {sug['voynich']} | {meaning} | {source} | {conf} |")
    
    lines.extend([
        "",
        "## Top Untranslated Words",
        "",
        "High-frequency words not in dictionary:",
        "",
        "| Word | Frequency | Skeleton |",
        "|------|-----------|----------|",
    ])
    
    for word, count in results['coverage']['top_untranslated'][:20]:
        skeleton = get_consonant_skeleton(word)
        lines.append(f"| {word} | {count} | {skeleton} |")
    
    lines.extend([
        "",
        "## Conclusions",
        "",
    ])
    
    coverage = results['coverage']['coverage_rate']
    body_matches = len(results['body_part_matches'])
    bathing_matches = len(results['bathing_vocabulary'])
    
    if coverage > 0.4:
        lines.append("✅ **Dictionary works on biological section** - similar coverage to other sections.")
    elif coverage > 0.25:
        lines.append("⚠️ **Partial dictionary coverage** - some unique vocabulary in this section.")
    else:
        lines.append("❌ **Low coverage** - biological section may use different vocabulary system.")
    
    if body_matches > 5 or bathing_matches > 5:
        lines.append("")
        lines.append("✅ **Body/bathing vocabulary detected** - content aligns with visual elements.")
        if bathing_matches > body_matches:
            lines.append("   Focus appears to be on *bathing/purification* rather than anatomy.")
        else:
            lines.append("   Focus appears to be on *anatomy/body parts*.")
    
    lines.extend([
        "",
        "### What This Section Might Represent",
        "",
        "Based on our analysis, possible interpretations:",
        "",
        "1. **Bathing/Hygiene Manual**: Instructions for ritual or medical bathing",
        "2. **Humoral Medicine**: Diagrams of body fluids and their circulation",
        "3. **Mikveh Instructions**: Jewish ritual bath procedures",
        "4. **Gynecological Treatise**: Female anatomy and health",
        "",
        "---",
        "*Generated by Track 66: Biological Section Exploration*",
    ])
    
    return "\n".join(lines)


def main():
    print("Track 66: Biological Section Exploration")
    print("=" * 50)
    
    print("\nLoading dictionary...")
    dictionary = load_dictionary()
    print(f"  Dictionary entries: {len(dictionary)}")
    
    print("\nLoading biological section text...")
    folios, labels, paragraphs = load_biological_text()
    print(f"  Folios found: {len(folios)}")
    
    for folio in sorted(folios.keys()):
        label_count = len(labels.get(folio, []))
        para_count = len(paragraphs.get(folio, []))
        print(f"    {folio}: {label_count} labels, {para_count} paragraph words")
    
    print("\nExtracting words...")
    all_words = extract_words(folios)
    print(f"  Total words: {len(all_words)}")
    
    print("\nApplying dictionary...")
    coverage = apply_dictionary(all_words, dictionary)
    print(f"  Coverage: {coverage['coverage_rate']*100:.1f}%")
    print(f"  Translated: {coverage['translated']}/{coverage['total_words']}")
    
    print("\nSearching for body part vocabulary...")
    body_matches = search_vocabulary(all_words, BODY_PARTS, "body")
    print(f"  Body part matches: {len(body_matches)}")
    
    print("\nSearching for bathing/water vocabulary...")
    bathing_matches = search_vocabulary(all_words, BATHING_VOCAB, "bathing")
    print(f"  Bathing matches: {len(bathing_matches)}")
    
    print("\nSearching for humoral/medical vocabulary...")
    humoral_matches = search_vocabulary(all_words, HUMORAL_VOCAB, "humoral")
    print(f"  Humoral matches: {len(humoral_matches)}")
    
    print("\nAnalyzing labels...")
    label_analysis = analyze_labels(labels)
    print(f"  Total labels: {label_analysis['total_labels']}")
    print(f"  Unique labels: {label_analysis['unique_labels']}")
    
    print("\nCross-referencing with recipes section...")
    recipe_words = cross_reference_recipes()
    cross_ref = compare_with_recipes(all_words, recipe_words)
    print(f"  Overlap rate: {cross_ref['overlap_rate']*100:.1f}%")
    print(f"  Shared vocabulary: {cross_ref['overlap_count']} words")
    
    print("\nGenerating new vocabulary suggestions...")
    new_vocab = suggest_new_vocabulary(
        coverage['top_untranslated'],
        body_matches,
        bathing_matches,
        humoral_matches
    )
    print(f"  Suggestions: {len(new_vocab)}")
    
    results = {
        "folios_analyzed": sorted(folios.keys()),
        "dictionary_size": dictionary,
        "coverage": coverage,
        "body_part_matches": body_matches,
        "bathing_vocabulary": bathing_matches,
        "humoral_vocabulary": humoral_matches,
        "labels_found": label_analysis,
        "cross_reference_recipes": cross_ref,
        "new_vocabulary": new_vocab,
        "folio_details": {
            folio: {
                "labels": labels.get(folio, []),
                "paragraph_words": paragraphs.get(folio, [])[:50],
            }
            for folio in folios.keys()
        },
    }
    
    results_for_json = {
        "folios_analyzed": results["folios_analyzed"],
        "dictionary_size": len(dictionary),
        "coverage": results["coverage"],
        "body_part_matches": results["body_part_matches"],
        "bathing_vocabulary": results["bathing_vocabulary"],
        "humoral_vocabulary": results["humoral_vocabulary"],
        "labels_found": results["labels_found"],
        "cross_reference_recipes": results["cross_reference_recipes"],
        "new_vocabulary": results["new_vocabulary"],
        "folio_details": results["folio_details"],
    }
    
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results_for_json, f, indent=2)
    print(f"\nSaved: {OUTPUT_JSON}")
    
    report = generate_report(results_for_json)
    with open(OUTPUT_MD, "w") as f:
        f.write(report)
    print(f"Saved: {OUTPUT_MD}")
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Folios analyzed: {len(folios)}")
    print(f"Total words: {len(all_words)}")
    print(f"Dictionary coverage: {coverage['coverage_rate']*100:.1f}%")
    print(f"Body part matches: {len(body_matches)}")
    print(f"Bathing matches: {len(bathing_matches)}")
    print(f"Humoral matches: {len(humoral_matches)}")
    print(f"Recipe overlap: {cross_ref['overlap_rate']*100:.1f}%")
    
    if body_matches:
        print("\nTop body part candidates:")
        for m in body_matches[:5]:
            print(f"  {m['voynich_word']} -> {m['possible_term']} ({m['hebrew']}/{m['italian']})")
    
    if bathing_matches:
        print("\nTop bathing/water candidates:")
        for m in bathing_matches[:5]:
            print(f"  {m['voynich_word']} -> {m['possible_term']} ({m['hebrew']}/{m['italian']})")


if __name__ == "__main__":
    main()




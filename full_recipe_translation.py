"""
Track 92: Full Recipe Translation (Grammar + Visual)
Translates the entire Recipe Section (f103-f116) using Grammar Frame + Visual Meanings.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from voynich_data import get_section_text

DICT_FILE = Path("results/master_dictionary_v4.json")
OUT_JSON = Path("results/full_recipe_translation.json")
OUT_MD = Path("results/full_recipe_report.md")

# VISUAL SEMANTIC OVERRIDES from Track 89 Low-Leakage Analysis
# These override phonetic guesses with visual evidence
VISUAL_OVERRIDES = {
    "char": {"meaning": "flower", "visual_pct": 0.93, "source": "visual:flowers"},
    "chl": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "chol": {"meaning": "leaf", "visual_pct": 0.93, "source": "visual:leaves"},
    "ar": {"meaning": "flower", "visual_pct": 0.97, "source": "visual:flowers"},
    "chor": {"meaning": "leaf", "visual_pct": 0.96, "source": "visual:leaves"},
    "cthor": {"meaning": "leaf", "visual_pct": 0.97, "source": "visual:leaves"},
    "cthy": {"meaning": "leaf", "visual_pct": 0.93, "source": "visual:leaves"},
    "cthol": {"meaning": "leaf", "visual_pct": 0.95, "source": "visual:leaves"},
    "sho": {"meaning": "root", "visual_pct": 0.89, "source": "visual:roots"},
    "chain": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "chaiin": {"meaning": "root", "visual_pct": 0.94, "source": "visual:roots"},
    "chan": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "ochor": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "qot": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "cphor": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "cphaiin": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "opchy": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "qotcho": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "kchy": {"meaning": "root", "visual_pct": 0.93, "source": "visual:roots"},
    "shaiin": {"meaning": "root", "visual_pct": 0.86, "source": "visual:roots"},
    "ypchedy": {"meaning": "root", "visual_pct": 1.0, "source": "visual:roots"},
    "chotaiin": {"meaning": "leaf", "visual_pct": 1.0, "source": "visual:leaves"},
    "qod": {"meaning": "flower", "visual_pct": 1.0, "source": "visual:flowers"},
    "chokchy": {"meaning": "flower", "visual_pct": 1.0, "source": "visual:flowers"},
    "cthar": {"meaning": "flower", "visual_pct": 0.71, "source": "visual:flowers"},
}

# Grammar elements from Track 89/90
VERBS = {"daiin", "dain", "sain", "tain"}
PREPOSITIONS = {"qok", "qokaiin", "qokain", "qokeey", "qokedy", "qoky", 
                "qokal", "qokchey", "qokchedy", "qokcheedy", "qokeeey", 
                "qokeedy", "qokan", "qokam", "qoked", "qokeo", "qokeod",
                "qokchor", "qokchol", "qokeechy", "qokeain", "qokor"}
ARTICLES = {"ol", "al", "or", "ar"}

CONFIRMED_PLANTS = {
    "ckhal": "ricinus (castor oil)",
    "chodar": "papaver (poppy)",
    "opol": "papaver (poppy)",
    "pchey": "thistle",
    "okshy": "botrychium",
    "chekar": "scabiosa",
    "alam": "geranium",
    "qokeod": "valerian",
    "soy": "smilax/tamus",
    "checkhey": "smilax/tamus",
    "lolain": "atropa",
    "doaiin": "tussilago",
}


def load_dict():
    if not DICT_FILE.exists():
        return {}
    data = json.loads(DICT_FILE.read_text())
    entries = data.get("entries", data)  # Handle both formats
    d = {}
    for w, info in entries.items():
        if isinstance(info, dict):
            d[w] = info.get("meaning", "?")
        else:
            d[w] = str(info)
    return d


def get_meaning(word, base_dict):
    if word in VISUAL_OVERRIDES:
        return VISUAL_OVERRIDES[word]["meaning"]
    if word in CONFIRMED_PLANTS:
        return f"[{CONFIRMED_PLANTS[word]}]"
    if word in base_dict:
        return base_dict[word]
    return None


def is_preposition(word):
    if word in PREPOSITIONS:
        return True
    return word.startswith("qok")


def parse_line(words, base_dict):
    """Parse a line using the Grammar Frame: VERB [OBJ] PREP [MODIFIER]"""
    result = {
        "verb": None,
        "verb_idx": None,
        "direct_object": None,
        "do_meaning": None,
        "preposition": None,
        "prep_object": None,
        "po_meaning": None,
        "article": None,
        "noun": None,
        "noun_meaning": None,
        "other": [],
        "translated_parts": [],
    }
    
    used = set()
    
    # Find verb (usually at start or end)
    for i, w in enumerate(words):
        if w in VERBS:
            result["verb"] = w
            result["verb_idx"] = i
            result["translated_parts"].append(("verb", w, "take/give"))
            used.add(i)
            break
    
    # Find direct object (word after verb if present)
    if result["verb_idx"] is not None:
        next_idx = result["verb_idx"] + 1
        if next_idx < len(words) and next_idx not in used:
            do_word = words[next_idx]
            if not is_preposition(do_word) and do_word not in ARTICLES:
                result["direct_object"] = do_word
                result["do_meaning"] = get_meaning(do_word, base_dict)
                meaning_str = result["do_meaning"] or f"[{do_word}]"
                result["translated_parts"].append(("object", do_word, meaning_str))
                used.add(next_idx)
    
    # Find preposition and its object
    for i, w in enumerate(words):
        if i in used:
            continue
        if is_preposition(w):
            result["preposition"] = w
            result["translated_parts"].append(("prep", w, "of"))
            used.add(i)
            # Object of preposition is next word
            if i + 1 < len(words) and (i + 1) not in used:
                po_word = words[i + 1]
                if po_word not in ARTICLES:
                    result["prep_object"] = po_word
                    result["po_meaning"] = get_meaning(po_word, base_dict)
                    meaning_str = result["po_meaning"] or f"[{po_word}]"
                    result["translated_parts"].append(("prep_obj", po_word, meaning_str))
                    used.add(i + 1)
            break
    
    # Find article and noun
    for i, w in enumerate(words):
        if i in used:
            continue
        if w in ARTICLES:
            result["article"] = w
            result["translated_parts"].append(("article", w, "the"))
            used.add(i)
            # Noun follows article
            if i + 1 < len(words) and (i + 1) not in used:
                noun = words[i + 1]
                result["noun"] = noun
                result["noun_meaning"] = get_meaning(noun, base_dict)
                meaning_str = result["noun_meaning"] or f"[{noun}]"
                result["translated_parts"].append(("noun", noun, meaning_str))
                used.add(i + 1)
            break
    
    # Remaining words
    for i, w in enumerate(words):
        if i not in used:
            meaning = get_meaning(w, base_dict)
            result["other"].append({"word": w, "meaning": meaning})
            if meaning:
                result["translated_parts"].append(("other", w, meaning))
            else:
                result["translated_parts"].append(("unknown", w, f"[{w}]"))
    
    return result


def translate_line(parsed):
    """Build English translation from parsed structure."""
    parts = []
    for role, word, meaning in parsed["translated_parts"]:
        if role == "verb":
            parts.append("Take")
        elif role == "object":
            parts.append(meaning if meaning else f"[{word}]")
        elif role == "prep":
            parts.append("of")
        elif role == "prep_obj":
            parts.append(meaning if meaning else f"[{word}]")
        elif role == "article":
            parts.append("the")
        elif role == "noun":
            parts.append(meaning if meaning else f"[{word}]")
        elif role == "other" or role == "unknown":
            parts.append(meaning if "[" not in str(meaning) else f"[{word}]")
    return " ".join(parts) if parts else None


def score_coherence(parsed, translation):
    """Score translation coherence."""
    score = 0.0
    factors = []
    
    if parsed["verb"]:
        score += 0.2
        factors.append("has_verb")
    if parsed["direct_object"]:
        score += 0.15
        factors.append("has_object")
    if parsed["do_meaning"] and "[" not in str(parsed["do_meaning"]):
        score += 0.15
        factors.append("object_translated")
    if parsed["preposition"]:
        score += 0.1
        factors.append("has_prep")
    if parsed["prep_object"]:
        score += 0.1
        factors.append("has_prep_obj")
    if parsed["po_meaning"] and "[" not in str(parsed["po_meaning"]):
        score += 0.15
        factors.append("prep_obj_translated")
    if parsed["article"] and parsed["noun"]:
        score += 0.1
        factors.append("has_article_noun")
    if parsed["noun_meaning"] and "[" not in str(parsed["noun_meaning"]):
        score += 0.05
        factors.append("noun_translated")
    
    return score, factors


def collect_modifier_words(results):
    """Collect words that appear after prepositions - likely plant names."""
    modifiers = defaultdict(int)
    for r in results:
        if r["parsed"]["prep_object"]:
            word = r["parsed"]["prep_object"]
            modifiers[word] += 1
    return dict(sorted(modifiers.items(), key=lambda x: -x[1]))


def main():
    print("Track 92: Full Recipe Translation")
    print("=" * 60)
    
    base_dict = load_dict()
    print(f"Loaded dictionary: {len(base_dict)} entries")
    print(f"Visual overrides: {len(VISUAL_OVERRIDES)} entries")
    print(f"Confirmed plants: {len(CONFIRMED_PLANTS)} entries")
    
    # Get recipe section (f103-f116)
    recipe_data = get_section_text('recipes', system='EVA')
    print(f"\nRecipe folios found: {len(recipe_data)}")
    
    results = []
    total_words = 0
    translated_words = 0
    high_coh = 0
    med_coh = 0
    low_coh = 0
    
    for folio in sorted(recipe_data.keys()):
        for loc, text in sorted(recipe_data[folio].items()):
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 1]
            
            if not words:
                continue
            
            total_words += len(words)
            
            parsed = parse_line(words, base_dict)
            translation = translate_line(parsed)
            coherence, factors = score_coherence(parsed, translation)
            
            # Count translated words
            for w in words:
                if get_meaning(w, base_dict):
                    translated_words += 1
            
            if coherence >= 0.5:
                high_coh += 1
            elif coherence >= 0.3:
                med_coh += 1
            else:
                low_coh += 1
            
            results.append({
                "folio": folio,
                "location": loc,
                "raw": text,
                "words": words,
                "parsed": parsed,
                "translation": translation,
                "coherence": coherence,
                "coherence_factors": factors,
            })
    
    # Collect modifier (plant candidate) words
    modifier_words = collect_modifier_words(results)
    
    coverage = translated_words / total_words * 100 if total_words else 0
    
    print(f"\nTotal lines: {len(results)}")
    print(f"Total words: {total_words}")
    print(f"Translated words: {translated_words} ({coverage:.1f}%)")
    print(f"\nCoherence distribution:")
    print(f"  HIGH (≥0.5): {high_coh} ({high_coh/len(results)*100:.1f}%)")
    print(f"  MEDIUM (0.3-0.5): {med_coh} ({med_coh/len(results)*100:.1f}%)")
    print(f"  LOW (<0.3): {low_coh} ({low_coh/len(results)*100:.1f}%)")
    
    print(f"\nModifier words (plant candidates): {len(modifier_words)}")
    print("Top 20:")
    for w, cnt in list(modifier_words.items())[:20]:
        meaning = get_meaning(w, base_dict)
        m_str = f" → {meaning}" if meaning else ""
        print(f"  {w}: {cnt} occurrences{m_str}")
    
    # Save results
    output = {
        "summary": {
            "total_lines": len(results),
            "total_words": total_words,
            "translated_words": translated_words,
            "coverage_pct": coverage,
            "high_coherence": high_coh,
            "medium_coherence": med_coh,
            "low_coherence": low_coh,
        },
        "modifier_words": modifier_words,
        "visual_overrides": {k: v["meaning"] for k, v in VISUAL_OVERRIDES.items()},
        "confirmed_plants": CONFIRMED_PLANTS,
        "translations": [
            {
                "folio": r["folio"],
                "location": r["location"],
                "raw": r["raw"],
                "words": r["words"],
                "translation": r["translation"],
                "coherence": r["coherence"],
                "parsed": {
                    "verb": r["parsed"]["verb"],
                    "direct_object": r["parsed"]["direct_object"],
                    "do_meaning": r["parsed"]["do_meaning"],
                    "preposition": r["parsed"]["preposition"],
                    "prep_object": r["parsed"]["prep_object"],
                    "po_meaning": r["parsed"]["po_meaning"],
                    "article": r["parsed"]["article"],
                    "noun": r["parsed"]["noun"],
                    "noun_meaning": r["parsed"]["noun_meaning"],
                },
            }
            for r in results
        ],
    }
    
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {OUT_JSON}")
    
    # Generate markdown report
    md = []
    md.append("# Track 92: Full Recipe Translation Report")
    md.append("")
    md.append("## Summary")
    md.append(f"- **Total Lines**: {len(results)}")
    md.append(f"- **Total Words**: {total_words}")
    md.append(f"- **Translated Words**: {translated_words} ({coverage:.1f}%)")
    md.append(f"- **HIGH Coherence (≥0.5)**: {high_coh} ({high_coh/len(results)*100:.1f}%)")
    md.append(f"- **MEDIUM Coherence (0.3-0.5)**: {med_coh} ({med_coh/len(results)*100:.1f}%)")
    md.append(f"- **LOW Coherence (<0.3)**: {low_coh} ({low_coh/len(results)*100:.1f}%)")
    md.append("")
    
    md.append("## Visual Semantic Overrides")
    md.append("")
    md.append("Words whose meanings were corrected based on visual correlation:")
    md.append("")
    md.append("| Word | Old Meaning | New Meaning | Visual % |")
    md.append("|------|-------------|-------------|----------|")
    for w, info in VISUAL_OVERRIDES.items():
        old = base_dict.get(w, "unknown")
        md.append(f"| `{w}` | {old} | **{info['meaning']}** | {info['visual_pct']*100:.0f}% |")
    md.append("")
    
    md.append("## Grammar Frame")
    md.append("")
    md.append("```")
    md.append("VERB [OBJECT] PREP [MODIFIER]")
    md.append("daiin char    qok- [plant]")
    md.append("Take  flower  of   [plant]")
    md.append("```")
    md.append("")
    
    md.append("## Modifier Words (Plant Candidates)")
    md.append("")
    md.append("Words appearing after prepositions - high probability plant names:")
    md.append("")
    md.append("| Word | Count | Current Meaning |")
    md.append("|------|-------|-----------------|")
    for w, cnt in list(modifier_words.items())[:30]:
        meaning = get_meaning(w, base_dict) or "[unknown]"
        md.append(f"| `{w}` | {cnt} | {meaning} |")
    md.append("")
    
    md.append("## Top Translated Recipes")
    md.append("")
    md.append("Lines with highest coherence scores:")
    md.append("")
    
    top = sorted(results, key=lambda x: -x["coherence"])[:30]
    for r in top:
        if r["translation"]:
            md.append(f"### {r['location']} (coherence: {r['coherence']:.2f})")
            md.append("")
            md.append(f"**Voynich**: `{' '.join(r['words'])}`")
            md.append("")
            md.append(f"**English**: {r['translation']}")
            md.append("")
            if r["parsed"]["verb"]:
                parts = []
                if r["parsed"]["direct_object"]:
                    parts.append(f"VERB `{r['parsed']['verb']}` + OBJ `{r['parsed']['direct_object']}`")
                if r["parsed"]["preposition"]:
                    parts.append(f"PREP `{r['parsed']['preposition']}`")
                if r["parsed"]["prep_object"]:
                    parts.append(f"MODIFIER `{r['parsed']['prep_object']}`")
                md.append(f"**Structure**: {' → '.join(parts)}")
                md.append("")
    
    md.append("## Sample Translations by Folio")
    md.append("")
    
    for folio in sorted(set(r["folio"] for r in results)):
        folio_results = [r for r in results if r["folio"] == folio]
        good = [r for r in folio_results if r["coherence"] >= 0.3][:5]
        if good:
            md.append(f"### {folio}")
            md.append("")
            for r in good:
                trans = r["translation"] or "[no translation]"
                md.append(f"- `{r['location']}`: {trans}")
            md.append("")
    
    OUT_MD.write_text("\n".join(md))
    print(f"Saved: {OUT_MD}")


if __name__ == "__main__":
    main()




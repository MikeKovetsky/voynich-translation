#!/usr/bin/env python3
"""
Track 29: Plant Name Matching
Match decoded Voynich plant labels to real botanical names.
"""

import json
import re
from collections import defaultdict
from difflib import SequenceMatcher

MEDIEVAL_PLANTS = [
    # Format: (latin_name, common_name, medieval_variants, genus)
    ("Artemisia absinthium", "Wormwood", ["absinthium", "absinthii", "artemisia"], "artemisia"),
    ("Artemisia vulgaris", "Mugwort", ["artemisia", "artemisiae"], "artemisia"),
    ("Papaver somniferum", "Opium Poppy", ["papaver", "papaueris", "papavere"], "papaver"),
    ("Papaver rhoeas", "Red Poppy", ["papaver", "rhoeados"], "papaver"),
    ("Salvia officinalis", "Sage", ["salvia", "salviae"], "salvia"),
    ("Rosmarinus officinalis", "Rosemary", ["rosmarinus", "rorismarini", "rosmarini"], "rosmarinus"),
    ("Urtica dioica", "Nettle", ["urtica", "urticae"], "urtica"),
    ("Cannabis sativa", "Hemp", ["cannabis", "cannabis"], "cannabis"),
    ("Ricinus communis", "Castor Bean", ["ricinus", "ricini", "cataputia"], "ricinus"),
    ("Centaurea cyanus", "Cornflower", ["centaurea", "centaureae", "cyanus"], "centaurea"),
    ("Helleborus niger", "Black Hellebore", ["helleborus", "hellebori", "elleborus"], "helleborus"),
    ("Cyclamen europaeum", "Cyclamen", ["cyclamen", "cyclaminis", "cyclamino"], "cyclamen"),
    ("Tamarix gallica", "Tamarisk", ["tamarix", "tamaricis", "tamariscus"], "tamarix"),
    ("Aloe vera", "Aloe", ["aloe", "aloes"], "aloe"),
    ("Quercus robur", "Oak", ["quercus", "quercum", "roboris"], "quercus"),
    ("Mentha piperita", "Peppermint", ["mentha", "menthae", "menta"], "mentha"),
    ("Origanum vulgare", "Oregano", ["origanum", "origani"], "origanum"),
    ("Plantago major", "Plantain", ["plantago", "plantaginis"], "plantago"),
    ("Verbena officinalis", "Vervain", ["verbena", "verbenae"], "verbena"),
    ("Betonica officinalis", "Betony", ["betonica", "betonicae"], "betonica"),
    ("Ruta graveolens", "Rue", ["ruta", "rutae"], "ruta"),
    ("Melissa officinalis", "Lemon Balm", ["melissa", "melissae"], "melissa"),
    ("Viola odorata", "Violet", ["viola", "violae"], "viola"),
    ("Lavandula angustifolia", "Lavender", ["lavandula", "lavendula", "spica"], "lavandula"),
    ("Achillea millefolium", "Yarrow", ["achillea", "millefolium"], "achillea"),
    ("Foeniculum vulgare", "Fennel", ["feniculum", "foeniculum", "feniculi"], "foeniculum"),
    ("Anethum graveolens", "Dill", ["anethum", "anethi"], "anethum"),
    ("Coriandrum sativum", "Coriander", ["coriandrum", "coriandri"], "coriandrum"),
    ("Cuminum cyminum", "Cumin", ["cuminum", "cyminum", "cumini"], "cuminum"),
    ("Crocus sativus", "Saffron", ["crocus", "croci"], "crocus"),
    ("Hyoscyamus niger", "Henbane", ["hyoscyamus", "hyoscyami", "iusquiamus"], "hyoscyamus"),
    ("Mandragora officinarum", "Mandrake", ["mandragora", "mandragorae"], "mandragora"),
    ("Atropa belladonna", "Deadly Nightshade", ["belladonna", "atropa", "solanum"], "atropa"),
    ("Digitalis purpurea", "Foxglove", ["digitalis"], "digitalis"),
    ("Juniperus communis", "Juniper", ["juniperus", "juniperi", "iuniperus"], "juniperus"),
    ("Sambucus nigra", "Elder", ["sambucus", "sambuci", "ebulus"], "sambucus"),
    ("Calendula officinalis", "Marigold", ["calendula", "calendulae"], "calendula"),
    ("Tanacetum vulgare", "Tansy", ["tanacetum", "tanaceti", "athanasia"], "tanacetum"),
    ("Thymus vulgaris", "Thyme", ["thymus", "thymi", "serpillum"], "thymus"),
    ("Hyssopus officinalis", "Hyssop", ["hyssopus", "hyssopi", "ysopus"], "hyssopus"),
    ("Petroselinum crispum", "Parsley", ["petroselinum", "petroseli", "apium"], "petroselinum"),
    ("Allium sativum", "Garlic", ["allium", "alei", "alium"], "allium"),
    ("Zingiber officinale", "Ginger", ["zingiber", "zingiberis", "gingiber"], "zingiber"),
    ("Piper nigrum", "Black Pepper", ["piper", "piperis"], "piper"),
    ("Cinnamomum verum", "Cinnamon", ["cinnamomum", "cinnamomi"], "cinnamomum"),
    ("Glycyrrhiza glabra", "Licorice", ["liquiritia", "glycyrrhiza", "dulcis"], "glycyrrhiza"),
    ("Valeriana officinalis", "Valerian", ["valeriana", "valerianae"], "valeriana"),
    ("Euphorbia lathyris", "Caper Spurge", ["euphorbia", "lathyris", "cataputia"], "euphorbia"),
    ("Chelidonium majus", "Greater Celandine", ["chelidonium", "chelidonia"], "chelidonium"),
    ("Taraxacum officinale", "Dandelion", ["taraxacum", "dens leonis"], "taraxacum"),
    ("Borago officinalis", "Borage", ["borago", "buglossa"], "borago"),
    ("Symphytum officinale", "Comfrey", ["symphytum", "consolida"], "symphytum"),
    ("Tussilago farfara", "Coltsfoot", ["tussilago", "tussilaginis", "farfara"], "tussilago"),
    ("Inula helenium", "Elecampane", ["inula", "enula", "helenium"], "inula"),
    ("Marrubium vulgare", "Horehound", ["marrubium", "marrubii"], "marrubium"),
    ("Pulmonaria officinalis", "Lungwort", ["pulmonaria"], "pulmonaria"),
    ("Senecio vulgaris", "Groundsel", ["senecio", "senecionis"], "senecio"),
    ("Malva sylvestris", "Mallow", ["malva", "malvae"], "malva"),
    ("Althaea officinalis", "Marshmallow", ["althaea", "althaae", "ibiscus"], "althaea"),
]

VISUAL_IDS = {
    "f17r": {"name": "Cornflower", "latin": "Centaurea cyanus", "voynich": "f2o89", "decoded": "fba-orum", "conf": 0.75},
    "f5r": {"name": "Hellebore", "latin": "Helleborus sp.", "voynich": "h2o89", "decoded": "rba-orum", "conf": 0.6},
    "f2v": {"name": "Cyclamen", "latin": "Cyclamen sp.", "voynich": "hoom", "decoded": "raam", "conf": 0.5},
    "f4r": {"name": "Tamarisk", "latin": "Tamarix sp.", "voynich": "ho8ae19", "decoded": "radeit-us", "conf": 0.5},
    "f6r": {"name": "Poppy", "latin": "Papaver sp.", "voynich": "foay", "decoded": "fa-i", "conf": 0.5},
    "f25v": {"name": "Castor Bean", "latin": "Ricinus communis", "voynich": "goCam", "decoded": "gach-am", "conf": 0.5},
    "f3r": {"name": "Aloe", "latin": "Aloe sp.", "voynich": "k2cos", "decoded": "nbcax", "conf": 0.4},
    "f9r": {"name": "Oak", "latin": "Quercus sp.", "voynich": "k98eo", "decoded": "nsdia", "conf": 0.4},
}


def build_plant_stems():
    """Build dictionary of plant name stems for matching."""
    stems = {}
    for latin, common, variants, genus in MEDIEVAL_PLANTS:
        base = genus.lower()
        stems[base] = {"latin": latin, "common": common, "variants": variants}
        for var in variants:
            stems[var.lower()] = {"latin": latin, "common": common, "variants": variants}
    return stems


def clean_decoded(text):
    """Remove hyphens and standardize decoded text."""
    return re.sub(r'[-]', '', text.lower().strip())


def phonetic_similarity(s1, s2):
    """Calculate phonetic similarity using sequence matching."""
    s1, s2 = clean_decoded(s1), clean_decoded(s2)
    if not s1 or not s2:
        return 0.0
    return SequenceMatcher(None, s1, s2).ratio()


def stem_match(decoded, plant_stems):
    """Find stem matches for decoded word."""
    cleaned = clean_decoded(decoded)
    if len(cleaned) < 3:
        return None, 0
    
    best_match = None
    best_score = 0
    
    for stem, info in plant_stems.items():
        if len(stem) < 3:
            continue
        
        if cleaned.startswith(stem[:3]) or stem.startswith(cleaned[:3]):
            sim = phonetic_similarity(cleaned, stem)
            if sim > best_score and sim > 0.5:
                best_score = sim
                best_match = info
        
        if stem in cleaned or cleaned in stem:
            sim = phonetic_similarity(cleaned, stem)
            if sim > best_score:
                best_score = sim
                best_match = info
    
    return best_match, best_score


def exact_match(decoded, plant_stems):
    """Check for exact or near-exact matches."""
    cleaned = clean_decoded(decoded)
    
    for stem in plant_stems:
        if cleaned == stem or stem == cleaned:
            return plant_stems[stem], 1.0
        
        if len(cleaned) > 4 and len(stem) > 4:
            if cleaned[:5] == stem[:5]:
                return plant_stems[stem], 0.9
    
    return None, 0


def edit_distance_match(decoded, plant_stems, max_dist=2):
    """Find matches within edit distance threshold."""
    cleaned = clean_decoded(decoded)
    if len(cleaned) < 4:
        return None, 0
    
    best = None
    best_score = 0
    
    for stem, info in plant_stems.items():
        if len(stem) < 4:
            continue
        
        len_diff = abs(len(cleaned) - len(stem))
        if len_diff > max_dist:
            continue
        
        sim = phonetic_similarity(cleaned, stem)
        if sim > 0.7 and sim > best_score:
            best = info
            best_score = sim
    
    return best, best_score


def classify_match(decoded, plant_stems):
    """Classify match type and return best match."""
    info, score = exact_match(decoded, plant_stems)
    if info and score > 0.85:
        return {"match": info, "score": score, "type": "exact"}
    
    info, score = stem_match(decoded, plant_stems)
    if info and score > 0.6:
        return {"match": info, "score": score, "type": "stem"}
    
    info, score = edit_distance_match(decoded, plant_stems)
    if info and score > 0.65:
        return {"match": info, "score": score, "type": "phonetic"}
    
    return {"match": None, "score": 0, "type": "none"}


def extract_labels(botanical_data):
    """Extract potential plant labels from each folio."""
    labels = []
    
    for page in botanical_data.get("pages", []):
        folio = page.get("folio", "")
        raw = page.get("raw_text", "")
        decoded = page.get("decoded_text", "")
        
        # Split on dots which separate words in Voynich transcription
        raw_words = [w.strip() for w in re.split(r'[.,\s]+', raw) if w.strip()][:10]
        decoded_words = [w.strip() for w in re.split(r'[.,\s]+', decoded) if w.strip()][:10]
        
        first_raw = raw_words[0] if raw_words else ""
        first_decoded = decoded_words[0] if decoded_words else ""
        
        labels.append({
            "folio": folio,
            "voynich_label": first_raw,
            "decoded_label": first_decoded,
            "all_words_raw": raw_words,
            "all_words_decoded": decoded_words
        })
    
    return labels


def match_visual_ids(labels, plant_stems):
    """Cross-reference decoded labels with visual identifications."""
    results = []
    
    for folio, vis_info in VISUAL_IDS.items():
        label_entry = next((l for l in labels if l["folio"] == folio), None)
        
        # Use pre-decoded value if available
        decoded = vis_info.get("decoded", "")
        if not decoded and label_entry:
            decoded = label_entry["decoded_label"]
        
        voynich_label = vis_info.get("voynich", "")
        if not voynich_label and label_entry:
            voynich_label = label_entry["voynich_label"]
        
        match_result = classify_match(decoded, plant_stems)
        
        # Find expected genus
        expected_genus = None
        for latin, common, variants, genus in MEDIEVAL_PLANTS:
            if vis_info["name"].lower() in common.lower() or genus in vis_info["latin"].lower():
                expected_genus = genus
                break
        
        # Check direct similarity to expected Latin name
        expected_latin_clean = clean_decoded(vis_info["latin"].split()[0])  # Get genus only
        decoded_clean = clean_decoded(decoded)
        direct_similarity = phonetic_similarity(decoded_clean, expected_latin_clean)
        
        # Check if matched plant matches visual ID
        name_match = False
        if match_result["match"]:
            matched_latin = match_result["match"]["latin"].lower()
            name_match = any([
                expected_genus and expected_genus in matched_latin,
                vis_info["name"].lower() in match_result["match"]["common"].lower()
            ])
        
        # Also consider direct similarity > 0.5 as partial match
        partial_match = direct_similarity > 0.5
        
        results.append({
            "folio": folio,
            "voynich_label": voynich_label,
            "decoded": decoded,
            "visual_id": vis_info["name"],
            "latin_name": vis_info["latin"],
            "expected_genus": expected_genus,
            "visual_conf": vis_info["conf"],
            "matched_plant": match_result["match"]["latin"] if match_result["match"] else None,
            "match_type": match_result["type"],
            "match_score": round(match_result["score"], 3),
            "direct_similarity": round(direct_similarity, 3),
            "matches_visual": name_match,
            "partial_match": partial_match,
            "notes": ""
        })
    
    return results


def analyze_all_labels(labels, plant_stems):
    """Analyze all labels for plant name matches."""
    matches = []
    stats = {"exact": 0, "stem": 0, "phonetic": 0, "none": 0}
    
    for label in labels:
        decoded = label["decoded_label"]
        result = classify_match(decoded, plant_stems)
        
        stats[result["type"]] += 1
        
        if result["match"]:
            matches.append({
                "folio": label["folio"],
                "voynich": label["voynich_label"],
                "decoded": decoded,
                "matched": result["match"]["latin"],
                "common": result["match"]["common"],
                "type": result["type"],
                "score": round(result["score"], 3)
            })
    
    return matches, stats


def secondary_word_analysis(labels, plant_stems):
    """Analyze non-first words for potential plant names."""
    plant_words = []
    
    for label in labels:
        for i, word in enumerate(label["all_words_decoded"][1:5], 1):
            cleaned = clean_decoded(word)
            if len(cleaned) < 4:
                continue
            
            result = classify_match(word, plant_stems)
            if result["match"] and result["score"] > 0.6:
                plant_words.append({
                    "folio": label["folio"],
                    "position": i,
                    "decoded": word,
                    "matched": result["match"]["latin"],
                    "score": round(result["score"], 3)
                })
    
    return plant_words


def run():
    with open("results/botanical_decoded.json") as f:
        botanical_data = json.load(f)
    
    plant_stems = build_plant_stems()
    print(f"Reference database: {len(MEDIEVAL_PLANTS)} plants, {len(plant_stems)} searchable terms")
    
    labels = extract_labels(botanical_data)
    print(f"Extracted labels from {len(labels)} folios")
    
    visual_results = match_visual_ids(labels, plant_stems)
    
    print("\n=== Visual ID Cross-Reference ===")
    print(f"{'Folio':<8} {'Visual ID':<15} {'Voynich':<12} {'Decoded':<15} {'Expected':<12} {'Similarity':<10} {'Status'}")
    print("-" * 95)
    for r in visual_results:
        status = "✓" if r["matches_visual"] else ("~" if r["partial_match"] else "✗")
        expected = r["expected_genus"] or r["latin_name"].split()[0].lower()
        print(f"{r['folio']:<8} {r['visual_id']:<15} {r['voynich_label']:<12} {r['decoded']:<15} {expected:<12} {r['direct_similarity']:<10.3f} {status}")
    print()
    
    all_matches, stats = analyze_all_labels(labels, plant_stems)
    
    print(f"\n=== Overall Statistics ===")
    total = sum(stats.values())
    print(f"Total labels analyzed: {total}")
    print(f"Exact matches: {stats['exact']} ({100*stats['exact']/total:.1f}%)")
    print(f"Stem matches: {stats['stem']} ({100*stats['stem']/total:.1f}%)")
    print(f"Phonetic matches: {stats['phonetic']} ({100*stats['phonetic']/total:.1f}%)")
    print(f"No match: {stats['none']} ({100*stats['none']/total:.1f}%)")
    
    match_rate = (stats['exact'] + stats['stem'] + stats['phonetic']) / total
    print(f"\nOverall match rate: {100*match_rate:.1f}%")
    
    visual_match_rate = sum(1 for r in visual_results if r["matches_visual"]) / len(visual_results)
    partial_match_rate = sum(1 for r in visual_results if r["partial_match"]) / len(visual_results)
    avg_similarity = sum(r["direct_similarity"] for r in visual_results) / len(visual_results)
    print(f"Visual ID exact match rate: {100*visual_match_rate:.1f}%")
    print(f"Visual ID partial match rate: {100*partial_match_rate:.1f}%")
    print(f"Average decoded-to-expected similarity: {100*avg_similarity:.1f}%")
    
    secondary = secondary_word_analysis(labels, plant_stems)
    
    results = {
        "total_labels_extracted": len(labels),
        "reference_plants": len(MEDIEVAL_PLANTS),
        "visual_id_matches": visual_results,
        "all_label_matches": all_matches[:50],
        "secondary_matches": secondary[:30],
        "summary": {
            "exact_matches": stats["exact"],
            "stem_matches": stats["stem"],
            "phonetic_matches": stats["phonetic"],
            "no_match": stats["none"],
            "overall_match_rate": round(match_rate, 3),
            "visual_exact_match_rate": round(visual_match_rate, 3),
            "visual_partial_match_rate": round(partial_match_rate, 3),
            "avg_decoded_similarity": round(avg_similarity, 3)
        },
        "analysis": {
            "conclusion": "",
            "evidence_for": [],
            "evidence_against": [],
            "interpretation": ""
        }
    }
    
    if visual_match_rate > 0.5:
        results["analysis"]["conclusion"] = "STRONG: Labels correlate with plant identities"
        results["analysis"]["evidence_for"].append(f"High visual-label match rate ({100*visual_match_rate:.0f}%)")
    elif partial_match_rate > 0.3 or avg_similarity > 0.35:
        results["analysis"]["conclusion"] = "WEAK: Some correlation between labels and plants"
        results["analysis"]["evidence_for"].append(f"Partial similarity detected ({100*avg_similarity:.0f}% avg)")
    else:
        results["analysis"]["conclusion"] = "NEGATIVE: Decoded labels do NOT match expected plant names"
        results["analysis"]["evidence_against"].append(f"Low visual-label match rate ({100*visual_match_rate:.0f}%)")
        results["analysis"]["evidence_against"].append(f"Low average similarity ({100*avg_similarity:.0f}%)")
    
    if match_rate > 0.3:
        results["analysis"]["evidence_for"].append(f"Many labels match Latin plant terminology ({100*match_rate:.0f}%)")
    else:
        results["analysis"]["evidence_against"].append(f"Few labels match plant names ({100*match_rate:.0f}%)")
    
    results["analysis"]["interpretation"] = """
The decoded Voynich labels do NOT match the visually-identified plants.
Possible explanations:
1. The phonetic decoding is incorrect
2. Visual plant identifications are wrong  
3. Labels are not plant names (could be descriptions, uses, or locations)
4. The encoding uses a different language than Latin
5. The text uses heavily abbreviated or symbolic naming
"""
    
    with open("results/plant_name_matches.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to results/plant_name_matches.json")
    print(f"\nConclusion: {results['analysis']['conclusion']}")
    
    return results


if __name__ == "__main__":
    run()




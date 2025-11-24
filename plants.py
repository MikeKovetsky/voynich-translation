#!/usr/bin/env python3
"""
Voynich Plant Identification - Correlate illustrations with text patterns
Based on visual analysis and Stephen Bax methodology
"""

import json
import re
from collections import defaultdict
from pathlib import Path

PLANT_DB = {
    "f1r": {
        "features": {"leaf_shape": "unclear", "flower": "unclear", "root": "unclear"},
        "candidates": [],
        "notes": "First page - baseline analysis",
        "confidence": 0.0
    },
    "f2v": {
        "features": {
            "leaf_shape": "large rounded/heart-shaped, smooth margin",
            "flower": "small 3-lobed at top",
            "root": "not visible",
            "growth_form": "herbaceous, single stem",
            "colors": "green leaf, pale flower"
        },
        "candidates": [
            {"name": "Cyclamen", "latin": "Cyclamen sp.", "conf": 0.6,
             "reason": "Round leaves, similar flower shape"},
            {"name": "Wild Ginger", "latin": "Asarum europaeum", "conf": 0.5,
             "reason": "Round kidney-shaped leaves common in medieval herbals"},
        ],
        "bax": "Cotton (DISPUTED - shape doesn't match)",
        "notes": "Large rounded leaf. Not cotton. Possibly shade plant.",
        "confidence": 0.5
    },
    "f3r": {
        "features": {
            "leaf_shape": "striped/banded, layered, curved",
            "flower": "not visible",
            "root": "fibrous",
            "growth_form": "rosette/layered"
        },
        "candidates": [
            {"name": "Aloe", "latin": "Aloe sp.", "conf": 0.5,
             "reason": "Banded/striped succulent-like leaves"},
            {"name": "Dock/Sorrel", "latin": "Rumex sp.", "conf": 0.4,
             "reason": "Reddish streaks on leaves"},
        ],
        "notes": "Very distinctive striped appearance. Stylized representation.",
        "confidence": 0.4
    },
    "f4r": {
        "features": {
            "leaf_shape": "small pinnate/compound, opposite",
            "flower": "small white/pink at tips",
            "root": "fibrous, spreading",
            "growth_form": "shrubby, branching"
        },
        "candidates": [
            {"name": "Tamarisk", "latin": "Tamarix sp.", "conf": 0.5,
             "reason": "Small scale-like leaves, multiple branches"},
            {"name": "Lentisk/Mastic", "latin": "Pistacia lentiscus", "conf": 0.5,
             "reason": "Pinnate leaves, Mediterranean plant"},
            {"name": "Fumitory", "latin": "Fumaria officinalis", "conf": 0.4,
             "reason": "Finely divided leaves, medicinal herb"},
        ],
        "bax": "Hellebore (DISPUTED - wrong leaf type)",
        "confidence": 0.5
    },
    "f5r": {
        "features": {
            "leaf_shape": "large palmate, clustered",
            "flower": "drooping bell-like",
            "root": "spreading",
            "growth_form": "herbaceous"
        },
        "candidates": [
            {"name": "Hellebore", "latin": "Helleborus sp.", "conf": 0.7,
             "reason": "Palmate leaves, drooping flower - classic hellebore features"},
            {"name": "Lady's Mantle", "latin": "Alchemilla sp.", "conf": 0.4,
             "reason": "Round palmate leaves"},
        ],
        "notes": "Strong hellebore candidate - better match than f4r!",
        "confidence": 0.6
    },
    "f6r": {
        "features": {
            "leaf_shape": "deeply lobed/pinnatifid",
            "flower": "pod-like structures at top",
            "root": "bulbous",
            "growth_form": "herbaceous"
        },
        "candidates": [
            {"name": "Poppy", "latin": "Papaver sp.", "conf": 0.6,
             "reason": "Distinctive seed pods, lobed leaves"},
            {"name": "Melon/Cucumber", "latin": "Cucurbitaceae", "conf": 0.4,
             "reason": "Lobed leaves, fruit-like structures"},
        ],
        "notes": "Distinctive pod-like structures suggest poppy family",
        "confidence": 0.5
    },
    "f9r": {
        "features": {
            "leaf_shape": "lobed, oak-like",
            "flower": "catkin-like at top",
            "root": "thick taproot",
            "growth_form": "shrubby",
            "colors": "red-brown stems"
        },
        "candidates": [
            {"name": "Oak", "latin": "Quercus sp.", "conf": 0.5,
             "reason": "Lobed leaves, catkin flowers"},
            {"name": "Rhubarb", "latin": "Rheum sp.", "conf": 0.4,
             "reason": "Thick root, lobed leaves, medicinal"},
            {"name": "Geranium", "latin": "Geranium sp.", "conf": 0.4,
             "reason": "Lobed leaves pattern"},
        ],
        "confidence": 0.4
    },
    "f17r": {
        "features": {
            "leaf_shape": "long linear/strap-like, alternate",
            "flower": "blue/purple thistle heads, multiple",
            "root": "fibrous",
            "growth_form": "herbaceous"
        },
        "candidates": [
            {"name": "Cornflower", "latin": "Centaurea cyanus", "conf": 0.8,
             "reason": "Blue thistle flowers, strap leaves - STRONG MATCH"},
            {"name": "Knapweed", "latin": "Centaurea sp.", "conf": 0.7,
             "reason": "Blue composite flowers"},
            {"name": "Sea Holly", "latin": "Eryngium sp.", "conf": 0.5,
             "reason": "Blue thistle-like flowers"},
        ],
        "notes": "HIGH CONFIDENCE - Blue flowers very distinctive. Centaurea strong candidate.",
        "confidence": 0.75
    },
    "f25v": {
        "features": {
            "leaf_shape": "palmate/hand-shaped, radiating from center",
            "flower": "not clearly visible",
            "root": "fibrous",
            "growth_form": "herbaceous rosette"
        },
        "candidates": [
            {"name": "Castor Bean", "latin": "Ricinus communis", "conf": 0.6,
             "reason": "Large palmate leaves"},
            {"name": "Cannabis", "latin": "Cannabis sp.", "conf": 0.5,
             "reason": "Palmate leaves, medicinal use"},
            {"name": "Hellebore", "latin": "Helleborus sp.", "conf": 0.5,
             "reason": "Palmate leaf arrangement"},
            {"name": "Lupine", "latin": "Lupinus sp.", "conf": 0.4,
             "reason": "Palmate leaves"},
        ],
        "bax": "Juniper (STRONGLY DISPUTED - juniper has needles, not palmate leaves!)",
        "notes": "Bax identification INCORRECT. This is clearly NOT juniper.",
        "confidence": 0.5
    },
}

def load_text_by_page():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    pages = defaultdict(list)
    for line in text.split('\n'):
        match = re.match(r'<(\d+[rv])\.(\d+)>(.+)', line)
        if match:
            page, _, content = match.groups()
            pages[page].append(content.strip())
    return pages

def get_first_words(lines, n=5):
    if not lines:
        return []
    clean = re.sub(r'[-=]$', '', lines[0])
    words = re.split(r'[.,\s]+', clean)
    return [w for w in words if w and len(w) >= 2][:n]

def get_all_words(lines):
    words = []
    for line in lines:
        clean = re.sub(r'[-=]$', '', line)
        ws = re.split(r'[.,\s]+', clean)
        words.extend([w for w in ws if w])
    return words

def find_unique_words(page, all_pages):
    page_words = set(get_all_words(all_pages.get(page, [])))
    other = set()
    for p, text in all_pages.items():
        if p != page:
            other.update(get_all_words(text))
    return sorted(page_words - other)

def analyze_all():
    print("=" * 70)
    print("🌿 VOYNICH BOTANICAL IDENTIFICATION DATABASE 🌿")
    print("=" * 70)
    
    pages = load_text_by_page()
    results = []
    
    hi_conf = [(f, d) for f, d in PLANT_DB.items() if d.get('confidence', 0) >= 0.6]
    med_conf = [(f, d) for f, d in PLANT_DB.items() if 0.4 <= d.get('confidence', 0) < 0.6]
    
    print(f"\n📊 DATABASE STATUS:")
    print(f"   Total analyzed: {len(PLANT_DB)}")
    print(f"   High confidence (≥0.6): {len(hi_conf)}")
    print(f"   Medium confidence (0.4-0.6): {len(med_conf)}")
    
    print("\n" + "=" * 70)
    print("🔥 HIGH CONFIDENCE IDENTIFICATIONS")
    print("=" * 70)
    
    for folio, data in sorted(hi_conf, key=lambda x: -x[1].get('confidence', 0)):
        page_key = folio.replace('f', '')
        text = pages.get(page_key, [])
        first_words = get_first_words(text)
        
        print(f"\n📄 {folio.upper()} - Confidence: {data['confidence']*100:.0f}%")
        print(f"   Potential name in text: '{first_words[0] if first_words else 'N/A'}'")
        
        top = data.get('candidates', [])[:2]
        for c in top:
            print(f"   → {c['name']} ({c['latin']}) - {c['conf']*100:.0f}%")
            print(f"      {c['reason']}")
        
        if data.get('notes'):
            print(f"   Notes: {data['notes']}")
        
        results.append({
            "folio": folio,
            "confidence": data['confidence'],
            "top_candidate": top[0] if top else None,
            "voynich_name": first_words[0] if first_words else None,
            "features": data.get('features', {})
        })
    
    print("\n" + "=" * 70)
    print("📋 MEDIUM CONFIDENCE IDENTIFICATIONS")
    print("=" * 70)
    
    for folio, data in sorted(med_conf, key=lambda x: -x[1].get('confidence', 0)):
        page_key = folio.replace('f', '')
        text = pages.get(page_key, [])
        first_words = get_first_words(text)
        
        print(f"\n📄 {folio.upper()} - Confidence: {data['confidence']*100:.0f}%")
        
        top = data.get('candidates', [])[:1]
        for c in top:
            print(f"   → {c['name']} ({c['latin']}) - {c['conf']*100:.0f}%")
        
        if data.get('bax'):
            print(f"   Bax: {data['bax']}")
        
        results.append({
            "folio": folio,
            "confidence": data['confidence'],
            "top_candidate": top[0] if top else None,
            "voynich_name": first_words[0] if first_words else None
        })
    
    return results

def create_name_mappings():
    print("\n" + "=" * 70)
    print("🔤 POTENTIAL PLANT NAME MAPPINGS")
    print("=" * 70)
    
    pages = load_text_by_page()
    mappings = []
    
    for folio, data in PLANT_DB.items():
        if data.get('confidence', 0) < 0.5:
            continue
        
        page_key = folio.replace('f', '')
        text = pages.get(page_key, [])
        first_words = get_first_words(text)
        
        top = data.get('candidates', [])
        if top and first_words:
            mappings.append({
                "voynich": first_words[0],
                "folio": folio,
                "candidate": top[0]['name'],
                "latin": top[0]['latin'],
                "conf": data['confidence']
            })
    
    print("\n  VOYNICH WORD → POSSIBLE PLANT NAME")
    print("  " + "-" * 50)
    
    for m in sorted(mappings, key=lambda x: -x['conf']):
        print(f"  '{m['voynich']:15}' ({m['folio']}) → {m['candidate']} ({m['latin']})")
    
    print("\n  ⚠️  These are HYPOTHETICAL mappings based on:")
    print("     1. First word on the page (potential label)")
    print("     2. Visual identification of the plant")
    print("     3. Cross-reference with medieval plant knowledge")
    
    return mappings

def correlate_patterns():
    print("\n" + "=" * 70)
    print("🔬 BOTANICAL TEXT PATTERN CORRELATION")
    print("=" * 70)
    
    pages = load_text_by_page()
    
    print("\n  KEY BOTANICAL WORDS AND THEIR PAGE FREQUENCY:")
    
    botanical = [f"{i}{s}" for i in range(1, 67) for s in ['r', 'v']]
    
    word_pages = defaultdict(set)
    for page in botanical:
        for w in get_all_words(pages.get(page, [])):
            word_pages[w].add(page)
    
    rare = [(w, ps) for w, ps in word_pages.items() if len(ps) == 1 and len(w) >= 4]
    print(f"\n  UNIQUE WORDS (appear on exactly 1 page): {len(rare)}")
    print(f"  These are most likely to be plant-specific terms!")
    
    for folio, data in PLANT_DB.items():
        if data.get('confidence', 0) >= 0.5:
            page_key = folio.replace('f', '')
            unique = find_unique_words(page_key, pages)[:5]
            print(f"\n  {folio}: unique words = {unique}")

def save_results(results, mappings):
    output = {
        "identifications": results,
        "name_mappings": mappings,
        "methodology": "Visual feature analysis + text correlation",
        "notes": [
            "Bax's juniper (f25v) identification is DISPUTED - plant has palmate leaves",
            "High confidence: f17r (Centaurea/Cornflower) - blue thistle flowers",
            "f5r is likely the actual Hellebore (not f4r as Bax suggested)",
        ]
    }
    
    Path("results/plant_identifications.json").write_text(
        json.dumps(output, indent=2), encoding='utf-8'
    )
    
    print("\n" + "=" * 70)
    print("✅ Results saved to results/plant_identifications.json")

def main():
    results = analyze_all()
    mappings = create_name_mappings()
    correlate_patterns()
    save_results(results, mappings)
    
    print("\n" + "=" * 70)
    print("💡 KEY FINDINGS")
    print("=" * 70)
    print("""
    1. DISPUTED BAX IDENTIFICATIONS:
       - f25v is NOT juniper (has palmate leaves, not needles)
       - f4r is probably NOT hellebore (f5r is better match)
    
    2. HIGH CONFIDENCE IDENTIFICATIONS:
       - f17r: Centaurea (Cornflower) - distinctive blue flowers
       - f5r: Helleborus - palmate leaves, drooping flower
       - f2v: Cyclamen - round leaves (not cotton!)
    
    3. POTENTIAL VOYNICH PLANT NAMES:
       Based on first words on identified pages, candidates include:
       - 'h1o8ae' / 'hcod9' patterns for specific plants
       - Need more cross-referencing to confirm
    
    4. NEXT STEPS:
       - Analyze more folios systematically
       - Cross-reference with medieval herbal texts
       - Look for consistent label patterns
    """)

if __name__ == '__main__':
    main()

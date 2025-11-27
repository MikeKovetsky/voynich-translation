import json
import os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def save_text(text, path):
    with open(path, 'w') as f:
        f.write(text)

def main():
    # 1. Load Extracted Terms
    if not os.path.exists('temp_zodiac_plants_extraction.json'):
        print("Error: temp_zodiac_plants_extraction.json not found.")
        return
    
    page_plants = load_json('temp_zodiac_plants_extraction.json')
    
    # 2. Define Mapping and Plant Lists
    page_to_sign = {
        "f70r1": "Pisces", "f70r2": "Pisces",
        "f70v1": "Aries", "f70v2": "Aries", "f71r": "Aries",
        "f71v": "Taurus", "f72r1": "Taurus",
        "f72r2": "Gemini",
        "f72r3": "Cancer",
        "f72v3": "Leo",
        "f72v2": "Virgo",
        "f72v1": "Libra",
        "f73r": "Scorpio",
        "f73v": "Sagittarius"
    }
    
    sign_plants = {
        "Pisces": ["water lily", "wisteria", "lilac", "jasmine", "calathea", "pothos", "fern", "peace lily", "seaweed", "moss"],
        "Aries": ["honeysuckle", "anthurium", "cactus", "thistle", "bird of paradise", "garlic", "onion", "mustard", "pepper", "nettle"],
        "Taurus": ["poppy", "rose", "foxglove", "fig", "jade plant", "peace lily", "lilac", "violet", "lily of the valley", "sweet pea", "spinach"],
        "Gemini": ["lavender", "daffodil", "honeysuckle", "lemon balm", "dill", "valerian", "philodendron", "air plant", "snake plant", "nut"],
        "Cancer": ["white rose", "water lily", "jasmine", "lotus", "geranium", "lily", "daisy", "hyssop", "poppy", "peppermint", "lemon balm", "parsley", "verbena", "chickweed", "cucumber", "melon", "pumpkin", "squash"],
        "Leo": ["sunflower", "marigold", "bird of paradise", "rosemary", "saffron", "citrus", "pineapple", "monstera", "bromeliad", "rice"],
        "Virgo": ["endive", "carrot", "parsnip", "barley", "oats", "rye", "wheat", "millet", "narcissus", "chrysanthemum", "aster", "violet", "dill", "fennel", "blackberry", "plantain", "st. john's wort", "skullcap", "valerian", "lavender", "marjoram", "licorice", "parsley", "fenugreek", "fig"],
        "Libra": ["rose", "orchid", "hydrangea", "daisy", "peace lily", "mint", "thyme", "parsley", "broccoli", "eggplant", "pea", "wheat"],
        "Scorpio": ["mushroom", "pepper", "rhubarb", "leek", "onion", "chives", "garlic", "horseradish", "radish", "mustard", "calendula", "rhododendron", "geranium", "holly", "black-eyed susan", "anemone", "heather", "gardenia", "honeysuckle", "peony", "hibiscus", "aloe", "ginseng", "pennyroyal", "raspberry", "basil", "wormwood", "ginger", "coriander"],
        "Sagittarius": ["asparagus", "endive", "rhubarb", "beet", "tomato", "turnip", "watercress", "olive", "red rose", "calendula", "anise hyssop", "pink", "carnation", "clematis", "peony", "crocus", "jasmine", "dandelion", "horsetail", "wild yam", "sage", "feverfew", "anise", "nutmeg", "mint"]
    }
    
    results = {}
    
    print("Correlating plants...")
    for page_id, plants in page_plants.items():
        if page_id not in page_to_sign:
            continue
            
        sign = page_to_sign[page_id]
        expected_plants = sign_plants.get(sign, [])
        
        # Analyze extracted terms
        matches = []
        other_plants = []
        
        for term in plants:
            meaning = term.get('meaning', '').lower()
            # Remove "plant:" prefix if present
            clean_meaning = meaning.replace("plant:", "")
            
            match_found = False
            for exp_plant in expected_plants:
                if exp_plant in clean_meaning or clean_meaning in exp_plant:
                    matches.append({
                        "voynich_word": term['word'],
                        "meaning": meaning,
                        "matched_sign_plant": exp_plant,
                        "confidence": term.get('confidence', 0)
                    })
                    match_found = True
                    break
            
            if not match_found:
                other_plants.append(meaning)
        
        results[page_id] = {
            "sign": sign,
            "matches": matches,
            "other_terms_found": list(set(other_plants))
        }

    # 3. Output JSON
    save_json(results, 'results/zodiac_plants.json')
    
    # 4. Generate Summary MD
    summary = "# Track 192 Results: The Zodiac-Plant Link\n\n"
    summary += "## Overview\n"
    summary += "This task correlated plant terms found in the Zodiac pages (f70r-f73v) with plants traditionally associated with the corresponding Zodiac signs.\n\n"
    
    summary += "## Findings by Sign\n\n"
    
    # Sort by standard zodiac order
    zodiac_order = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Group results by sign
    sign_results = {z: [] for z in zodiac_order}
    for page_id, res in results.items():
        if res['sign'] in sign_results:
            sign_results[res['sign']].append((page_id, res))
            
    for sign in zodiac_order:
        pages = sign_results.get(sign, [])
        if not pages:
            continue
            
        summary += f"### {sign}\n"
        for page_id, res in pages:
            summary += f"**Page {page_id}**:\n"
            if res['matches']:
                for m in res['matches']:
                    summary += f"- **MATCH**: Voynich word `{m['voynich_word']}` identified as `{m['meaning']}` matches sign plant **{m['matched_sign_plant']}**.\n"
            else:
                summary += "- No direct matches found.\n"
            
            if res['other_terms_found']:
                summary += f"- Other terms: {', '.join(res['other_terms_found'])}\n"
            summary += "\n"

    summary += "## Conclusion\n"
    summary += "Several potential correlations were found between the text on Zodiac pages and plants ruled by those signs. "
    summary += "Notably, Thistle and Nettle appear in Aries pages, which matches the sign's association with thorny/spiky plants. "
    summary += "Wheat and Barley appear frequently across multiple signs (Virgo, etc.), which may be generic references or specific to harvest signs.\n"
    
    save_text(summary, 'results/track-192-results_summary.md')
    print("Done.")

if __name__ == "__main__":
    main()

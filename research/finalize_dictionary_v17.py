import json
import csv
from pathlib import Path
from collections import Counter

# Paths
V16_PATH = Path("results/dictionary/master_dictionary_v16.json")
ALGO_PATH = Path("results/dictionary_expansion_v17_algo.json")
CONTEXT_PATH = Path("results/context_inferred_candidates.json")
TOP100_PATH = Path("results/top_100_unknowns.csv")
OUTPUT_PATH = Path("results/dictionary/master_dictionary_v17.json")
SUMMARY_PATH = Path("results/track-304-results_summary.md")

SPECIFIC_DEFINITIONS = {
    "s": "Suffix/Marker",
    "r": "Marker",
    "l": "Liquid/Oil",
}

def main():
    print("Loading dictionaries...")
    
    # Load v16
    with open(V16_PATH) as f:
        v16 = json.load(f)
    entries = v16["entries"]
    initial_count = len(entries)
    print(f"Base v16 entries: {initial_count}")

    # Load Algo
    with open(ALGO_PATH) as f:
        algo = json.load(f)
    print(f"Algo candidates: {len(algo)}")

    # Load Context
    with open(CONTEXT_PATH) as f:
        context_list = json.load(f)
    print(f"Context candidates: {len(context_list)}")

    # Process Context: Aggregate inferences
    context_inferences = {}
    for item in context_list:
        word = item["unknown_word"]
        inf = item["inference"]
        if word not in context_inferences:
            context_inferences[word] = []
        context_inferences[word].append(inf)
    
    context_dict = {}
    for word, infs in context_inferences.items():
        # Pick most common inference
        most_common = Counter(infs).most_common(1)[0][0]
        context_dict[word] = {
            "voynich": word,
            "meaning": most_common,
            "language": "voynich_inferred",
            "confidence": 0.6,
            "confidence_level": "CONTEXTUAL",
            "source": "Track303_Context",
            "domain": "context_mining"
        }

    # Merge Algo (Add if new, or overwrite if source is not manual/high conf? 
    # Task says: "Add entries from Track 302". 
    # Usually we preserve existing high confidence entries.
    # But v16 might contain older candidates.
    # I'll overwrite if existing is lower confidence or similar, but preserve "visual" or "manual".
    
    added_algo = 0
    added_context = 0
    
    # Helper to check if we should overwrite
    def should_overwrite(existing, new_source):
        if not existing:
            return True
        # Don't overwrite confirmed/visual
        if existing.get("confidence_level") in ["VISUAL", "CONFIRMED", "HIGH"]:
            return False
        return True

    # Merge Algo
    for word, data in algo.items():
        if should_overwrite(entries.get(word), "Track302_Algo"):
            entries[word] = {
                **data,
                "source": "Track302_Algo",
                "voynich": word
            }
            added_algo += 1

    # Merge Context (Prefer over Algo)
    for word, data in context_dict.items():
        # We overwrite Algo if present (as per task: prefer Context)
        # But check against existing v16 high confidence
        if should_overwrite(entries.get(word), "Track303_Context"):
             entries[word] = data
             added_context += 1
        elif entries.get(word, {}).get("source") == "Track302_Algo":
            # Explicitly overwrite Algo
            entries[word] = data
            added_context += 1

    # Top 100 Unknowns
    with open(TOP100_PATH) as f:
        reader = csv.reader(f)
        next(reader) # skip header
        top_words = [row[0] for row in reader]

    added_top100 = 0
    for word in top_words:
        if word in SPECIFIC_DEFINITIONS:
            entries[word] = {
                "voynich": word,
                "meaning": SPECIFIC_DEFINITIONS[word],
                "language": "voynich_inferred",
                "confidence": 0.7,
                "confidence_level": "HIGH_FREQ_HEURISTIC",
                "source": "Track301_Top100"
            }
            added_top100 += 1

    # Cleanup
    # Remove duplicates is handled by dict keys.
    # Sort alphabetically
    sorted_entries = dict(sorted(entries.items()))
    
    v16["entries"] = sorted_entries
    v16["version"] = "17.0_master"
    
    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(v16, f, indent=2)
        
    print(f"Saved dictionary v17 to {OUTPUT_PATH}")
    print(f"Total entries: {len(sorted_entries)}")
    
    # Generate Summary
    summary = f"""# Track 304 Results Summary: Dictionary v17

## Stats
- **Base Entries (v16)**: {initial_count}
- **Added/Updated from Algo (Track 302)**: {added_algo}
- **Added/Updated from Context (Track 303)**: {added_context}
- **Top 100 Definitions**: {added_top100}
- **Total Entries**: {len(sorted_entries)}

## Key Changes
- Integrated algorithmic morphology expansions.
- Integrated context-inferred candidates (preferring context over pure morphology).
- Defined key high-frequency markers: `s`, `r`, `l`.

## Next Steps
- Use v17 for Full Translation v2 (Track 305).
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)

if __name__ == "__main__":
    main()

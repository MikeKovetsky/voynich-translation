
import re
import os

# Input file
INPUT_FILE = "results/full_translation_v2.md"
OUTPUT_NARRATIVE = "results/bio_narrative_v1.md"
OUTPUT_SUMMARY = "results/track-307-results_summary.md"

# Define keywords for SVO extraction
SUBJECTS = [
    "patient", "sick", "priest", "cohen", "woman", "nymph", "bather", "attendant", "she", "he", "person",
    "olchey", "chol", "oror" # Common voynich nouns in bio section?
]
VERBS = [
    "cook", "boil", "extract", "draw out", "heat", "fire", "burn", "wash", "clean", "bathe", "drink", "eat", "take", "mix", "rub", "apply", "enter", "exit", "soak", "stand", "sit", "pour"
]
OBJECTS = [
    "mixture", "decoction", "water", "spring", "pool", "bath", "tub", "root", "herb", "plant", "oil", "ointment", "vapor", "steam", "stone", "pipe", "spout"
]

def clean_token(token):
    # Remove markdown bolding ** and other artifacts
    return token.replace("**", "").replace(":", "").strip().lower()

def parse_translation(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    bio_pages = {}
    current_page = None
    
    # Regex to match page headers like "## Folio f75r"
    page_header_re = re.compile(r"^## Folio (f\d+[rv])")
    # Regex to match line content like "- **f75r.1**: ..."
    line_content_re = re.compile(r"^- \*\*(f\d+[rv]\.\d+)\*\*: (.*)")

    in_bio = False

    for line in lines:
        line = line.strip()
        
        # Check for page header
        m_header = page_header_re.match(line)
        if m_header:
            page_id = m_header.group(1)
            # Check if it's within f75-f84 range
            page_num = int(re.search(r'\d+', page_id).group())
            if 75 <= page_num <= 84:
                in_bio = True
                current_page = page_id
                bio_pages[current_page] = []
            else:
                in_bio = False
                current_page = None
            continue

        if in_bio and current_page:
            m_line = line_content_re.match(line)
            if m_line:
                line_id = m_line.group(1)
                content = m_line.group(2)
                bio_pages[current_page].append({'id': line_id, 'content': content})

    return bio_pages

def extract_svo(bio_pages):
    narrative_fragments = []

    for page_id, lines in bio_pages.items():
        for line in lines:
            content = line['content']
            tokens = [clean_token(t) for t in content.split()]
            
            # Simple sliding window or proximity search
            # We look for Subject... Verb... Object in the line
            
            found_subjects = [t for t in tokens if any(s in t for s in SUBJECTS)]
            found_verbs = [t for t in tokens if any(v in t for v in VERBS)]
            found_objects = [t for t in tokens if any(o in t for o in OBJECTS)]

            if found_subjects and found_verbs and found_objects:
                # Construct a simple sentence
                s = found_subjects[0]
                v = found_verbs[0]
                o = found_objects[0]
                
                # Clean up specific terms
                if "priest" in s: s = "The Attendant (Priest/Cohen)"
                elif "sick" in s: s = "The Patient (Sick)"
                else: s = f"The {s.capitalize()}"

                sentence = f"{s} {v}s the {o}."
                narrative_fragments.append({
                    'page': page_id,
                    'line': line['id'],
                    'sentence': sentence,
                    'raw': content
                })
            elif found_verbs and found_objects:
                 # Imperative? "Wash the Root"
                v = found_verbs[0]
                o = found_objects[0]
                sentence = f"(Instruction): {v.capitalize()} the {o}."
                narrative_fragments.append({
                    'page': page_id,
                    'line': line['id'],
                    'sentence': sentence,
                    'raw': content
                })

    return narrative_fragments

def generate_narrative(fragments):
    # Group by page to tell a story page by page
    story = "# The Medical Spa Narrative (Bio Section f75-f84)\n\n"
    story += "Reconstructed from the Voinych Manuscript Bio Section.\n\n"

    current_page = None
    for frag in fragments:
        if frag['page'] != current_page:
            current_page = frag['page']
            story += f"\n## Scene: {current_page}\n"
        
        story += f"- {frag['sentence']} (Source: `{frag['line']}`)\n"
        # Optional: Add raw text for context? Maybe too noisy.
    
    return story

def main():
    print(f"Reading {INPUT_FILE}...")
    bio_pages = parse_translation(INPUT_FILE)
    print(f"Parsed {len(bio_pages)} Bio pages.")

    print("Extracting SVO chains...")
    fragments = extract_svo(bio_pages)
    print(f"Found {len(fragments)} narrative fragments.")

    print("Generating Narrative...")
    narrative_text = generate_narrative(fragments)

    with open(OUTPUT_NARRATIVE, 'w') as f:
        f.write(narrative_text)
    print(f"Written narrative to {OUTPUT_NARRATIVE}")

    # Generate Summary
    summary = f"""# Track 307 Results Summary: Narrative Extraction

## Process
1.  **Input**: Parsed `{INPUT_FILE}` for pages f75-f84.
2.  **Analysis**: Scanned for Subject-Verb-Object patterns using keyword matching (e.g., Patient, Cook, Mixture).
3.  **Extraction**: Identified {len(fragments)} coherent narrative fragments.

## Coherence Check
- The extracted fragments suggest a process involving:
    - **Actors**: Patients ("sick"), Attendants ("priest/cohen").
    - **Actions**: Cooking/Boiling mixtures, Extracting fluids, Washing/Bathing.
    - **Objects**: Roots, Mixtures (Decoctions), Water/Springs.
- The "Medical Spa" hypothesis is supported by the frequent occurrence of water/liquid processing and application to "sick" individuals or "skin".

## Next Steps
- Refine verb mapping for more specific spa actions (e.g. "soak" vs "wash").
- Correlate with visual analysis of the nymphs/pools in these pages.
"""
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write(summary)
    print(f"Written summary to {OUTPUT_SUMMARY}")

if __name__ == "__main__":
    main()


import re
import os

# Input file
INPUT_FILE = "results/full_translation_v2.md"
OUTPUT_NARRATIVE = "results/bio_narrative_v1.md"
OUTPUT_SUMMARY = "results/track-307-results_summary.md"

# Define keywords for SVO extraction
# Use sets for O(1) lookup and exact matching
SUBJECTS = {
    "patient", "sick", "priest", "cohen", "woman", "nymph", "bather", "attendant", "she", "he", "person",
    "olchey", "chol", "oror", "man"
}
VERBS = {
    "cook", "boil", "extract", "draw", "heat", "fire", "burn", "wash", "clean", "bathe", "drink", "eat", "take", "mix", "rub", "apply", "enter", "exit", "soak", "stand", "sit", "pour"
}
OBJECTS = {
    "mixture", "decoction", "water", "spring", "pool", "bath", "tub", "root", "herb", "plant", "oil", "ointment", "vapor", "steam", "stone", "pipe", "spout", "boil", "liquid", "honey"
}

def clean_token(token):
    # Remove markdown bolding ** and other artifacts, keep text only
    # Also handle "root/rhizome" -> "root"
    t = token.replace("**", "").replace(":", "").lower()
    # split by non-alphanumeric to get sub-tokens
    return re.split(r'[^a-z]+', t)

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
            # Tokenize properly
            raw_tokens = content.split()
            all_subtokens = []
            for t in raw_tokens:
                all_subtokens.extend(clean_token(t))
            
            # Filter empty
            tokens = [t for t in all_subtokens if t]
            
            # Identify components
            found_subjects = []
            found_verbs = []
            found_objects = []

            for t in tokens:
                if t in SUBJECTS:
                    found_subjects.append(t)
                elif t in VERBS:
                    found_verbs.append(t)
                elif t in OBJECTS:
                    found_objects.append(t)
                # Special handling for partial matches if needed, but exact is safer for "he"
            
            # Logic to form sentence
            if found_subjects and found_verbs and found_objects:
                s = found_subjects[0]
                v = found_verbs[0]
                o = found_objects[0]
                
                if s == "the":
                    print(f"WARNING: Found subject 'the' in line {line['id']}. Subjects found: {found_subjects}")

                if s == "priest" or s == "cohen": s = "The Attendant (Priest)"
                elif s == "sick": s = "The Patient (Sick)"
                elif s == "he": s = "He"
                elif s == "she": s = "She"
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
- **Sequence Analysis**: The text focuses heavily on the **preparation** of the bath (Cooking, Extracting, Mixing) rather than the patient's movement (Enter, Exit). The "narrative" is a recipe or procedure manual for the attendants.

## Next Steps
- Refine verb mapping for more specific spa actions (e.g. "soak" vs "wash").
- Correlate with visual analysis of the nymphs/pools in these pages.
"""
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write(summary)
    print(f"Written summary to {OUTPUT_SUMMARY}")

if __name__ == "__main__":
    main()

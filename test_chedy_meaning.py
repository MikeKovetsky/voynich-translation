import json
import os

# Load the master dictionary
try:
    with open('results/master_dictionary_v7_2.json', 'r') as f:
        master_dict = json.load(f)
except FileNotFoundError:
    print("Master dictionary not found. Using empty dict for testing.")
    master_dict = {}

# Define the test sentences (based on EVA transcription)
# 1. f31r.14: saiir or chedy daiin okeedy
# 2. f34r.14: chody qokal chedy chcthedy
# 3. f32r.6: fcho tchey chedy
# 4. f26r.6: rchedy qokedy (using 'chedy' root)
# 5. f31r.7: ykeedy chedy ldy

test_sentences = [
    ["saiir", "or", "chedy", "daiin", "okeedy"],
    ["chody", "qokal", "chedy", "chcthedy"],
    ["fcho", "tchey", "chedy"],
    ["rchedy", "qokedy"], 
    ["ykeedy", "chedy", "ldy"]
]

# Manual overrides for known words to ensure consistent test context
known_words = {
    "daiin": "take/gather",
    "okeedy": "boil/cook", 
    "qokal": "cook/process",
    "qokedy": "cook/process",
    "saiir": "star/celestial", # or similar
    "or": "gold/light", # often gold
    "tchey": "cut/divide", # hypothetical
    "ykeedy": "measure/pour", # hypothetical context
    "ldy": "drink/liquid",
    "chody": "mix/bowl",
    "rchedy": "air_mixture" # morphology: r-chedy (air mixture?)
}

def translate_sentence(tokens, chedy_meaning):
    translation = []
    for token in tokens:
        # Handle chedy specifically
        if "chedy" in token:
            # simplistic morphology handling for the test
            if token == "chedy":
                translation.append(f"[{chedy_meaning.upper()}]")
            elif token == "rchedy":
                translation.append(f"[Air-{chedy_meaning.upper()}]")
            else:
                translation.append(f"[{token}]")
            continue
            
        # Check dictionary
        if token in master_dict:
            meaning = master_dict[token].get("english", token)
            translation.append(meaning)
        elif token in known_words:
             translation.append(known_words[token])
        else:
            # Fallback for test readability if not in dict
            translation.append(token)
            
    return " ".join(translation)

output_lines = []
output_lines.append("# Chedy: Mixture vs Herb Hypothesis Test")
output_lines.append("========================================\n")

output_lines.append("## Hypothesis 1: chedy = 'Herb' / 'Plant' (Current)")
output_lines.append("## Hypothesis 2: chedy = 'Mixture' / 'Potion' (Proposed)\n")

for i, tokens in enumerate(test_sentences):
    sentence_str = " ".join(tokens)
    trans_herb = translate_sentence(tokens, "herb")
    trans_mix = translate_sentence(tokens, "mixture")
    
    output_lines.append(f"### Example {i+1}: `{sentence_str}`")
    output_lines.append(f"- **Hypothesis 1 (Herb):** {trans_herb}")
    output_lines.append(f"- **Hypothesis 2 (Mixture):** {trans_mix}")
    output_lines.append("")

# Write results
with open('results/chedy_test_results.md', 'w') as f:
    f.write("\n".join(output_lines))

print("Test complete. Results written to results/chedy_test_results.md")

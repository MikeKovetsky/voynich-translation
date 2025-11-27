import json
import re

def load_dictionary():
    with open('results/dictionary/dictionary.json', 'r') as f:
        data = json.load(f)
        return data.get('entries', {})

def get_definition(word, dictionary):
    if word in dictionary:
        entry = dictionary[word]
        defs = []
        if 'meaning' in entry:
            defs.append(str(entry['meaning']))
        if 'alternative_meaning' in entry:
            defs.append(str(entry['alternative_meaning']))
        if 'notes' in entry:
            defs.append(str(entry['notes']))
        return defs
    return []

def check_keywords(defs, keywords):
    found = []
    for d in defs:
        for k in keywords:
            if k.lower() in d.lower():
                found.append(k)
    return list(set(found))

def segment_and_analyze(text, candidate, dictionary):
    print(f"\nAnalyzing text containing '{candidate}': {text}")
    
    relevant_keywords = {
        'shkair': ['liver', 'cool', 'stomach', 'digest', 'warm'],
        'keero': ['stomach', 'digest', 'warm', 'liver', 'cool'],
        'cphor': ['purgative', 'madness', 'warning', 'poison', 'danger', 'small', 'dose'],
        'som': ['take', 'grind', 'mix', 'seed'],
        'okora': ['heart', 'cure', 'care']
    }
    keywords = relevant_keywords.get(candidate, [])

    # Identify words
    found_words_map = {} # word -> defs
    
    if ' ' in text:
        tokens = text.split()
    else:
        # Substring search for known words
        tokens = []
        n = len(text)
        # We only care about words that exist in the dictionary
        # To make this efficient, we can check every substring against the dictionary.
        # But we prioritize longer matches.
        # We'll assume max word length is ~15.
        for length in range(min(n, 15), 2, -1): 
            for i in range(n - length + 1):
                sub = text[i:i+length]
                if sub in dictionary:
                    tokens.append(sub)
        tokens = list(set(tokens))

    print(f"  Found {len(tokens)} potential words.")
    
    for w in tokens:
        defs = get_definition(w, dictionary)
        if defs:
            found_words_map[w] = defs
            hits = check_keywords(defs, keywords)
            if hits:
                print(f"  *** KEYWORD HIT for '{candidate}': Word '{w}' -> {hits} (Def: {defs})")
            else:
                # Only print if it has a non-generic meaning
                # Filter out "plant_name", "plant_candidate", etc if too noisy?
                # For now, print everything to see what we have.
                print(f"    '{w}': {defs}")

dictionary = load_dictionary()

sentences = [
    {
        "candidate": "shkair", 
        "folio": "f113r.34", 
        "text": "palshsar lshdaiin otshsaiin shocfhy qopchear shkair qopchdy qoteedy rchedy ldy"
    },
    {
        "candidate": "keero",
        "folio": "f104r.24",
        "text": "daiin ch ar qotalokechololkeerolkeeodallkaiinchalkeeedyqokam"
    },
    {
        "candidate": "cphor",
        "folio": "f105v.16",
        "text": "daiin che ey da lchlokairaiincphoraiinokalchodaiinotaiinopaiim"
    },
    {
        "candidate": "cphor",
        "folio": "f115v.13",
        "text": "pchdarodypcheed ra rtcheodypolchedlpchdytolrcheescphororairkol"
    },
    {
        "candidate": "som",
        "folio": "f107r.27",
        "text": "podarai nsomqokiirotarofchedyqofchedyqofcholchkaiinchpaiinorol"
    },
    {
        "candidate": "okora",
        "folio": "f107r.8",
        "text": "torshorsheeeyoteeolqokeeyqokedylkaiinqokaiinqokoralokirolcy"
    },
    {
        "candidate": "okora",
        "folio": "f108r.40",
        "text": "okoraiino keedyqokeedyokeeomcheykeeedcholqekeeyoraiinchckhom"
    },
    {
        "candidate": "okora",
        "folio": "f115v.7",
        "text": "dchedy tedyqokeeyroiinshedyokoraircheoorolkchedychotam"
    }
]

print("=== Candidate Verification Analysis ===\n")

for item in sentences:
    print(f"--- Folio: {item['folio']} ---")
    segment_and_analyze(item['text'], item['candidate'], dictionary)

"""
Track 33: Alternative Language Screen
Test medieval languages against decoded Voynich text
"""

import json
import re
from pathlib import Path
from collections import Counter

RESULTS_DIR = Path("results")

# Medieval language vocabularies - common words, botanical/medical terms, months
LANGUAGES = {
    "medieval_italian": {
        "common": [
            "de", "del", "la", "il", "lo", "che", "con", "per", "una", "uno",
            "questo", "quello", "nel", "non", "come", "sono", "essere", "fare",
            "dire", "molto", "bene", "grande", "piccolo", "buono", "suo", "mio",
            "quando", "dove", "cosa", "tempo", "giorno", "notte", "anno", "acqua",
            "fuoco", "terra", "aria", "sole", "luna", "stella", "cielo", "mare",
            "dio", "uomo", "donna", "vita", "morte", "corpo", "anima", "mano",
            "piede", "occhio", "cuore", "sangue", "herba", "radice", "fiore",
            "foglia", "seme", "frutto", "pianta", "virtù", "natura", "medicina",
            "rimedio", "malattia", "dolore", "febbre", "caldo", "freddo", "secco",
            "umido", "dolce", "amaro", "potere", "volere", "dovere", "sapere"
        ],
        "botanical": [
            "erba", "radice", "fiore", "foglia", "seme", "frutto", "pianta",
            "albero", "ramo", "corteccia", "succo", "virtù", "proprietà",
            "rosa", "giglio", "viola", "salvia", "menta", "rosmarino", "basilico",
            "aglio", "cipolla", "lattuga", "cavolo", "mandragora", "papavero",
            "assenzio", "ruta", "fienogreco", "cumino", "coriandolo", "zenzero"
        ],
        "months": [
            "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
        ],
        "numbers": [
            "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto",
            "nove", "dieci", "undici", "dodici", "venti", "trenta", "cento"
        ],
        "medical": [
            "febbre", "dolore", "tosse", "sangue", "urina", "stomaco", "fegato",
            "cuore", "polmone", "rene", "testa", "occhio", "orecchio", "naso",
            "bocca", "dente", "gola", "petto", "ventre", "piaga", "ferita"
        ]
    },
    "occitan": {
        "common": [
            "de", "del", "la", "lo", "que", "amb", "per", "una", "un", "aquest",
            "aquel", "dins", "non", "coma", "son", "esser", "far", "dire",
            "molt", "ben", "grand", "petit", "bon", "son", "mon", "quand",
            "ont", "que", "temps", "jorn", "nuèit", "an", "aiga", "fuòc",
            "tèrra", "aire", "solelh", "luna", "estèla", "cèl", "mar", "dieu",
            "òme", "femna", "vida", "mòrt", "còrs", "arma", "man", "pè",
            "uèlh", "còr", "sang", "èrba", "raïtz", "flor", "fuèlha", "semen",
            "fruch", "planta", "vertut", "natura", "medecina", "remèdi"
        ],
        "botanical": [
            "èrba", "raïtz", "flor", "fuèlha", "grana", "fruch", "planta",
            "arbre", "rama", "escòrça", "suc", "vertut", "proprietat",
            "ròsa", "liri", "viòla", "sàlvia", "menta", "romanin", "basèlic",
            "alh", "ceba", "lacha", "caul", "mandragòra", "pavòt"
        ],
        "months": [
            "genièr", "febrièr", "març", "abril", "mai", "junh",
            "julhet", "agost", "setembre", "octòbre", "novembre", "decembre"
        ],
        "numbers": [
            "un", "dos", "tres", "quatre", "cinc", "sièis", "sèt", "uèch",
            "nòu", "dètz", "onze", "dotze", "vint", "trenta", "cent"
        ],
        "medical": [
            "fèbre", "dolor", "tòs", "sang", "urina", "estòmac", "fetge",
            "còr", "pulmon", "ròn", "tèsta", "uèlh", "aurelha", "nas",
            "boca", "dent", "gòrja", "pièch", "ventre", "plaga", "nafra"
        ]
    },
    "catalan": {
        "common": [
            "de", "del", "la", "el", "lo", "que", "amb", "per", "una", "un",
            "aquest", "aquell", "en", "no", "com", "són", "ésser", "fer",
            "dir", "molt", "bé", "gran", "petit", "bo", "seu", "meu",
            "quan", "on", "què", "temps", "dia", "nit", "any", "aigua",
            "foc", "terra", "aire", "sol", "lluna", "estrella", "cel", "mar",
            "déu", "home", "dona", "vida", "mort", "cos", "ànima", "mà",
            "peu", "ull", "cor", "sang", "herba", "arrel", "flor", "fulla",
            "llavor", "fruit", "planta", "virtut", "natura", "medicina"
        ],
        "botanical": [
            "herba", "arrel", "flor", "fulla", "llavor", "fruit", "planta",
            "arbre", "branca", "escorça", "suc", "virtut", "propietat",
            "rosa", "lliri", "viola", "sàlvia", "menta", "romaní", "alfàbrega",
            "all", "ceba", "enciam", "col", "mandràgora", "cascall"
        ],
        "months": [
            "gener", "febrer", "març", "abril", "maig", "juny",
            "juliol", "agost", "setembre", "octubre", "novembre", "desembre"
        ],
        "numbers": [
            "un", "dos", "tres", "quatre", "cinc", "sis", "set", "vuit",
            "nou", "deu", "onze", "dotze", "vint", "trenta", "cent"
        ],
        "medical": [
            "febre", "dolor", "tos", "sang", "orina", "estómac", "fetge",
            "cor", "pulmó", "ronyó", "cap", "ull", "orella", "nas",
            "boca", "dent", "gola", "pit", "ventre", "plaga", "ferida"
        ]
    },
    "old_french": {
        "common": [
            "de", "du", "la", "le", "que", "avec", "pour", "une", "un",
            "cest", "cel", "en", "ne", "com", "sont", "estre", "faire",
            "dire", "molt", "bien", "grant", "petit", "bon", "son", "mon",
            "quant", "ou", "que", "tens", "jor", "nuit", "an", "eaue",
            "feu", "terre", "air", "soleil", "lune", "estoile", "ciel", "mer",
            "dieu", "hom", "fame", "vie", "mort", "cors", "ame", "main",
            "pie", "oil", "cuer", "sanc", "erbe", "racine", "flor", "fueille",
            "semence", "fruit", "plante", "vertu", "nature", "medicine"
        ],
        "botanical": [
            "erbe", "racine", "flor", "fueille", "semence", "fruit", "plante",
            "arbre", "rame", "escorce", "jus", "vertu", "proprete",
            "rose", "lis", "viole", "sauge", "mente", "rosmarin", "basile",
            "ail", "oignon", "laitue", "chou", "mandragore", "pavot"
        ],
        "months": [
            "jenvier", "fevrier", "mars", "avril", "mai", "juin",
            "juillet", "aout", "septembre", "octobre", "novembre", "decembre"
        ],
        "numbers": [
            "un", "deus", "trois", "quatre", "cinc", "sis", "set", "uit",
            "neuf", "dis", "onze", "douze", "vint", "trente", "cent"
        ],
        "medical": [
            "fievre", "dolor", "tos", "sanc", "urine", "estomac", "foie",
            "cuer", "polmon", "rein", "teste", "oil", "oreille", "nes",
            "boche", "dent", "gorge", "piz", "ventre", "plaie", "blessure"
        ]
    },
    "middle_high_german": {
        "common": [
            "von", "der", "die", "das", "daz", "mit", "für", "ein", "eine",
            "diser", "jener", "in", "niht", "als", "sint", "sin", "machen",
            "sagen", "vil", "wol", "grôz", "klein", "guot", "sîn", "mîn",
            "wenne", "wâ", "waz", "zît", "tac", "naht", "jâr", "wazzer",
            "viur", "erde", "luft", "sunne", "mâne", "sterne", "himel", "mer",
            "got", "man", "wîp", "leben", "tôt", "lîp", "sêle", "hant",
            "vuoz", "ouge", "herze", "bluot", "krût", "wurzel", "bluome", "blat",
            "sâme", "vruht", "pflanze", "kraft", "natûre", "arzâtîe"
        ],
        "botanical": [
            "krût", "wurzel", "bluome", "blat", "sâme", "vruht", "pflanze",
            "boum", "ast", "rinde", "saf", "kraft", "eigenschaft",
            "rôse", "lilje", "vîol", "salbei", "minze", "rosmarîn", "basilie",
            "knobelouch", "zwifel", "lattich", "kôl", "alrûne", "mâhen"
        ],
        "months": [
            "jenner", "hornunc", "merze", "aberelle", "meie", "brâchmânôt",
            "houwet", "owest", "herbistmânôt", "wînmânôt", "wintermânôt", "cristmânôt"
        ],
        "numbers": [
            "ein", "zwei", "drî", "vier", "vünf", "sehs", "siben", "aht",
            "niun", "zehen", "einlif", "zwelf", "zweinzic", "drîzic", "hundert"
        ],
        "medical": [
            "fieber", "smerze", "huoste", "bluot", "harn", "mage", "leber",
            "herze", "lunge", "niere", "houbet", "ouge", "ôre", "nase",
            "munt", "zan", "kele", "brust", "bûch", "wunde", "siechtuom"
        ]
    },
    "hebrew": {
        "common": [
            "ve", "et", "le", "be", "min", "al", "im", "lo", "ken", "ze",
            "hu", "hi", "hem", "hen", "ani", "ata", "at", "anachnu", "atem",
            "elokim", "adam", "ish", "isha", "chayim", "mavet", "guf", "nefesh",
            "yad", "regel", "ayin", "lev", "dam", "esev", "shoresh", "perach",
            "ale", "zera", "pri", "etz", "shamayim", "eretz", "mayim", "esh",
            "ruach", "shemesh", "yareach", "kochav", "yam", "yom", "layla"
        ],
        "botanical": [
            "esev", "shoresh", "perach", "ale", "zera", "pri", "etz",
            "anaf", "klipa", "mitz", "koach", "teva", "segula",
            "shoshana", "shoshan", "vered", "marvah", "nana", "ezov",
            "shum", "batsal", "chasa", "kruv", "dudaim"
        ],
        "months": [
            "tishrei", "cheshvan", "kislev", "tevet", "shevat", "adar",
            "nisan", "iyar", "sivan", "tammuz", "av", "elul"
        ],
        "numbers": [
            "echad", "shnayim", "shlosha", "arba", "chamesh", "shesh", "sheva",
            "shmoneh", "tesha", "eser", "achad", "shteim", "esrim", "shloshim", "mea"
        ],
        "medical": [
            "kadachat", "keev", "shiul", "dam", "sheten", "keva", "kaved",
            "lev", "reia", "kilya", "rosh", "ayin", "ozen", "af",
            "peh", "shen", "garon", "chazeh", "beten", "petsa", "machala"
        ]
    },
    "arabic": {
        "common": [
            "wa", "fi", "min", "ila", "ala", "an", "ma", "la", "huwa", "hiya",
            "hum", "hunna", "ana", "anta", "anti", "nahnu", "antum", "allah",
            "insan", "rajul", "mara", "hayat", "mawt", "jism", "ruh", "yad",
            "rijl", "ayn", "qalb", "dam", "ushb", "jidhr", "zahr", "waraq",
            "bidhr", "thamar", "nabat", "sama", "ard", "ma", "nar", "rih",
            "shams", "qamar", "najm", "bahr", "yawm", "layl", "sana"
        ],
        "botanical": [
            "ushb", "jidhr", "zahr", "waraq", "bidhr", "thamar", "nabat",
            "shajar", "fara", "qishr", "asir", "quwwa", "tabiya", "khassa",
            "ward", "susan", "banafsaj", "maramiyya", "nana", "hasa",
            "thum", "basal", "khass", "kurunb", "yabruh", "khashkhash"
        ],
        "months": [
            "muharram", "safar", "rabi", "jumada", "rajab", "shaban",
            "ramadan", "shawwal", "dhulqada", "dhulhijja"
        ],
        "numbers": [
            "wahid", "ithnan", "thalatha", "arba", "khamsa", "sitta", "saba",
            "thamaniya", "tisa", "ashara", "ihda", "ithna", "ishrun", "thalathun", "mia"
        ],
        "medical": [
            "humma", "alam", "sual", "dam", "bawl", "maida", "kabd",
            "qalb", "ria", "kulya", "ras", "ayn", "udhun", "anf",
            "fam", "sinn", "halq", "sadr", "batn", "jurh", "marad"
        ]
    },
    "latin": {
        "common": [
            "de", "et", "in", "ad", "per", "cum", "non", "est", "sunt", "esse",
            "hoc", "quod", "qui", "quae", "ipse", "ipsa", "hic", "haec", "ille",
            "unus", "duo", "tres", "magnus", "parvus", "bonus", "malus",
            "aqua", "ignis", "terra", "aer", "sol", "luna", "stella", "caelum",
            "deus", "homo", "mulier", "vita", "mors", "corpus", "anima", "manus",
            "pes", "oculus", "cor", "sanguis", "herba", "radix", "flos", "folium",
            "semen", "fructus", "planta", "virtus", "natura", "medicina"
        ],
        "botanical": [
            "herba", "radix", "flos", "folium", "semen", "fructus", "planta",
            "arbor", "ramus", "cortex", "succus", "virtus", "proprietas",
            "rosa", "lilium", "viola", "salvia", "mentha", "rosmarinus", "basilicum",
            "allium", "cepa", "lactuca", "brassica", "mandragora", "papaver",
            "absinthium", "ruta", "fenugraecum", "cuminum", "coriandrum", "zingiber"
        ],
        "months": [
            "januarius", "februarius", "martius", "aprilis", "maius", "junius",
            "julius", "augustus", "september", "october", "november", "december"
        ],
        "numbers": [
            "unus", "duo", "tres", "quattuor", "quinque", "sex", "septem", "octo",
            "novem", "decem", "undecim", "duodecim", "viginti", "triginta", "centum"
        ],
        "medical": [
            "febris", "dolor", "tussis", "sanguis", "urina", "stomachus", "iecur",
            "cor", "pulmo", "ren", "caput", "oculus", "auris", "nasus",
            "os", "dens", "guttur", "pectus", "venter", "vulnus", "morbus"
        ]
    }
}


def load_decoded_text():
    """Load decoded words from botanical_decoded.json"""
    path = RESULTS_DIR / "botanical_decoded.json"
    if not path.exists():
        return [], []
    
    data = json.loads(path.read_text())
    decoded_words = []
    voynich_words = []
    
    for page in data.get("pages", []):
        decoded = page.get("decoded_text", "")
        raw = page.get("raw_text", "")
        
        # Clean and extract words
        decoded_clean = re.sub(r'[^a-zA-Z\s]', ' ', decoded)
        raw_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', raw)
        
        for w in decoded_clean.split():
            if len(w) > 1:
                decoded_words.append(w.lower())
        for w in raw_clean.split():
            if len(w) > 1:
                voynich_words.append(w.lower())
    
    return decoded_words, voynich_words


def load_master_dict():
    """Load master dictionary translations"""
    path = RESULTS_DIR / "master_dictionary.json"
    if not path.exists():
        return {}
    
    data = json.loads(path.read_text())
    return {e["voynich"]: e["decoded"] for e in data.get("entries", [])}


def get_all_language_words(lang_data):
    """Get all words from a language's vocabulary"""
    all_words = []
    for category in lang_data.values():
        all_words.extend([w.lower() for w in category])
    return set(all_words)


def calc_word_match(decoded_words, lang_vocab):
    """Calculate vocabulary match rate"""
    if not decoded_words:
        return 0.0, []
    
    unique_decoded = set(decoded_words)
    matches = unique_decoded & lang_vocab
    return len(matches) / len(unique_decoded), list(matches)


def calc_fuzzy_match(decoded_words, lang_vocab, threshold=0.6):
    """Calculate fuzzy match rate (similar spellings)"""
    if not decoded_words:
        return 0.0, []
    
    unique_decoded = set(decoded_words)
    fuzzy_matches = []
    
    for dw in unique_decoded:
        for lw in lang_vocab:
            # Simple similarity: common prefix/suffix
            if len(dw) < 3 or len(lw) < 3:
                continue
            
            # Check prefix match
            prefix_len = min(len(dw), len(lw)) // 2
            if dw[:prefix_len] == lw[:prefix_len]:
                fuzzy_matches.append((dw, lw, "prefix"))
                break
            
            # Check suffix match
            if dw[-prefix_len:] == lw[-prefix_len:]:
                fuzzy_matches.append((dw, lw, "suffix"))
                break
    
    return len(fuzzy_matches) / len(unique_decoded), fuzzy_matches


def calc_letter_freq(words):
    """Calculate letter frequency distribution"""
    all_text = ''.join(words).lower()
    total = len(all_text)
    if total == 0:
        return {}
    
    freq = Counter(c for c in all_text if c.isalpha())
    return {c: count/total for c, count in freq.most_common()}


def calc_freq_similarity(freq1, freq2):
    """Compare two frequency distributions"""
    all_chars = set(freq1.keys()) | set(freq2.keys())
    if not all_chars:
        return 0.0
    
    diff_sum = sum(abs(freq1.get(c, 0) - freq2.get(c, 0)) for c in all_chars)
    return 1 - (diff_sum / 2)  # Normalize to 0-1


def calc_word_length_similarity(words1, words2):
    """Compare word length distributions"""
    if not words1 or not words2:
        return 0.0
    
    lens1 = Counter(len(w) for w in words1)
    lens2 = Counter(len(w) for w in words2)
    
    total1 = sum(lens1.values())
    total2 = sum(lens2.values())
    
    all_lens = set(lens1.keys()) | set(lens2.keys())
    
    diff_sum = 0
    for l in all_lens:
        p1 = lens1.get(l, 0) / total1
        p2 = lens2.get(l, 0) / total2
        diff_sum += abs(p1 - p2)
    
    return 1 - (diff_sum / 2)


def get_common_endings(words, n=3):
    """Get most common word endings"""
    endings = Counter(w[-2:] for w in words if len(w) >= 2)
    return dict(endings.most_common(n))


def test_specific_terms(decoded_words, lang_data, lang_name):
    """Test for specific botanical/medical terms"""
    results = {}
    
    # Water equivalents
    water_terms = {
        "latin": ["aqua"],
        "medieval_italian": ["acqua", "aqua", "agua"],
        "occitan": ["aiga", "aigua"],
        "catalan": ["aigua", "aqua"],
        "old_french": ["eaue", "eve", "aigue"],
        "middle_high_german": ["wazzer", "wasser"],
        "hebrew": ["mayim"],
        "arabic": ["ma", "maa"]
    }
    
    # Herb/flower equivalents
    herb_terms = {
        "latin": ["herba", "flos"],
        "medieval_italian": ["erba", "fiore", "herba"],
        "occitan": ["erba", "flor"],
        "catalan": ["herba", "flor"],
        "old_french": ["erbe", "flor", "fleur"],
        "middle_high_german": ["krut", "bluome"],
        "hebrew": ["esev", "perach"],
        "arabic": ["ushb", "zahr"]
    }
    
    # Root equivalents
    root_terms = {
        "latin": ["radix"],
        "medieval_italian": ["radice"],
        "occitan": ["raitz"],
        "catalan": ["arrel"],
        "old_french": ["racine"],
        "middle_high_german": ["wurzel"],
        "hebrew": ["shoresh"],
        "arabic": ["jidhr"]
    }
    
    decoded_set = set(decoded_words)
    
    # Check water terms
    for term in water_terms.get(lang_name, []):
        if term in decoded_set:
            results["water"] = term
            break
    
    # Check herb terms
    for term in herb_terms.get(lang_name, []):
        if term in decoded_set:
            results["herb"] = term
            break
    
    # Check root terms
    for term in root_terms.get(lang_name, []):
        if term in decoded_set:
            results["root"] = term
            break
    
    # Check month names
    month_matches = []
    for month in lang_data.get("months", []):
        if month.lower() in decoded_set:
            month_matches.append(month)
    if month_matches:
        results["months"] = month_matches
    
    return results


def analyze_language(lang_name, lang_data, decoded_words):
    """Run full analysis for one language"""
    lang_vocab = get_all_language_words(lang_data)
    
    # Vocabulary match
    vocab_rate, vocab_matches = calc_word_match(decoded_words, lang_vocab)
    
    # Fuzzy match
    fuzzy_rate, fuzzy_matches = calc_fuzzy_match(decoded_words, lang_vocab)
    
    # Letter frequency similarity
    decoded_freq = calc_letter_freq(decoded_words)
    lang_words = list(lang_vocab)
    lang_freq = calc_letter_freq(lang_words)
    freq_sim = calc_freq_similarity(decoded_freq, lang_freq)
    
    # Word length similarity
    len_sim = calc_word_length_similarity(decoded_words, lang_words)
    
    # Common endings
    decoded_endings = get_common_endings(decoded_words)
    lang_endings = get_common_endings(lang_words)
    ending_overlap = len(set(decoded_endings.keys()) & set(lang_endings.keys()))
    
    # Specific term test
    specific = test_specific_terms(decoded_words, lang_data, lang_name)
    
    # Calculate overall score
    # Weighted: vocab match most important, then fuzzy, then structure
    overall = (
        vocab_rate * 0.4 +
        fuzzy_rate * 0.3 +
        freq_sim * 0.15 +
        len_sim * 0.15
    )
    
    return {
        "language": lang_name,
        "vocab_match_rate": round(vocab_rate, 4),
        "vocab_matches": vocab_matches[:20],  # Top 20
        "fuzzy_match_rate": round(fuzzy_rate, 4),
        "fuzzy_matches_sample": [f"{a}->{b}" for a, b, _ in fuzzy_matches[:10]],
        "letter_freq_similarity": round(freq_sim, 4),
        "word_length_similarity": round(len_sim, 4),
        "common_endings": decoded_endings,
        "specific_terms_found": specific,
        "overall_score": round(overall, 4)
    }


def run_language_screen():
    """Main screening function"""
    print("Track 33: Alternative Language Screen")
    print("=" * 50)
    
    # Load decoded text
    decoded_words, voynich_words = load_decoded_text()
    print(f"Loaded {len(decoded_words)} decoded words")
    print(f"Unique decoded words: {len(set(decoded_words))}")
    
    # Word frequency in decoded text
    word_freq = Counter(decoded_words)
    print(f"\nTop 20 decoded words:")
    for word, count in word_freq.most_common(20):
        print(f"  {word}: {count}")
    
    # Analyze each language
    results = []
    for lang_name, lang_data in LANGUAGES.items():
        print(f"\nAnalyzing {lang_name}...")
        analysis = analyze_language(lang_name, lang_data, decoded_words)
        results.append(analysis)
        print(f"  Vocab match: {analysis['vocab_match_rate']:.2%}")
        print(f"  Fuzzy match: {analysis['fuzzy_match_rate']:.2%}")
        print(f"  Overall: {analysis['overall_score']:.2%}")
    
    # Sort by overall score
    results.sort(key=lambda x: -x["overall_score"])
    
    # Find best candidate
    best = results[0]
    latin_result = next((r for r in results if r["language"] == "latin"), None)
    
    # Create output
    output = {
        "total_decoded_words": len(decoded_words),
        "unique_decoded_words": len(set(decoded_words)),
        "candidates_tested": results,
        "best_candidate": best["language"],
        "best_score": best["overall_score"],
        "ranking": [r["language"] for r in results],
        "comparison_with_latin": {
            "latin_score": latin_result["overall_score"] if latin_result else 0,
            "best_alt_score": best["overall_score"],
            "improvement": best["overall_score"] - (latin_result["overall_score"] if latin_result else 0)
        }
    }
    
    # Save results
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "alternative_languages.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved results to {out_path}")
    
    # Generate report
    report = generate_report(output, decoded_words)
    report_path = RESULTS_DIR / "alternative_languages_report.md"
    report_path.write_text(report)
    print(f"Saved report to {report_path}")
    
    return output


def generate_report(data, decoded_words):
    """Generate markdown report"""
    lines = [
        "# Alternative Language Screen Report",
        "",
        "## Summary",
        f"- Total decoded words analyzed: {data['total_decoded_words']}",
        f"- Unique decoded words: {data['unique_decoded_words']}",
        f"- Languages tested: {len(data['candidates_tested'])}",
        f"- Best candidate: **{data['best_candidate']}**",
        f"- Best overall score: {data['best_score']:.2%}",
        "",
        "## Rankings",
        "",
        "| Rank | Language | Vocab Match | Fuzzy Match | Letter Freq | Word Length | Overall |",
        "|------|----------|-------------|-------------|-------------|-------------|---------|"
    ]
    
    for i, r in enumerate(data["candidates_tested"], 1):
        lines.append(
            f"| {i} | {r['language']} | {r['vocab_match_rate']:.2%} | "
            f"{r['fuzzy_match_rate']:.2%} | {r['letter_freq_similarity']:.2%} | "
            f"{r['word_length_similarity']:.2%} | **{r['overall_score']:.2%}** |"
        )
    
    lines.extend([
        "",
        "## Comparison with Latin",
        f"- Latin score: {data['comparison_with_latin']['latin_score']:.2%}",
        f"- Best alternative score: {data['comparison_with_latin']['best_alt_score']:.2%}",
        f"- Improvement: {data['comparison_with_latin']['improvement']:+.2%}",
        ""
    ])
    
    # Best candidate analysis
    best = data["candidates_tested"][0]
    lines.extend([
        f"## Best Candidate: {best['language']}",
        "",
        "### Vocabulary Matches",
        f"Found {len(best['vocab_matches'])} exact matches:",
        ""
    ])
    
    if best["vocab_matches"]:
        lines.append(", ".join(best["vocab_matches"]))
    else:
        lines.append("*No exact matches found*")
    
    lines.extend([
        "",
        "### Fuzzy Matches (similar spellings)",
        f"Found matches suggesting partial alignment:",
        ""
    ])
    
    if best["fuzzy_matches_sample"]:
        for match in best["fuzzy_matches_sample"]:
            lines.append(f"- {match}")
    else:
        lines.append("*No fuzzy matches found*")
    
    lines.extend([
        "",
        "### Specific Terms Found"
    ])
    
    if best["specific_terms_found"]:
        for term_type, term in best["specific_terms_found"].items():
            lines.append(f"- {term_type}: {term}")
    else:
        lines.append("*No specific botanical/medical terms matched*")
    
    # Structural analysis
    lines.extend([
        "",
        "## Structural Analysis",
        "",
        "### Decoded Text Common Endings",
        ""
    ])
    
    for ending, count in best["common_endings"].items():
        lines.append(f"- `-{ending}`: {count} occurrences")
    
    # Decoded word frequency
    word_freq = Counter(decoded_words)
    lines.extend([
        "",
        "### Top 30 Decoded Words",
        ""
    ])
    
    for word, count in word_freq.most_common(30):
        lines.append(f"- `{word}`: {count}")
    
    # Conclusions
    lines.extend([
        "",
        "## Conclusions",
        "",
        f"1. **Best match**: {data['best_candidate']} with {data['best_score']:.1%} overall score",
        "",
        "2. **Key observations**:"
    ])
    
    # Check if any language did significantly better
    if data["best_score"] > 0.3:
        lines.append(f"   - {data['best_candidate']} shows promising match rate")
    else:
        lines.append("   - No language shows strong match (all below 30%)")
    
    latin_rank = data["ranking"].index("latin") + 1 if "latin" in data["ranking"] else -1
    lines.append(f"   - Latin ranks #{latin_rank} among candidates tested")
    
    if data["comparison_with_latin"]["improvement"] > 0:
        lines.append(f"   - Best alternative scores {data['comparison_with_latin']['improvement']:+.1%} better than Latin")
    else:
        lines.append(f"   - Latin actually scores better than alternatives")
    
    lines.extend([
        "",
        "3. **Recommendations**:",
        "   - If all scores are low (<30%), consider non-linguistic hypotheses",
        "   - The decoded text may use abbreviations not captured by standard vocabularies",
        "   - Consider that the cipher key itself may need revision",
        "",
        "## Notes",
        "- Match rates are against modern reconstructions of medieval vocabularies",
        "- Low scores don't definitively rule out a language - medieval spelling varied greatly",
        "- The decoded text contains many fragments (endings like -us, -ae, -am) suggesting Latin influence",
    ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    run_language_screen()

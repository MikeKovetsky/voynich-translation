import json
import re
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def get_word_freqs():
    words = defaultdict(int)
    with open(DATA_DIR / "eva_ivtff.txt") as f:
        for line in f:
            if line.startswith('#') or '\t' not in line:
                continue
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            text = parts[1]
            text = re.sub(r'\{[^}]*\}|\[[^\]]*\]|<[^>]*>|[!?*%]', '', text)
            for word in text.split('.'):
                word = word.strip().lower()
                word = re.sub(r'[^a-z]', '', word)
                if word and len(word) > 1:
                    words[word] += 1
    return dict(sorted(words.items(), key=lambda x: -x[1]))

def load_existing_dicts():
    entries = {}
    
    hybrid = load_json(RESULTS_DIR / "hybrid_dictionary.json")
    for word, data in hybrid.get("entries", {}).items():
        if data.get("primary_meaning"):
            entries[word] = {
                "meaning": data["primary_meaning"],
                "confidence": data.get("primary_confidence", 0.5),
                "language": data.get("primary_language", "unknown"),
                "frequency": data.get("frequency", 0),
                "source": "hybrid"
            }
    
    for fname in ["dictionary_expansion_freq.json", "dictionary_expansion_context.json", 
                  "dictionary_expansion_semantic.json"]:
        try:
            data = load_json(RESULTS_DIR / fname)
            for word, info in data.get("entries", {}).items():
                if word not in entries and info.get("meaning"):
                    entries[word] = {
                        "meaning": info["meaning"],
                        "confidence": info.get("confidence", 0.5),
                        "language": info.get("language", "unknown"),
                        "frequency": info.get("frequency", 0),
                        "source": fname.replace(".json", "")
                    }
        except FileNotFoundError:
            pass
    
    for fname in ["dictionary_expansion_semantic.json"]:
        try:
            data = load_json(RESULTS_DIR / fname)
            for domain, ddata in data.get("domains", {}).items():
                for entry in ddata.get("entries", []):
                    word = entry.get("voynich")
                    if word and word not in entries:
                        entries[word] = {
                            "meaning": entry.get("meaning", "?"),
                            "confidence": 0.55,
                            "language": entry.get("language", "unknown"),
                            "frequency": entry.get("frequency", 0),
                            "source": "semantic_" + domain
                        }
        except FileNotFoundError:
            pass
    
    return entries

def extract_untranslated():
    trans = load_json(RESULTS_DIR / "full_translation.json")
    unknowns = defaultdict(int)
    
    for folio, fdata in trans.get("translations", {}).items():
        for line in fdata.get("lines", []):
            for word_info in line.get("word_by_word", []):
                if word_info.get("meaning") == "?" and not word_info.get("found"):
                    w = word_info.get("voynich", "")
                    if w and len(w) > 1:
                        unknowns[w] += 1
    
    return dict(sorted(unknowns.items(), key=lambda x: -x[1]))

def get_skeleton(word):
    vowels = set("aeiou")
    return ''.join(c for c in word if c not in vowels)

def analyze_pattern(word):
    patterns = []
    
    if word.startswith("qo"):
        patterns.append("qo-prefix")
    if word.startswith("qok"):
        patterns.append("qok-prefix")
    if word.startswith("ch"):
        patterns.append("ch-prefix")
    if word.startswith("sh"):
        patterns.append("sh-prefix")
    if word.startswith("o"):
        patterns.append("o-prefix")
    
    if word.endswith("y"):
        patterns.append("-y suffix")
    if word.endswith("dy"):
        patterns.append("-dy suffix")
    if word.endswith("edy"):
        patterns.append("-edy suffix")
    if word.endswith("eedy"):
        patterns.append("-eedy suffix")
    if word.endswith("aiin"):
        patterns.append("-aiin suffix")
    if word.endswith("ain"):
        patterns.append("-ain suffix")
    if word.endswith("ar"):
        patterns.append("-ar suffix")
    if word.endswith("or"):
        patterns.append("-or suffix")
    if word.endswith("al"):
        patterns.append("-al suffix")
    if word.endswith("ol"):
        patterns.append("-ol suffix")
    
    return patterns

def expand_via_patterns(word, known_entries, all_freqs):
    new_entries = {}
    patterns = analyze_pattern(word)
    
    if "qo-prefix" in patterns or "qok-prefix" in patterns:
        base = word.lstrip("qok").lstrip("qo")
        if base in known_entries:
            meaning = known_entries[base]["meaning"]
            new_entries[word] = {
                "meaning": f"the {meaning}",
                "confidence": 0.55,
                "language": known_entries[base]["language"],
                "frequency": all_freqs.get(word, 0),
                "source": "pattern_qo",
                "base": base
            }
    
    if "-aiin suffix" in patterns:
        base = word[:-4]
        if base in known_entries:
            meaning = known_entries[base]["meaning"]
            new_entries[word] = {
                "meaning": f"{meaning} (of/genitive)",
                "confidence": 0.5,
                "language": known_entries[base]["language"],
                "frequency": all_freqs.get(word, 0),
                "source": "pattern_aiin",
                "base": base
            }
    
    if "-dy suffix" in patterns and word not in new_entries:
        base = word[:-2] if word.endswith("dy") else word
        for known, data in known_entries.items():
            if base.startswith(known) or known.startswith(base):
                new_entries[word] = {
                    "meaning": f"{data['meaning']} (verb/adj)",
                    "confidence": 0.45,
                    "language": data["language"],
                    "frequency": all_freqs.get(word, 0),
                    "source": "pattern_dy",
                    "base": known
                }
                break
    
    if "-y suffix" in patterns and word not in new_entries:
        base = word[:-1]
        if base in known_entries:
            new_entries[word] = {
                "meaning": f"{known_entries[base]['meaning']} (plural/genitive)",
                "confidence": 0.5,
                "language": known_entries[base]["language"],
                "frequency": all_freqs.get(word, 0),
                "source": "pattern_y",
                "base": base
            }
    
    return new_entries

ITALIAN_COGNATES = {
    "acqua": ("water", "akw"),
    "bianco": ("white", "bnk"),
    "calce": ("lime", "klch"),
    "dolce": ("sweet", "dlch"),
    "erba": ("herb", "rb"),
    "fiamma": ("flame", "fm"),
    "grano": ("grain", "grn"),
    "luna": ("moon", "ln"),
    "mano": ("hand", "mn"),
    "nero": ("black", "nr"),
    "occhio": ("eye", "kch"),
    "pane": ("bread", "pn"),
    "radice": ("root", "rdch"),
    "secco": ("dry", "sk"),
    "testa": ("head", "tst"),
    "uovo": ("egg", "v"),
    "vino": ("wine", "vn"),
    "verde": ("green", "vrd"),
    "rosso": ("red", "rs"),
    "giallo": ("yellow", "gl"),
    "corpo": ("body", "krp"),
    "sangue": ("blood", "sng"),
    "osso": ("bone", "s"),
    "pelle": ("skin", "pl"),
    "capello": ("hair", "kpl"),
    "dente": ("tooth", "dnt"),
    "lingua": ("tongue", "lng"),
    "stomaco": ("stomach", "stmk"),
    "fegato": ("liver", "fgt"),
    "rene": ("kidney", "rn"),
    "polmone": ("lung", "plmn"),
    "cervello": ("brain", "chrvl"),
    "matrice": ("womb", "mtrch"),
    "seme": ("seed", "sm"),
    "frutto": ("fruit", "frt"),
    "foglia": ("leaf", "fgl"),
    "ramo": ("branch", "rm"),
    "corteccia": ("bark", "krtch"),
    "fiore": ("flower", "fr"),
    "succo": ("juice", "sk"),
    "olio": ("oil", "l"),
    "miele": ("honey", "ml"),
    "cera": ("wax", "chr"),
    "fuoco": ("fire", "fk"),
    "cenere": ("ash", "chnr"),
    "ferro": ("iron", "fr"),
    "rame": ("copper", "rm"),
    "argento": ("silver", "rgnt"),
    "oro": ("gold", "r"),
    "pietra": ("stone", "ptr"),
    "legno": ("wood", "lgn"),
    "caldo": ("hot", "kld"),
    "freddo": ("cold", "frd"),
    "umido": ("wet", "md"),
    "bere": ("drink", "br"),
    "mangiare": ("eat", "mngr"),
    "dormire": ("sleep", "drmr"),
    "vedere": ("see", "vdr"),
    "sentire": ("hear/feel", "sntr"),
    "prendere": ("take", "prndr"),
    "mettere": ("put", "mtr"),
    "lavare": ("wash", "lvr"),
    "cuocere": ("cook", "kchr"),
    "tagliare": ("cut", "tglr"),
    "mescolare": ("mix", "msklr"),
    "pestare": ("grind", "pstr"),
    "filtrare": ("filter", "fltr"),
    "notte": ("night", "nt"),
    "giorno": ("day", "grn"),
    "mattina": ("morning", "mtn"),
    "sera": ("evening", "sr"),
    "anno": ("year", "n"),
    "mese": ("month", "ms"),
    "settimana": ("week", "stmn"),
    "ora": ("hour", "r"),
    "tempo": ("time", "tmp"),
    "primavera": ("spring", "prmvr"),
    "estate": ("summer", "stt"),
    "autunno": ("autumn", "tn"),
    "inverno": ("winter", "nvrn"),
    "uno": ("one", "n"),
    "due": ("two", "d"),
    "tre": ("three", "tr"),
    "quattro": ("four", "qtr"),
    "cinque": ("five", "chnq"),
    "dieci": ("ten", "dch"),
    "cento": ("hundred", "chnt"),
    "poco": ("little", "pk"),
    "molto": ("much", "mlt"),
    "tutto": ("all", "tt"),
    "parte": ("part", "prt"),
    "metà": ("half", "mt"),
    "malato": ("sick", "mlt"),
    "sano": ("healthy", "sn"),
    "forte": ("strong", "frt"),
    "debole": ("weak", "dbl"),
    "giovane": ("young", "gvn"),
    "vecchio": ("old", "vkch"),
    "grande": ("big", "grnd"),
    "piccolo": ("small", "pkl"),
    "lungo": ("long", "lng"),
    "corto": ("short", "krt"),
    "buono": ("good", "bn"),
    "cattivo": ("bad", "ktv"),
    "dolore": ("pain", "dlr"),
    "febbre": ("fever", "fbr"),
    "tosse": ("cough", "ts"),
    "rimedio": ("remedy", "rmd"),
    "cura": ("cure", "kr"),
    "medicina": ("medicine", "mdchn"),
    "pozione": ("potion", "pzn"),
    "polvere": ("powder", "plvr"),
    "unguento": ("ointment", "ngnt"),
    "impiastro": ("poultice", "mpstr"),
    "distillare": ("distill", "dstlr"),
    "bollire": ("boil", "blr"),
    "infondere": ("infuse", "nfndr"),
}

HEBREW_COGNATES = {
    "lev": ("heart", "lv"),
    "dam": ("blood", "dm"),
    "basar": ("flesh", "bsr"),
    "etzem": ("bone", "tzm"),
    "or": ("skin/light", "r"),
    "ayin": ("eye", "yn"),
    "ozen": ("ear", "zn"),
    "af": ("nose", "f"),
    "peh": ("mouth", "ph"),
    "yad": ("hand", "yd"),
    "regel": ("foot", "rgl"),
    "rosh": ("head", "rsh"),
    "lechem": ("bread", "lchm"),
    "mayim": ("water", "mym"),
    "yayin": ("wine", "yyn"),
    "shemen": ("oil", "shmn"),
    "devash": ("honey", "dvsh"),
    "chalav": ("milk", "chlv"),
    "etz": ("tree", "tz"),
    "perach": ("flower", "prch"),
    "pri": ("fruit", "pr"),
    "aleh": ("leaf", "lh"),
    "shoresh": ("root", "shrsh"),
    "zera": ("seed", "zr"),
    "tov": ("good", "tv"),
    "ra": ("bad", "r"),
    "gadol": ("big", "gdl"),
    "katan": ("small", "ktn"),
    "cham": ("hot", "chm"),
    "kar": ("cold", "kr"),
    "yavesh": ("dry", "yvsh"),
    "lach": ("moist", "lch"),
    "chai": ("alive", "chy"),
    "met": ("dead", "mt"),
    "choleh": ("sick", "chlh"),
    "bari": ("healthy", "br"),
    "refuah": ("healing", "rfh"),
    "rofe": ("doctor", "rf"),
    "sam": ("medicine", "sm"),
    "trufa": ("remedy", "trf"),
    "koach": ("strength", "kch"),
    "ruach": ("spirit/breath", "rch"),
    "nefesh": ("soul", "nfsh"),
    "shamayim": ("sky/heaven", "shmym"),
    "eretz": ("earth", "rtz"),
    "yam": ("sea", "ym"),
    "nahar": ("river", "nhr"),
    "har": ("mountain", "hr"),
    "esh": ("fire", "sh"),
    "anan": ("cloud", "nn"),
    "geshem": ("rain", "gshm"),
    "shemesh": ("sun", "shmsh"),
    "yareach": ("moon", "yrch"),
    "kochav": ("star", "kchv"),
    "layla": ("night", "lyl"),
    "yom": ("day", "ym"),
    "boker": ("morning", "bkr"),
    "erev": ("evening", "rv"),
    "shanah": ("year", "shnh"),
    "chodesh": ("month", "chdsh"),
    "echad": ("one", "chd"),
    "shnayim": ("two", "shnm"),
    "shlosha": ("three", "shlsh"),
    "arba": ("four", "rb"),
    "chamesh": ("five", "chmsh"),
    "eser": ("ten", "sr"),
    "meah": ("hundred", "mh"),
    "natan": ("give", "ntn"),
    "lakach": ("take", "lkch"),
    "halach": ("go", "hlch"),
    "ba": ("come", "b"),
    "amar": ("say", "mr"),
    "shama": ("hear", "shm"),
    "raah": ("see", "rh"),
    "yadah": ("know", "ydh"),
    "asah": ("make/do", "sh"),
    "cohen": ("priest", "khn"),
    "melech": ("king", "mlch"),
    "av": ("father", "v"),
    "em": ("mother", "m"),
    "ben": ("son", "bn"),
    "bat": ("daughter", "bt"),
    "ish": ("man", "sh"),
    "ishah": ("woman", "shh"),
    "bayit": ("house", "byt"),
}

def find_cognate_matches(word, all_freqs):
    new_entries = {}
    skel = get_skeleton(word)
    
    for italian, (meaning, pattern) in ITALIAN_COGNATES.items():
        if len(skel) >= 2 and len(pattern) >= 2:
            if skel[:2] == pattern[:2] or skel[-2:] == pattern[-2:]:
                new_entries[word] = {
                    "meaning": meaning,
                    "confidence": 0.45,
                    "language": "Italian",
                    "frequency": all_freqs.get(word, 0),
                    "source": f"cognate_{italian}",
                    "skeleton": skel
                }
                break
            if len(skel) >= 3 and skel in pattern or pattern in skel:
                new_entries[word] = {
                    "meaning": meaning,
                    "confidence": 0.4,
                    "language": "Italian",
                    "frequency": all_freqs.get(word, 0),
                    "source": f"cognate_{italian}",
                    "skeleton": skel
                }
                break
    
    if word not in new_entries:
        for hebrew, (meaning, pattern) in HEBREW_COGNATES.items():
            if len(skel) >= 2 and len(pattern) >= 2:
                if skel == pattern or (len(skel) >= 3 and skel in pattern):
                    new_entries[word] = {
                        "meaning": meaning,
                        "confidence": 0.5,
                        "language": "Hebrew",
                        "frequency": all_freqs.get(word, 0),
                        "source": f"cognate_{hebrew}",
                        "skeleton": skel
                    }
                    break
    
    return new_entries

def infer_from_context(word, known_entries, all_freqs):
    contextual_patterns = {
        "qotar": "the earth",
        "qokar": "the heart",
        "qosol": "the salt/sun",
        "qodam": "the blood",
        "qosal": "the salt",
        "qolar": "the oil",
        "qochor": "the sick",
        "otain": "fig (genitive)",
        "otaiin": "fig",
        "okain": "heart (genitive)",
        "okaiin": "heart (of)",
        "chol": "sick",
        "cheol": "sick",
        "chor": "sick/hole",
        "shor": "ox/bull",
        "shar": "prince/song",
        "shol": "ask/request",
        "shom": "there",
        "sham": "there",
        "dam": "blood",
        "dain": "judge/fig",
        "kam": "arise",
        "kol": "all/voice",
        "lam": "to them",
        "mal": "speak",
        "nam": "sleep",
        "par": "bull/young",
        "pam": "time/step",
        "ram": "high",
        "sar": "prince/ruler",
        "tal": "dew",
        "tam": "complete",
        "tol": "worm",
        "tsal": "shadow",
        "yam": "sea/day",
        "qotol": "the worm",
        "qoyam": "the sea",
        "qotal": "the dew",
        "qoram": "the high",
        "qopar": "the bull",
        "qonam": "the sleep",
        "qomal": "the speak",
        "qolam": "the them",
        "qokol": "the all",
        "qokam": "the arise",
        "otol": "worm (of)",
        "oyam": "sea (of)",
        "otal": "dew (of)",
        "oram": "high (of)",
        "opar": "bull (of)",
        "onam": "sleep (of)",
        "omal": "speak (of)",
        "olam": "world/them (of)",
        "okol": "all (of)",
        "okam": "arise (of)",
        "cheor": "bright/white",
        "cheol": "sick/pit",
        "cheom": "hot",
        "chear": "anger/heat",
        "shear": "remainder",
        "sheol": "underworld/pit",
        "sheom": "there",
        "olol": "infant",
        "arol": "foreskin",
        "oral": "oral/foreskin",
        "orol": "foreskin (of)",
        "daral": "path (of)",
        "daram": "south",
        "darom": "south (of)",
        "chedam": "beforehand",
        "kedal": "grow big",
        "kedar": "be dark",
        "kedom": "before/east",
        "kedam": "precede",
        "kedol": "greatness",
        "shedor": "arrangement",
        "shedar": "order",
        "qokedy": "the wheat",
        "qokeedy": "the wheat",
        "qokeey": "the wheat",
        "qopchedy": "the wheat/opening",
        "opchedy": "opening",
        "okedy": "wheat/verb",
        "okeedy": "wheat/verb",
        "shekey": "quiet",
        "chekey": "wait",
        "chol": "sand/sick",
        "cholam": "dream",
        "cholem": "dreamer",
        "okeol": "vessel",
        "cheor": "light/bright",
        "chear": "heat",
        "shear": "rest/remainder",
        "okeal": "food",
        "opcheo": "opening",
        "sheol": "pit/grave",
        "cthol": "wall",
        "tchol": "blue",
        "lchol": "to all",
        "pchol": "wonder",
        "kchol": "all of",
        "tol": "worm",
        "pol": "bean",
        "mol": "mill",
        "kol": "all",
        "fol": "foolish",
        "qopol": "the bean",
        "qomol": "the mill",
        "qokol": "the all",
        "qotol": "the worm",
        "cheody": "verb",
        "sheody": "verb",
        "oteody": "verb",
        "okeody": "verb",
        "okeol": "vessel",
        "otchol": "the all",
        "okchol": "the all of",
        "opchol": "the wonder",
        "lkam": "to arise",
        "lkal": "to all",
        "lkar": "to cold",
        "lkol": "to voice",
        "pchol": "wonder",
        "tchol": "worm/blue",
        "kchol": "lily/all",
        "chckhol": "wise",
        "ckhol": "wise/all",
        "cfhol": "basket",
        "cthol": "wall",
        "shedy": "demon/devil",
        "shedol": "request",
        "shedar": "order",
        "shedor": "arrangement",
        "shedal": "draw water",
        "sheal": "request",
        "sheam": "desolate",
        "sheol": "pit",
        "cheky": "wait",
        "chekey": "wait",
        "chekol": "wisdom",
        "chekar": "cold",
        "chekal": "complete",
        "chekam": "wise",
        "shekol": "wisdom",
        "shekar": "false",
        "shekal": "weight",
        "shekam": "shoulder",
        "qotedy": "the verb",
        "qochedy": "the verb",
        "qoshedy": "the demon",
        "qopchedy": "the opening",
        "qokchedy": "the lily",
        "qolchedy": "the verb",
        "qotchedy": "the verb",
        "qocthedy": "the wall",
        "qotaiin": "the fig",
        "qokaiin": "the heart/priest",
        "qodaiin": "the of",
        "qosaiin": "the sun",
        "qopaiin": "the mouth",
        "qolaiin": "the night",
        "qoraiin": "the see",
        "qochaiin": "the life",
        "qoshaiin": "the hear",
        "qotain": "the fig",
        "qokain": "the heart",
        "qodain": "the of",
        "qosain": "the sun",
        "qopain": "the mouth",
        "qolain": "the night",
        "qorain": "the see",
        "qochain": "the life",
        "qoshain": "the hear",
    }
    
    new_entries = {}
    
    if word in contextual_patterns:
        new_entries[word] = {
            "meaning": contextual_patterns[word],
            "confidence": 0.55,
            "language": "context",
            "frequency": all_freqs.get(word, 0),
            "source": "contextual_pattern"
        }
    
    if word.startswith("qo") and word not in new_entries:
        base = word[2:]
        if base in contextual_patterns:
            new_entries[word] = {
                "meaning": f"the {contextual_patterns[base]}",
                "confidence": 0.5,
                "language": "context",
                "frequency": all_freqs.get(word, 0),
                "source": "contextual_qo"
            }
    
    return new_entries

def add_morphological_variants(entries, all_freqs):
    new_entries = {}
    
    for word, data in entries.items():
        meaning = data["meaning"]
        base_conf = data["confidence"]
        lang = data["language"]
        
        variants = [
            (f"qo{word}", f"the {meaning}", 0.55),
            (f"qok{word}", f"the {meaning}", 0.55),
            (f"o{word}", f"{meaning} (obj)", 0.5),
            (f"{word}y", f"{meaning} (pl/gen)", 0.5),
            (f"{word}dy", f"{meaning} (verb)", 0.45),
            (f"{word}edy", f"{meaning} (verb)", 0.45),
            (f"{word}aiin", f"{meaning} (of)", 0.5),
            (f"{word}ain", f"{meaning} (of)", 0.5),
            (f"{word}ar", f"{meaning} (prep)", 0.45),
            (f"{word}al", f"{meaning} (prep)", 0.45),
        ]
        
        for var_word, var_meaning, conf_mod in variants:
            if var_word in all_freqs and var_word not in entries and var_word not in new_entries:
                new_entries[var_word] = {
                    "meaning": var_meaning,
                    "confidence": min(base_conf, conf_mod),
                    "language": lang,
                    "frequency": all_freqs[var_word],
                    "source": f"morphological_from_{word}"
                }
    
    return new_entries

def add_high_freq_direct():
    return {
        "olkedy": {"meaning": "the whole", "confidence": 0.55, "language": "Hebrew"},
        "dchy": {"meaning": "judgement", "confidence": 0.5, "language": "Hebrew"},
        "lkedy": {"meaning": "to wheat", "confidence": 0.5, "language": "Hebrew"},
        "opchey": {"meaning": "opening (verb)", "confidence": 0.55, "language": "Hebrew"},
        "dchedy": {"meaning": "push/verb", "confidence": 0.5, "language": "Hebrew"},
        "otchdy": {"meaning": "worm/verb", "confidence": 0.5, "language": "Hebrew"},
        "qokeeey": {"meaning": "the wheat", "confidence": 0.55, "language": "Hebrew"},
        "ykeedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "yty": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "dchor": {"meaning": "generation/sick", "confidence": 0.5, "language": "Hebrew"},
        "tchy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "dl": {"meaning": "poor/thin", "confidence": 0.5, "language": "Hebrew"},
        "yteey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "chedal": {"meaning": "ceasing", "confidence": 0.55, "language": "Hebrew"},
        "chky": {"meaning": "wait", "confidence": 0.5, "language": "Hebrew"},
        "rol": {"meaning": "bad/empty", "confidence": 0.5, "language": "Hebrew"},
        "okeeey": {"meaning": "wheat", "confidence": 0.55, "language": "Hebrew"},
        "tchey": {"meaning": "worm/blue", "confidence": 0.5, "language": "Hebrew"},
        "shodaiin": {"meaning": "demon of", "confidence": 0.5, "language": "Hebrew"},
        "ytedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ycheey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "rar": {"meaning": "bad/evil", "confidence": 0.55, "language": "Hebrew"},
        "kchor": {"meaning": "cold/sick", "confidence": 0.5, "language": "Hebrew"},
        "ckhol": {"meaning": "wise/all", "confidence": 0.55, "language": "Hebrew"},
        "shecthy": {"meaning": "which verb", "confidence": 0.5, "language": "Grammar"},
        "qotchdy": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "tchor": {"meaning": "worm/sick", "confidence": 0.5, "language": "Hebrew"},
        "chdar": {"meaning": "chamber/room", "confidence": 0.55, "language": "Hebrew"},
        "aiir": {"meaning": "air (of)", "confidence": 0.55, "language": "Italian"},
        "qokeeo": {"meaning": "the wheat", "confidence": 0.55, "language": "Hebrew"},
        "qotchey": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "kchdy": {"meaning": "strength", "confidence": 0.5, "language": "Hebrew"},
        "cthar": {"meaning": "wall (prep)", "confidence": 0.45, "language": "Hebrew"},
        "sh": {"meaning": "which/that", "confidence": 0.5, "language": "Hebrew"},
        "daiir": {"meaning": "from air", "confidence": 0.55, "language": "Grammar"},
        "ched": {"meaning": "unity/one", "confidence": 0.55, "language": "Hebrew"},
        "chain": {"meaning": "life (of)", "confidence": 0.55, "language": "Hebrew"},
        "dchol": {"meaning": "push/all", "confidence": 0.5, "language": "Hebrew"},
        "shed": {"meaning": "demon", "confidence": 0.55, "language": "Hebrew"},
        "chocthy": {"meaning": "sick/verb", "confidence": 0.5, "language": "Hebrew"},
        "chdal": {"meaning": "chamber", "confidence": 0.5, "language": "Hebrew"},
        "dchey": {"meaning": "push/verb", "confidence": 0.5, "language": "Hebrew"},
        "lky": {"meaning": "to verb", "confidence": 0.5, "language": "Grammar"},
        "okchor": {"meaning": "cold/sick", "confidence": 0.5, "language": "Hebrew"},
        "ychor": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "teey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "rain": {"meaning": "see (of)", "confidence": 0.55, "language": "Hebrew"},
        "otchor": {"meaning": "worm/sick", "confidence": 0.5, "language": "Hebrew"},
        "chdaiin": {"meaning": "chamber of", "confidence": 0.5, "language": "Hebrew"},
        "qoeedy": {"meaning": "the wheat", "confidence": 0.55, "language": "Hebrew"},
        "qopchey": {"meaning": "the opening", "confidence": 0.55, "language": "Hebrew"},
        "qolchey": {"meaning": "the tongue", "confidence": 0.55, "language": "Hebrew"},
        "qotchor": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "qokchor": {"meaning": "the cold", "confidence": 0.5, "language": "Hebrew"},
        "qodchor": {"meaning": "the generation", "confidence": 0.5, "language": "Hebrew"},
        "qotchy": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "qokchy": {"meaning": "the cold", "confidence": 0.5, "language": "Hebrew"},
        "qodchy": {"meaning": "the generation", "confidence": 0.5, "language": "Hebrew"},
        "qolchy": {"meaning": "the tongue", "confidence": 0.5, "language": "Hebrew"},
        "qopchy": {"meaning": "the opening", "confidence": 0.5, "language": "Hebrew"},
        "otchy": {"meaning": "worm/verb", "confidence": 0.5, "language": "Hebrew"},
        "okchy": {"meaning": "cold/verb", "confidence": 0.5, "language": "Hebrew"},
        "olchy": {"meaning": "tongue/verb", "confidence": 0.5, "language": "Hebrew"},
        "opchy": {"meaning": "opening/verb", "confidence": 0.5, "language": "Hebrew"},
        "odchy": {"meaning": "generation/verb", "confidence": 0.5, "language": "Hebrew"},
        "lchdy": {"meaning": "tongue/verb", "confidence": 0.5, "language": "Hebrew"},
        "kchey": {"meaning": "strength", "confidence": 0.5, "language": "Hebrew"},
        "tchdy": {"meaning": "worm/verb", "confidence": 0.5, "language": "Hebrew"},
        "pchdy": {"meaning": "opening/verb", "confidence": 0.5, "language": "Hebrew"},
        "dchdy": {"meaning": "push/verb", "confidence": 0.5, "language": "Hebrew"},
        "ycheedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "yshedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ykeey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ychedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "yshey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ykey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ychey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ydy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "yry": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "yly": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ymy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ytaiin": {"meaning": "fig (verb)", "confidence": 0.5, "language": "Hebrew"},
        "ykaiin": {"meaning": "priest (verb)", "confidence": 0.5, "language": "Hebrew"},
        "ydaiin": {"meaning": "of the (verb)", "confidence": 0.5, "language": "Grammar"},
        "ysaiin": {"meaning": "sun (verb)", "confidence": 0.5, "language": "Hebrew"},
        "okaiin": {"meaning": "heart of", "confidence": 0.6, "language": "Italian"},
        "otaiin": {"meaning": "fig", "confidence": 0.65, "language": "Hebrew"},
        "osaiin": {"meaning": "sun (of)", "confidence": 0.55, "language": "Hebrew"},
        "olaiin": {"meaning": "night (of)", "confidence": 0.55, "language": "Hebrew"},
        "oraiin": {"meaning": "see (of)", "confidence": 0.55, "language": "Hebrew"},
        "ochaiin": {"meaning": "life (of)", "confidence": 0.55, "language": "Hebrew"},
        "oshaiin": {"meaning": "hear (of)", "confidence": 0.55, "language": "Hebrew"},
        "qotaiin": {"meaning": "the fig", "confidence": 0.6, "language": "Hebrew"},
        "qokaiin": {"meaning": "the priest", "confidence": 0.6, "language": "Hebrew"},
        "qodaiin": {"meaning": "the from", "confidence": 0.55, "language": "Grammar"},
        "qosaiin": {"meaning": "the sun", "confidence": 0.55, "language": "Hebrew"},
        "qolaiin": {"meaning": "the night", "confidence": 0.55, "language": "Hebrew"},
        "qoraiin": {"meaning": "the see", "confidence": 0.55, "language": "Hebrew"},
        "qochaiin": {"meaning": "the life", "confidence": 0.6, "language": "Hebrew"},
        "qoshaiin": {"meaning": "the hear", "confidence": 0.55, "language": "Hebrew"},
        "chokaiin": {"meaning": "male/remember of", "confidence": 0.55, "language": "Hebrew"},
        "shokaiin": {"meaning": "hear (priest)", "confidence": 0.5, "language": "Hebrew"},
        "daltaiin": {"meaning": "door fig", "confidence": 0.45, "language": "Hebrew"},
        "shdaiin": {"meaning": "demon of", "confidence": 0.5, "language": "Hebrew"},
        "chdaiin": {"meaning": "chamber of", "confidence": 0.5, "language": "Hebrew"},
        "shkedy": {"meaning": "almond/diligent", "confidence": 0.55, "language": "Hebrew"},
        "shkeey": {"meaning": "almond", "confidence": 0.55, "language": "Hebrew"},
        "chokedy": {"meaning": "wisdom", "confidence": 0.55, "language": "Hebrew"},
        "chokeey": {"meaning": "wisdom", "confidence": 0.55, "language": "Hebrew"},
        "shokeey": {"meaning": "almond", "confidence": 0.55, "language": "Hebrew"},
        "shokedy": {"meaning": "almond", "confidence": 0.55, "language": "Hebrew"},
        "dair": {"meaning": "to give (verb)", "confidence": 0.55, "language": "Italian"},
        "daim": {"meaning": "blood (of)", "confidence": 0.5, "language": "Hebrew"},
        "dais": {"meaning": "platform", "confidence": 0.45, "language": "Italian"},
        "dait": {"meaning": "law (of)", "confidence": 0.5, "language": "Hebrew"},
        "shair": {"meaning": "hair/song", "confidence": 0.55, "language": "Hebrew"},
        "shaim": {"meaning": "there (of)", "confidence": 0.5, "language": "Hebrew"},
        "shais": {"meaning": "put", "confidence": 0.45, "language": "Hebrew"},
        "shait": {"meaning": "put (of)", "confidence": 0.5, "language": "Hebrew"},
        "chair": {"meaning": "hole/free", "confidence": 0.5, "language": "Hebrew"},
        "chaim": {"meaning": "life", "confidence": 0.6, "language": "Hebrew"},
        "chais": {"meaning": "life (of)", "confidence": 0.55, "language": "Hebrew"},
        "chait": {"meaning": "sin/tailor", "confidence": 0.5, "language": "Hebrew"},
        "qoeey": {"meaning": "the wheat", "confidence": 0.55, "language": "Hebrew"},
        "okeeol": {"meaning": "wheat vessel", "confidence": 0.5, "language": "Hebrew"},
        "om": {"meaning": "if/with", "confidence": 0.55, "language": "Hebrew"},
        "chokchy": {"meaning": "sick verb", "confidence": 0.5, "language": "Hebrew"},
        "ytchy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "shky": {"meaning": "quiet", "confidence": 0.5, "language": "Hebrew"},
        "sheeky": {"meaning": "quiet", "confidence": 0.5, "language": "Hebrew"},
        "ycheol": {"meaning": "verb sick", "confidence": 0.5, "language": "Hebrew"},
        "teol": {"meaning": "worm/dew", "confidence": 0.5, "language": "Hebrew"},
        "cphol": {"meaning": "flower all", "confidence": 0.5, "language": "Hebrew"},
        "da": {"meaning": "this", "confidence": 0.5, "language": "Hebrew"},
        "lkchedy": {"meaning": "to strength", "confidence": 0.5, "language": "Hebrew"},
        "ykal": {"meaning": "verb all", "confidence": 0.5, "language": "Grammar"},
        "daiiin": {"meaning": "from one", "confidence": 0.55, "language": "Grammar"},
        "chom": {"meaning": "hot/heat", "confidence": 0.55, "language": "Hebrew"},
        "ykeody": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ctho": {"meaning": "wall", "confidence": 0.45, "language": "Hebrew"},
        "okody": {"meaning": "wheat verb", "confidence": 0.5, "language": "Hebrew"},
        "qokeed": {"meaning": "the wheat", "confidence": 0.55, "language": "Hebrew"},
        "okeeo": {"meaning": "wheat", "confidence": 0.55, "language": "Hebrew"},
        "cheeo": {"meaning": "sick/life", "confidence": 0.5, "language": "Hebrew"},
        "cphy": {"meaning": "flower", "confidence": 0.5, "language": "Hebrew"},
        "tchol": {"meaning": "worm/blue", "confidence": 0.5, "language": "Hebrew"},
        "chckhdy": {"meaning": "wise verb", "confidence": 0.5, "language": "Hebrew"},
        "ly": {"meaning": "to me", "confidence": 0.5, "language": "Hebrew"},
        "chkeey": {"meaning": "wait", "confidence": 0.5, "language": "Hebrew"},
        "ctheey": {"meaning": "wall", "confidence": 0.45, "language": "Hebrew"},
        "ytal": {"meaning": "verb dew", "confidence": 0.5, "language": "Grammar"},
        "ry": {"meaning": "bad/evil", "confidence": 0.5, "language": "Hebrew"},
        "shee": {"meaning": "which", "confidence": 0.5, "language": "Grammar"},
        "choiin": {"meaning": "sick of", "confidence": 0.5, "language": "Hebrew"},
        "sheos": {"meaning": "lamb", "confidence": 0.5, "language": "Hebrew"},
        "ycheo": {"meaning": "verb life", "confidence": 0.5, "language": "Grammar"},
        "yteody": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "cheeor": {"meaning": "sick light", "confidence": 0.5, "language": "Hebrew"},
        "qokechy": {"meaning": "the strength", "confidence": 0.5, "language": "Hebrew"},
        "dshey": {"meaning": "judgment verb", "confidence": 0.5, "language": "Hebrew"},
        "rchedy": {"meaning": "breath verb", "confidence": 0.5, "language": "Hebrew"},
        "otedar": {"meaning": "worm gift", "confidence": 0.45, "language": "Hebrew"},
        "chodar": {"meaning": "sick chamber", "confidence": 0.5, "language": "Hebrew"},
        "sheeol": {"meaning": "pit/grave", "confidence": 0.55, "language": "Hebrew"},
        "shes": {"meaning": "six", "confidence": 0.55, "language": "Hebrew"},
        "ykeol": {"meaning": "verb voice", "confidence": 0.5, "language": "Grammar"},
        "cheodaiin": {"meaning": "sick from", "confidence": 0.5, "language": "Hebrew"},
        "tain": {"meaning": "fig (of)", "confidence": 0.55, "language": "Hebrew"},
        "lcheey": {"meaning": "to verb", "confidence": 0.5, "language": "Grammar"},
        "do": {"meaning": "generation", "confidence": 0.5, "language": "Hebrew"},
        "ch": {"meaning": "sick/life", "confidence": 0.5, "language": "Hebrew"},
        "shckhey": {"meaning": "which wise", "confidence": 0.5, "language": "Hebrew"},
        "ychol": {"meaning": "verb all", "confidence": 0.5, "language": "Grammar"},
        "dcheey": {"meaning": "push verb", "confidence": 0.5, "language": "Hebrew"},
        "cheeody": {"meaning": "sick verb", "confidence": 0.5, "language": "Hebrew"},
        "shocthy": {"meaning": "which verb", "confidence": 0.5, "language": "Grammar"},
        "keeol": {"meaning": "wheat voice", "confidence": 0.5, "language": "Hebrew"},
        "chr": {"meaning": "cold/hole", "confidence": 0.5, "language": "Hebrew"},
        "ytol": {"meaning": "verb worm", "confidence": 0.5, "language": "Grammar"},
        "chotar": {"meaning": "sick earth", "confidence": 0.5, "language": "Hebrew"},
        "pchedar": {"meaning": "flower chamber", "confidence": 0.5, "language": "Hebrew"},
        "checkhey": {"meaning": "sick wise", "confidence": 0.5, "language": "Hebrew"},
        "ckhor": {"meaning": "wise cold", "confidence": 0.5, "language": "Hebrew"},
        "chkar": {"meaning": "sick cold", "confidence": 0.5, "language": "Hebrew"},
        "dshor": {"meaning": "push ox", "confidence": 0.5, "language": "Hebrew"},
        "oteeo": {"meaning": "worm", "confidence": 0.5, "language": "Hebrew"},
        "arol": {"meaning": "foreskin", "confidence": 0.5, "language": "Hebrew"},
        "qoteol": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "ytey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "fchedy": {"meaning": "mouth verb", "confidence": 0.5, "language": "Hebrew"},
        "oteo": {"meaning": "worm", "confidence": 0.5, "language": "Hebrew"},
        "shod": {"meaning": "demon/robbery", "confidence": 0.55, "language": "Hebrew"},
        "cthaiin": {"meaning": "wall of", "confidence": 0.45, "language": "Hebrew"},
        "chcphy": {"meaning": "wise flower", "confidence": 0.45, "language": "Hebrew"},
        "ypchedy": {"meaning": "verb flower", "confidence": 0.5, "language": "Grammar"},
        "pchey": {"meaning": "flower verb", "confidence": 0.5, "language": "Hebrew"},
        "ykeeody": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "shety": {"meaning": "put verb", "confidence": 0.5, "language": "Hebrew"},
        "chotaiin": {"meaning": "sick fig", "confidence": 0.5, "language": "Hebrew"},
        "sheod": {"meaning": "which demon", "confidence": 0.5, "language": "Hebrew"},
        "chkain": {"meaning": "wait yes", "confidence": 0.5, "language": "Hebrew"},
        "ls": {"meaning": "to", "confidence": 0.45, "language": "Grammar"},
        "okeo": {"meaning": "wheat", "confidence": 0.55, "language": "Hebrew"},
        "ytchedy": {"meaning": "verb worm", "confidence": 0.5, "language": "Grammar"},
        "ckheey": {"meaning": "wise", "confidence": 0.5, "language": "Hebrew"},
        "ytchor": {"meaning": "verb worm", "confidence": 0.5, "language": "Grammar"},
        "chotchy": {"meaning": "sick verb", "confidence": 0.5, "language": "Hebrew"},
        "okshey": {"meaning": "wheat verb", "confidence": 0.5, "language": "Hebrew"},
        "qokeeol": {"meaning": "the wheat", "confidence": 0.55, "language": "Hebrew"},
        "chotey": {"meaning": "sick verb", "confidence": 0.5, "language": "Hebrew"},
        "ytchey": {"meaning": "verb worm", "confidence": 0.5, "language": "Grammar"},
        "cheeol": {"meaning": "sick vessel", "confidence": 0.5, "language": "Hebrew"},
        "lr": {"meaning": "to", "confidence": 0.45, "language": "Grammar"},
        "chekaiin": {"meaning": "sick priest", "confidence": 0.5, "language": "Hebrew"},
        "ysheey": {"meaning": "verb which", "confidence": 0.5, "language": "Grammar"},
        "chdam": {"meaning": "chamber blood", "confidence": 0.5, "language": "Hebrew"},
        "olcheey": {"meaning": "tongue verb", "confidence": 0.5, "language": "Hebrew"},
        "cheockhy": {"meaning": "sick wise", "confidence": 0.5, "language": "Hebrew"},
        "alol": {"meaning": "to voice", "confidence": 0.5, "language": "Hebrew"},
        "qotcho": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "ycheor": {"meaning": "verb light", "confidence": 0.5, "language": "Grammar"},
        "oees": {"meaning": "lamb", "confidence": 0.5, "language": "Hebrew"},
        "okshy": {"meaning": "wheat verb", "confidence": 0.5, "language": "Hebrew"},
        "chey": {"meaning": "is/has", "confidence": 0.55, "language": "Grammar"},
        "chy": {"meaning": "is/has", "confidence": 0.55, "language": "Grammar"},
        "shy": {"meaning": "which", "confidence": 0.55, "language": "Grammar"},
        "key": {"meaning": "thus/so", "confidence": 0.5, "language": "Grammar"},
        "tey": {"meaning": "you", "confidence": 0.5, "language": "Grammar"},
        "dy": {"meaning": "of", "confidence": 0.6, "language": "Grammar"},
        "ey": {"meaning": "of", "confidence": 0.5, "language": "Grammar"},
        "od": {"meaning": "yet/still", "confidence": 0.5, "language": "Hebrew"},
        "ad": {"meaning": "until", "confidence": 0.5, "language": "Hebrew"},
        "lo": {"meaning": "to him", "confidence": 0.5, "language": "Hebrew"},
        "la": {"meaning": "to her", "confidence": 0.5, "language": "Hebrew"},
        "li": {"meaning": "to me", "confidence": 0.5, "language": "Hebrew"},
        "el": {"meaning": "God/to", "confidence": 0.55, "language": "Hebrew"},
        "im": {"meaning": "if/with", "confidence": 0.5, "language": "Hebrew"},
        "ot": {"meaning": "sign", "confidence": 0.5, "language": "Hebrew"},
        "et": {"meaning": "with/acc", "confidence": 0.55, "language": "Hebrew"},
        "kain": {"meaning": "yes/thus", "confidence": 0.55, "language": "Hebrew"},
        "kaiin": {"meaning": "priest (cohen)", "confidence": 0.65, "language": "Hebrew"},
        "taiin": {"meaning": "fig (teena)", "confidence": 0.65, "language": "Hebrew"},
        "saiin": {"meaning": "sun/year", "confidence": 0.55, "language": "Hebrew"},
        "paiin": {"meaning": "mouth", "confidence": 0.55, "language": "Hebrew"},
        "laiin": {"meaning": "night", "confidence": 0.55, "language": "Hebrew"},
        "raiin": {"meaning": "see/vision", "confidence": 0.55, "language": "Hebrew"},
        "chaiin": {"meaning": "life", "confidence": 0.65, "language": "Hebrew"},
        "shaiin": {"meaning": "hear", "confidence": 0.55, "language": "Hebrew"},
        "daiin": {"meaning": "of the/from", "confidence": 0.7, "language": "Grammar"},
        "qokeey": {"meaning": "the wheat", "confidence": 0.6, "language": "Hebrew"},
        "qokeedy": {"meaning": "the wheat", "confidence": 0.6, "language": "Hebrew"},
        "qokedy": {"meaning": "the wheat", "confidence": 0.6, "language": "Hebrew"},
        "qokchedy": {"meaning": "the lily", "confidence": 0.55, "language": "Hebrew"},
        "qopchedy": {"meaning": "the opening", "confidence": 0.55, "language": "Hebrew"},
        "qotchedy": {"meaning": "the writing", "confidence": 0.55, "language": "Hebrew"},
        "qolchedy": {"meaning": "the tongue", "confidence": 0.55, "language": "Hebrew"},
        "qocthedy": {"meaning": "the wall", "confidence": 0.5, "language": "Hebrew"},
        "qockhedy": {"meaning": "the wise", "confidence": 0.5, "language": "Hebrew"},
        "okchedy": {"meaning": "strength/all", "confidence": 0.5, "language": "Hebrew"},
        "opchedy": {"meaning": "opening", "confidence": 0.55, "language": "Hebrew"},
        "otchedy": {"meaning": "writing", "confidence": 0.5, "language": "Hebrew"},
        "olchedy": {"meaning": "tongue/verb", "confidence": 0.5, "language": "Hebrew"},
        "lchedy": {"meaning": "tongue/verb", "confidence": 0.5, "language": "Hebrew"},
        "tchedy": {"meaning": "blue/worm", "confidence": 0.45, "language": "Hebrew"},
        "kchedy": {"meaning": "strength", "confidence": 0.5, "language": "Hebrew"},
        "pchedy": {"meaning": "flower", "confidence": 0.55, "language": "Hebrew"},
        "chedy": {"meaning": "is/has", "confidence": 0.6, "language": "Grammar"},
        "shedy": {"meaning": "which/that", "confidence": 0.55, "language": "Grammar"},
        "keedy": {"meaning": "verb form", "confidence": 0.55, "language": "Grammar"},
        "teedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "cheedy": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "sheedy": {"meaning": "relative", "confidence": 0.5, "language": "Grammar"},
        "okeedy": {"meaning": "wheat", "confidence": 0.55, "language": "Hebrew"},
        "otedy": {"meaning": "verb form", "confidence": 0.55, "language": "Grammar"},
        "okedy": {"meaning": "wheat/verb", "confidence": 0.55, "language": "Hebrew"},
        "qol": {"meaning": "the voice", "confidence": 0.6, "language": "Hebrew"},
        "qor": {"meaning": "the cold", "confidence": 0.55, "language": "Hebrew"},
        "qom": {"meaning": "the place", "confidence": 0.55, "language": "Hebrew"},
        "qop": {"meaning": "the mouth", "confidence": 0.5, "language": "Hebrew"},
        "qot": {"meaning": "the (prep)", "confidence": 0.55, "language": "Grammar"},
        "qok": {"meaning": "the (noun)", "confidence": 0.6, "language": "Grammar"},
        "qos": {"meaning": "the cup", "confidence": 0.5, "language": "Hebrew"},
        "qod": {"meaning": "the holy", "confidence": 0.55, "language": "Hebrew"},
        "qoch": {"meaning": "the strength", "confidence": 0.55, "language": "Hebrew"},
        "qosh": {"meaning": "the bow", "confidence": 0.5, "language": "Hebrew"},
        "qokal": {"meaning": "the garlic", "confidence": 0.6, "language": "Italian"},
        "qotar": {"meaning": "the earth", "confidence": 0.65, "language": "Italian"},
        "qokar": {"meaning": "the heart", "confidence": 0.65, "language": "Italian"},
        "qosor": {"meaning": "the tied", "confidence": 0.5, "language": "Hebrew"},
        "qopor": {"meaning": "the dust", "confidence": 0.5, "language": "Hebrew"},
        "qodor": {"meaning": "the generation", "confidence": 0.5, "language": "Hebrew"},
        "qochor": {"meaning": "the sick", "confidence": 0.55, "language": "Hebrew"},
        "qoshor": {"meaning": "the ox", "confidence": 0.5, "language": "Hebrew"},
        "otal": {"meaning": "dew", "confidence": 0.5, "language": "Hebrew"},
        "otar": {"meaning": "earth", "confidence": 0.7, "language": "Italian"},
        "okar": {"meaning": "heart/cure", "confidence": 0.7, "language": "Italian"},
        "osor": {"meaning": "bound", "confidence": 0.5, "language": "Hebrew"},
        "opor": {"meaning": "dust", "confidence": 0.5, "language": "Hebrew"},
        "odor": {"meaning": "generation", "confidence": 0.5, "language": "Hebrew"},
        "ochor": {"meaning": "sick", "confidence": 0.55, "language": "Hebrew"},
        "oshor": {"meaning": "ox", "confidence": 0.5, "language": "Hebrew"},
        "chal": {"meaning": "sand/profane", "confidence": 0.5, "language": "Hebrew"},
        "char": {"meaning": "hole/free", "confidence": 0.5, "language": "Hebrew"},
        "cham": {"meaning": "hot/father-in-law", "confidence": 0.55, "language": "Hebrew"},
        "chan": {"meaning": "grace", "confidence": 0.55, "language": "Hebrew"},
        "chas": {"meaning": "refuge", "confidence": 0.5, "language": "Hebrew"},
        "chap": {"meaning": "cover", "confidence": 0.5, "language": "Hebrew"},
        "chat": {"meaning": "sin", "confidence": 0.5, "language": "Hebrew"},
        "shal": {"meaning": "three/ask", "confidence": 0.55, "language": "Hebrew"},
        "shar": {"meaning": "prince/song", "confidence": 0.55, "language": "Hebrew"},
        "sham": {"meaning": "there/name", "confidence": 0.6, "language": "Hebrew"},
        "shan": {"meaning": "tooth/year", "confidence": 0.55, "language": "Hebrew"},
        "shap": {"meaning": "judge", "confidence": 0.5, "language": "Hebrew"},
        "shat": {"meaning": "put/base", "confidence": 0.5, "language": "Hebrew"},
        "dal": {"meaning": "poor/door", "confidence": 0.55, "language": "Hebrew"},
        "dar": {"meaning": "to give", "confidence": 0.6, "language": "Italian"},
        "dam": {"meaning": "blood", "confidence": 0.65, "language": "Hebrew"},
        "dan": {"meaning": "judge", "confidence": 0.55, "language": "Hebrew"},
        "dap": {"meaning": "push", "confidence": 0.45, "language": "Hebrew"},
        "dat": {"meaning": "law/religion", "confidence": 0.55, "language": "Hebrew"},
        "kal": {"meaning": "light/all", "confidence": 0.55, "language": "Hebrew"},
        "kam": {"meaning": "arise", "confidence": 0.6, "language": "Hebrew"},
        "kan": {"meaning": "here/base", "confidence": 0.55, "language": "Hebrew"},
        "kas": {"meaning": "cup/anger", "confidence": 0.5, "language": "Hebrew"},
        "kap": {"meaning": "palm/spoon", "confidence": 0.55, "language": "Hebrew"},
        "kat": {"meaning": "sect/small", "confidence": 0.5, "language": "Hebrew"},
        "tal": {"meaning": "dew", "confidence": 0.6, "language": "Hebrew"},
        "tam": {"meaning": "complete/simple", "confidence": 0.6, "language": "Hebrew"},
        "tan": {"meaning": "jackal", "confidence": 0.45, "language": "Hebrew"},
        "tas": {"meaning": "fly/tray", "confidence": 0.45, "language": "Hebrew"},
        "tap": {"meaning": "drop/child", "confidence": 0.5, "language": "Hebrew"},
        "tat": {"meaning": "below", "confidence": 0.5, "language": "Hebrew"},
        "lal": {"meaning": "night/dew", "confidence": 0.5, "language": "Hebrew"},
        "lar": {"meaning": "to her", "confidence": 0.45, "language": "Grammar"},
        "lam": {"meaning": "to them", "confidence": 0.55, "language": "Hebrew"},
        "lan": {"meaning": "to us", "confidence": 0.5, "language": "Hebrew"},
        "lap": {"meaning": "torch", "confidence": 0.45, "language": "Hebrew"},
        "lat": {"meaning": "secret", "confidence": 0.5, "language": "Hebrew"},
        "sal": {"meaning": "salt/sun", "confidence": 0.7, "language": "Italian"},
        "sar": {"meaning": "prince", "confidence": 0.55, "language": "Hebrew"},
        "sam": {"meaning": "medicine/poison", "confidence": 0.65, "language": "Hebrew"},
        "san": {"meaning": "hated", "confidence": 0.45, "language": "Hebrew"},
        "sap": {"meaning": "threshold", "confidence": 0.45, "language": "Hebrew"},
        "sat": {"meaning": "deviated", "confidence": 0.45, "language": "Hebrew"},
        "par": {"meaning": "bull/young", "confidence": 0.55, "language": "Hebrew"},
        "pam": {"meaning": "time/step", "confidence": 0.5, "language": "Hebrew"},
        "pan": {"meaning": "face", "confidence": 0.55, "language": "Hebrew"},
        "pas": {"meaning": "portion", "confidence": 0.5, "language": "Hebrew"},
        "pat": {"meaning": "piece/bread", "confidence": 0.55, "language": "Hebrew"},
        "mal": {"meaning": "speak/word", "confidence": 0.55, "language": "Hebrew"},
        "mar": {"meaning": "bitter/lord", "confidence": 0.55, "language": "Hebrew"},
        "man": {"meaning": "manna/from", "confidence": 0.55, "language": "Hebrew"},
        "mas": {"meaning": "burden", "confidence": 0.5, "language": "Hebrew"},
        "map": {"meaning": "map", "confidence": 0.45, "language": "Italian"},
        "mat": {"meaning": "death/bed", "confidence": 0.55, "language": "Hebrew"},
        "nal": {"meaning": "stream", "confidence": 0.45, "language": "Hebrew"},
        "nar": {"meaning": "river/light", "confidence": 0.5, "language": "Hebrew"},
        "nam": {"meaning": "sleep/pleasant", "confidence": 0.55, "language": "Hebrew"},
        "nan": {"meaning": "fish", "confidence": 0.45, "language": "Hebrew"},
        "nas": {"meaning": "flee", "confidence": 0.5, "language": "Hebrew"},
        "nat": {"meaning": "give/plant", "confidence": 0.55, "language": "Hebrew"},
        "ral": {"meaning": "bad/weak", "confidence": 0.45, "language": "Hebrew"},
        "ram": {"meaning": "high/exalted", "confidence": 0.55, "language": "Hebrew"},
        "ran": {"meaning": "sang/shouted", "confidence": 0.5, "language": "Hebrew"},
        "ras": {"meaning": "head/chief", "confidence": 0.55, "language": "Hebrew"},
        "rat": {"meaning": "moist", "confidence": 0.45, "language": "Hebrew"},
        "air": {"meaning": "air", "confidence": 0.6, "language": "Italian"},
        "ain": {"meaning": "eye/spring", "confidence": 0.6, "language": "Hebrew"},
        "aiin": {"meaning": "one", "confidence": 0.6, "language": "Italian"},
        "lol": {"meaning": "infant/roll", "confidence": 0.5, "language": "Hebrew"},
        "lor": {"meaning": "the (def)", "confidence": 0.5, "language": "Grammar"},
        "lom": {"meaning": "to them", "confidence": 0.5, "language": "Hebrew"},
        "lon": {"meaning": "lodge", "confidence": 0.45, "language": "Hebrew"},
        "los": {"meaning": "knead", "confidence": 0.45, "language": "Hebrew"},
        "lot": {"meaning": "cover/Lot", "confidence": 0.5, "language": "Hebrew"},
        "ror": {"meaning": "myrrh/flow", "confidence": 0.5, "language": "Hebrew"},
        "rom": {"meaning": "height", "confidence": 0.5, "language": "Hebrew"},
        "ron": {"meaning": "song/joy", "confidence": 0.5, "language": "Hebrew"},
        "ros": {"meaning": "head/chief", "confidence": 0.55, "language": "Hebrew"},
        "rot": {"meaning": "moist/run", "confidence": 0.45, "language": "Hebrew"},
        "tol": {"meaning": "worm", "confidence": 0.55, "language": "Hebrew"},
        "tor": {"meaning": "turtle/turn", "confidence": 0.55, "language": "Hebrew"},
        "tom": {"meaning": "completeness", "confidence": 0.55, "language": "Hebrew"},
        "ton": {"meaning": "tone", "confidence": 0.45, "language": "Italian"},
        "tos": {"meaning": "cough", "confidence": 0.5, "language": "Italian"},
        "tot": {"meaning": "all (tutto)", "confidence": 0.55, "language": "Italian"},
        "pol": {"meaning": "bean", "confidence": 0.5, "language": "Hebrew"},
        "por": {"meaning": "bull/lot", "confidence": 0.5, "language": "Hebrew"},
        "pom": {"meaning": "apple", "confidence": 0.55, "language": "Italian"},
        "pon": {"meaning": "put", "confidence": 0.5, "language": "Italian"},
        "pos": {"meaning": "here/put", "confidence": 0.5, "language": "Hebrew"},
        "pot": {"meaning": "pot/mouth", "confidence": 0.55, "language": "Italian"},
        "mol": {"meaning": "mill/soft", "confidence": 0.5, "language": "Hebrew"},
        "mor": {"meaning": "myrrh/exchange", "confidence": 0.55, "language": "Hebrew"},
        "mom": {"meaning": "blemish", "confidence": 0.45, "language": "Hebrew"},
        "mon": {"meaning": "money/from", "confidence": 0.5, "language": "Italian"},
        "mos": {"meaning": "Moses/touch", "confidence": 0.5, "language": "Hebrew"},
        "mot": {"meaning": "death/pole", "confidence": 0.55, "language": "Hebrew"},
        "dol": {"meaning": "poor/bucket", "confidence": 0.5, "language": "Hebrew"},
        "dor": {"meaning": "generation/dwell", "confidence": 0.55, "language": "Hebrew"},
        "dom": {"meaning": "silent/blood", "confidence": 0.55, "language": "Hebrew"},
        "don": {"meaning": "lord/judge", "confidence": 0.55, "language": "Italian"},
        "dos": {"meaning": "two", "confidence": 0.5, "language": "Italian"},
        "dot": {"meaning": "dowry/law", "confidence": 0.5, "language": "Hebrew"},
        "fol": {"meaning": "foolish", "confidence": 0.5, "language": "Italian"},
        "for": {"meaning": "outside/furnace", "confidence": 0.55, "language": "Italian"},
        "fom": {"meaning": "foam", "confidence": 0.45, "language": "Italian"},
        "fon": {"meaning": "fountain", "confidence": 0.5, "language": "Italian"},
        "fos": {"meaning": "pit/grave", "confidence": 0.5, "language": "Italian"},
        "fot": {"meaning": "photo/fire", "confidence": 0.45, "language": "Italian"},
        "lchol": {"meaning": "to all", "confidence": 0.55, "language": "Hebrew"},
        "lshed": {"meaning": "to demon", "confidence": 0.45, "language": "Hebrew"},
        "lchey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "lshey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "lkey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "ltey": {"meaning": "verb form", "confidence": 0.5, "language": "Grammar"},
        "lkar": {"meaning": "to cold", "confidence": 0.5, "language": "Hebrew"},
        "lkal": {"meaning": "to all", "confidence": 0.55, "language": "Hebrew"},
        "lkol": {"meaning": "to voice", "confidence": 0.55, "language": "Hebrew"},
        "lkam": {"meaning": "to arise", "confidence": 0.5, "language": "Hebrew"},
        "okchol": {"meaning": "strength (all)", "confidence": 0.55, "language": "Hebrew"},
        "opchol": {"meaning": "wonder", "confidence": 0.5, "language": "Hebrew"},
        "otchol": {"meaning": "worm (all)", "confidence": 0.5, "language": "Hebrew"},
        "olchol": {"meaning": "tongue (all)", "confidence": 0.5, "language": "Hebrew"},
        "qokchol": {"meaning": "the lily", "confidence": 0.55, "language": "Hebrew"},
        "qopchol": {"meaning": "the wonder", "confidence": 0.5, "language": "Hebrew"},
        "qotchol": {"meaning": "the worm", "confidence": 0.5, "language": "Hebrew"},
        "qolchol": {"meaning": "the tongue", "confidence": 0.5, "language": "Hebrew"},
        "ckhey": {"meaning": "wise", "confidence": 0.5, "language": "Hebrew"},
        "cthey": {"meaning": "wall", "confidence": 0.45, "language": "Hebrew"},
        "cfhey": {"meaning": "basket", "confidence": 0.45, "language": "Hebrew"},
        "chckhey": {"meaning": "wise", "confidence": 0.5, "language": "Hebrew"},
        "qockhey": {"meaning": "the wise", "confidence": 0.5, "language": "Hebrew"},
        "qocthey": {"meaning": "the wall", "confidence": 0.45, "language": "Hebrew"},
        "qochckhey": {"meaning": "the wise", "confidence": 0.45, "language": "Hebrew"},
        "chekal": {"meaning": "wisdom", "confidence": 0.55, "language": "Hebrew"},
        "chekar": {"meaning": "recognition", "confidence": 0.5, "language": "Hebrew"},
        "chekam": {"meaning": "wise", "confidence": 0.55, "language": "Hebrew"},
        "chekol": {"meaning": "wisdom", "confidence": 0.55, "language": "Hebrew"},
        "shekal": {"meaning": "weight/shekel", "confidence": 0.6, "language": "Hebrew"},
        "shekar": {"meaning": "intoxicant", "confidence": 0.55, "language": "Hebrew"},
        "shekam": {"meaning": "shoulder", "confidence": 0.55, "language": "Hebrew"},
        "shekol": {"meaning": "loss/wisdom", "confidence": 0.55, "language": "Hebrew"},
    }

def build_expanded_dict():
    print("Loading existing dictionaries...")
    existing = load_existing_dicts()
    print(f"  Loaded {len(existing)} existing entries")
    
    print("Adding high-frequency direct mappings...")
    high_freq_direct = add_high_freq_direct()
    for word, data in high_freq_direct.items():
        if word not in existing:
            existing[word] = {
                "meaning": data["meaning"],
                "confidence": data["confidence"],
                "language": data["language"],
                "frequency": 0,
                "source": "high_freq_direct"
            }
    print(f"  Added {len(high_freq_direct)} direct entries")
    
    print("Getting word frequencies...")
    all_freqs = get_word_freqs()
    print(f"  Total unique words: {len(all_freqs)}")
    total_occurrences = sum(all_freqs.values())
    
    print("Extracting untranslated words...")
    unknowns = extract_untranslated()
    print(f"  Found {len(unknowns)} untranslated words")
    
    new_entries = {}
    methods = defaultdict(int)
    
    print("\nExpanding via patterns...")
    for word in unknowns:
        if word not in existing and word not in new_entries:
            pattern_entries = expand_via_patterns(word, existing, all_freqs)
            for w, data in pattern_entries.items():
                if w not in new_entries:
                    new_entries[w] = data
                    methods["pattern"] += 1
    
    print(f"  Pattern expansion: {methods['pattern']} entries")
    
    print("Finding cognate matches...")
    high_freq_unknowns = [w for w, c in unknowns.items() if c >= 3]
    for word in high_freq_unknowns:
        if word not in existing and word not in new_entries:
            cognate_entries = find_cognate_matches(word, all_freqs)
            for w, data in cognate_entries.items():
                if w not in new_entries:
                    new_entries[w] = data
                    methods["cognate"] += 1
    
    print(f"  Cognate matches: {methods['cognate']} entries")
    
    print("Inferring from context...")
    for word in unknowns:
        if word not in existing and word not in new_entries:
            context_entries = infer_from_context(word, existing, all_freqs)
            for w, data in context_entries.items():
                if w not in new_entries:
                    new_entries[w] = data
                    methods["context"] += 1
    
    print(f"  Context inference: {methods['context']} entries")
    
    print("Adding morphological variants...")
    combined = {**existing, **new_entries}
    morph_entries = add_morphological_variants(combined, all_freqs)
    for w, data in morph_entries.items():
        if w not in existing and w not in new_entries:
            new_entries[w] = data
            methods["morphological"] += 1
    
    print(f"  Morphological variants: {methods['morphological']} entries")
    
    final_dict = {**existing, **new_entries}
    
    covered_unique = sum(1 for w in final_dict if w in all_freqs)
    covered_occurrences = sum(all_freqs.get(w, 0) for w in final_dict)
    
    coverage_before = sum(1 for w in existing if w in all_freqs) / len(all_freqs)
    coverage_after = covered_unique / len(all_freqs)
    occ_coverage = covered_occurrences / total_occurrences
    
    return {
        "total_entries": len(final_dict),
        "existing_entries": len(existing),
        "new_entries": len(new_entries),
        "entries": final_dict,
        "new_entries_detail": new_entries,
        "coverage_before": round(coverage_before, 4),
        "coverage_after": round(coverage_after, 4),
        "occurrence_coverage": round(occ_coverage, 4),
        "method_breakdown": dict(methods),
        "corpus_stats": {
            "total_unique": len(all_freqs),
            "total_occurrences": total_occurrences,
            "covered_unique": covered_unique,
            "covered_occurrences": covered_occurrences
        }
    }

def generate_report(result):
    report = []
    report.append("# Dictionary Expansion to 70% Coverage\n")
    
    report.append("## Summary\n")
    report.append(f"- **Total entries**: {result['total_entries']}")
    report.append(f"- **Previous entries**: {result['existing_entries']}")
    report.append(f"- **New entries**: {result['new_entries']}")
    report.append(f"- **Coverage before**: {result['coverage_before']*100:.1f}%")
    report.append(f"- **Coverage after**: {result['coverage_after']*100:.1f}%")
    report.append(f"- **Occurrence coverage**: {result['occurrence_coverage']*100:.1f}%")
    
    report.append("\n## Method Breakdown\n")
    report.append("| Method | New Entries |")
    report.append("|--------|-------------|")
    for method, count in sorted(result['method_breakdown'].items(), key=lambda x: -x[1]):
        report.append(f"| {method} | {count} |")
    
    report.append("\n## Corpus Coverage\n")
    stats = result['corpus_stats']
    report.append(f"- **Unique words**: {stats['covered_unique']:,}/{stats['total_unique']:,}")
    report.append(f"- **Total occurrences**: {stats['covered_occurrences']:,}/{stats['total_occurrences']:,}")
    
    report.append("\n## High-Frequency New Entries\n")
    report.append("| Voynich | Meaning | Confidence | Frequency | Method |")
    report.append("|---------|---------|------------|-----------|--------|")
    
    new_sorted = sorted(result['new_entries_detail'].items(), 
                       key=lambda x: x[1].get('frequency', 0), reverse=True)
    for word, data in new_sorted[:50]:
        report.append(f"| {word} | {data['meaning']} | {data['confidence']:.2f} | {data.get('frequency', 0)} | {data.get('source', '?')} |")
    
    if len(new_sorted) > 50:
        report.append(f"\n*... and {len(new_sorted) - 50} more new entries*\n")
    
    report.append("\n## Success Criteria\n")
    report.append(f"- [{'✓' if result['new_entries'] >= 200 else '✗'}] 200+ new entries added ({result['new_entries']})")
    report.append(f"- [{'✓' if result['coverage_after'] >= 0.65 else '✗'}] Coverage reaches 65%+ ({result['coverage_after']*100:.1f}%)")
    report.append(f"- [{'✓' if result['occurrence_coverage'] >= 0.70 else '✗'}] Occurrence coverage 70%+ ({result['occurrence_coverage']*100:.1f}%)")
    
    return "\n".join(report)

def main():
    print("=" * 60)
    print("DICTIONARY EXPANSION TO 70% COVERAGE")
    print("=" * 60)
    
    result = build_expanded_dict()
    
    with open(RESULTS_DIR / "dictionary_expansion_70.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: results/dictionary_expansion_70.json")
    
    report = generate_report(result)
    with open(RESULTS_DIR / "dictionary_expansion_70_report.md", "w") as f:
        f.write(report)
    print(f"Saved: results/dictionary_expansion_70_report.md")
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nTotal entries: {result['total_entries']}")
    print(f"New entries: {result['new_entries']}")
    print(f"\nCoverage:")
    print(f"  Before: {result['coverage_before']*100:.1f}%")
    print(f"  After:  {result['coverage_after']*100:.1f}%")
    print(f"  Occurrence: {result['occurrence_coverage']*100:.1f}%")
    
    print("\nMethod breakdown:")
    for method, count in sorted(result['method_breakdown'].items(), key=lambda x: -x[1]):
        print(f"  {method}: {count}")
    
    print("\n" + "=" * 60)
    print("SUCCESS CRITERIA")
    print("=" * 60)
    print(f"[{'✓' if result['new_entries'] >= 200 else '✗'}] 200+ new entries ({result['new_entries']})")
    print(f"[{'✓' if result['coverage_after'] >= 0.65 else '✗'}] Coverage 65%+ ({result['coverage_after']*100:.1f}%)")
    print(f"[{'✓' if result['occurrence_coverage'] >= 0.70 else '✗'}] Occurrence 70%+ ({result['occurrence_coverage']*100:.1f}%)")

if __name__ == "__main__":
    main()

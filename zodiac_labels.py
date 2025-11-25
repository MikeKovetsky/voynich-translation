import json
import re
from collections import defaultdict

EVA_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/master_dictionary.json"
OUT_JSON = "results/zodiac_label_analysis.json"

ZODIAC_FOLIOS = {
    "f70v1": {"sign": "Pisces", "hebrew_month": "Adar", "hebrew_sign": "dagim"},
    "f70v2": {"sign": "Aries", "hebrew_month": "Nisan", "hebrew_sign": "taleh"},
    "f71r": {"sign": "Aries", "hebrew_month": "Nisan", "hebrew_sign": "taleh"},
    "f71v": {"sign": "Taurus", "hebrew_month": "Iyyar", "hebrew_sign": "shor"},
    "f72r1": {"sign": "Taurus", "hebrew_month": "Iyyar", "hebrew_sign": "shor"},
    "f72r2": {"sign": "Gemini", "hebrew_month": "Sivan", "hebrew_sign": "teomim"},
    "f72r3": {"sign": "Cancer", "hebrew_month": "Tammuz", "hebrew_sign": "sartan"},
    "f72v1": {"sign": "Aries", "hebrew_month": "Nisan", "hebrew_sign": "taleh"},
    "f72v2": {"sign": "Taurus", "hebrew_month": "Iyyar", "hebrew_sign": "shor"},
    "f72v3": {"sign": "Leo", "hebrew_month": "Av", "hebrew_sign": "aryeh"},
    "f73r": {"sign": "Sagittarius", "hebrew_month": "Kislev", "hebrew_sign": "keshet"},
    "f73v": {"sign": "Sagittarius", "hebrew_month": "Kislev", "hebrew_sign": "keshet"},
    "f69r": {"sign": "zodiac", "hebrew_month": None, "hebrew_sign": None},
    "f69v": {"sign": "zodiac", "hebrew_month": None, "hebrew_sign": None},
    "f70r1": {"sign": "zodiac", "hebrew_month": None, "hebrew_sign": None},
    "f70r2": {"sign": "zodiac", "hebrew_month": None, "hebrew_sign": None},
}

HEBREW_MONTHS = {
    "nisan": {"hebrew": "ניסן", "skeleton": "nsn", "patterns": ["nisn", "nsan", "nson"]},
    "iyyar": {"hebrew": "אייר", "skeleton": "yr", "patterns": ["iyar", "iyr", "aiyr"]},
    "sivan": {"hebrew": "סיון", "skeleton": "svn", "patterns": ["sivn", "svan", "svon"]},
    "tammuz": {"hebrew": "תמוז", "skeleton": "tmz", "patterns": ["tamz", "tumz", "tomz"]},
    "av": {"hebrew": "אב", "skeleton": "v", "patterns": ["av", "ab"]},
    "elul": {"hebrew": "אלול", "skeleton": "ll", "patterns": ["elol", "alol", "elul"]},
    "tishrei": {"hebrew": "תשרי", "skeleton": "tshr", "patterns": ["tishr", "tesr", "tshr"]},
    "cheshvan": {"hebrew": "חשון", "skeleton": "chshvn", "patterns": ["chsvn", "chesv"]},
    "kislev": {"hebrew": "כסלו", "skeleton": "kslv", "patterns": ["kslv", "kisl", "kesl"]},
    "tevet": {"hebrew": "טבת", "skeleton": "tvt", "patterns": ["tevt", "tvt", "tbt"]},
    "shevat": {"hebrew": "שבט", "skeleton": "shvt", "patterns": ["shvt", "shbt", "svt"]},
    "adar": {"hebrew": "אדר", "skeleton": "dr", "patterns": ["adar", "adr", "odar", "dar"]},
}

HEBREW_ZODIAC = {
    "taleh": {"hebrew": "טלה", "skeleton": "tlh", "sign": "Aries", "patterns": ["tal", "tol", "dal", "dol", "tlh", "tchol"]},
    "shor": {"hebrew": "שור", "skeleton": "shr", "sign": "Taurus", "patterns": ["shor", "shur", "sor", "sary", "chsary", "sheeor"]},
    "teomim": {"hebrew": "תאומים", "skeleton": "tmm", "sign": "Gemini", "patterns": ["teom", "taom", "tomm"]},
    "sartan": {"hebrew": "סרטן", "skeleton": "srtn", "sign": "Cancer", "patterns": ["sart", "sartn", "srtan", "cheen", "sheeen"]},
    "aryeh": {"hebrew": "אריה", "skeleton": "ryh", "sign": "Leo", "patterns": ["ary", "arey", "oreeey", "ariey"]},
    "betulah": {"hebrew": "בתולה", "skeleton": "btlh", "sign": "Virgo", "patterns": ["betol", "btul"]},
    "moznayim": {"hebrew": "מאזניים", "skeleton": "mznym", "sign": "Libra", "patterns": ["mozn", "mzn", "octhy"]},
    "akrav": {"hebrew": "עקרב", "skeleton": "qrv", "sign": "Scorpio", "patterns": ["okery", "akr", "qrv", "okrb"]},
    "keshet": {"hebrew": "קשת", "skeleton": "qsht", "sign": "Sagittarius", "patterns": ["kesht", "qsht", "ksht"]},
    "gdi": {"hebrew": "גדי", "skeleton": "gd", "sign": "Capricorn", "patterns": ["gdi", "gdy", "gedy"]},
    "dli": {"hebrew": "דלי", "skeleton": "dl", "sign": "Aquarius", "patterns": ["dli", "daly", "doly", "dlo"]},
    "dagim": {"hebrew": "דגים", "skeleton": "dgm", "sign": "Pisces", "patterns": ["dagm", "dgm", "doiim"]},
}

LATIN_MONTHS = {
    "march": {"latin": "Martius", "italian": "Marzo", "skeleton": "mrt", "patterns": ["mart", "marz", "mars"]},
    "april": {"latin": "Aprilis", "italian": "Aprile", "skeleton": "prl", "patterns": ["aprl", "opral", "opril"]},
    "may": {"latin": "Maius", "italian": "Maggio", "skeleton": "ms", "patterns": ["mai", "mag", "may"]},
    "june": {"latin": "Junius", "italian": "Giugno", "skeleton": "jn", "patterns": ["jun", "giun", "gn"]},
    "july": {"latin": "Julius", "italian": "Luglio", "skeleton": "jl", "patterns": ["jul", "lug", "lugl"]},
    "august": {"latin": "Augustus", "italian": "Agosto", "skeleton": "gst", "patterns": ["aug", "agst", "ogst"]},
    "september": {"latin": "September", "italian": "Settembre", "skeleton": "sptmbr", "patterns": ["sept", "setem"]},
    "october": {"latin": "October", "italian": "Ottobre", "skeleton": "ctbr", "patterns": ["octo", "otob", "octhy"]},
    "november": {"latin": "November", "italian": "Novembre", "skeleton": "nvmbr", "patterns": ["novem", "novm"]},
    "december": {"latin": "December", "italian": "Dicembre", "skeleton": "dcmbr", "patterns": ["decem", "dicm"]},
    "january": {"latin": "Januarius", "italian": "Gennaio", "skeleton": "jn", "patterns": ["jan", "gen", "genn"]},
    "february": {"latin": "Februarius", "italian": "Febbraio", "skeleton": "fbr", "patterns": ["febr", "feb"]},
}


def load_eva():
    lines = []
    with open(EVA_FILE, "r") as f:
        for line in f:
            if line.startswith("#") or line.startswith("##"):
                continue
            if line.strip():
                lines.append(line.strip())
    return lines


def extract_folio_text(eva_lines, folio_id):
    words = []
    labels = []
    in_folio = False
    current_type = None
    
    folio_pattern = re.compile(rf"^<{folio_id}[.>\s]")
    
    for line in eva_lines:
        if line.startswith("<" + folio_id + ">") or line.startswith("<" + folio_id + "."):
            in_folio = True
        elif in_folio and line.startswith("<f") and not line.startswith("<" + folio_id):
            break
        
        if not in_folio:
            continue
        
        if "@L" in line or "@Ri" in line or "@Ro" in line:
            current_type = "label"
        elif "@P" in line or "@C" in line:
            current_type = "text"
        
        match = re.match(r"<[^>]+>\s+(.+)", line)
        if match:
            text = match.group(1)
            text = re.sub(r"<[^>]*>", "", text)
            text = re.sub(r"\{[^}]*\}", "", text)
            text = re.sub(r"[!?,<>=%\-\+\[\]]", "", text)
            
            for word in text.split("."):
                word = word.strip()
                if word and len(word) > 0 and not word.isdigit():
                    words.append(word)
                    if current_type == "label":
                        labels.append(word)
    
    return words, labels


def consonant_skeleton(word):
    vowels = set("aeiouy")
    return "".join(c for c in word.lower() if c not in vowels)


def match_score(word, pattern):
    word = word.lower()
    pattern = pattern.lower()
    
    if pattern in word or word in pattern:
        return 1.0
    
    skel_word = consonant_skeleton(word)
    skel_pat = consonant_skeleton(pattern)
    
    if skel_pat in skel_word or skel_word in skel_pat:
        return 0.8
    
    common = sum(1 for c in set(skel_word) if c in skel_pat)
    total = max(len(set(skel_word)), len(set(skel_pat)), 1)
    
    return common / total * 0.6


def find_month_matches(words, month_dict):
    matches = []
    for word in words:
        for month, data in month_dict.items():
            best_score = 0
            for pat in data["patterns"]:
                score = match_score(word, pat)
                best_score = max(best_score, score)
            
            skel_score = match_score(consonant_skeleton(word), data["skeleton"])
            best_score = max(best_score, skel_score)
            
            if best_score >= 0.4:
                matches.append({
                    "voynich": word,
                    "match": month,
                    "score": round(best_score, 2),
                    "type": "month"
                })
    return matches


def find_zodiac_matches(words, zodiac_dict):
    matches = []
    for word in words:
        for sign, data in zodiac_dict.items():
            best_score = 0
            for pat in data["patterns"]:
                score = match_score(word, pat)
                best_score = max(best_score, score)
            
            skel_score = match_score(consonant_skeleton(word), data["skeleton"])
            best_score = max(best_score, skel_score)
            
            if best_score >= 0.4:
                matches.append({
                    "voynich": word,
                    "match": sign,
                    "zodiac_sign": data["sign"],
                    "score": round(best_score, 2),
                    "type": "zodiac"
                })
    return matches


def main():
    print("Loading EVA transcription...")
    eva_lines = load_eva()
    
    print("Loading master dictionary...")
    with open(DICT_FILE, "r") as f:
        master_dict = json.load(f)
    
    results = {
        "folios_analyzed": 0,
        "total_words_extracted": 0,
        "total_labels_extracted": 0,
        "folio_data": {},
        "hebrew_month_matches": [],
        "latin_month_matches": [],
        "hebrew_zodiac_matches": [],
        "new_vocabulary": [],
        "calendar_patterns": [],
        "month_frequency": defaultdict(int),
        "zodiac_frequency": defaultdict(int),
    }
    
    all_words = []
    all_labels = []
    
    for folio_id, meta in ZODIAC_FOLIOS.items():
        print(f"Extracting {folio_id}...")
        words, labels = extract_folio_text(eva_lines, folio_id)
        
        results["folio_data"][folio_id] = {
            "zodiac_sign": meta["sign"],
            "hebrew_month": meta["hebrew_month"],
            "hebrew_sign": meta.get("hebrew_sign"),
            "word_count": len(words),
            "label_count": len(labels),
            "unique_words": len(set(words)),
            "labels": labels[:30],
        }
        
        all_words.extend(words)
        all_labels.extend(labels)
        results["folios_analyzed"] += 1
    
    results["total_words_extracted"] = len(all_words)
    results["total_labels_extracted"] = len(all_labels)
    
    print("\nSearching for Hebrew month matches...")
    heb_month_matches = find_month_matches(all_labels, HEBREW_MONTHS)
    results["hebrew_month_matches"] = sorted(heb_month_matches, key=lambda x: -x["score"])[:50]
    
    print("Searching for Latin month matches...")
    lat_month_matches = find_month_matches(all_labels, LATIN_MONTHS)
    results["latin_month_matches"] = sorted(lat_month_matches, key=lambda x: -x["score"])[:50]
    
    print("Searching for Hebrew zodiac sign matches...")
    zodiac_matches = find_zodiac_matches(all_labels, HEBREW_ZODIAC)
    results["hebrew_zodiac_matches"] = sorted(zodiac_matches, key=lambda x: -x["score"])[:50]
    
    for m in results["hebrew_month_matches"]:
        if m["score"] >= 0.5:
            results["month_frequency"][m["match"]] += 1
    
    for m in results["hebrew_zodiac_matches"]:
        if m["score"] >= 0.5:
            results["zodiac_frequency"][m["match"]] += 1
    
    existing_words = set(master_dict.get("entries", {}).keys())
    new_vocab = []
    
    for word in set(all_labels):
        if word not in existing_words and len(word) >= 3:
            heb_m = [m for m in results["hebrew_month_matches"] if m["voynich"] == word and m["score"] >= 0.5]
            lat_m = [m for m in results["latin_month_matches"] if m["voynich"] == word and m["score"] >= 0.5]
            zod_m = [m for m in results["hebrew_zodiac_matches"] if m["voynich"] == word and m["score"] >= 0.5]
            
            if heb_m or lat_m or zod_m:
                entry = {"voynich": word, "matches": []}
                if heb_m:
                    entry["matches"].append({"type": "hebrew_month", "match": heb_m[0]["match"], "score": heb_m[0]["score"]})
                if lat_m:
                    entry["matches"].append({"type": "latin_month", "match": lat_m[0]["match"], "score": lat_m[0]["score"]})
                if zod_m:
                    entry["matches"].append({"type": "hebrew_zodiac", "match": zod_m[0]["match"], "score": zod_m[0]["score"]})
                new_vocab.append(entry)
    
    results["new_vocabulary"] = sorted(new_vocab, key=lambda x: -max(m["score"] for m in x["matches"]))
    
    patterns = []
    
    dar_count = sum(1 for w in all_labels if "dar" in w)
    if dar_count > 0:
        patterns.append({
            "pattern": "dar",
            "occurrences": dar_count,
            "meaning": "Adar (Hebrew month)",
            "confidence": "high"
        })
    
    sal_count = sum(1 for w in all_labels if "sal" in w or "sol" in w)
    if sal_count > 0:
        patterns.append({
            "pattern": "sal/sol",
            "occurrences": sal_count,
            "meaning": "possibly month marker or Aries variant",
            "confidence": "medium"
        })
    
    shor_count = sum(1 for w in all_labels if "shor" in w or "sary" in w)
    if shor_count > 0:
        patterns.append({
            "pattern": "shor/sary",
            "occurrences": shor_count,
            "meaning": "Taurus (Hebrew shor)",
            "confidence": "high"
        })
    
    dal_count = sum(1 for w in all_labels if w.startswith("dal") or w.startswith("dol"))
    if dal_count > 0:
        patterns.append({
            "pattern": "dal/dol",
            "occurrences": dal_count,
            "meaning": "Aries (taleh) or Aquarius (dli)",
            "confidence": "medium"
        })
    
    ary_count = sum(1 for w in all_labels if "ary" in w or "ory" in w)
    if ary_count > 0:
        patterns.append({
            "pattern": "ary/ory",
            "occurrences": ary_count,
            "meaning": "Leo (Hebrew aryeh)",
            "confidence": "medium"
        })
    
    results["calendar_patterns"] = patterns
    results["month_frequency"] = dict(results["month_frequency"])
    results["zodiac_frequency"] = dict(results["zodiac_frequency"])
    
    heb_high = len([m for m in results["hebrew_month_matches"] if m["score"] >= 0.6])
    lat_high = len([m for m in results["latin_month_matches"] if m["score"] >= 0.6])
    zod_high = len([m for m in results["hebrew_zodiac_matches"] if m["score"] >= 0.6])
    
    results["summary"] = {
        "folios_analyzed": results["folios_analyzed"],
        "total_words": results["total_words_extracted"],
        "total_labels": results["total_labels_extracted"],
        "hebrew_month_high_matches": heb_high,
        "latin_month_high_matches": lat_high,
        "hebrew_zodiac_high_matches": zod_high,
        "new_vocabulary_count": len(results["new_vocabulary"]),
        "dominant_calendar": "Hebrew" if heb_high + zod_high > lat_high else "Latin" if lat_high > heb_high + zod_high else "Mixed",
    }
    
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("ZODIAC LABEL ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Folios analyzed: {results['folios_analyzed']}")
    print(f"Total words extracted: {results['total_words_extracted']}")
    print(f"Total labels extracted: {results['total_labels_extracted']}")
    print(f"\nHebrew month matches (score>=0.6): {heb_high}")
    print(f"Latin month matches (score>=0.6): {lat_high}")
    print(f"Hebrew zodiac matches (score>=0.6): {zod_high}")
    print(f"\nDominant calendar system: {results['summary']['dominant_calendar']}")
    print(f"New vocabulary entries: {len(results['new_vocabulary'])}")
    
    print("\n--- TOP HEBREW MONTH MATCHES ---")
    for m in results["hebrew_month_matches"][:10]:
        print(f"  {m['voynich']:15} → {m['match']:12} (score: {m['score']})")
    
    print("\n--- TOP HEBREW ZODIAC MATCHES ---")
    for m in results["hebrew_zodiac_matches"][:10]:
        print(f"  {m['voynich']:15} → {m['match']:12} = {m['zodiac_sign']:12} (score: {m['score']})")
    
    print("\n--- CALENDAR PATTERNS FOUND ---")
    for p in results["calendar_patterns"]:
        print(f"  {p['pattern']:12} ({p['occurrences']} occurrences) → {p['meaning']}")
    
    print(f"\nResults saved to {OUT_JSON}")
    return results


if __name__ == "__main__":
    main()

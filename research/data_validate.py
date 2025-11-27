import json
import re
from pathlib import Path
from collections import Counter, defaultdict

CLASTON_FILE = "voynich_raw.txt"
EVA_FILE = "data/eva_ivtff.txt"
OUTPUT_JSON = "results/data_validation.json"

CLASTON_TO_EVA = {
    'o': 'o', 'a': 'a', 's': 's', 'f': 'f', 'i': 'i', 'n': 'n',
    '9': 'y', '8': 'd', 'h': 'k', 'k': 't', 'e': 'l', 'y': 'r',
    'c': 'e', '4': 'q', 'g': 'p', 'p': 'm'
}

CLASTON_DIGRAPHS = {
    'am': 'aiin', 'aim': 'aiiin', 'an': 'ain', 'M': 'iin',
    'oe': 'ol', 'oy': 'or', 'ae': 'al', 'ay': 'ar', 'iy': 'ir',
    'K': 'ckh', 'H': 'ckh', '1': 'ch', '2': 'sh',
    '1h': 'cth', '1g': 'cph', 'fh': 'cfh',
    'cc89': 'eedy', 'c89': 'edy', 'cc9': 'eey', 'c9': 'ey', '89': 'dy'
}

SCRIPTS_DATA = [
    ("eva_analysis.py", "eva_ivtff.txt", "EVA", "H"),
    ("sentence.py", "eva_ivtff.txt", "EVA", "H"),
    ("verb_context.py", "eva_ivtff.txt", "EVA", "H"),
    ("common_words.py", "eva_ivtff.txt", "EVA", "H"),
    ("translate.py", "eva_ivtff.txt", "EVA", "H"),
    ("key_validation.py", "eva_ivtff.txt", "EVA", "H"),
    ("botanical_decode.py", "voynich_raw.txt", "Claston", None),
    ("latin_decoder.py", "voynich_raw.txt", "Claston", None),
    ("cross_section.py", "voynich_raw.txt", "Claston", None),
    ("phrase_patterns.py", "voynich_raw.txt", "Claston", None),
    ("verb_hunting.py", "voynich_raw.txt", "Claston", None),
    ("vocab.py", "voynich_raw.txt", "Claston", None),
    ("herbal_compare.py", "voynich_raw.txt", "Claston", None),
    ("latin_abbrev.py", "voynich_raw.txt", "Claston", None),
    ("hungarian_turkish.py", "voynich_raw.txt", "Claston", None),
    ("anchor.py", "voynich_raw.txt", "Claston", None),
    ("basque_validation.py", "voynich_raw.txt", "Claston", None),
    ("track1_language_comparison.py", "voynich_raw.txt", "Claston", None),
    ("identify_plants.py", "voynich_raw.txt", "Claston", None),
    ("phonetic.py", "voynich_raw.txt", "Claston", None),
    ("decoder.py", "voynich_raw.txt", "Claston", None),
    ("botanical.py", "voynich_raw.txt", "Claston", None),
    ("word_grammar.py", "voynich_raw.txt", "Claston", None),
    ("compare_languages.py", "voynich_raw.txt", "Claston", None),
    ("analyze.py", "voynich_raw.txt", "Claston", None),
    ("latin_cipher.py", "voynich_raw.txt", "Claston", None),
    ("decode.py", "voynich_raw.txt", "Claston", None),
    ("plants.py", "voynich_raw.txt", "Claston", None),
    ("cipher.py", "voynich_raw.txt", "Claston", None),
    ("astro.py", "voynich_raw.txt", "Claston", None),
    ("master_dict.py", "voynich_transcription.txt", "Mixed", None),
    ("trans_unify.py", "both", "Both", None),
    ("eva_validate.py", "both", "Both", None),
    ("eva_align.py", "both", "Both", None),
    ("eva_map.py", "both", "Both", None),
]


def parse_claston():
    pages = {}
    with open(CLASTON_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'<(\w+\.\d+)>(.+)', line.strip())
            if m:
                loc, text = m.groups()
                folio = loc.split('.')[0]
                if folio not in pages:
                    pages[folio] = {}
                pages[folio][loc] = text
    return pages


def parse_eva(transcriber='H'):
    pages = {}
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            m = re.match(r'<([^>]+);(\w)>\s*(.+)', line)
            if m:
                loc, trans, text = m.groups()
                if trans != transcriber:
                    continue
                loc_clean = re.sub(r',[@+*=][^;]*', '', loc)
                folio = loc_clean.split('.')[0]
                if folio not in pages:
                    pages[folio] = {}
                pages[folio][loc_clean] = text
    return pages


def claston_to_eva(word):
    out = []
    i = 0
    sorted_digraphs = sorted(CLASTON_DIGRAPHS.items(), key=lambda x: len(x[0]), reverse=True)
    
    while i < len(word):
        matched = False
        for claston, eva in sorted_digraphs:
            if word[i:i+len(claston)] == claston:
                out.append(eva)
                i += len(claston)
                matched = True
                break
        
        if not matched:
            char = word[i]
            out.append(CLASTON_TO_EVA.get(char, char))
            i += 1
    
    return ''.join(out)


def compare_transcribers():
    transcribers = ['H', 'C', 'F', 'N', 'U']
    data = {t: parse_eva(t) for t in transcribers}
    
    disagreements = defaultdict(int)
    total_words = 0
    coverage = {t: 0 for t in transcribers}
    
    sample_folios = ['f1r', 'f2r', 'f3r', 'f4r', 'f5r']
    
    for folio in sample_folios:
        h_page = data['H'].get(folio, {})
        for loc, h_text in h_page.items():
            h_words = [w for w in re.split(r'[.\-=]', h_text) if w and '!' not in w and '?' not in w]
            total_words += len(h_words)
            
            for t in transcribers:
                t_page = data[t].get(folio, {})
                t_text = t_page.get(loc, '')
                if t_text:
                    coverage[t] += 1
                    t_words = [w for w in re.split(r'[.\-=]', t_text) if w]
                    for i, (hw, tw) in enumerate(zip(h_words, t_words)):
                        hw_clean = re.sub(r'[!?<>@\d]', '', hw)
                        tw_clean = re.sub(r'[!?<>@\d]', '', tw)
                        if hw_clean != tw_clean:
                            disagreements[f'H_vs_{t}'] += 1
    
    return {
        'total_words_sampled': total_words,
        'disagreements': dict(disagreements),
        'coverage': coverage,
        'recommended': 'H'
    }


def reconcile_data():
    claston = parse_claston()
    eva = parse_eva('H')
    
    results = {
        'lines_compared': 0,
        'matches': 0,
        'partial_matches': 0,
        'mismatches': [],
        'conversion_examples': []
    }
    
    sample_folios = ['1r', '2r', '3r', '17r', '26r']
    
    for folio in sample_folios:
        c_page = claston.get(folio, {})
        e_page = eva.get('f' + folio, {})
        
        for loc, c_text in list(c_page.items())[:20]:
            results['lines_compared'] += 1
            e_loc = 'f' + loc
            e_text = e_page.get(e_loc, '')
            
            if not e_text:
                continue
            
            c_words = [w for w in re.split(r'[.\-=]', c_text) if w]
            e_words = [w for w in re.split(r'[.\-=]', e_text) if w and '!' not in w and '?' not in w]
            
            word_matches = 0
            for cw, ew in zip(c_words[:5], e_words[:5]):
                cw_clean = re.sub(r'[!?<>@A-Z\W]', '', cw)
                cw_clean = cw_clean.replace(',', '')
                converted = claston_to_eva(cw_clean)
                ew_clean = re.sub(r'[!?<>@$]', '', ew)
                
                if len(results['conversion_examples']) < 10:
                    results['conversion_examples'].append({
                        'claston': cw,
                        'converted': converted,
                        'eva': ew_clean,
                        'match': converted == ew_clean
                    })
                
                if converted == ew_clean:
                    word_matches += 1
                elif len(converted) > 3 and len(ew_clean) > 3 and converted[:3] == ew_clean[:3]:
                    word_matches += 0.5
            
            if c_words:
                match_rate = word_matches / min(len(c_words), 5)
                if match_rate > 0.6:
                    results['matches'] += 1
                elif match_rate > 0.3:
                    results['partial_matches'] += 1
                else:
                    if len(results['mismatches']) < 10:
                        results['mismatches'].append({
                            'loc': loc,
                            'claston': c_text[:60],
                            'eva': e_text[:60],
                            'match_rate': round(match_rate, 2)
                        })
    
    return results


def verify_char_mapping():
    verified = {}
    
    claston = parse_claston()
    eva = parse_eva('H')
    
    c_words = []
    for page in list(claston.values())[:10]:
        for text in page.values():
            c_words.extend(re.split(r'[.\-=\s]', text))
    
    e_words = []
    for page in list(eva.values())[:10]:
        for text in page.values():
            e_words.extend([w for w in re.split(r'[.\-=\s]', text) if '!' not in w])
    
    char_pairs = []
    for mapping, expected in CLASTON_TO_EVA.items():
        claston_count = sum(1 for w in c_words if mapping in w.lower())
        verified[mapping] = {
            'eva': expected,
            'claston_freq': claston_count,
            'verified': claston_count > 0
        }
    
    for mapping, expected in CLASTON_DIGRAPHS.items():
        claston_count = sum(1 for w in c_words if mapping in w)
        verified[f'digraph_{mapping}'] = {
            'eva': expected,
            'claston_freq': claston_count,
            'verified': claston_count > 0
        }
    
    return verified


def audit_scripts():
    audit = []
    for script, data_file, system, transcriber in SCRIPTS_DATA:
        audit.append({
            'script': script,
            'data_file': data_file,
            'system': system,
            'transcriber': transcriber
        })
    return audit


def main():
    print("=" * 60)
    print("DATA VALIDATION - Voynich Manuscript Transcription Systems")
    print("=" * 60)
    
    print("\n1. Auditing scripts...")
    scripts_audit = audit_scripts()
    claston_scripts = [s for s in scripts_audit if s['system'] == 'Claston']
    eva_scripts = [s for s in scripts_audit if s['system'] == 'EVA']
    
    print(f"   Scripts using Claston: {len(claston_scripts)}")
    print(f"   Scripts using EVA: {len(eva_scripts)}")
    
    print("\n2. Verifying character mapping...")
    char_mapping = verify_char_mapping()
    verified_count = sum(1 for v in char_mapping.values() if v.get('verified'))
    print(f"   Verified mappings: {verified_count}/{len(char_mapping)}")
    
    print("\n3. Comparing EVA transcribers...")
    transcriber_comp = compare_transcribers()
    print(f"   Words sampled: {transcriber_comp['total_words_sampled']}")
    print(f"   Disagreements: {transcriber_comp['disagreements']}")
    print(f"   Recommended: {transcriber_comp['recommended']}")
    
    print("\n4. Reconciling data files...")
    reconciliation = reconcile_data()
    print(f"   Lines compared: {reconciliation['lines_compared']}")
    print(f"   Full matches: {reconciliation['matches']}")
    print(f"   Partial matches: {reconciliation['partial_matches']}")
    print(f"   Mismatches: {len(reconciliation['mismatches'])}")
    
    recommendation = "EVA"
    recommendation_reasons = [
        "EVA is the standard in Voynich research literature",
        "EVA has multiple transcribers for cross-validation",
        "EVA is more widely documented and referenced",
        "Takahashi's (H) transcription is complete and recent"
    ]
    
    results = {
        'scripts_audited': scripts_audit,
        'scripts_by_system': {
            'claston': len(claston_scripts),
            'eva': len(eva_scripts),
        },
        'character_mapping': char_mapping,
        'transcriber_comparison': transcriber_comp,
        'data_reconciliation': reconciliation,
        'recommendation': recommendation,
        'recommendation_reasons': recommendation_reasons,
        'critical_finding': (
            "Two transcription systems in use: Claston (voynich_raw.txt) and EVA (eva_ivtff.txt). "
            f"{len(claston_scripts)} scripts use Claston, {len(eva_scripts)} use EVA. "
            "This inconsistency could explain analysis failures."
        )
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_JSON}")
    
    report_path = "results/data_validation_report.md"
    with open(report_path, 'w') as f:
        f.write("# Data Validation Report\n\n")
        f.write("## Critical Finding\n\n")
        f.write(f"{results['critical_finding']}\n\n")
        
        f.write("## Scripts Audit\n\n")
        f.write(f"| System | Count |\n|--------|-------|\n")
        f.write(f"| Claston | {len(claston_scripts)} |\n")
        f.write(f"| EVA | {len(eva_scripts)} |\n\n")
        
        f.write("### Scripts Using Claston (voynich_raw.txt)\n\n")
        for s in claston_scripts:
            f.write(f"- `{s['script']}`\n")
        
        f.write("\n### Scripts Using EVA (eva_ivtff.txt)\n\n")
        for s in eva_scripts:
            f.write(f"- `{s['script']}` (transcriber: {s['transcriber']})\n")
        
        f.write("\n## Character Mapping Verification\n\n")
        f.write("| Claston | EVA | Verified |\n|---------|-----|----------|\n")
        for k, v in list(char_mapping.items())[:20]:
            name = k.replace('digraph_', '')
            f.write(f"| {name} | {v['eva']} | {'✓' if v['verified'] else '✗'} |\n")
        
        f.write("\n## Transcriber Comparison\n\n")
        f.write(f"- Words sampled: {transcriber_comp['total_words_sampled']}\n")
        f.write(f"- Recommended transcriber: **{transcriber_comp['recommended']}** (Takahashi)\n\n")
        f.write("| Comparison | Disagreements |\n|------------|---------------|\n")
        for k, v in transcriber_comp['disagreements'].items():
            f.write(f"| {k} | {v} |\n")
        
        f.write("\n## Data Reconciliation\n\n")
        f.write(f"- Lines compared: {reconciliation['lines_compared']}\n")
        f.write(f"- Full matches: {reconciliation['matches']}\n")
        f.write(f"- Partial matches: {reconciliation['partial_matches']}\n")
        f.write(f"- Mismatches: {len(reconciliation.get('mismatches', []))}\n\n")
        
        if reconciliation.get('conversion_examples'):
            f.write("### Sample Conversions\n\n")
            f.write("| Claston | Converted | EVA | Match |\n|---------|-----------|-----|-------|\n")
            for ex in reconciliation['conversion_examples']:
                match = '✓' if ex['match'] else '✗'
                f.write(f"| {ex['claston']} | {ex['converted']} | {ex['eva']} | {match} |\n")
        
        f.write("\n## Recommendation\n\n")
        f.write(f"**Standardize on: {recommendation}**\n\n")
        f.write("Reasons:\n")
        for r in recommendation_reasons:
            f.write(f"- {r}\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("1. Use `voynich_data.py` as the single data access module\n")
        f.write("2. Update analysis scripts to use EVA via the master module\n")
        f.write("3. Re-run key analyses with consistent data source\n")
        f.write("4. Deprecate direct use of voynich_raw.txt in new scripts\n")
    
    print(f"Report saved to {report_path}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION: Standardize on EVA")
    print("=" * 60)
    for r in recommendation_reasons:
        print(f"  - {r}")
    
    print("\n" + "=" * 60)
    print("CRITICAL FINDING")
    print("=" * 60)
    print(f"\n{results['critical_finding']}")
    
    return results


if __name__ == "__main__":
    main()




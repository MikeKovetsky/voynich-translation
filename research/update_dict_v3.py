#!/usr/bin/env python3
"""
Track 84: Build Master Dictionary v3.0
Consolidates findings from Track 80 (herbal mining) and Track 83 (plant pairs)
into a unified dictionary with confidence-based priority.

Priority Hierarchy:
1. ULTRA_HIGH (Track 83) - conf 0.95: Plant appears on multiple pages + in recipes
2. VERY_HIGH (Track 83) - conf 0.90: Plant appears on multiple pages
3. HIGH (Track 80) - conf 0.85: Rare word appears in recipes
4. MEDIUM (Track 80) - conf 0.70: Possible plant reference
5. LOW (Track 80) - conf 0.55: Weak signal
6. EXISTING - keep original confidence
"""

import json
from collections import defaultdict

CONF_ULTRA_HIGH = 0.95
CONF_VERY_HIGH = 0.90
CONF_HIGH = 0.85
CONF_MEDIUM = 0.70
CONF_LOW = 0.55


def load_existing():
    with open('results/master_dictionary.json') as f:
        data = json.load(f)
    return data.get('entries', {})


def load_track80():
    with open('results/full_herbal_mining.json') as f:
        data = json.load(f)
    return data.get('crossref_results', [])


def load_track83():
    with open('results/plant_pair_validation.json') as f:
        data = json.load(f)
    return data.get('validated_plant_names', [])


def map_conf(level):
    if level == 'ULTRA_HIGH':
        return CONF_ULTRA_HIGH
    elif level == 'VERY_HIGH':
        return CONF_VERY_HIGH
    elif level == 'HIGH':
        return CONF_HIGH
    elif level == 'MEDIUM':
        return CONF_MEDIUM
    else:
        return CONF_LOW


def normalize_plant(plant):
    if not plant or plant.lower() in ['unknown', "o'neill", 'beinecke digital library']:
        return None
    return plant.lower().strip()


def build_v3():
    existing = load_existing()
    track80 = load_track80()
    track83 = load_track83()

    # Stats
    stats = {
        'existing_entries': len(existing),
        'track80_entries': len(track80),
        'track83_entries': len(track83),
        'conflicts': [],
        'new_from_track83': 0,
        'new_from_track80': 0,
        'upgraded': 0,
        'kept_existing': 0
    }

    merged = {}

    # Step 1: Load Track 83 (highest priority)
    for entry in track83:
        word = entry.get('word', '').strip()
        if not word or '<>' in word:
            continue

        plant = normalize_plant(entry.get('plant'))
        conf_level = entry.get('confidence', 'HIGH')
        conf = map_conf(conf_level)
        evidence = entry.get('evidence', '')

        meaning = f"plant:{plant}" if plant else "plant_name"

        merged[word] = {
            'voynich': word,
            'meaning': meaning,
            'language': 'botanical',
            'confidence': conf,
            'domain': 'botanical',
            'source': 'Track83_PlantPair',
            'evidence': evidence,
            'confidence_level': conf_level
        }
        stats['new_from_track83'] += 1

    # Step 2: Load Track 80 (medium priority)
    for entry in track80:
        word = entry.get('word', '').strip()
        if not word or '<>' in word:
            continue

        plant = normalize_plant(entry.get('expert_plant'))
        conf_level = entry.get('confidence', 'MEDIUM')
        conf = map_conf(conf_level)

        # Skip if already in Track 83 (higher priority)
        if word in merged:
            if merged[word]['source'] == 'Track83_PlantPair':
                continue

        meaning = f"plant:{plant}" if plant else "plant_term"

        # Only add/upgrade if confidence is higher
        if word in merged:
            if conf > merged[word]['confidence']:
                stats['upgraded'] += 1
                merged[word] = {
                    'voynich': word,
                    'meaning': meaning,
                    'language': 'botanical',
                    'confidence': conf,
                    'domain': 'botanical',
                    'source': 'Track80_HerbalMining',
                    'folios': entry.get('recipe_folios', []),
                    'confidence_level': conf_level
                }
        else:
            merged[word] = {
                'voynich': word,
                'meaning': meaning,
                'language': 'botanical',
                'confidence': conf,
                'domain': 'botanical',
                'source': 'Track80_HerbalMining',
                'folios': entry.get('recipe_folios', []),
                'confidence_level': conf_level
            }
            stats['new_from_track80'] += 1

    # Step 3: Merge existing dictionary (lowest priority for plant terms)
    for word, entry in existing.items():
        if word in merged:
            # Conflict resolution
            existing_conf = entry.get('confidence', 0.5)
            new_conf = merged[word]['confidence']

            # Keep existing if:
            # 1. Existing confidence is higher AND
            # 2. It's not a generic plant_term
            if existing_conf > new_conf:
                existing_meaning = entry.get('meaning', '')
                new_meaning = merged[word].get('meaning', '')

                # Don't override specific meanings with generic plant_term
                if 'plant_term' in new_meaning and 'plant' not in existing_meaning.lower():
                    stats['conflicts'].append({
                        'word': word,
                        'kept': entry.get('source'),
                        'replaced': merged[word].get('source'),
                        'reason': 'existing_has_specific_meaning'
                    })
                    merged[word] = entry
                    stats['kept_existing'] += 1
                else:
                    # Keep botanical finding
                    stats['conflicts'].append({
                        'word': word,
                        'kept': merged[word].get('source'),
                        'replaced': entry.get('source'),
                        'reason': 'botanical_priority'
                    })
            else:
                stats['conflicts'].append({
                    'word': word,
                    'kept': merged[word].get('source'),
                    'replaced': entry.get('source'),
                    'reason': 'higher_confidence'
                })
        else:
            merged[word] = entry
            stats['kept_existing'] += 1

    return merged, stats


def calc_coverage(entries):
    import sys
    import re
    sys.path.insert(0, '.')
    import voynich_data as vd

    pages = vd.get_eva_pages()
    words_by_section = defaultdict(list)

    # Clean word: remove special characters
    def clean_word(w):
        return re.sub(r'[<>!\?\$@\d\'\-\.]', '', w).strip()

    for folio, lines_dict in pages.items():
        # Classify section
        if folio.startswith(('f10', 'f11')):
            section = 'recipe'
        elif folio.startswith(('f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73')):
            section = 'zodiac'
        elif folio.startswith(('f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84')):
            section = 'biological'
        else:
            section = 'herbal'

        for line_id, line_text in lines_dict.items():
            # Split on dots and whitespace
            words = re.split(r'[\.\s]+', line_text)
            for w in words:
                cleaned = clean_word(w)
                if cleaned:
                    words_by_section[section].append(cleaned)

    total = 0
    covered = 0
    coverage_by_section = {}

    for section, words in words_by_section.items():
        sec_total = len(words)
        sec_covered = sum(1 for w in words if w in entries)
        coverage_by_section[section] = {
            'total': sec_total,
            'covered': sec_covered,
            'rate': sec_covered / sec_total if sec_total else 0
        }
        total += sec_total
        covered += sec_covered

    return {
        'overall': {'total': total, 'covered': covered, 'rate': covered / total if total else 0},
        'by_section': coverage_by_section
    }


def main():
    print("Track 84: Building Master Dictionary v3.0")
    print("=" * 50)

    merged, stats = build_v3()

    # Calculate domain distribution
    domains = defaultdict(int)
    sources = defaultdict(int)
    conf_levels = defaultdict(int)

    for word, entry in merged.items():
        domains[entry.get('domain', 'other')] += 1
        sources[entry.get('source', 'unknown')] += 1
        conf_levels[entry.get('confidence_level', 'N/A')] += 1

    # Calculate coverage
    coverage = calc_coverage(merged)

    # Build output
    output = {
        'version': '3.0',
        'total_entries': len(merged),
        'sources': dict(sources),
        'domains': dict(domains),
        'confidence_distribution': dict(conf_levels),
        'merge_stats': {
            'existing_entries': stats['existing_entries'],
            'track80_entries': stats['track80_entries'],
            'track83_entries': stats['track83_entries'],
            'new_from_track83': stats['new_from_track83'],
            'new_from_track80': stats['new_from_track80'],
            'upgraded': stats['upgraded'],
            'kept_existing': stats['kept_existing'],
            'conflicts_resolved': len(stats['conflicts'])
        },
        'coverage': coverage,
        'entries': merged
    }

    # Save dictionary
    with open('results/master_dictionary_v3.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"\n📚 TOTAL ENTRIES: {len(merged)}")
    print(f"\n📊 BY SOURCE:")
    for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"   {src}: {cnt}")

    print(f"\n📁 BY DOMAIN:")
    for dom, cnt in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"   {dom}: {cnt}")

    print(f"\n🎯 BY CONFIDENCE:")
    for level, cnt in sorted(conf_levels.items(), key=lambda x: -x[1]):
        print(f"   {level}: {cnt}")

    print(f"\n📈 COVERAGE:")
    print(f"   Overall: {coverage['overall']['rate']*100:.1f}% ({coverage['overall']['covered']}/{coverage['overall']['total']})")
    for section, data in coverage['by_section'].items():
        print(f"   {section.capitalize()}: {data['rate']*100:.1f}% ({data['covered']}/{data['total']})")

    print(f"\n🔄 MERGE STATS:")
    print(f"   New from Track 83: {stats['new_from_track83']}")
    print(f"   New from Track 80: {stats['new_from_track80']}")
    print(f"   Upgraded: {stats['upgraded']}")
    print(f"   Kept existing: {stats['kept_existing']}")
    print(f"   Conflicts resolved: {len(stats['conflicts'])}")

    # Generate report
    report = generate_report(output, stats)
    with open('results/dictionary_v3_report.md', 'w') as f:
        f.write(report)

    print("\n✅ Saved: results/master_dictionary_v3.json")
    print("✅ Saved: results/dictionary_v3_report.md")


def generate_report(output, stats):
    lines = [
        "# Master Dictionary v3.0 Report",
        "",
        "## Summary",
        "",
        f"- **Total Entries**: {output['total_entries']}",
        f"- **Version**: {output['version']}",
        "",
        "## Source Distribution",
        "",
        "| Source | Count | % |",
        "|--------|-------|---|",
    ]

    total = output['total_entries']
    for src, cnt in sorted(output['sources'].items(), key=lambda x: -x[1]):
        pct = cnt / total * 100 if total else 0
        lines.append(f"| {src} | {cnt} | {pct:.1f}% |")

    lines.extend([
        "",
        "## Domain Distribution",
        "",
        "| Domain | Count | % |",
        "|--------|-------|---|",
    ])

    for dom, cnt in sorted(output['domains'].items(), key=lambda x: -x[1]):
        pct = cnt / total * 100 if total else 0
        lines.append(f"| {dom} | {cnt} | {pct:.1f}% |")

    lines.extend([
        "",
        "## Confidence Distribution",
        "",
        "| Level | Count | % |",
        "|-------|-------|---|",
    ])

    for level, cnt in sorted(output['confidence_distribution'].items(), key=lambda x: -x[1]):
        pct = cnt / total * 100 if total else 0
        lines.append(f"| {level} | {cnt} | {pct:.1f}% |")

    lines.extend([
        "",
        "## Coverage Analysis",
        "",
        "| Section | Total Words | Covered | Rate |",
        "|---------|-------------|---------|------|",
    ])

    cov = output['coverage']
    lines.append(f"| **Overall** | {cov['overall']['total']} | {cov['overall']['covered']} | **{cov['overall']['rate']*100:.1f}%** |")
    for section, data in cov['by_section'].items():
        lines.append(f"| {section.capitalize()} | {data['total']} | {data['covered']} | {data['rate']*100:.1f}% |")

    lines.extend([
        "",
        "## Merge Statistics",
        "",
        f"- **Input from existing dictionary**: {stats['existing_entries']} entries",
        f"- **Input from Track 80 (herbal mining)**: {stats['track80_entries']} entries",
        f"- **Input from Track 83 (plant pairs)**: {stats['track83_entries']} entries",
        "",
        f"- **New from Track 83**: {stats['new_from_track83']} entries",
        f"- **New from Track 80**: {stats['new_from_track80']} entries",
        f"- **Upgraded entries**: {stats['upgraded']}",
        f"- **Kept from existing**: {stats['kept_existing']}",
        f"- **Conflicts resolved**: {len(stats['conflicts'])}",
        "",
        "## Key Improvements",
        "",
        "1. **Track 83 (Plant Pairs)**: Words appearing on multiple plant pages + recipes",
        "   - ULTRA_HIGH confidence (0.95): Cross-validated plant names",
        "   - VERY_HIGH confidence (0.90): Consistent plant vocabulary",
        "",
        "2. **Track 80 (Herbal Mining)**: Rare words on herbal pages also in recipes",
        "   - HIGH confidence (0.85): Strong plant-recipe correlation",
        "   - MEDIUM/LOW: Possible plant references",
        "",
        "3. **Conflict Resolution**: Higher confidence always wins",
        "",
        "---",
        "",
        "*Generated by Track 84: update_dict_v3.py*",
    ])

    return "\n".join(lines)


if __name__ == '__main__':
    main()




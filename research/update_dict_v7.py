#!/usr/bin/env python3
"""
Track 109: Master Dictionary Update (v7)
Consolidates findings from the "Spring" Lexicon research.

Updates:
1. Integrate "Spring" Lexicon (aiin, daiin, etc.)
2. Add Morphology Rules
3. Root Merging
"""

import json
import re
from collections import defaultdict
import sys
import os

# Add current directory to path to import voynich_data if needed
sys.path.insert(0, '.')
try:
    import voynich_data as vd
except ImportError:
    vd = None

CONF_HIGH = 0.90  # High confidence for verified words

def load_v6():
    path = 'results/master_dictionary_v6.json'
    if not os.path.exists(path):
        # Fallback to v5 if v6 doesn't exist, as per some workflows
        path = 'results/master_dictionary_v5.json'
        print(f"Warning: {path} not found. Falling back to v5.")
    
    with open(path) as f:
        return json.load(f)

def update_entries(entries):
    updates = {
        'aiin': {
            'meaning': 'spring/source',
            'category': 'elemental',
            'confidence': CONF_HIGH,
            'pos': 'noun',
            'source': 'Track109_SpringLexicon'
        },
        'daiin': {
            'meaning': 'from the spring / take water',
            'category': 'recipe_instruction',
            'confidence': CONF_HIGH,
            'pos': 'verb/phrase',
            'source': 'Track109_SpringLexicon',
            'root': 'aiin',
            'morphology': 'd-aiin'
        },
        'qokaiin': {
            'meaning': 'in the spring',
            'category': 'location',
            'confidence': CONF_HIGH,
            'pos': 'phrase',
            'source': 'Track109_SpringLexicon',
            'root': 'aiin',
            'morphology': 'qok-aiin'
        },
        'shedy': {
            'meaning': 'which/that',
            'category': 'grammar',
            'confidence': CONF_HIGH,
            'pos': 'relative_pronoun',
            'source': 'Track109_SpringLexicon'
        },
        'chedy': {
            'meaning': 'herb/plant',
            'category': 'botanical',
            'confidence': CONF_HIGH,
            'pos': 'noun',
            'source': 'Track109_SpringLexicon'
        },
        'qok-': {
            'meaning': 'in/with (instrumental)',
            'category': 'prefix',
            'confidence': CONF_HIGH,
            'pos': 'prefix',
            'source': 'Track109_SpringLexicon',
            'is_morpheme': True
        },
        'ok-': {
            'meaning': 'liquid/mixture',
            'category': 'prefix',
            'confidence': CONF_HIGH,
            'pos': 'prefix',
            'source': 'Track109_SpringLexicon',
            'is_morpheme': True
        }
    }
    
    stats = {'updated': 0, 'new': 0}
    
    for word, data in updates.items():
        if word in entries:
            # Update existing
            entries[word].update(data)
            stats['updated'] += 1
        else:
            # Create new
            entries[word] = data
            entries[word]['voynich'] = word
            stats['new'] += 1
            
    return entries, stats

def apply_root_merging(entries):
    # Task 3: Root Merging
    # qokaiin -> Root: aiin (Already handled in update_entries)
    # okeedy -> Root: eedy (or keep as okeedy if unique)
    
    stats = {'merged': 0}
    
    if 'okeedy' in entries and 'eedy' in entries:
        # Link okeedy to eedy
        entries['okeedy']['root'] = 'eedy'
        entries['okeedy']['morphology'] = 'ok-eedy'
        # If eedy doesn't have a strong meaning, maybe inherit hints? 
        # For now just link.
        stats['merged'] += 1
        
    return entries, stats

def get_morphology_rules():
    return {
        'q-': 'in/with',
        'd-': 'from/of',
        'o-': 'the/it (definite article variant?)',
        'y-': 'and/also (or plural?)',
        'qok-': 'in/with (instrumental)',
        'ok-': 'liquid/mixture'
    }

def calc_coverage(entries):
    if not vd:
        return {'overall': {'rate': 0, 'covered': 0, 'total': 0}, 'by_section': {}}
        
    pages = vd.get_eva_pages()
    words_by_section = defaultdict(list)

    def clean_word(w):
        return re.sub(r'[<>!\?\$@\d\'\-\.]', '', w).strip()

    for folio, lines_dict in pages.items():
        if folio.startswith(('f10', 'f11')):
            section = 'recipe'
        elif folio.startswith(('f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73')):
            section = 'zodiac'
        elif folio.startswith(('f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84')):
            section = 'biological'
        else:
            section = 'herbal'

        for line_text in lines_dict.values():
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

def generate_report(output, update_stats, root_stats):
    lines = [
        "# Master Dictionary v7.0 Report",
        "",
        "## Summary",
        "",
        f"- **Total Entries**: {output['total_entries']}",
        f"- **Version**: {output['version']}",
        "",
        "## Updates (Spring Lexicon)",
        "",
        f"- **Updated Entries**: {update_stats['updated']}",
        f"- **New Entries**: {update_stats['new']}",
        f"- **Root Merges**: {root_stats['merged']}",
        "",
        "### Key Definitions Added/Updated",
        "- `aiin`: spring/source",
        "- `daiin`: from the spring / take water",
        "- `qokaiin`: in the spring",
        "- `shedy`: which/that",
        "- `chedy`: herb/plant",
        "",
        "## Morphology Rules",
        "",
        "| Prefix | Meaning |",
        "|--------|---------|",
    ]
    
    for p, m in output.get('morphology_rules', {}).items():
        lines.append(f"| `{p}` | {m} |")
        
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

    return "\n".join(lines)

def main():
    print("Track 109: Building Master Dictionary v7.0")
    
    # Load previous version
    data = load_v6()
    entries = data.get('entries', {})
    
    # Apply updates
    entries, update_stats = update_entries(entries)
    
    # Apply root merging
    entries, root_stats = apply_root_merging(entries)
    
    # Calculate coverage
    coverage = calc_coverage(entries)
    
    # Prepare output
    output = {
        'version': '7.0',
        'total_entries': len(entries),
        'entries': entries,
        'morphology_rules': get_morphology_rules(),
        'coverage': coverage,
        'sources': data.get('sources', {}), # Preserve if exists
        'domains': data.get('domains', {})
    }
    
    # Update sources/domains stats roughly
    # (Skipping detailed recalc for brevity, but could be added)
    
    # Save dictionary
    with open('results/master_dictionary_v7.json', 'w') as f:
        json.dump(output, f, indent=2)
        
    # Generate and save report
    report = generate_report(output, update_stats, root_stats)
    with open('results/dictionary_v7_report.md', 'w') as f:
        f.write(report)
        
    print(f"Updated {update_stats['updated']} entries, Added {update_stats['new']} entries.")
    print(f"Saved results/master_dictionary_v7.json")
    print(f"Saved results/dictionary_v7_report.md")

if __name__ == "__main__":
    main()

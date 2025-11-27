import json
from pathlib import Path

RESULTS = Path("results")

def load_dict():
    with open(RESULTS / "master_dictionary_v5.json") as f:
        return json.load(f)

def load_modifier_links():
    with open(RESULTS / "modifier_plant_links.json") as f:
        return json.load(f)

def load_modifier_report():
    with open(RESULTS / "modifier_report.md") as f:
        return f.read()

def get_generic_terms():
    """High-frequency modifiers that appear on many pages = generic botanical terms"""
    return {
        "chedy": {"meaning": "herb/plant (generic)", "notes": "32+ pages, generic term"},
        "chey": {"meaning": "herb/plant (generic)", "notes": "65+ pages, generic term"},
        "chckhy": {"meaning": "herb/plant (generic)", "notes": "40+ pages, generic term"},
        "oteedy": {"meaning": "herb/plant (generic)", "notes": "High-frequency modifier"},
        "okeedy": {"meaning": "herb/plant (generic)", "notes": "High-frequency modifier"},
        "lchedy": {"meaning": "herb/plant (generic)", "notes": "Common botanical modifier"},
        "otchedy": {"meaning": "herb/plant (generic)", "notes": "Common botanical modifier"},
        "cthedy": {"meaning": "herb/plant (generic)", "notes": "Common botanical modifier"},
    }

def get_specific_plants():
    """Ultra-specific and specific modifiers that ARE plant names"""
    return {
        # ULTRA_SPECIFIC (HIGH confidence - single page)
        "qotain": {
            "meaning": "geranium",
            "confidence": 0.9,
            "evidence": "ULTRA_SPECIFIC: Only on f58v (geranium page) + 4 recipes",
            "category": "source_modifier"
        },
        "okchedy": {
            "meaning": "specific_plant (f50r)",
            "confidence": 0.8,
            "evidence": "ULTRA_SPECIFIC: Only on f50r + recipes",
            "category": "source_modifier"
        },
        "lkar": {
            "meaning": "specific_plant (f66r)",
            "confidence": 0.8,
            "evidence": "ULTRA_SPECIFIC: Only on f66r + recipes",
            "category": "source_modifier"
        },
        # SPECIFIC (MEDIUM confidence - 2-3 pages)
        "chedal": {
            "meaning": "geranium/polygonum",
            "confidence": 0.7,
            "evidence": "SPECIFIC: f31v (polygonum), f43v (polygonum), f58v (geranium) + 3 recipes",
            "category": "source_modifier"
        },
        "lkeey": {
            "meaning": "papaver/poppy",
            "confidence": 0.7,
            "evidence": "SPECIFIC: f48v (papaver), f56v (scammonia/tamus) + 4 recipes",
            "category": "source_modifier"
        },
        "olkeedy": {
            "meaning": "specific_plant",
            "confidence": 0.7,
            "evidence": "SPECIFIC: f50r, f94r, f95r1 + recipes",
            "category": "source_modifier"
        },
        "lkeedy": {
            "meaning": "specific_plant (f55r/f66r)",
            "confidence": 0.7,
            "evidence": "SPECIFIC: f55r, f66r + recipes",
            "category": "source_modifier"
        },
        # From reverse analysis - specific modifiers on plant pages
        "otoly": {
            "meaning": "valerian",
            "confidence": 0.75,
            "evidence": "Found specifically on f101v (valerian), f37r (valerian) + recipe",
            "category": "source_modifier"
        },
        "chols": {
            "meaning": "botrychium",
            "confidence": 0.7,
            "evidence": "Found specifically on f100v (botrychium) + recipes",
            "category": "source_modifier"
        },
        "shdar": {
            "meaning": "scabiosa",
            "confidence": 0.7,
            "evidence": "Found specifically on f33r (scabiosa) + recipes",
            "category": "source_modifier"
        },
        "chekar": {
            "meaning": "scabiosa",
            "confidence": 0.75,
            "evidence": "From Track83: f33r + f34r (both scabiosa) + recipe",
            "category": "source_modifier"
        },
        "chodain": {
            "meaning": "papaver/moss",
            "confidence": 0.65,
            "evidence": "f2v (moss), f89v1 (papaver) + recipes",
            "category": "source_modifier"
        },
        "oy": {
            "meaning": "tamus/smilax",
            "confidence": 0.7,
            "evidence": "f17v (tamus communis), f89r2 + recipes",
            "category": "source_modifier"
        },
        "okshy": {
            "meaning": "botrychium",
            "confidence": 0.8,
            "evidence": "From Track83: f13v + f14v (botrychium) + recipe",
            "category": "source_modifier"
        },
        "chodar": {
            "meaning": "papaver",
            "confidence": 0.85,
            "evidence": "From Track83: f89v1 + f90v2 (papaver) + 4 recipes",
            "category": "source_modifier"
        },
        "opol": {
            "meaning": "papaver",
            "confidence": 0.8,
            "evidence": "From Track83: f89v1 + f90v2 (papaver) + recipe",
            "category": "source_modifier"
        },
        "pchey": {
            "meaning": "thistle",
            "confidence": 0.8,
            "evidence": "From Track83: f40r + f41r (thistle) + 2 recipes",
            "category": "source_modifier"
        },
        "alam": {
            "meaning": "geranium",
            "confidence": 0.85,
            "evidence": "From Track83: f58r + f58v + f65r (geranium) + 5 recipes",
            "category": "source_modifier"
        },
        "qokeod": {
            "meaning": "valerian",
            "confidence": 0.8,
            "evidence": "From Track83: f101v + f102v2 (valerian/gemswurz) + 3 recipes",
            "category": "source_modifier"
        },
        "soy": {
            "meaning": "smilax/tamus",
            "confidence": 0.75,
            "evidence": "From Track83: f17r + f96v (smilax/tamus) + recipe",
            "category": "source_modifier"
        },
        "checkhey": {
            "meaning": "smilax/tamus",
            "confidence": 0.8,
            "evidence": "From Track83: 3 plant pages + 4 recipes",
            "category": "source_modifier"
        },
        "ckhal": {
            "meaning": "ricinus (castor oil)",
            "confidence": 0.95,
            "evidence": "VALIDATED: f6v + f51r (both ricinus) + f116r recipe",
            "category": "source_modifier"
        },
    }

def update_dictionary():
    data = load_dict()
    entries = data.get("entries", {})
    
    generics = get_generic_terms()
    specifics = get_specific_plants()
    
    changes = {
        "generics_updated": [],
        "specifics_updated": [],
        "specifics_added": [],
        "category_added": []
    }
    
    # Update generic terms
    for word, info in generics.items():
        if word in entries:
            old = entries[word].get("meaning", "")
            entries[word]["meaning"] = info["meaning"]
            entries[word]["notes"] = info["notes"]
            entries[word]["domain"] = "botanical"
            entries[word]["category"] = "generic_botanical"
            entries[word]["confidence"] = 0.5  # lower confidence - generic
            changes["generics_updated"].append({"word": word, "old": old, "new": info["meaning"]})
        else:
            entries[word] = {
                "voynich": word,
                "meaning": info["meaning"],
                "language": "botanical",
                "confidence": 0.5,
                "domain": "botanical",
                "source": "Track98_FinalDict",
                "category": "generic_botanical",
                "notes": info["notes"]
            }
            changes["generics_updated"].append({"word": word, "old": None, "new": info["meaning"]})
    
    # Update specific plant names
    for word, info in specifics.items():
        if word in entries:
            old = entries[word].get("meaning", "")
            entries[word]["meaning"] = info["meaning"]
            entries[word]["confidence"] = info["confidence"]
            entries[word]["domain"] = "botanical"
            entries[word]["category"] = info.get("category", "source_modifier")
            entries[word]["evidence"] = info["evidence"]
            entries[word]["source"] = "Track98_FinalDict"
            changes["specifics_updated"].append({"word": word, "old": old, "new": info["meaning"]})
        else:
            entries[word] = {
                "voynich": word,
                "meaning": info["meaning"],
                "language": "botanical",
                "confidence": info["confidence"],
                "domain": "botanical",
                "source": "Track98_FinalDict",
                "category": info.get("category", "source_modifier"),
                "evidence": info["evidence"]
            }
            changes["specifics_added"].append({"word": word, "meaning": info["meaning"]})
    
    # Update version info
    data["version"] = "6.0"
    data["total_entries"] = len(entries)
    data["entries"] = entries
    
    # Update sources
    if "sources" not in data:
        data["sources"] = {}
    data["sources"]["Track98_FinalDict"] = len(generics) + len(specifics)
    
    return data, changes

def calc_coverage(entries):
    """Recalculate coverage with updated dictionary"""
    import re
    import voynich_data as vd
    
    sections = {
        "herbal": ["herbal_a", "herbal_b"],
        "recipe": ["recipes"],
        "zodiac": ["astronomical"],
        "biological": ["biological"]
    }
    
    results = {"by_section": {}}
    total_words = 0
    total_covered = 0
    
    for section, types in sections.items():
        words = []
        for t in types:
            try:
                section_data = vd.get_section_text(t)
                for folio_data in section_data.values():
                    for line_text in folio_data.values():
                        clean = re.sub(r'[!?<>@$\d]', '', str(line_text))
                        for w in re.split(r'[.\-=,\s]', clean):
                            if w and len(w) > 1:
                                words.append(w)
            except Exception:
                pass
        
        covered = sum(1 for w in words if w in entries)
        results["by_section"][section] = {
            "total": len(words),
            "covered": covered,
            "rate": covered / len(words) if words else 0
        }
        total_words += len(words)
        total_covered += covered
    
    results["overall"] = {
        "total": total_words,
        "covered": total_covered,
        "rate": total_covered / total_words if total_words else 0
    }
    
    return results

def generate_report(changes, old_data, new_data):
    report = ["# Track 98: Final Dictionary Update Report", ""]
    report.append("## Summary")
    report.append(f"- **Dictionary Version**: v5.0 → v6.0")
    report.append(f"- **Total Entries**: {old_data['total_entries']} → {new_data['total_entries']}")
    report.append("")
    
    report.append("## Changes Made")
    report.append("")
    
    report.append("### Generic Terms Updated")
    report.append("These high-frequency modifiers now correctly mean 'herb/plant (generic)':")
    report.append("")
    report.append("| Word | Old Meaning | New Meaning |")
    report.append("|------|-------------|-------------|")
    for c in changes["generics_updated"]:
        old = c["old"] or "(not in dict)"
        report.append(f"| `{c['word']}` | {old} | {c['new']} |")
    report.append("")
    
    report.append("### Specific Plant Names Updated")
    report.append("These page-specific modifiers are actual plant names:")
    report.append("")
    report.append("| Word | Old Meaning | New Meaning |")
    report.append("|------|-------------|-------------|")
    for c in changes["specifics_updated"]:
        report.append(f"| `{c['word']}` | {c['old']} | {c['new']} |")
    report.append("")
    
    report.append("### New Plant Names Added")
    report.append("")
    report.append("| Word | Meaning |")
    report.append("|------|---------|")
    for c in changes["specifics_added"]:
        report.append(f"| `{c['word']}` | {c['meaning']} |")
    report.append("")
    
    report.append("## Category Distribution")
    report.append("")
    entries = new_data["entries"]
    categories = {}
    for e in entries.values():
        cat = e.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1
    
    report.append("| Category | Count |")
    report.append("|----------|-------|")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        report.append(f"| {cat} | {count} |")
    report.append("")
    
    # Coverage analysis
    report.append("## Coverage")
    report.append("")
    cov = new_data.get("coverage", {})
    if "overall" in cov:
        report.append(f"**Overall**: {cov['overall']['rate']*100:.1f}%")
        report.append("")
        if "by_section" in cov:
            report.append("| Section | Coverage |")
            report.append("|---------|----------|")
            for sec, stats in cov["by_section"].items():
                report.append(f"| {sec} | {stats['rate']*100:.1f}% |")
    report.append("")
    
    report.append("## Key Insights")
    report.append("")
    report.append("### The Generic vs Specific Distinction")
    report.append("")
    report.append("**Generic terms** like `chedy`, `chey` appear on 30-65+ pages.")
    report.append("They cannot be plant names - they mean 'herb' or 'plant' generically.")
    report.append("")
    report.append("**Specific terms** like `qotain`, `ckhal` appear on 1-3 plant pages.")
    report.append("These ARE the actual plant names used in recipes.")
    report.append("")
    report.append("### Validated Plant Names (HIGH confidence)")
    report.append("")
    report.append("| Voynich | Plant | Evidence |")
    report.append("|---------|-------|----------|")
    report.append("| `ckhal` | ricinus (castor oil) | f6v + f51r + recipe |")
    report.append("| `qotain` | geranium | f58v + 4 recipes |")
    report.append("| `chodar` | papaver | f89v1 + f90v2 + 4 recipes |")
    report.append("| `alam` | geranium | f58r + f58v + f65r + 5 recipes |")
    report.append("| `otoly` | valerian | f101v + f37r + recipe |")
    report.append("")
    
    return "\n".join(report)

def main():
    print("Track 98: Final Dictionary Update")
    print("=" * 50)
    
    # Load old data
    old_data = load_dict()
    print(f"Loaded v{old_data['version']} with {old_data['total_entries']} entries")
    
    # Update dictionary
    new_data, changes = update_dictionary()
    print(f"\nChanges:")
    print(f"  - Generics updated: {len(changes['generics_updated'])}")
    print(f"  - Specifics updated: {len(changes['specifics_updated'])}")
    print(f"  - Specifics added: {len(changes['specifics_added'])}")
    
    # Recalculate coverage
    print("\nRecalculating coverage...")
    try:
        new_data["coverage"] = calc_coverage(new_data["entries"])
        print(f"  - Overall: {new_data['coverage']['overall']['rate']*100:.1f}%")
    except Exception as e:
        print(f"  - Coverage calculation skipped: {e}")
    
    # Save new dictionary
    out_path = RESULTS / "master_dictionary_v6.json"
    with open(out_path, "w") as f:
        json.dump(new_data, f, indent=2)
    print(f"\nSaved: {out_path}")
    
    # Generate report
    report = generate_report(changes, old_data, new_data)
    report_path = RESULTS / "final_dict_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report: {report_path}")
    
    print("\n✅ Track 98 Complete!")

if __name__ == "__main__":
    main()




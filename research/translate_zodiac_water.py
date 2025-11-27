import json
import os

DICTIONARY_FILE = "results/master_dictionary_v7_1.json"
OUTPUT_TRANSLATION = "results/zodiac_water_translation.md"
OUTPUT_REPORT = "results/zodiac_water_report.md"

# Text Data (Takahashi 'H' transcription)
PISCES_TEXT = {
    "f70v2.1": "okcheo.dar.otey.ykeey.tchy.otsheo.oteotey.shey.sheckh.opcheol.dair.dateey.sal.ody.choteey.choeteedy.oteoteotsho.yteos.alain.sheodaly.ckho.aiin.cholkal.chotear.oteody.cholaiin.oteeeo.al.ol.sheeor.okey.chol.dy.otees.cho.r.ol.ar.otoaiin.oteeody.sos.todaiin.chokain.otalal.otcham",
    "f70v2.R2": "chedaiin.otchy.dair.shchey.daiin.chalaly.oteody.chotol.chedy.oteatey.otcheor.ar.alody.daiir.oteedar.otchy.tchy.dal.al.cheoltey.oteedy.sheeteey.shs.keeol.ykeeos.shey.okear.ar.ar.alos.daim.dy.otar.am.ar.al.otard",
    "f70v2.R1": "otal.dlay.oteoal.dal.aildy.otaiir.ar.oteey.shal.o.qoteeal.ar.al.otaiin.al.teodaiin.oteeo.cthey.otchos.oteos.aiin.diy",
    "Labels": [
        "oty", "oky.ody", "oty.or", "okaly", "otody", "otald", "otal.dar", "okody", "opys.am", "chckhhy", "otaly", "otal.rar", "otal.dy", "okeoly", "oky.dy", "okees", "otalalg", "okasy", "otar"
    ]
}

CANCER_TEXT = {
    "f72r3.R1": "okeey.cheky.oteo.ykeey.chedaiin.okeeol.cheeor.chocthar.ar.oteody.oteedy.okeolaiin.oteey.okarar.dy.sheol.al.alaiiin.okeos.olaiin.okos.okeoar.otes.sar.aiin.chekaithhy.chokees.oteedy.chekar.okar.ch.ches.os.oiin.okeeey.cheey.ches.oteody.cheal.dy.shocthy.choteey.ereoly.oheol.sheey.chorain",
    "f72r3.R2": "otochedy.otal.okoey.sheedy.oteodar.ykeolal.yar.oteos.cheolaiin.ykeeoly.otaiin.shear.oiin.oro.oa.sheokeor.oteody.oekes.otees.oeteos.dotsey.seor.oteol.shol.cheem.okeody.sheol.shey.sheysy.sho.teey.cheor.yoeteey.okeeoy.chy.okeeo.ykoly",
    "f72r3.R3": "oteey.arary.eeer.chem.shses.opcholalaiin.oteeor.am.sheal.otaipchy.oteees.ar.am.olaiin.otedas.olol.choty.oteol.sheshdy.chedy.chedy.dy.shes.eedy.sheol.chy.ckhol",
    "f72r3.R4": "okeos.aiin.olaiin.oraiin.octheol.arl.okeeody.oteos.aiin.koly",
    "Labels": [
         "ykolairol", "olkalaiin", "olalsy", "or.aiin.am", "os.as.sheeen", "otos.aiin", "opoiisooin.al.aes", "ypaiin.aloly", "oteey.daiin", "oeeeodaiin", "ofsholdy", "opoeey.okaiin", "olfsheoral", "or.alkam", "ytairal", "oeees.aiin", "ory", "ochey.fydy", "ofais.o.seesaly", "ykairaiin.oiral", "okalar", "orara", "oeaiin.olaikhy", "oletal", "opalal", "yfary", "osaiisal", "ytoar.shor", "octho", "oral"
    ]
}

def load_dictionary():
    if not os.path.exists(DICTIONARY_FILE):
        print(f"Dictionary not found at {DICTIONARY_FILE}")
        return {}
    with open(DICTIONARY_FILE, 'r') as f:
        return json.load(f).get("entries", {})

def translate_word(word, dictionary):
    clean_word = word.replace("!", "").replace("?", "")
    
    # Direct match
    if clean_word in dictionary:
        return dictionary[clean_word].get("meaning", "??")
    
    # Check suffix/prefix handling if needed (simple version)
    # y- prefix (And)
    if clean_word.startswith("y") and len(clean_word) > 1:
        base = clean_word[1:]
        if base in dictionary:
             return f"And {dictionary[base].get('meaning', '??')}"

    # o- prefix (The/It)
    if clean_word.startswith("o") and len(clean_word) > 1:
         base = clean_word[1:]
         if base in dictionary:
             return f"The {dictionary[base].get('meaning', '??')}"
             
    return "[Unknown]"

def analyze_text(text_data, dictionary, title):
    output_lines = []
    report_lines = []
    
    output_lines.append(f"# Translation: {title}\n")
    report_lines.append(f"## Analysis: {title}\n")
    
    water_hits = 0
    aiin_count = 0
    daiin_count = 0
    
    for section, content in text_data.items():
        output_lines.append(f"### {section}\n")
        
        if isinstance(content, list):
            words = content # Labels are already a list of strings
            original_text = ", ".join(content)
        else:
            words = content.replace(".", " ").split()
            original_text = content
            
        output_lines.append(f"**Original:** `{original_text}`\n")
        
        translation = []
        for word in words:
            # Handle dot separated labels
            subwords = word.split('.')
            sub_trans = []
            for sw in subwords:
                meaning = translate_word(sw, dictionary)
                
                # Keyword Tracking
                if "aiin" in sw:
                    aiin_count += 1
                    meaning = f"**{meaning}**" 
                if "daiin" in sw:
                    daiin_count += 1
                    meaning = f"**{meaning}**"
                if "Water" in meaning or "Spring" in meaning:
                    water_hits += 1
                
                sub_trans.append(f"{sw}({meaning})")
            translation.append(" ".join(sub_trans))
            
        output_lines.append(f"**Translation:** {' '.join(translation)}\n")
    
    report_lines.append(f"- **Water/Spring Hits:** {water_hits}")
    report_lines.append(f"- **'aiin' count:** {aiin_count}")
    report_lines.append(f"- **'daiin' count:** {daiin_count}")
    
    return output_lines, report_lines

def main():
    dictionary = load_dictionary()
    
    pisces_out, pisces_rep = analyze_text(PISCES_TEXT, dictionary, "Pisces (f70v2)")
    cancer_out, cancer_rep = analyze_text(CANCER_TEXT, dictionary, "Cancer (f72r3)")
    
    with open(OUTPUT_TRANSLATION, 'w') as f:
        f.write("\n".join(pisces_out))
        f.write("\n\n")
        f.write("\n".join(cancer_out))
        
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Zodiac Water Section Analysis\n\n")
        f.write("## Hypothesis Check\n")
        f.write("Goal: Confirm if Pisces and Cancer pages contain water-related vocabulary.\n\n")
        f.write("\n".join(pisces_rep))
        f.write("\n\n")
        f.write("\n".join(cancer_rep))
        f.write("\n\n## Conclusion\n")
        
        total_aiin = 0
        total_daiin = 0
        # Simple counting from the text constants directly to avoid scope issues in this quick script
        all_pisces = " ".join([str(v) for v in PISCES_TEXT.values()])
        all_cancer = " ".join([str(v) for v in CANCER_TEXT.values()])
        total_aiin += all_pisces.count("aiin") + all_cancer.count("aiin")
        total_daiin += all_pisces.count("daiin") + all_cancer.count("daiin")
        
        f.write(f"Total `aiin` (Spring/Water) occurrences: {total_aiin}\n")
        f.write(f"Total `daiin` (From Spring/Take water) occurrences: {total_daiin}\n")
        
        if total_aiin > 5 or total_daiin > 2:
             f.write("strong evidence supporting the Water hypothesis for these pages.\n")
        else:
             f.write("Weak lexical evidence for Water hypothesis found so far.\n")

    print(f"Generated {OUTPUT_TRANSLATION}")
    print(f"Generated {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()

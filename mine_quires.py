import json
import re
import urllib.request
from html.parser import HTMLParser

QUIRE_URLS = {
    "q01": "https://voynich.nu/q01/index.html",
    "q02": "https://voynich.nu/q02/index.html",
    "q03": "https://voynich.nu/q03/index.html",
    "q04": "https://voynich.nu/q04/index.html",
    "q05": "https://voynich.nu/q05/index.html",
    "q06": "https://voynich.nu/q06/index.html",
    "q07": "https://voynich.nu/q07/index.html",
    "q08": "https://voynich.nu/q08/index.html",
    "q09": "https://voynich.nu/q09/index.html",
    "q10": "https://voynich.nu/q10/index.html",
    "q11": "https://voynich.nu/q11/index.html",
    "q12": "https://voynich.nu/q12/index.html",
    "q13": "https://voynich.nu/q13/index.html",
    "q14": "https://voynich.nu/q14/index.html",
    "q15": "https://voynich.nu/q15/index.html",
    "q17": "https://voynich.nu/q17/index.html",
    "q19": "https://voynich.nu/q19/index.html",
    "q20": "https://voynich.nu/q20/index.html",
}

QUIRE_SECTIONS = {
    "q01": "herbal_a", "q02": "herbal_a", "q03": "herbal_a", "q04": "herbal_a",
    "q05": "herbal_a", "q06": "herbal_a", "q07": "herbal_a", "q08": "herbal_a",
    "q09": "cosmological", "q10": "zodiac",
    "q11": "zodiac", "q12": "zodiac",
    "q13": "biological",
    "q14": "cosmological", "q15": "pharmaceutical",
    "q17": "herbal_b", "q19": "pharmaceutical",
    "q20": "recipes",
}


class VoynichHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_body = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
    
    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
    
    def handle_data(self, data):
        if self.in_body:
            self.text.append(data.strip())
    
    def get_text(self):
        return " ".join(t for t in self.text if t)


def fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_folios(html, quire_id, default_section):
    parser = VoynichHTMLParser()
    parser.feed(html)
    text = parser.get_text()
    
    folios = []
    folio_pattern = re.compile(r'\bf(\d+[rv]\d?)\b', re.IGNORECASE)
    folio_matches = list(folio_pattern.finditer(text))
    
    seen_folios = set()
    for match in folio_matches:
        folio_name = "f" + match.group(1).lower()
        if folio_name in seen_folios:
            continue
        seen_folios.add(folio_name)
        
        start_pos = match.start()
        end_pos = start_pos + 3000
        context = text[start_pos:end_pos]
        
        folio_data = {
            "folio": folio_name,
            "quire": quire_id,
            "section": default_section,
            "elv_id": None,
            "thp_id": None,
            "description": "",
            "currier_lang": None,
            "lfd_hand": None,
            "visual_elements": [],
        }
        
        currier_match = re.search(r'Currier language:\s*([AB])', context)
        if currier_match:
            folio_data["currier_lang"] = currier_match.group(1)
        
        lfd_match = re.search(r'LFD hand:\s*(\d+)', context)
        if lfd_match:
            folio_data["lfd_hand"] = int(lfd_match.group(1))
        
        elv_match = re.search(r'ELV:\s*([^.;]+)', context)
        if elv_match:
            folio_data["elv_id"] = elv_match.group(1).strip()
        
        thp_match = re.search(r'ThP:\s*([^.;]+)', context)
        if thp_match:
            folio_data["thp_id"] = thp_match.group(1).strip()
        
        illust_match = re.search(r'Illustration\(s\)\s*(.{50,400}?)(?:Text|Herbal drawing)', context, re.DOTALL)
        if illust_match:
            folio_data["description"] = re.sub(r'\s+', ' ', illust_match.group(1)).strip()[:200]
        
        visual = []
        context_lower = context.lower()
        if "root" in context_lower:
            visual.append("roots")
        if "flower" in context_lower:
            visual.append("flowers")
        if "leaf" in context_lower or "leaves" in context_lower:
            visual.append("leaves")
        if "stem" in context_lower:
            visual.append("stem")
        if "pod" in context_lower or "fruit" in context_lower:
            visual.append("fruits")
        if "nymph" in context_lower or "figure" in context_lower or "woman" in context_lower:
            visual.append("figures")
        if "star" in context_lower:
            visual.append("stars")
        if "pool" in context_lower or "bath" in context_lower:
            visual.append("pools")
        if "jar" in context_lower:
            visual.append("jars")
        if "zodiac" in context_lower:
            visual.append("zodiac")
        folio_data["visual_elements"] = visual
        
        if "zodiac" in context_lower or "Aries" in context or "Taurus" in context:
            zodiac_match = re.search(r'(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)', context)
            if zodiac_match:
                folio_data["zodiac_sign"] = zodiac_match.group(1)
                folio_data["section"] = "zodiac"
        
        folios.append(folio_data)
    
    return folios


def mine_quire(quire_id):
    url = QUIRE_URLS.get(quire_id)
    if not url:
        return []
    section = QUIRE_SECTIONS.get(quire_id, "unknown")
    print(f"  Fetching {quire_id} from {url}...")
    html = fetch_url(url)
    folios = extract_folios(html, quire_id, section)
    print(f"  Found {len(folios)} folios in {quire_id}")
    return folios


def mine_quire_set(quire_ids, output_file):
    all_folios = []
    for qid in quire_ids:
        folios = mine_quire(qid)
        all_folios.extend(folios)
    
    result = {
        "quires": quire_ids,
        "folios": all_folios,
        "total_folios": len(all_folios),
        "expert_ids": sum(1 for f in all_folios if f.get("elv_id") or f.get("thp_id")),
    }
    
    with open(output_file, "w") as fp:
        json.dump(result, fp, indent=2)
    print(f"Saved {output_file}")
    return result


def build_plant_lookup(all_folios):
    plant_lookup = {}
    for folio in all_folios:
        elv = folio.get("elv_id")
        thp = folio.get("thp_id")
        if elv:
            for plant in re.split(r'[,;]', elv):
                plant = plant.strip().lower().rstrip('?')
                if plant and len(plant) > 2:
                    if plant not in plant_lookup:
                        plant_lookup[plant] = {"folios": [], "source": "ELV"}
                    plant_lookup[plant]["folios"].append(folio["folio"])
        if thp:
            for plant in re.split(r'[,;]', thp):
                plant = plant.strip().lower().rstrip('?')
                if plant and len(plant) > 2:
                    if plant not in plant_lookup:
                        plant_lookup[plant] = {"folios": [], "source": "ThP"}
                    plant_lookup[plant]["folios"].append(folio["folio"])
    return plant_lookup


def main():
    print("Mining Quires 1-2 (Track 73a)")
    mine_quire_set(["q01", "q02"], "results/quire_01_02_plants.json")
    
    print("\nMining Quires 3-4 (Track 73b)")
    mine_quire_set(["q03", "q04"], "results/quire_03_04_plants.json")
    
    print("\nMining Quires 5-6 (Track 73c)")
    mine_quire_set(["q05", "q06"], "results/quire_05_06_plants.json")
    
    print("\nMining Quires 7-8 (Track 73d)")
    mine_quire_set(["q07", "q08"], "results/quire_07_08_plants.json")
    
    print("\nMining Quires 9-10 (Track 73e)")
    mine_quire_set(["q09", "q10"], "results/quire_09_10_zodiac.json")
    
    print("\nMining Quires 11-12 (Track 73f)")
    mine_quire_set(["q11", "q12"], "results/quire_11_12_zodiac.json")
    
    print("\nMining Quire 13 (Track 73g)")
    mine_quire_set(["q13"], "results/quire_13_biological.json")
    
    print("\nMining Quires 14-15 (Track 73h)")
    mine_quire_set(["q14", "q15"], "results/quire_14_15_cosmo_pharma.json")
    
    print("\nMining Quires 17, 19 (Track 73i)")
    mine_quire_set(["q17", "q19"], "results/quire_17_19_herbal_b.json")
    
    print("\nMining Quire 20 (Track 73j)")
    mine_quire_set(["q20"], "results/quire_20_recipes.json")
    
    print("\n✅ All quire mining complete!")


if __name__ == "__main__":
    main()

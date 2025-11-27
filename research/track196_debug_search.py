import voynich_data
import re
import json

def run_debug_search():
    print("Loading EVA pages...")
    pages = voynich_data.get_eva_pages()
    
    herbal_folios = []
    for i in range(1, 67):
        for side in ['r', 'v']:
            folio = f"f{i}{side}"
            if folio in pages:
                herbal_folios.append(folio)

    print(f"Scanning {len(herbal_folios)} herbal folios for 'ald' and 'choly' anywhere...")
    
    hits = []
    
    for folio in herbal_folios:
        lines = pages[folio]
        sorted_locs = sorted(lines.keys())
        
        for i, loc in enumerate(sorted_locs):
            text = lines[loc]
            # Clean text
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w]
            
            if 'ald' in words:
                hits.append(f"{folio} {loc} (Word {words.index('ald') + 1}/{len(words)}): {text}")
            if 'choly' in words:
                hits.append(f"{folio} {loc} (Word {words.index('choly') + 1}/{len(words)}): {text}")

    print(f"Found {len(hits)} hits.")
    for hit in hits[:20]:
        print(hit)

if __name__ == "__main__":
    run_debug_search()

import voynich_data
import re
import json
from pathlib import Path

def get_first_word(text):
    # Remove garbage characters and split
    text_clean = re.sub(r'[!?<>@$\d]', '', text)
    words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w]
    if words:
        return words[0]
    return None

def run_search():
    print("Loading EVA pages...")
    pages = voynich_data.get_eva_pages()
    
    herbal_folios = []
    # Define Herbal Section f1r-f66r
    # Note: numbering is not continuous, so we check what exists in pages
    for i in range(1, 67):
        for side in ['r', 'v']:
            folio = f"f{i}{side}"
            if folio in pages:
                herbal_folios.append(folio)
            elif f"{i}{side}" in pages: # sometimes keys might be without 'f'? voynich_data adds 'f' in get_folio_text but keys in pages are from file
                # voynich_data.get_eva_pages keys: "folio = loc_clean.split('.')[0]" which usually includes 'f' e.g. 'f1r'
                pass

    print(f"Scanning {len(herbal_folios)} herbal folios...")
    
    targets = {
        "ald": [],
        "choly": []
    }
    
    for folio in herbal_folios:
        lines = pages[folio]
        # Sort lines by location key
        sorted_locs = sorted(lines.keys())
        
        if not sorted_locs:
            continue
            
        # Check first word of the page (Label?)
        first_loc = sorted_locs[0]
        first_line_text = lines[first_loc]
        first_word = get_first_word(first_line_text)
        
        # Check for 'ald'
        if first_word == 'ald':
            targets['ald'].append({
                'folio': folio,
                'loc': first_loc,
                'type': 'Page Start',
                'text': first_line_text
            })
        
        # Check for 'choly'
        if first_word == 'choly':
            targets['choly'].append({
                'folio': folio,
                'loc': first_loc,
                'type': 'Page Start',
                'text': first_line_text
            })
            
        # Also check if they appear as the *only* word in a line (Label)
        # or start of a paragraph (if logic differs from page start)
        for loc in sorted_locs:
            text = lines[loc]
            f_word = get_first_word(text)
            
            # If we already found it at page start, don't duplicate unless it's distinct
            # But simple list is fine for now.
            
            if f_word == 'ald':
                # check if it's a paragraph start or isolated label
                is_para = '.P.' in loc
                is_short = len(text.strip().split()) == 1
                
                if (is_para or is_short) and loc != first_loc:
                     targets['ald'].append({
                        'folio': folio,
                        'loc': loc,
                        'type': 'Paragraph/Label',
                        'text': text
                    })

            if f_word == 'choly':
                 is_para = '.P.' in loc
                 is_short = len(text.strip().split()) == 1
                 
                 if (is_para or is_short) and loc != first_loc:
                     targets['choly'].append({
                        'folio': folio,
                        'loc': loc,
                        'type': 'Paragraph/Label',
                        'text': text
                    })

    print("\nResults:")
    print(json.dumps(targets, indent=2))
    
    # Also save to a file for the next step
    with open('results/track196_search_results.json', 'w') as f:
        json.dump(targets, f, indent=2)

if __name__ == "__main__":
    run_search()

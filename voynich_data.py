"""
Master data access module for Voynich manuscript transcriptions.
Provides single source of truth for all analysis scripts.
"""

import re
from pathlib import Path
from functools import lru_cache

EVA_FILE = Path("data/eva_ivtff.txt")
CLASTON_FILE = Path("voynich_raw.txt")

CLASTON_TO_EVA_CHARS = {
    'o': 'o', 'a': 'a', 's': 's', 'f': 'f', 'i': 'i', 'n': 'n',
    '9': 'y', '8': 'd', 'h': 'k', 'k': 't', 'e': 'l', 'y': 'r',
    'c': 'e', '4': 'q', 'g': 'p', 'p': 'm'
}

CLASTON_TO_EVA_DIGRAPHS = {
    'cc89': 'eedy', 'c89': 'edy', 'cc9': 'eey', 'c9': 'ey', '89': 'dy',
    'am': 'aiin', 'aim': 'aiiin', 'an': 'ain', 'M': 'iin',
    'oe': 'ol', 'oy': 'or', 'ae': 'al', 'ay': 'ar', 'iy': 'ir',
    'K': 'ckh', 'H': 'ckh', '1h': 'cth', '1g': 'cph', 'fh': 'cfh',
    '1': 'ch', '2': 'sh'
}

EVA_TO_CLASTON_CHARS = {v: k for k, v in CLASTON_TO_EVA_CHARS.items()}
EVA_TO_CLASTON_DIGRAPHS = {v: k for k, v in CLASTON_TO_EVA_DIGRAPHS.items()}

FOLIO_SECTIONS = {
    'herbal_a': [f'f{i}r' for i in range(1, 26)] + [f'f{i}v' for i in range(1, 26)],
    'herbal_b': [f'f{i}r' for i in range(26, 57)] + [f'f{i}v' for i in range(26, 57)],
    'astronomical': [f'f{i}r' for i in range(67, 74)] + [f'f{i}v' for i in range(67, 74)],
    'biological': [f'f{i}r' for i in range(75, 85)] + [f'f{i}v' for i in range(75, 85)],
    'pharmaceutical': [f'f{i}r' for i in range(88, 103)] + [f'f{i}v' for i in range(88, 103)],
    'recipes': [f'f{i}r' for i in range(103, 117)] + [f'f{i}v' for i in range(103, 117)],
}


@lru_cache(maxsize=1)
def _load_eva_raw():
    if not EVA_FILE.exists():
        raise FileNotFoundError(f"EVA file not found: {EVA_FILE}")
    return EVA_FILE.read_text(encoding='utf-8')


@lru_cache(maxsize=1)
def _load_claston_raw():
    if not CLASTON_FILE.exists():
        raise FileNotFoundError(f"Claston file not found: {CLASTON_FILE}")
    return CLASTON_FILE.read_text(encoding='utf-8')


def get_eva_pages(transcriber='H'):
    """
    Get all pages from EVA transcription.
    
    Args:
        transcriber: Which transcriber version to use (H=Takahashi recommended)
    
    Returns:
        dict: {folio: {line_loc: text, ...}, ...}
    """
    pages = {}
    raw = _load_eva_raw()
    
    for line in raw.split('\n'):
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


def get_claston_pages():
    """
    Get all pages from Claston transcription.
    
    Returns:
        dict: {folio: {line_loc: text, ...}, ...}
    """
    pages = {}
    raw = _load_claston_raw()
    
    for line in raw.split('\n'):
        m = re.match(r'<(\w+\.\d+)>(.+)', line.strip())
        if m:
            loc, text = m.groups()
            folio = loc.split('.')[0]
            if folio not in pages:
                pages[folio] = {}
            pages[folio][loc] = text
    
    return pages


def get_folio_text(folio, system='EVA', transcriber='H'):
    """
    Get all text from a specific folio.
    
    Args:
        folio: Folio identifier (e.g., 'f1r', '1r')
        system: 'EVA' or 'Claston'
        transcriber: For EVA, which transcriber (default 'H')
    
    Returns:
        dict: {line_loc: text, ...}
    """
    folio_clean = folio.lower().lstrip('f')
    
    if system.upper() == 'EVA':
        pages = get_eva_pages(transcriber)
        eva_folio = 'f' + folio_clean
        return pages.get(eva_folio, {})
    else:
        pages = get_claston_pages()
        return pages.get(folio_clean, {})


def get_all_words(system='EVA', transcriber='H'):
    """
    Get all unique words from the manuscript.
    
    Args:
        system: 'EVA' or 'Claston'
        transcriber: For EVA, which transcriber
    
    Returns:
        list: All unique words
    """
    if system.upper() == 'EVA':
        pages = get_eva_pages(transcriber)
    else:
        pages = get_claston_pages()
    
    words = set()
    for page in pages.values():
        for text in page.values():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            for w in re.split(r'[.\-=,\s]', text_clean):
                if w and len(w) > 1:
                    words.add(w)
    
    return list(words)


def get_word_frequencies(system='EVA', transcriber='H'):
    """
    Get word frequency counts.
    
    Returns:
        dict: {word: count, ...}
    """
    if system.upper() == 'EVA':
        pages = get_eva_pages(transcriber)
    else:
        pages = get_claston_pages()
    
    freq = {}
    for page in pages.values():
        for text in page.values():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            for w in re.split(r'[.\-=,\s]', text_clean):
                if w and len(w) > 1:
                    freq[w] = freq.get(w, 0) + 1
    
    return dict(sorted(freq.items(), key=lambda x: -x[1]))


def get_section_text(section, system='EVA', transcriber='H'):
    """
    Get all text from a manuscript section.
    
    Args:
        section: One of 'herbal_a', 'herbal_b', 'astronomical', 
                 'biological', 'pharmaceutical', 'recipes'
        system: 'EVA' or 'Claston'
        transcriber: For EVA, which transcriber
    
    Returns:
        dict: {folio: {line_loc: text}, ...}
    """
    if section not in FOLIO_SECTIONS:
        raise ValueError(f"Unknown section: {section}")
    
    result = {}
    for folio in FOLIO_SECTIONS[section]:
        folio_text = get_folio_text(folio, system, transcriber)
        if folio_text:
            result[folio] = folio_text
    
    return result


def convert_claston_to_eva(word):
    """
    Convert a Claston word to EVA notation.
    Note: This is approximate due to ambiguous mappings.
    """
    result = list(word)
    out = []
    i = 0
    
    sorted_digraphs = sorted(CLASTON_TO_EVA_DIGRAPHS.items(),
                             key=lambda x: len(x[0]), reverse=True)
    
    while i < len(result):
        matched = False
        for claston, eva in sorted_digraphs:
            if word[i:i+len(claston)] == claston:
                out.append(eva)
                i += len(claston)
                matched = True
                break
        
        if not matched:
            char = result[i]
            out.append(CLASTON_TO_EVA_CHARS.get(char, char))
            i += 1
    
    return ''.join(out)


def convert_eva_to_claston(word):
    """
    Convert an EVA word to Claston notation.
    Note: This is approximate due to ambiguous mappings.
    """
    out = []
    i = 0
    
    sorted_digraphs = sorted(EVA_TO_CLASTON_DIGRAPHS.items(),
                             key=lambda x: len(x[0]), reverse=True)
    
    while i < len(word):
        matched = False
        for eva, claston in sorted_digraphs:
            if word[i:i+len(eva)] == eva:
                out.append(claston)
                i += len(eva)
                matched = True
                break
        
        if not matched:
            char = word[i]
            out.append(EVA_TO_CLASTON_CHARS.get(char, char))
            i += 1
    
    return ''.join(out)


def get_transcribers():
    """
    List available transcribers in the EVA file.
    
    Returns:
        dict: {code: description}
    """
    return {
        'H': 'Takeshi Takahashi (complete, recommended)',
        'C': 'Prescott Currier',
        'F': 'First Study Group (Friedman)',
        'N': 'Gabriel Landini',
        'U': 'Jorge Stolfi',
        'm': 'Majority consensus',
        'c': 'Complete consensus'
    }


if __name__ == "__main__":
    print("Voynich Data Module - Quick Test")
    print("=" * 50)
    
    eva_pages = get_eva_pages()
    print(f"EVA pages loaded: {len(eva_pages)}")
    
    claston_pages = get_claston_pages()
    print(f"Claston pages loaded: {len(claston_pages)}")
    
    f1r_eva = get_folio_text('f1r', 'EVA')
    f1r_claston = get_folio_text('f1r', 'Claston')
    print(f"\nf1r EVA lines: {len(f1r_eva)}")
    print(f"f1r Claston lines: {len(f1r_claston)}")
    
    if f1r_eva:
        first_line = list(f1r_eva.values())[0]
        print(f"\nFirst EVA line: {first_line[:50]}...")
    
    test_word = "fa19s"
    converted = convert_claston_to_eva(test_word)
    print(f"\nConversion test: '{test_word}' -> '{converted}'")
    
    print("\nAvailable transcribers:")
    for code, desc in get_transcribers().items():
        print(f"  {code}: {desc}")

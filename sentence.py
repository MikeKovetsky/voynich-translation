import json
import re
from collections import Counter, defaultdict

EVA_FILE = "data/eva_ivtff.txt"
OUTPUT_JSON = "results/sentence_structure.json"
OUTPUT_REPORT = "results/sentence_structure_report.md"

PHONETIC_MAP = {
    "o": "a", "k": "n", "a": "e", "e": "i", "y": "r", "d": "d",
    "ch": "t", "sh": "b", "q": "qu", "s": "x", "l": "l", "r": "s",
    "t": "c", "p": "p", "f": "f", "n": "n", "i": "i", "c": "h",
    "h": "r", "m": "m", "g": "g", "cth": "ct", "cph": "cp", "cfh": "cf"
}

LATIN_BOTANICAL = [
    'radix', 'herba', 'flos', 'folium', 'fructus', 'semen', 'cortex', 'succus',
    'caulis', 'ramus', 'spina', 'bacca', 'arbor', 'aqua', 'oleum', 'vinum'
]

LATIN_PREPOSITIONS = ['in', 'ad', 'pro', 'contra', 'cum', 'de', 'per', 'sub', 'ex', 'ab']
LATIN_VERBS = ['est', 'sunt', 'habet', 'facit', 'curat', 'sanat', 'valet', 'prodest']

SENTENCE_STARTERS = ['s', 'd', 'o', 'q', 'ch', 'f', 'y', 'k', 't', 'p', 'cth']
LIKELY_PREPOSITIONS = ['ol', 'or', 'ar', 'al', 'ok', 'ot', 'od']


def load_eva():
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def parse_eva_lines(text, transcriber='H'):
    lines = []
    pattern = re.compile(rf'<f(\d+)([rv])\.(\d+),([=@+\*])P([^;]*);{transcriber}>\s*(.+)')
    
    for match in pattern.finditer(text):
        folio_num = int(match.group(1))
        page_side = match.group(2)
        line_num = int(match.group(3))
        para_marker = match.group(4)
        para_info = match.group(5)
        content = match.group(6).strip()
        
        if folio_num > 57:
            continue
            
        folio = f"f{folio_num}{page_side}"
        
        is_para_start = para_marker in ['@', '=', '*']
        is_title = 't' in para_info.lower()
        
        content = content.rstrip('-=')
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'[!\?\*]', '', content)
        
        words = [w.strip() for w in re.split(r'[.,]', content) if w.strip()]
        words = [re.sub(r'[^a-zA-Z]', '', w) for w in words if re.sub(r'[^a-zA-Z]', '', w)]
        
        if words:
            lines.append({
                'folio': folio,
                'line': line_num,
                'words': words,
                'raw': content,
                'para_start': is_para_start,
                'is_title': is_title,
                'para_marker': para_marker
            })
    
    return lines


def decode_eva_word(word):
    result = word.lower()
    for src, dst in [('cth', 'ct'), ('cph', 'cp'), ('cfh', 'cf'), ('sh', 'b'), ('ch', 't')]:
        result = result.replace(src, dst)
    
    mapping = {'o': 'a', 'a': 'e', 'e': 'i', 'y': 'r', 'k': 'n', 'l': 'l', 
               'd': 'd', 'q': 'qu', 's': 'x', 't': 'c', 'p': 'p', 'f': 'f',
               'n': 'n', 'i': 'i', 'c': 'h', 'h': 'r', 'm': 'm', 'g': 'g', 'r': 's'}
    
    out = []
    for c in result:
        out.append(mapping.get(c, c))
    return ''.join(out)


def analyze_line_stats(lines):
    words_per_line = [len(ln['words']) for ln in lines]
    
    initial_words = Counter()
    final_words = Counter()
    initial_chars = Counter()
    final_chars = Counter()
    
    for ln in lines:
        if ln['words']:
            first = ln['words'][0]
            last = ln['words'][-1]
            initial_words[first] += 1
            final_words[last] += 1
            if first:
                initial_chars[first[0]] += 1
            if last:
                final_chars[last[-1]] += 1
    
    return {
        'total_lines': len(lines),
        'total_words': sum(words_per_line),
        'avg_words_per_line': round(sum(words_per_line) / len(lines), 2) if lines else 0,
        'min_words': min(words_per_line) if words_per_line else 0,
        'max_words': max(words_per_line) if words_per_line else 0,
        'line_initial_words': initial_words.most_common(30),
        'line_final_words': final_words.most_common(30),
        'line_initial_chars': initial_chars.most_common(15),
        'line_final_chars': final_chars.most_common(15)
    }


def find_paragraph_breaks(lines):
    paragraphs = []
    current_para = []
    
    for ln in lines:
        if ln['para_start'] and current_para:
            paragraphs.append(current_para)
            current_para = []
        current_para.append(ln)
    
    if current_para:
        paragraphs.append(current_para)
    
    para_initial_words = Counter()
    para_final_words = Counter()
    title_words = Counter()
    para_lengths = []
    
    for para in paragraphs:
        para_lengths.append(len(para))
        if para:
            first_ln = para[0]
            last_ln = para[-1]
            if first_ln['words']:
                para_initial_words[first_ln['words'][0]] += 1
            if last_ln['words']:
                para_final_words[last_ln['words'][-1]] += 1
            if first_ln['is_title'] and first_ln['words']:
                title_words[' '.join(first_ln['words'][:3])] += 1
    
    return {
        'total_paragraphs': len(paragraphs),
        'avg_lines_per_para': round(sum(para_lengths) / len(para_lengths), 2) if para_lengths else 0,
        'paragraph_initial_words': para_initial_words.most_common(20),
        'paragraph_final_words': para_final_words.most_common(20),
        'title_patterns': title_words.most_common(20),
        'paragraphs': paragraphs
    }


def find_punctuation_candidates(lines):
    rare_patterns = Counter()
    double_spaces = 0
    single_char_words = Counter()
    
    for ln in lines:
        if '  ' in ln['raw']:
            double_spaces += 1
        
        for w in ln['words']:
            if len(w) == 1:
                single_char_words[w] += 1
            
            if re.search(r'([a-z])\1{2,}', w):
                rare_patterns[w] += 1
    
    word_endings = Counter()
    for ln in lines:
        for w in ln['words']:
            if len(w) >= 2:
                word_endings[w[-2:]] += 1
    
    return {
        'double_space_lines': double_spaces,
        'single_char_words': single_char_words.most_common(20),
        'rare_repeated_patterns': rare_patterns.most_common(20),
        'common_word_endings': word_endings.most_common(30)
    }


def split_into_sentences(words, boundary_words):
    sentences = []
    current = []
    
    for w in words:
        current.append(w)
        if w in boundary_words and len(current) >= 4:
            sentences.append(current)
            current = []
    
    if current:
        sentences.append(current)
    
    return sentences


def analyze_word_order(lines, paragraphs):
    all_words = []
    for para in paragraphs:
        for ln in para:
            all_words.extend(ln['words'])
    
    word_freq = Counter(all_words)
    common_finals = ['daiin', 'dy', 'dal', 'dam', 'dar', 'dan', 'dain', 'aiin', 'y', 'ol', 'or', 'ar', 'am']
    boundary_words = set(w for w in common_finals if word_freq.get(w, 0) > 50)
    
    sentences = []
    
    for para in paragraphs:
        para_words = []
        for ln in para:
            para_words.extend(ln['words'])
        
        if len(para_words) <= 15:
            sentences.append(para_words)
        else:
            sents = split_into_sentences(para_words, boundary_words)
            sentences.extend(sents)
    
    sent_lengths = [len(s) for s in sentences]
    
    preposition_positions = []
    first_word_patterns = Counter()
    last_word_patterns = Counter()
    second_word_patterns = Counter()
    penult_word_patterns = Counter()
    
    for sent in sentences:
        if len(sent) >= 2:
            first_word_patterns[sent[0]] += 1
            last_word_patterns[sent[-1]] += 1
            second_word_patterns[sent[1]] += 1
            penult_word_patterns[sent[-2]] += 1
        
        for i, w in enumerate(sent):
            if w in LIKELY_PREPOSITIONS:
                rel_pos = i / len(sent) if sent else 0
                preposition_positions.append(rel_pos)
    
    avg_prep_pos = sum(preposition_positions) / len(preposition_positions) if preposition_positions else 0
    
    word_lengths_by_position = defaultdict(list)
    for sent in sentences:
        for i, w in enumerate(sent):
            rel_pos = i / len(sent) if sent else 0
            if rel_pos < 0.2:
                word_lengths_by_position['start'].append(len(w))
            elif rel_pos > 0.8:
                word_lengths_by_position['end'].append(len(w))
            else:
                word_lengths_by_position['middle'].append(len(w))
    
    avg_lens = {}
    for pos, lens in word_lengths_by_position.items():
        avg_lens[pos] = round(sum(lens) / len(lens), 2) if lens else 0
    
    return {
        'total_sentences': len(sentences),
        'avg_sentence_length': round(sum(len(s) for s in sentences) / len(sentences), 2) if sentences else 0,
        'min_sentence_length': min(sent_lengths) if sent_lengths else 0,
        'max_sentence_length': max(sent_lengths) if sent_lengths else 0,
        'boundary_words_used': list(boundary_words),
        'sentence_initial_words': first_word_patterns.most_common(30),
        'sentence_final_words': last_word_patterns.most_common(30),
        'second_position_words': second_word_patterns.most_common(20),
        'penultimate_words': penult_word_patterns.most_common(20),
        'avg_preposition_position': round(avg_prep_pos, 3),
        'avg_word_length_by_position': avg_lens,
        'sentences': sentences
    }


def detect_sentence_boundaries(lines, word_order):
    potential_starters = set()
    potential_enders = set()
    
    for w, c in word_order['sentence_initial_words'][:15]:
        if c >= 5:
            potential_starters.add(w)
    
    for w, c in word_order['sentence_final_words'][:15]:
        if c >= 5:
            potential_enders.add(w)
    
    boundaries = []
    for i, ln in enumerate(lines):
        markers = []
        
        if ln['para_start']:
            markers.append('paragraph_start')
        
        if ln['is_title']:
            markers.append('title')
        
        if ln['words']:
            if ln['words'][0] in potential_starters:
                markers.append('potential_start')
            if ln['words'][-1] in potential_enders:
                markers.append('potential_end')
        
        if markers:
            boundaries.append({
                'folio': ln['folio'],
                'line': ln['line'],
                'markers': markers,
                'words': ln['words']
            })
    
    return {
        'potential_starters': list(potential_starters),
        'potential_enders': list(potential_enders),
        'boundary_count': len(boundaries),
        'sample_boundaries': boundaries[:50]
    }


def extract_sample_sentences(word_order, n=20):
    samples = []
    sentences = word_order['sentences']
    
    sorted_sents = sorted(sentences, key=len)
    mid_idx = len(sorted_sents) // 2
    selected = sorted_sents[max(0, mid_idx-n//2):mid_idx+n//2+1][:n]
    
    for sent in selected:
        decoded = [decode_eva_word(w) for w in sent]
        
        latin_matches = []
        for d in decoded:
            for lat in LATIN_BOTANICAL + LATIN_PREPOSITIONS + LATIN_VERBS:
                if d.startswith(lat[:3]) or lat.startswith(d[:3]):
                    latin_matches.append(lat)
                    break
        
        coherence = len(latin_matches) / len(decoded) if decoded else 0
        
        samples.append({
            'voynich': ' '.join(sent),
            'decoded': ' '.join(decoded),
            'word_count': len(sent),
            'latin_matches': latin_matches[:5],
            'coherence_score': round(coherence, 3)
        })
    
    samples.sort(key=lambda x: x['coherence_score'], reverse=True)
    return samples


def analyze_medieval_latin_patterns(word_order):
    sentences = word_order['sentences']
    
    sov_score = 0
    svo_score = 0
    
    for sent in sentences:
        if len(sent) < 3:
            continue
        
        decoded = [decode_eva_word(w) for w in sent]
        
        verb_like = []
        for i, d in enumerate(decoded):
            if d.endswith('t') or d.endswith('nt') or d.endswith('r'):
                verb_like.append(i)
        
        if verb_like:
            avg_verb_pos = sum(verb_like) / len(verb_like) / len(decoded)
            if avg_verb_pos > 0.7:
                sov_score += 1
            elif avg_verb_pos < 0.4:
                svo_score += 1
    
    adj_before_noun = 0
    adj_after_noun = 0
    
    for sent in sentences:
        decoded = [decode_eva_word(w) for w in sent]
        for i, d in enumerate(decoded[:-1]):
            if d.endswith('us') or d.endswith('a') or d.endswith('um'):
                next_d = decoded[i + 1]
                if next_d.endswith('is') or next_d.endswith('ix') or next_d.endswith('em'):
                    adj_before_noun += 1
                elif next_d.endswith('us') or next_d.endswith('a'):
                    adj_after_noun += 1
    
    return {
        'sov_indicators': sov_score,
        'svo_indicators': svo_score,
        'likely_word_order': 'SOV' if sov_score > svo_score else 'SVO',
        'adjective_before_noun': adj_before_noun,
        'adjective_after_noun': adj_after_noun,
        'adj_position': 'before' if adj_before_noun > adj_after_noun else 'after'
    }


def generate_report(results):
    lines = ["# Sentence Structure Analysis Report\n"]
    
    lines.append("## Line Statistics\n")
    ls = results['line_statistics']
    lines.append(f"- **Total lines analyzed**: {ls['total_lines']}")
    lines.append(f"- **Total words**: {ls['total_words']}")
    lines.append(f"- **Average words per line**: {ls['avg_words_per_line']}")
    lines.append(f"- **Range**: {ls['min_words']} - {ls['max_words']} words\n")
    
    lines.append("### Most Common Line-Initial Words\n")
    for w, c in ls['line_initial_words'][:15]:
        decoded = decode_eva_word(w)
        lines.append(f"- `{w}` ({decoded}): {c} occurrences")
    
    lines.append("\n### Most Common Line-Final Words\n")
    for w, c in ls['line_final_words'][:15]:
        decoded = decode_eva_word(w)
        lines.append(f"- `{w}` ({decoded}): {c} occurrences")
    
    lines.append("\n## Paragraph Analysis\n")
    pa = results['paragraph_analysis']
    lines.append(f"- **Total paragraphs**: {pa['total_paragraphs']}")
    lines.append(f"- **Average lines per paragraph**: {pa['avg_lines_per_para']}\n")
    
    lines.append("### Paragraph-Initial Words (sentence starters)\n")
    for w, c in pa.get('paragraph_initial_words', [])[:15]:
        decoded = decode_eva_word(w)
        lines.append(f"- `{w}` ({decoded}): {c} occurrences")
    
    lines.append("\n### Paragraph-Final Words (sentence enders)\n")
    for w, c in pa.get('paragraph_final_words', [])[:15]:
        decoded = decode_eva_word(w)
        lines.append(f"- `{w}` ({decoded}): {c} occurrences")
    
    if pa.get('title_patterns'):
        lines.append("\n### Title Patterns\n")
        for w, c in pa['title_patterns'][:10]:
            lines.append(f"- `{w}`: {c} occurrences")
    
    lines.append("\n## Punctuation Candidates\n")
    pc = results['punctuation_candidates']
    lines.append(f"- **Lines with double spaces**: {pc['double_space_lines']}")
    
    lines.append("\n### Single-Character Words (possible function words)\n")
    for w, c in pc['single_char_words'][:10]:
        lines.append(f"- `{w}`: {c} occurrences")
    
    lines.append("\n### Common Word Endings (potential case markers)\n")
    for e, c in pc['common_word_endings'][:15]:
        lines.append(f"- `-{e}`: {c} occurrences")
    
    lines.append("\n## Word Order Analysis\n")
    wo = results['word_order_analysis']
    lines.append(f"- **Total sentences detected**: {wo['total_sentences']}")
    lines.append(f"- **Average sentence length**: {wo['avg_sentence_length']} words")
    lines.append(f"- **Sentence length range**: {wo.get('min_sentence_length', 0)} - {wo.get('max_sentence_length', 0)} words")
    lines.append(f"- **Average preposition position**: {wo['avg_preposition_position']:.1%} into sentence")
    
    if wo.get('boundary_words_used'):
        lines.append(f"- **Boundary words used**: {', '.join(wo['boundary_words_used'])}\n")
    else:
        lines.append("")
    
    lines.append("### Word Length by Position\n")
    for pos, avg in wo['avg_word_length_by_position'].items():
        lines.append(f"- **{pos.capitalize()}**: {avg} chars average")
    
    lines.append("\n### Sentence-Initial Words\n")
    for w, c in wo['sentence_initial_words'][:15]:
        decoded = decode_eva_word(w)
        lines.append(f"- `{w}` ({decoded}): {c} times")
    
    lines.append("\n### Sentence-Final Words\n")
    for w, c in wo['sentence_final_words'][:15]:
        decoded = decode_eva_word(w)
        lines.append(f"- `{w}` ({decoded}): {c} times")
    
    lines.append("\n## Latin Syntax Analysis\n")
    ml = results['medieval_latin_patterns']
    lines.append(f"- **Likely word order**: {ml['likely_word_order']}")
    lines.append(f"- **SOV indicators**: {ml['sov_indicators']}")
    lines.append(f"- **SVO indicators**: {ml['svo_indicators']}")
    lines.append(f"- **Adjective position**: {ml['adj_position']} noun")
    
    lines.append("\n## Sentence Boundaries\n")
    sb = results['sentence_boundaries']
    lines.append(f"- **Potential sentence starters**: {', '.join(sb['potential_starters'][:10])}")
    lines.append(f"- **Potential sentence enders**: {', '.join(sb['potential_enders'][:10])}")
    
    lines.append("\n## Sample Sentences\n")
    lines.append("Top 20 sentences ranked by coherence score:\n")
    
    for i, s in enumerate(results['sample_sentences'][:20], 1):
        lines.append(f"### Sentence {i} (coherence: {s['coherence_score']:.1%})")
        lines.append(f"- **Voynich**: `{s['voynich']}`")
        lines.append(f"- **Decoded**: `{s['decoded']}`")
        lines.append(f"- **Latin matches**: {', '.join(s['latin_matches']) if s['latin_matches'] else 'none'}\n")
    
    lines.append("\n## Conclusions\n")
    lines.append("Based on analysis:")
    lines.append(f"1. Average sentence length is ~{wo['avg_sentence_length']:.0f} words")
    lines.append(f"2. Word order appears to be **{ml['likely_word_order']}** (verb typically {'final' if ml['likely_word_order'] == 'SOV' else 'medial'})")
    lines.append(f"3. Adjectives tend to come **{ml['adj_position']}** their nouns")
    lines.append(f"4. Paragraph breaks (=) serve as primary sentence delimiters")
    lines.append(f"5. Common sentence starters suggest topic-focused structure")
    
    return '\n'.join(lines)


def main():
    print("Loading EVA transcription...")
    eva_text = load_eva()
    
    print("Parsing botanical section lines...")
    lines = parse_eva_lines(eva_text, transcriber='H')
    print(f"  Found {len(lines)} lines")
    
    print("Analyzing line statistics...")
    line_stats = analyze_line_stats(lines)
    
    print("Finding paragraph breaks...")
    para_analysis = find_paragraph_breaks(lines)
    
    print("Finding punctuation candidates...")
    punct_candidates = find_punctuation_candidates(lines)
    
    print("Analyzing word order...")
    word_order = analyze_word_order(lines, para_analysis['paragraphs'])
    
    print("Detecting sentence boundaries...")
    boundaries = detect_sentence_boundaries(lines, word_order)
    
    print("Extracting sample sentences...")
    samples = extract_sample_sentences(word_order, n=30)
    
    print("Analyzing medieval Latin patterns...")
    latin_patterns = analyze_medieval_latin_patterns(word_order)
    
    results = {
        'line_statistics': line_stats,
        'paragraph_analysis': {k: v for k, v in para_analysis.items() if k != 'paragraphs'},
        'punctuation_candidates': punct_candidates,
        'word_order_analysis': {
            k: v for k, v in word_order.items() if k != 'sentences'
        },
        'sentence_boundaries': boundaries,
        'sample_sentences': samples,
        'medieval_latin_patterns': latin_patterns
    }
    
    print(f"Saving results to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Generating report {OUTPUT_REPORT}...")
    report = generate_report(results)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n=== SUMMARY ===")
    print(f"Lines analyzed: {line_stats['total_lines']}")
    print(f"Total words: {line_stats['total_words']}")
    print(f"Paragraphs found: {para_analysis['total_paragraphs']}")
    print(f"Avg sentence length: {word_order['avg_sentence_length']} words")
    print(f"Likely word order: {latin_patterns['likely_word_order']}")
    print(f"Sample sentences extracted: {len(samples)}")


if __name__ == '__main__':
    main()

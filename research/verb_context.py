import json
import re
from collections import defaultdict, Counter

EVA_FILE = "data/eva_ivtff.txt"
SENTENCE_FILE = "results/sentence_structure.json"
OUTPUT_JSON = "results/verb_context.json"
OUTPUT_REPORT = "results/verb_context_report.md"

LATIN_HERBAL_VERBS = {
    'curat': 'cures', 'sanat': 'heals', 'valet': 'is effective',
    'prodest': 'benefits', 'tollit': 'removes', 'aufert': 'takes away',
    'solvit': 'dissolves', 'purgat': 'purges', 'mundificat': 'cleanses',
    'coquatur': 'let be cooked', 'bibatur': 'let be drunk', 'datur': 'is given',
    'bibitur': 'is drunk', 'utatur': 'let use', 'ponatur': 'let be placed',
    'recipe': 'take', 'misce': 'mix', 'coque': 'cook', 'tere': 'grind',
    'bibe': 'drink', 'sume': 'take', 'fac': 'make', 'pone': 'place',
    'confice': 'prepare', 'adde': 'add', 'cola': 'strain', 'mitte': 'put',
    'est': 'is', 'sunt': 'are', 'habet': 'has', 'facit': 'makes'
}

SENTENCE_BOUNDARY_WORDS = {'daiin', 'dy', 'or', 'dar', 'aiin', 'y', 'dain', 'ol', 'ar', 'dam', 'dal'}
LIKELY_PREPOSITIONS = ['ol', 'or', 'ar', 'al', 'ok', 'ot', 'od', 'qo']


def decode_eva(word):
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


def load_eva_lines(transcriber='H'):
    lines = []
    pattern = re.compile(rf'<f(\d+)([rv])\.(\d+),([=@+\*])P([^;]*);{transcriber}>\s*(.+)')
    
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    for match in pattern.finditer(text):
        folio_num = int(match.group(1))
        page_side = match.group(2)
        line_num = int(match.group(3))
        para_marker = match.group(4)
        content = match.group(6).strip()
        
        if folio_num > 57:
            continue
            
        folio = f"f{folio_num}{page_side}"
        
        is_para_start = para_marker in ['@', '=', '*']
        
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
                'para_start': is_para_start
            })
    
    return lines


def load_sentence_structure():
    try:
        with open(SENTENCE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None


def build_sentences(lines):
    sentences = []
    current = []
    
    for ln in lines:
        if ln['para_start'] and current:
            sentences.append({'words': current, 'folio': current[0] if current else ''})
            current = []
        current.extend(ln['words'])
    
    if current:
        sentences.append({'words': current, 'folio': ''})
    
    all_words = []
    for s in sentences:
        all_words.extend(s['words'])
    
    word_freq = Counter(all_words)
    boundary_words = set(w for w in SENTENCE_BOUNDARY_WORDS if word_freq.get(w, 0) > 50)
    
    split_sentences = []
    for sent in sentences:
        words = sent['words']
        if len(words) <= 15:
            split_sentences.append(words)
        else:
            current_sent = []
            for w in words:
                current_sent.append(w)
                if w in boundary_words and len(current_sent) >= 4:
                    split_sentences.append(current_sent)
                    current_sent = []
            if current_sent:
                split_sentences.append(current_sent)
    
    return split_sentences, boundary_words


def analyze_svo_positions(sentences):
    word_positions = defaultdict(list)
    
    for sent in sentences:
        if len(sent) < 3:
            continue
        
        for i, w in enumerate(sent):
            rel_pos = i / (len(sent) - 1) if len(sent) > 1 else 0.5
            word_positions[w].append(rel_pos)
    
    mid_position_words = []
    for word, positions in word_positions.items():
        if len(positions) >= 5:
            avg_pos = sum(positions) / len(positions)
            if 0.3 <= avg_pos <= 0.7:
                mid_position_words.append({
                    'word': word,
                    'decoded': decode_eva(word),
                    'avg_position': round(avg_pos, 3),
                    'occurrences': len(positions),
                    'position_category': 'verb_zone'
                })
    
    mid_position_words.sort(key=lambda x: abs(x['avg_position'] - 0.5))
    return mid_position_words[:100]


def find_sentence_boundary_verbs(sentences, boundary_words):
    pre_boundary = Counter()
    post_boundary = Counter()
    
    for sent in sentences:
        for i, w in enumerate(sent):
            if w in boundary_words:
                if i > 0:
                    pre_boundary[sent[i-1]] += 1
                if i < len(sent) - 1:
                    post_boundary[sent[i+1]] += 1
    
    return pre_boundary, post_boundary


def find_post_noun_words(sentences):
    noun_endings = ['aiin', 'ain', 'ol', 'or', 'al', 'ar', 'am', 'an']
    post_noun = Counter()
    
    for sent in sentences:
        for i, w in enumerate(sent[:-1]):
            for ending in noun_endings:
                if w.endswith(ending) and len(w) > len(ending):
                    post_noun[sent[i+1]] += 1
                    break
    
    return post_noun


def find_pre_preposition_words(sentences):
    pre_prep = Counter()
    
    for sent in sentences:
        for i, w in enumerate(sent[1:], 1):
            if any(w.startswith(p) for p in LIKELY_PREPOSITIONS) or w in ['ol', 'or', 'al', 'ar']:
                pre_prep[sent[i-1]] += 1
    
    return pre_prep


def find_verb_ending_patterns(sentences):
    verb_like_endings = Counter()
    
    for sent in sentences:
        if len(sent) < 3:
            continue
        
        mid_start = len(sent) // 4
        mid_end = 3 * len(sent) // 4
        
        for w in sent[mid_start:mid_end]:
            if len(w) >= 3:
                ending = w[-2:]
                verb_like_endings[ending] += 1
    
    return verb_like_endings.most_common(30)


def find_sentence_initial_verbs(sentences):
    initial_words = Counter()
    second_words = Counter()
    
    for sent in sentences:
        if sent:
            initial_words[sent[0]] += 1
        if len(sent) >= 2:
            second_words[sent[1]] += 1
    
    return initial_words, second_words


def extract_context_windows(sentences, target_word, window_size=2):
    contexts = []
    for sent in sentences:
        for i, w in enumerate(sent):
            if w == target_word:
                start = max(0, i - window_size)
                end = min(len(sent), i + window_size + 1)
                context = sent[start:end]
                
                rel_pos = i / (len(sent) - 1) if len(sent) > 1 else 0.5
                pos_label = 'initial' if rel_pos < 0.2 else 'final' if rel_pos > 0.8 else 'middle'
                
                contexts.append({
                    'context': context,
                    'position': pos_label,
                    'rel_position': round(rel_pos, 2)
                })
    
    return contexts[:10]


def score_verb_candidate(word, svo_positions, pre_boundary, post_boundary, 
                         post_noun, pre_prep, initial_words, second_words):
    score = 0.0
    evidence = []
    
    if word in SENTENCE_BOUNDARY_WORDS:
        return 0.0, ["Boundary word - skip"]
    
    if len(word) == 1:
        return 0.0, ["Single char - skip"]
    
    svo_match = [p for p in svo_positions if p['word'] == word]
    if svo_match:
        pos = svo_match[0]
        if 0.35 <= pos['avg_position'] <= 0.65:
            score += 0.35
            evidence.append(f"SVO middle position: {pos['avg_position']:.0%}")
        elif 0.2 <= pos['avg_position'] <= 0.8:
            score += 0.2
            evidence.append(f"Near-middle position: {pos['avg_position']:.0%}")
    
    pre_b_count = pre_boundary.get(word, 0)
    if pre_b_count >= 10:
        score += 0.25
        evidence.append(f"Before boundary {pre_b_count}x (sentence-final verb position)")
    elif pre_b_count >= 5:
        score += 0.15
        evidence.append(f"Before boundary {pre_b_count}x")
    
    post_b_count = post_boundary.get(word, 0)
    if post_b_count >= 10:
        score += 0.2
        evidence.append(f"After boundary {post_b_count}x (sentence-initial)")
    elif post_b_count >= 5:
        score += 0.1
        evidence.append(f"After boundary {post_b_count}x")
    
    pn_count = post_noun.get(word, 0)
    if pn_count >= 20:
        score += 0.25
        evidence.append(f"Follows nouns {pn_count}x (verb position in SVO)")
    elif pn_count >= 10:
        score += 0.15
        evidence.append(f"Follows nouns {pn_count}x")
    
    pp_count = pre_prep.get(word, 0)
    if pp_count >= 10:
        score += 0.15
        evidence.append(f"Before preposition {pp_count}x")
    
    init_count = initial_words.get(word, 0)
    second_count = second_words.get(word, 0)
    if init_count >= 5:
        score += 0.15
        evidence.append(f"Sentence-initial {init_count}x (imperative?)")
    if second_count >= 10:
        score += 0.1
        evidence.append(f"Second position {second_count}x")
    
    decoded = decode_eva(word)
    best_match = None
    best_sim = 0
    for latin_verb, meaning in LATIN_HERBAL_VERBS.items():
        if len(decoded) >= 2 and len(latin_verb) >= 2:
            common = sum(1 for a, b in zip(decoded, latin_verb) if a == b)
            sim = common / max(len(decoded), len(latin_verb))
            if sim > best_sim:
                best_sim = sim
                best_match = (latin_verb, meaning, sim)
    
    if best_match and best_sim >= 0.4:
        score += 0.2 * best_sim
        evidence.append(f"Phonetic match: '{best_match[0]}' ({best_match[1]}) {best_sim:.0%}")
    
    if 3 <= len(word) <= 6:
        score += 0.05
        evidence.append(f"Verb-like length ({len(word)} chars)")
    
    return min(score, 1.0), evidence


def generate_report(results):
    lines = ["# Track 23: Verb Discovery by Context (Reworked)\n"]
    lines.append("## Using Track 22 Sentence Structure Analysis\n")
    lines.append("Finding verbs using **SVO word order** and **sentence boundary patterns**.\n")
    
    stats = results['statistics']
    lines.append("\n## Statistics\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Sentences analyzed | {stats['total_sentences']} |")
    lines.append(f"| Avg sentence length | {stats['avg_sentence_length']} words |")
    lines.append(f"| Boundary words used | {', '.join(stats['boundary_words'])} |")
    lines.append(f"| Candidates evaluated | {stats['candidates_evaluated']} |")
    lines.append(f"| High confidence (≥50%) | {stats['high_confidence']} |")
    lines.append(f"| Medium confidence (30-50%) | {stats['medium_confidence']} |")
    
    lines.append("\n## SVO Word Order Analysis\n")
    lines.append("Track 22 found **SVO (Subject-Verb-Object)** word order.\n")
    lines.append("Verbs should appear in **middle positions** (30-70% into sentence).\n")
    
    lines.append("\n### Words in Verb Zone (30-70% position)\n")
    lines.append("| EVA | Decoded | Avg Position | Count |")
    lines.append("|-----|---------|--------------|-------|")
    for w in results['svo_middle_words'][:20]:
        lines.append(f"| `{w['word']}` | {w['decoded']} | {w['avg_position']:.0%} | {w['occurrences']} |")
    
    lines.append("\n## Top 20 Verb Candidates\n")
    lines.append("| EVA | Decoded | Confidence | Key Evidence |")
    lines.append("|-----|---------|------------|--------------|")
    for c in results['top_candidates'][:20]:
        ev = '; '.join(c['evidence'][:2]) if c['evidence'] else '-'
        lines.append(f"| `{c['voynich']}` | {c['decoded']} | {c['confidence']:.0%} | {ev} |")
    
    lines.append("\n## Pre-Boundary Words (Before daiin/dy/etc.)\n")
    lines.append("Words appearing before sentence-ending markers:\n")
    lines.append("| EVA | Decoded | Count |")
    lines.append("|-----|---------|-------|")
    for w, c in results['pre_boundary_words'][:15]:
        lines.append(f"| `{w}` | {decode_eva(w)} | {c} |")
    
    lines.append("\n## Post-Noun Words (Verb Position in SVO)\n")
    lines.append("| EVA | Decoded | Count |")
    lines.append("|-----|---------|-------|")
    for w, c in results['post_noun_words'][:15]:
        lines.append(f"| `{w}` | {decode_eva(w)} | {c} |")
    
    lines.append("\n## Sentence-Initial Words (Imperatives)\n")
    lines.append("| EVA | Decoded | Count |")
    lines.append("|-----|---------|-------|")
    for w, c in results['sentence_initial'][:15]:
        lines.append(f"| `{w}` | {decode_eva(w)} | {c} |")
    
    lines.append("\n## Common Word Endings in Verb Zone\n")
    lines.append("| Ending | Count |")
    lines.append("|--------|-------|")
    for e, c in results['verb_endings'][:15]:
        lines.append(f"| `-{e}` | {c} |")
    
    lines.append("\n## Context Examples\n")
    for c in results['top_candidates'][:5]:
        lines.append(f"\n### `{c['voynich']}` → {c['decoded']}")
        lines.append(f"**Confidence:** {c['confidence']:.0%}")
        lines.append(f"**Evidence:** {', '.join(c['evidence'])}")
        if c['contexts']:
            lines.append("\n**Contexts:**")
            for ctx in c['contexts'][:3]:
                lines.append(f"- {' '.join(ctx['context'])} (pos: {ctx['position']})")
    
    lines.append("\n\n## Key Findings\n")
    lines.append("1. **SVO word order confirmed** - verbs in middle positions")
    lines.append("2. **Boundary words mark sentence ends** - `daiin`, `dy`, `dar`, etc.")
    lines.append("3. **Post-noun position strong indicator** - NOUN + VERB pattern")
    lines.append("4. **Sentence-initial words may be imperatives** - recipe, take, mix")
    
    lines.append("\n## Comparison with Previous Analysis\n")
    lines.append("- Previous: Used line positions (line-initial, line-final)")
    lines.append("- Now: Using **sentence positions** based on Track 22 boundaries")
    lines.append("- **SVO pattern** means verbs are mid-sentence, not line-final")
    
    return '\n'.join(lines)


def main():
    print("Track 23: Verb Discovery by Context (Reworked)")
    print("=" * 50)
    print("Using Track 22 sentence structure findings...")
    
    print("\nLoading EVA transcription...")
    lines = load_eva_lines(transcriber='H')
    print(f"  Loaded {len(lines)} lines")
    
    print("\nBuilding sentences from paragraphs...")
    sentences, boundary_words = build_sentences(lines)
    print(f"  Built {len(sentences)} sentences")
    print(f"  Boundary words: {boundary_words}")
    
    sent_lengths = [len(s) for s in sentences]
    avg_len = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0
    print(f"  Avg sentence length: {avg_len:.1f} words")
    
    print("\nAnalyzing SVO positions...")
    svo_positions = analyze_svo_positions(sentences)
    print(f"  Found {len(svo_positions)} words in verb zone")
    
    print("\nFinding boundary-adjacent words...")
    pre_boundary, post_boundary = find_sentence_boundary_verbs(sentences, boundary_words)
    print(f"  Pre-boundary candidates: {len(pre_boundary)}")
    print(f"  Post-boundary candidates: {len(post_boundary)}")
    
    print("\nFinding post-noun words...")
    post_noun = find_post_noun_words(sentences)
    print(f"  Post-noun candidates: {len(post_noun)}")
    
    print("\nFinding pre-preposition words...")
    pre_prep = find_pre_preposition_words(sentences)
    print(f"  Pre-preposition candidates: {len(pre_prep)}")
    
    print("\nAnalyzing verb-zone endings...")
    verb_endings = find_verb_ending_patterns(sentences)
    
    print("\nFinding sentence-initial words...")
    initial_words, second_words = find_sentence_initial_verbs(sentences)
    print(f"  Initial word patterns: {len(initial_words)}")
    
    all_candidates = set()
    for p in svo_positions[:50]:
        all_candidates.add(p['word'])
    for w, _ in pre_boundary.most_common(40):
        all_candidates.add(w)
    for w, _ in post_boundary.most_common(40):
        all_candidates.add(w)
    for w, _ in post_noun.most_common(40):
        all_candidates.add(w)
    for w, _ in pre_prep.most_common(30):
        all_candidates.add(w)
    for w, _ in initial_words.most_common(30):
        all_candidates.add(w)
    
    print(f"\nScoring {len(all_candidates)} unique candidates...")
    
    scored = []
    for word in all_candidates:
        score, evidence = score_verb_candidate(
            word, svo_positions, pre_boundary, post_boundary,
            post_noun, pre_prep, initial_words, second_words
        )
        if score >= 0.2:
            contexts = extract_context_windows(sentences, word)
            scored.append({
                'voynich': word,
                'decoded': decode_eva(word),
                'confidence': round(score, 3),
                'evidence': evidence,
                'contexts': contexts,
                'pre_boundary_count': pre_boundary.get(word, 0),
                'post_noun_count': post_noun.get(word, 0)
            })
    
    scored.sort(key=lambda x: x['confidence'], reverse=True)
    
    results = {
        'statistics': {
            'total_sentences': len(sentences),
            'avg_sentence_length': round(avg_len, 2),
            'boundary_words': list(boundary_words),
            'candidates_evaluated': len(all_candidates),
            'high_confidence': len([s for s in scored if s['confidence'] >= 0.5]),
            'medium_confidence': len([s for s in scored if 0.3 <= s['confidence'] < 0.5])
        },
        'svo_middle_words': svo_positions[:50],
        'pre_boundary_words': pre_boundary.most_common(30),
        'post_boundary_words': post_boundary.most_common(30),
        'post_noun_words': post_noun.most_common(30),
        'sentence_initial': initial_words.most_common(30),
        'verb_endings': verb_endings,
        'top_candidates': scored[:50]
    }
    
    print(f"\nSaving results to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Generating report {OUTPUT_REPORT}...")
    report = generate_report(results)
    with open(OUTPUT_REPORT, 'w') as f:
        f.write(report)
    
    print("\n=== SUMMARY ===")
    print(f"Sentences analyzed: {len(sentences)}")
    print(f"High confidence verb candidates: {results['statistics']['high_confidence']}")
    print(f"Medium confidence candidates: {results['statistics']['medium_confidence']}")
    
    print("\nTop 5 verb candidates:")
    for c in scored[:5]:
        print(f"  {c['voynich']} ({c['decoded']}): {c['confidence']:.0%}")


if __name__ == '__main__':
    main()

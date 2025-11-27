#!/usr/bin/env python3
"""Track 26: Coherent Translation Attempt

Attempt to produce readable Latin translation sentence by sentence.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

EVA_FILE = 'data/eva_ivtff.txt'
MASTER_DICT = 'results/master_dictionary.json'
HIGH_CONF = 'results/high_confidence_words.json'
SENTENCE_STRUCT = 'results/sentence_structure.json'
VERB_CONTEXT = 'results/verb_context.json'

EVA_TO_PHONETIC = {
    'o': 'a', 'a': 'e', 'i': 'i', 'n': 'n',
    'y': 's', 'd': 'd', 'k': 'n', 't': 't',
    'l': 'l', 'r': 'r', 'e': 'i', 'q': 'qu',
    'p': 'p', 'm': 'm', 's': 'x', 'f': 'f', 'g': 'g',
    'c': 'c', 'h': 'r',
}

EVA_DIGRAPHS = {
    'ch': 'c', 'sh': 'b', 'cth': 'hc', 'cph': 'hp',
    'cfh': 'hf', 'ckh': 'hn',
    'aiin': 'eiin', 'aiiin': 'eiiin', 'ain': 'ein',
    'ol': 'al', 'or': 'as', 'al': 'el', 'ar': 'es',
    'dy': 'dr', 'ey': 'ir', 'eey': 'iir', 'eedy': 'iidr',
    'edy': 'idr',
}

MEDIEVAL_PATTERNS = {
    'herba_valet': r'(herb|plant).*?(valet|bonum|utilis)',
    'radix_curat': r'radi[cx].*?cur',
    'recipe': r'recipe|accipe|sume',
    'coque': r'coqu|decoc|infund',
    'contra_morbum': r'contra.*(dolor|morb|febr)',
    'folia_flores': r'foli|flor|semin|fruc',
    'tempore': r'tempor|mens|die|hor',
    'pondere': r'libr|unci|drachm',
}

LATIN_VERBS = [
    'est', 'sunt', 'habet', 'valet', 'curat', 'sanat',
    'facit', 'dat', 'ponit', 'bibit', 'comedit',
    'crescit', 'floret', 'nascitur', 'colligitur',
]

LATIN_NOUNS = [
    'herba', 'radix', 'folium', 'flos', 'semen', 'fructus',
    'aqua', 'vinum', 'oleum', 'mel', 'lac',
    'dolor', 'febris', 'morbus', 'vulnus', 'tumor',
    'caput', 'pectus', 'venter', 'hepar', 'ren',
]

LATIN_PREPOSITIONS = ['de', 'in', 'ad', 'per', 'cum', 'ex', 'pro', 'contra', 'ante', 'post']


class Translator:
    def __init__(self):
        self.master_dict = self.load_dict(MASTER_DICT)
        self.high_conf = self.load_dict(HIGH_CONF)
        self.sentence_struct = self.load_dict(SENTENCE_STRUCT)
        self.verb_candidates = self.load_verb_candidates()
        self.word_lookup = self.build_lookup()
        
    def load_dict(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return {}
    
    def load_verb_candidates(self):
        try:
            with open(VERB_CONTEXT) as f:
                data = json.load(f)
                return {v['word']: v for v in data.get('svo_middle_words', [])}
        except:
            return {}
    
    def build_lookup(self):
        lookup = {}
        for entry in self.high_conf.get('entries', []):
            lookup[entry['voynich']] = {
                'decoded': entry.get('decoded', ''),
                'latin': entry.get('latin', ''),
                'english': entry.get('english', ''),
                'confidence': entry.get('confidence', 0),
                'category': entry.get('category', 'unknown'),
            }
        return lookup
    
    def eva_to_phonetic(self, word):
        result = word.lower()
        for digraph, replacement in sorted(EVA_DIGRAPHS.items(), key=lambda x: -len(x[0])):
            result = result.replace(digraph, replacement)
        out = []
        for c in result:
            out.append(EVA_TO_PHONETIC.get(c, c))
        return ''.join(out)
    
    def decode_word(self, eva_word):
        clean = eva_word.strip('.,!?<>')
        if not clean:
            return None
        
        if clean in self.word_lookup:
            entry = self.word_lookup[clean]
            return {
                'eva': clean,
                'decoded': entry['decoded'],
                'latin': entry['latin'],
                'english': entry['english'],
                'confidence': entry['confidence'],
                'category': entry['category'],
                'source': 'high_confidence',
            }
        
        phonetic = self.eva_to_phonetic(clean)
        latin_match = self.find_latin_match(phonetic)
        
        return {
            'eva': clean,
            'decoded': phonetic,
            'latin': latin_match.get('word', '?'),
            'english': latin_match.get('meaning', '?'),
            'confidence': latin_match.get('score', 0),
            'category': latin_match.get('category', 'unknown'),
            'source': 'phonetic',
        }
    
    def find_latin_match(self, decoded):
        for verb in LATIN_VERBS:
            if self.levenshtein(decoded[:4], verb[:4]) <= 1:
                return {'word': verb, 'meaning': f'verb: {verb}', 'score': 0.6, 'category': 'verb'}
        
        for noun in LATIN_NOUNS:
            if self.levenshtein(decoded[:4], noun[:4]) <= 1:
                return {'word': noun, 'meaning': f'noun: {noun}', 'score': 0.5, 'category': 'noun'}
        
        for prep in LATIN_PREPOSITIONS:
            if decoded.startswith(prep) or self.levenshtein(decoded[:3], prep) <= 1:
                return {'word': prep, 'meaning': f'prep: {prep}', 'score': 0.7, 'category': 'preposition'}
        
        if decoded.endswith('s') or decoded.endswith('m'):
            return {'word': decoded, 'meaning': '?noun', 'score': 0.2, 'category': 'noun_guess'}
        if decoded.endswith('t') or decoded.endswith('nt'):
            return {'word': decoded, 'meaning': '?verb', 'score': 0.2, 'category': 'verb_guess'}
        
        return {'word': decoded, 'meaning': '?', 'score': 0.1, 'category': 'unknown'}
    
    def levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
            prev = curr
        return prev[-1]
    
    def extract_page(self, folio_id):
        lines = []
        seen_lines = set()
        with open(EVA_FILE) as f:
            in_folio = False
            for line in f:
                if line.startswith(f'<{folio_id}.'):
                    in_folio = True
                    if ';H>' not in line:
                        continue
                    line_num = line.split('.')[1].split(',')[0]
                    if line_num in seen_lines:
                        continue
                    seen_lines.add(line_num)
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        text_part = parts[1]
                        text = re.sub(r'<[^>]*>', '', text_part)
                        text = re.sub(r'[!?\-<>\n]', '', text)
                        words = [w.strip() for w in text.split('.') if w.strip()]
                        if words:
                            lines.append(words)
                elif in_folio and line.startswith('<f') and not line.startswith(f'<{folio_id}'):
                    break
        return lines
    
    def analyze_grammar(self, decoded_words):
        analysis = {
            'subject': None,
            'verb': None,
            'object': None,
            'prepositions': [],
            'modifiers': [],
        }
        
        for i, w in enumerate(decoded_words):
            if w['category'] == 'noun_botanical' and not analysis['subject']:
                analysis['subject'] = w
            elif w['category'] in ('verb', 'verb_guess') and not analysis['verb']:
                analysis['verb'] = w
            elif w['category'] == 'preposition':
                if i + 1 < len(decoded_words):
                    analysis['prepositions'].append({
                        'prep': w,
                        'object': decoded_words[i + 1]
                    })
            elif w['eva'] in self.verb_candidates:
                analysis['verb'] = w
        
        if not analysis['subject']:
            for w in decoded_words:
                if w['category'] in ('noun', 'noun_guess'):
                    analysis['subject'] = w
                    break
        
        return analysis
    
    def match_herbal_pattern(self, latin_text):
        matches = []
        text_lower = latin_text.lower()
        
        for pattern_name, pattern in MEDIEVAL_PATTERNS.items():
            if re.search(pattern, text_lower):
                matches.append(pattern_name)
        
        return matches
    
    def reconstruct_latin(self, decoded_words, grammar):
        parts = []
        
        if grammar['subject']:
            parts.append(grammar['subject']['latin'])
        
        for prep_obj in grammar['prepositions']:
            parts.append(f"{prep_obj['prep']['latin']} {prep_obj['object']['latin']}")
        
        if grammar['verb']:
            parts.append(grammar['verb']['latin'])
        
        if grammar['object']:
            parts.append(grammar['object']['latin'])
        
        if not parts:
            parts = [w['latin'] for w in decoded_words if w['latin'] != '?']
        
        return ' '.join(parts) if parts else '[unreadable]'
    
    def score_coherence(self, decoded_words, grammar, latin_text):
        score = 0.0
        factors = []
        
        high_conf_count = sum(1 for w in decoded_words if w['confidence'] >= 0.8)
        high_conf_ratio = high_conf_count / len(decoded_words) if decoded_words else 0
        score += high_conf_ratio * 30
        factors.append(f"high_conf_words: {high_conf_count}/{len(decoded_words)}")
        
        if grammar['subject']:
            score += 15
            factors.append("has_subject")
        if grammar['verb']:
            score += 20
            factors.append("has_verb")
        if grammar['prepositions']:
            score += 10
            factors.append(f"has_prepositions: {len(grammar['prepositions'])}")
        
        herbal_matches = self.match_herbal_pattern(latin_text)
        if herbal_matches:
            score += 15 * len(herbal_matches)
            factors.append(f"herbal_patterns: {herbal_matches}")
        
        latin_words = latin_text.split()
        real_latin = sum(1 for w in latin_words 
                        if w in LATIN_VERBS + LATIN_NOUNS + LATIN_PREPOSITIONS)
        if latin_words:
            latin_ratio = real_latin / len(latin_words)
            score += latin_ratio * 20
            factors.append(f"latin_words: {real_latin}/{len(latin_words)}")
        
        return min(score, 100), factors
    
    def translate_sentence(self, words):
        decoded = [self.decode_word(w) for w in words if w]
        decoded = [d for d in decoded if d]
        
        grammar = self.analyze_grammar(decoded)
        latin_recon = self.reconstruct_latin(decoded, grammar)
        coherence, factors = self.score_coherence(decoded, grammar, latin_recon)
        
        english = self.attempt_english(decoded, grammar)
        
        return {
            'voynich_raw': ' '.join(words),
            'voynich_segmented': words,
            'decoded_words': decoded,
            'grammar_parse': {
                'subject': grammar['subject']['eva'] if grammar['subject'] else None,
                'verb': grammar['verb']['eva'] if grammar['verb'] else None,
                'object': grammar['object']['eva'] if grammar['object'] else None,
                'prepositions': [(p['prep']['eva'], p['object']['eva']) 
                               for p in grammar['prepositions']],
            },
            'latin_reconstruction': latin_recon,
            'english_translation': english,
            'coherence_score': round(coherence, 1),
            'coherence_factors': factors,
        }
    
    def attempt_english(self, decoded, grammar):
        parts = []
        
        if grammar['subject']:
            eng = grammar['subject'].get('english', '?')
            if eng != '?':
                parts.append(f"The {eng}")
        
        for prep_obj in grammar['prepositions']:
            prep_eng = prep_obj['prep'].get('english', '?')
            obj_eng = prep_obj['object'].get('english', '?')
            if prep_eng != '?' and obj_eng != '?':
                parts.append(f"{prep_eng} {obj_eng}")
        
        if grammar['verb']:
            verb_eng = grammar['verb'].get('english', '?')
            if verb_eng != '?':
                parts.append(verb_eng)
        
        return ' '.join(parts) if parts else '[translation unclear]'
    
    def translate_page(self, folio_id):
        lines = self.extract_page(folio_id)
        if not lines:
            return None
        
        sentences = []
        for line_words in lines:
            if line_words:
                result = self.translate_sentence(line_words)
                sentences.append(result)
        
        coherent = [s for s in sentences if s['coherence_score'] >= 50]
        best = max(sentences, key=lambda s: s['coherence_score']) if sentences else None
        
        avg_coherence = sum(s['coherence_score'] for s in sentences) / len(sentences) if sentences else 0
        
        return {
            'page': folio_id,
            'total_sentences': len(sentences),
            'sentences': sentences,
            'overall_coherence': round(avg_coherence, 1),
            'readable_sentences': len(coherent),
            'best_sentence': best,
        }
    
    def analyze_candidates(self):
        candidates = ['f2v', 'f3v', 'f4r']
        results = []
        
        for folio in candidates:
            lines = self.extract_page(folio)
            if not lines:
                continue
            
            total_words = sum(len(line) for line in lines)
            high_conf_words = 0
            
            for line in lines:
                for word in line:
                    if word in self.word_lookup:
                        high_conf_words += 1
            
            results.append({
                'folio': folio,
                'lines': len(lines),
                'total_words': total_words,
                'high_conf_words': high_conf_words,
                'high_conf_ratio': high_conf_words / total_words if total_words else 0,
            })
        
        return sorted(results, key=lambda x: -x['high_conf_ratio'])


def generate_report(result):
    lines = []
    lines.append(f"# Page Translation Attempt: {result['page']}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total sentences/lines: {result['total_sentences']}")
    lines.append(f"- Readable sentences (>50% coherence): {result['readable_sentences']}")
    lines.append(f"- Overall coherence: {result['overall_coherence']}%")
    lines.append("")
    
    if result['best_sentence']:
        best = result['best_sentence']
        lines.append("## Best Sentence")
        lines.append(f"- Voynich: `{best['voynich_raw']}`")
        lines.append(f"- Latin: `{best['latin_reconstruction']}`")
        lines.append(f"- English: {best['english_translation']}")
        lines.append(f"- Coherence: {best['coherence_score']}%")
        lines.append("")
    
    lines.append("## Sentence-by-Sentence Analysis")
    lines.append("")
    
    for i, sent in enumerate(result['sentences'], 1):
        lines.append(f"### Line {i}")
        lines.append(f"**Voynich:** `{sent['voynich_raw']}`")
        lines.append("")
        
        lines.append("**Word-by-word decode:**")
        lines.append("| EVA | Decoded | Latin | English | Confidence |")
        lines.append("|-----|---------|-------|---------|------------|")
        for w in sent['decoded_words']:
            conf_pct = f"{w['confidence']*100:.0f}%"
            lines.append(f"| {w['eva']} | {w['decoded']} | {w['latin']} | {w['english']} | {conf_pct} |")
        lines.append("")
        
        lines.append("**Grammar Parse:**")
        gp = sent['grammar_parse']
        lines.append(f"- Subject: {gp['subject'] or '(none)'}")
        lines.append(f"- Verb: {gp['verb'] or '(none)'}")
        lines.append(f"- Object: {gp['object'] or '(none)'}")
        if gp['prepositions']:
            lines.append(f"- Prepositions: {gp['prepositions']}")
        lines.append("")
        
        lines.append(f"**Latin Reconstruction:** `{sent['latin_reconstruction']}`")
        lines.append(f"**English:** {sent['english_translation']}")
        lines.append(f"**Coherence Score:** {sent['coherence_score']}%")
        lines.append(f"- Factors: {', '.join(sent['coherence_factors'])}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    lines.append("## Honest Assessment")
    lines.append("")
    
    avg = result['overall_coherence']
    readable = result['readable_sentences']
    total = result['total_sentences']
    
    if avg >= 50 and readable >= 3:
        assessment = "**PARTIALLY READABLE**: Some sentences show coherent Latin structure."
    elif avg >= 30 and readable >= 1:
        assessment = "**MARGINALLY READABLE**: A few sentences may contain meaningful content."
    else:
        assessment = "**NOT YET READABLE**: Current decoding does not produce coherent Latin."
    
    lines.append(assessment)
    lines.append("")
    lines.append("### What Works")
    works = []
    if readable > 0:
        works.append(f"- {readable} sentences with coherence >50%")
    high_conf_total = sum(len([w for w in s['decoded_words'] if w['confidence'] >= 0.8]) 
                          for s in result['sentences'])
    if high_conf_total > 0:
        works.append(f"- {high_conf_total} high-confidence word matches")
    if not works:
        works.append("- Limited success with current approach")
    lines.extend(works)
    lines.append("")
    
    lines.append("### Problems Identified")
    problems = []
    no_verb = sum(1 for s in result['sentences'] if not s['grammar_parse']['verb'])
    if no_verb > total / 2:
        problems.append(f"- {no_verb}/{total} sentences lack identifiable verbs")
    no_subj = sum(1 for s in result['sentences'] if not s['grammar_parse']['subject'])
    if no_subj > total / 2:
        problems.append(f"- {no_subj}/{total} sentences lack identifiable subjects")
    low_conf = sum(len([w for w in s['decoded_words'] if w['confidence'] < 0.5])
                   for s in result['sentences'])
    if low_conf > 0:
        problems.append(f"- {low_conf} words decoded with <50% confidence")
    if not problems:
        problems.append("- Grammar reconstruction needs refinement")
    lines.extend(problems)
    lines.append("")
    
    lines.append("### Next Steps")
    lines.append("1. Expand high-confidence vocabulary through more anchor words")
    lines.append("2. Improve verb identification from context patterns")
    lines.append("3. Cross-reference with specific plant illustrations")
    lines.append("4. Try different pages or sections")
    
    return '\n'.join(lines)


def main():
    translator = Translator()
    
    print("=" * 60)
    print("TRACK 26: COHERENT TRANSLATION ATTEMPT")
    print("=" * 60)
    print()
    
    print("Analyzing candidate pages...")
    candidates = translator.analyze_candidates()
    
    print("\nPage Analysis:")
    print("-" * 50)
    for c in candidates:
        print(f"  {c['folio']}: {c['lines']} lines, {c['total_words']} words, "
              f"{c['high_conf_words']} high-conf ({c['high_conf_ratio']*100:.1f}%)")
    
    best_page = candidates[0]['folio'] if candidates else 'f3v'
    print(f"\nSelected page: {best_page}")
    print()
    
    print("Translating page...")
    result = translator.translate_page(best_page)
    
    if not result:
        print("ERROR: Could not extract page text")
        return
    
    print(f"\nResults:")
    print(f"  Total sentences: {result['total_sentences']}")
    print(f"  Readable (>50%): {result['readable_sentences']}")
    print(f"  Overall coherence: {result['overall_coherence']}%")
    
    if result['best_sentence']:
        print(f"\nBest sentence ({result['best_sentence']['coherence_score']}%):")
        print(f"  Voynich: {result['best_sentence']['voynich_raw']}")
        print(f"  Latin:   {result['best_sentence']['latin_reconstruction']}")
        print(f"  English: {result['best_sentence']['english_translation']}")
    
    out_json = 'results/page_translation_attempt.json'
    with open(out_json, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {out_json}")
    
    report = generate_report(result)
    out_report = 'results/page_translation_report.md'
    with open(out_report, 'w') as f:
        f.write(report)
    print(f"Saved: {out_report}")
    
    print()
    print("=" * 60)
    print("ASSESSMENT")
    print("=" * 60)
    
    avg = result['overall_coherence']
    readable = result['readable_sentences']
    
    if avg >= 50 and readable >= 3:
        print("✅ PARTIALLY READABLE - Some sentences show Latin structure")
    elif avg >= 30 and readable >= 1:
        print("⚠️ MARGINALLY READABLE - Limited meaningful content detected")
    else:
        print("❌ NOT YET READABLE - Current decoding insufficient")
    
    print(f"\nSuccess criteria:")
    print(f"  [{'✅' if readable >= 1 else '❌'}] At least 1 page fully analyzed")
    print(f"  [{'✅' if readable >= 3 else '❌'}] At least 3 sentences with coherence >50%")
    print(f"  [{'✅' if any(s['grammar_parse']['subject'] for s in result['sentences']) else '❌'}] Grammar parse for sentences")
    print(f"  [{'✅' if any('?' not in s['latin_reconstruction'] for s in result['sentences']) else '❌'}] Latin reconstruction attempted")


if __name__ == '__main__':
    main()

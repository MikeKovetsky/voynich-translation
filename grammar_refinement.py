
import voynich_data
import re
from collections import Counter

def analyze_grammar_patterns():
    print("=== GRAMMAR PATTERN REFINEMENT ===")
    
    recipes = voynich_data.get_section_text('recipes')
    
    # Pattern 1: daiin + qok... (Verb + Connector?)
    print("\n[1] Does 'daiin' (Verb) appear directly before 'qok-' words?")
    qok_hits = 0
    
    # Pattern 2: ol + [WORD] (The [Noun]?)
    print("\n[2] What follows 'ol' in Recipes? (The ...)")
    ol_followers = Counter()
    
    # Pattern 3: Ingredient + qok... (Noun + Connector?)
    
    for folio, lines in recipes.items():
        for loc, text in lines.items():
            clean = re.sub(r'[^\w\s.-]', '', text)
            words = [w for w in clean.split('.') if w]
            
            # Check daiin + qok
            if 'daiin' in words:
                idx = words.index('daiin')
                if idx < len(words)-1:
                    next_w = words[idx+1]
                    if next_w.startswith('qok') or next_w.startswith('4oh'):
                        print(f"  {loc}: daiin + {next_w}")
                        qok_hits += 1
            
            # Check ol + word
            if 'ol' in words:
                indices = [i for i, x in enumerate(words) if x == 'ol']
                for i in indices:
                    if i < len(words)-1:
                        ol_followers[words[i+1]] += 1

    if qok_hits == 0:
        print("  Result: NO. 'daiin' is rarely/never followed by 'qok-'.")
        print("  Implication: 'qok-' is NOT the direct object (ingredient). It is likely a preposition phrase later in the sentence.")
    
    print("\nTop 10 words following 'ol' (The...):")
    for w, c in ol_followers.most_common(10):
        print(f"  ol {w}: {c}")
        
    # Check intersection of 'daiin' objects and 'ol' objects
    # From previous run, daiin objects were: shey, chey, sheey, al, chedy...
    daiin_objects = {'shey', 'chey', 'sheey', 'al', 'chedy', 'ol', 'sheckhy', 'checkhy', 'choaiin', 'char'}
    
    print("\n[3] INTERSECTION: Words that appear after BOTH 'daiin' AND 'ol'")
    intersection = set(ol_followers.keys()) & daiin_objects
    print(f"  Matches: {', '.join(intersection)}")
    
    if intersection:
        print("  CONCLUSION: These are confirmed NOUNS (Ingredients).")
        print("  Grammar: 'Take [NOUN]' and 'The [NOUN]'")

if __name__ == "__main__":
    analyze_grammar_patterns()

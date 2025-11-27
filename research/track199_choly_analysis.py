import json
import os
import math
import re
from collections import Counter

def load_json(path):
    if not os.path.exists(path):
        print(f"Warning: {path} does not exist.")
        return None
    with open(path, 'r') as f:
        return json.load(f)

def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return numerator / denominator

def parse_tagged_text(path, page_id, transcription_source='H'):
    """
    Parses the tagged text file for a specific page and transcription source.
    """
    if not os.path.exists(path):
        return ""
    
    lines = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith(f"<{page_id}"):
                # Example: <f9r.1,@P0;H> tydlo.choly...
                parts = line.split('>', 1)
                if len(parts) < 2:
                    continue
                
                tag = parts[0] + '>'
                content = parts[1].strip()
                
                # Check transcription source (e.g., ;H>)
                if f";{transcription_source}>" in tag:
                    # Remove comments like <...> or { ... } if any
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\{[^}]+\}', '', content)
                    # Remove transcription markers like !, -, ?
                    content = content.replace('!', '').replace('-', '').replace('?', '')
                    # Replace dots with spaces for tokenization
                    content = content.replace('.', ' ')
                    lines.append(content)
                    
    return " ".join(lines)

def analyze_choly():
    print("Starting Task 199 Analysis...")
    
    tagged_text_path = 'results/segmented_text.txt'
    print(f"Loading text from: {tagged_text_path}")
    
    # Extract Text using 'H' transcription
    text_f9r = parse_tagged_text(tagged_text_path, 'f9r', 'H')
    text_f28v = parse_tagged_text(tagged_text_path, 'f28v', 'H')
    
    # Fallback to 'C' if 'H' is empty
    if not text_f9r:
        print("Warning: Could not find text for f9r with source H, trying C")
        text_f9r = parse_tagged_text(tagged_text_path, 'f9r', 'C')
    if not text_f28v:
        print("Warning: Could not find text for f28v with source H, trying C")
        text_f28v = parse_tagged_text(tagged_text_path, 'f28v', 'C')

    if not text_f9r:
        print("Error: Could not find text for f9r")
    if not text_f28v:
        print("Error: Could not find text for f28v")
        
    if not text_f9r or not text_f28v:
        return

    dictionary_path = 'results/dictionary/dictionary.json'
    print(f"Loading dictionary from: {dictionary_path}")
    dictionary = load_json(dictionary_path)

    # Normalize and tokenize
    tokens_f9r = [w for w in text_f9r.split() if w]
    tokens_f28v = [w for w in text_f28v.split() if w]
    
    print(f"\nf9r word count: {len(tokens_f9r)}")
    print(f"f28v word count: {len(tokens_f28v)}")
    
    # 1. Check for 'choly'
    target_word = 'choly'
    count_f9r = tokens_f9r.count(target_word)
    count_f28v = tokens_f28v.count(target_word)
    
    print(f"\nOccurrences of '{target_word}':")
    print(f"f9r: {count_f9r}")
    print(f"f28v: {count_f28v}")
    
    # Check for variants
    chol_variants_f9r = [w for w in tokens_f9r if 'chol' in w]
    chol_variants_f28v = [w for w in tokens_f28v if 'chol' in w]
    
    print(f"\nVariants containing 'chol' in f9r: {Counter(chol_variants_f9r)}")
    print(f"Variants containing 'chol' in f28v: {Counter(chol_variants_f28v)}")

    # 2. Compare Text - Cosine Similarity
    vec_f9r = Counter(tokens_f9r)
    vec_f28v = Counter(tokens_f28v)
    
    similarity = cosine_similarity(vec_f9r, vec_f28v)
    print(f"\nCosine Similarity between f9r and f28v: {similarity:.4f}")
    
    # 3. Shared Vocabulary
    shared_vocab = set(tokens_f9r) & set(tokens_f28v)
    print(f"Shared vocabulary size: {len(shared_vocab)}")
    
    # Look up meanings of shared words in dictionary
    shared_meanings = {}
    if dictionary:
        for word in shared_vocab:
            entry = dictionary.get(word)
            if entry:
                shared_meanings[word] = entry.get('meanings', [])
            
    # Save results for the report
    report_content = f"""# Investigation: 'choly' on f9r vs f28v

## 1. Text Comparison

### Statistics
- **f9r Word Count**: {len(tokens_f9r)}
- **f28v Word Count**: {len(tokens_f28v)}
- **Cosine Similarity**: {similarity:.4f}
- **Shared Vocabulary**: {len(shared_vocab)} words

### Occurrences of 'choly'
- **f9r**: {count_f9r}
- **f28v**: {count_f28v}

### Variants containing 'chol'
- **f9r**: {', '.join([f"{k}({v})" for k,v in Counter(chol_variants_f9r).items()])}
- **f28v**: {', '.join([f"{k}({v})" for k,v in Counter(chol_variants_f28v).items()])}

## 2. Shared Vocabulary Analysis
Top shared words (by frequency):
"""
    # Sort shared words by total frequency
    sorted_shared = sorted(list(shared_vocab), key=lambda w: vec_f9r[w] + vec_f28v[w], reverse=True)
    
    for word in sorted_shared[:20]:
        meanings = shared_meanings.get(word, "Unknown")
        report_content += f"- **{word}**: f9r({vec_f9r[word]}), f28v({vec_f28v[word]}) - Meaning: {meanings}\n"

    report_content += "\n## 3. Hypothesis Evaluation\n"
    report_content += "- **Same Plant**: " + ("Supported" if similarity > 0.3 else "Weak evidence from text similarity") + "\n"
    report_content += "- **Shared Name**: 'choly' appears in both. "
    if count_f9r > 0 and count_f28v > 0:
        report_content += "This suggests a potential link, possibly a shared name or category.\n"
    else:
        report_content += "Does not appear in both as exact match.\n"

    with open('results/choly_investigation_raw.md', 'w') as f:
        f.write(report_content)
    print("\nRaw investigation saved to results/choly_investigation_raw.md")

if __name__ == "__main__":
    analyze_choly()

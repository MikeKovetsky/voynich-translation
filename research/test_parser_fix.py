import re
import sys

def test_tokenization(text):
    print(f"Input: '{text}'")
    
    # Current logic in research/voynich_data.py (lines 148-149)
    # text_clean = re.sub(r'[!?<>@$\d]', '', text)
    # words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 1]
    
    # REPRODUCTION
    text_clean_buggy = re.sub(r'[!?<>@$\d]', '', text)
    words_buggy = [w for w in re.split(r'[.\-=,\s]', text_clean_buggy) if w and len(w) > 1]
    print(f"Current (Buggy) Output: {words_buggy}")
    
    # PROPOSED FIX
    # Treat ! and ? as separators (replace with space) instead of removing them
    text_clean_fixed = re.sub(r'[!?<>@$\d]', ' ', text) 
    words_fixed = [w for w in re.split(r'[.\-=,\s]', text_clean_fixed) if w and len(w) > 1]
    print(f"Fixed Output: {words_fixed}")
    print("-" * 20)

if __name__ == "__main__":
    print("Running Parser Fix Test...\n")
    test_tokenization("ytai!n")
    test_tokenization("word!break")
    test_tokenization("normal.word")
    test_tokenization("with?question")

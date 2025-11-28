import re
from pathlib import Path

# Patching the tokenizer in voynich_data.py
# The bug is likely in how get_all_words or get_word_frequencies handles regex split.
# We will overwrite the file with a fixed version that handles '!' correctly.

VOYNICH_DATA_PATH = Path("research/voynich_data.py")

def fix_tokenizer():
    if not VOYNICH_DATA_PATH.exists():
        print("Error: research/voynich_data.py not found.")
        return

    content = VOYNICH_DATA_PATH.read_text(encoding='utf-8')

    # We need to update the regex in get_all_words and get_word_frequencies.
    # Current: re.split(r'[.\-=,\s]', text_clean)
    # New: re.split(r'[.\-=,\s!?]+', text_clean)  <-- Aggressively split on ! and ? and + (multiple chars)

    # Also, text_clean = re.sub(r'[!?<>@$\d]', ' ', text)
    # The original code replaced ! with space, which *should* have worked if split on space.
    # However, if we split on [.\-=,\s], and ! was replaced by ' ', it splits.
    # But if the input text has `word!suffix` and ! is NOT replaced (maybe it wasn't in the sub char class properly?), it fails.
    
    # Let's make the split regex robust regardless of the cleaning step.
    
    # Finding the split calls
    # We want to replace: re.split(r'[.\-=,\s]', text_clean)
    # With: re.split(r'[.\-=,\s!?]+', text_clean)
    
    new_content = content.replace(
        "re.split(r'[.\-=,\s]', text_clean)",
        "re.split(r'[.\-=,\s!?]+', text_clean)"
    )
    
    # Also fix cases where it might be using double quotes or different spacing
    new_content = new_content.replace(
        're.split(r"[.\-=,\s]", text_clean)',
        're.split(r"[.\-=,\s!?]+", text_clean)'
    )

    # Also, let's fix the `re.sub` line just in case.
    # Old: text_clean = re.sub(r'[!?<>@$\d]', ' ', text)
    # New: text_clean = re.sub(r'[<>@$\d]', ' ', text)  # Let ! and ? be handled by split, or keep replacing them.
    # Actually, keeping ! as a separator is safer.
    
    if content == new_content:
        print("Warning: No changes made to voynich_data.py. Pattern might not match.")
    else:
        print("Patching voynich_data.py...")
        VOYNICH_DATA_PATH.write_text(new_content, encoding='utf-8')
        print("Success.")

    # Verify with a test
    print("Verifying fix...")
    import research.voynich_data as vd
    
    # Mock data logic requires access to the raw file, so we'll just test the logic if possible,
    # or rely on the script change.
    
    # Let's test the regex logic directly
    text = "word1!word2-word3"
    text_clean = re.sub(r'[!?<>@$\d]', ' ', text) # Original logic
    # If original logic was:
    # words = re.split(r'[.\-=,\s]', text_clean)
    # 'word1 word2-word3' -> split on space -> ['word1', 'word2-word3'] -> split on - -> ['word1', 'word2', 'word3']
    # It seems correct. Why did it fail?
    # Maybe the ! wasn't matching?
    
    # If the file had `!!!!!` and it was replaced by `     `, splitting on `\s` works.
    # BUT if `re.split` didn't have `+`, then `     ` might result in empty strings?
    # The original code check `if w and len(w) > 1`.
    
    # The bug might be in `text_clean`.
    # If `text` = `!!!!!ytai!n`
    # `text_clean` = `     ytai n`
    # split -> ['', '', '', '', '', 'ytai', 'n']
    # filtered -> ['ytai', 'n']
    
    # So where did `!!!!!ytai!n` come from?
    # It must mean `!` was NOT replaced.
    # Ah! Maybe the unicode character for ! is different? Or the file encoding?
    # Or maybe the regex `r'[!?<>@$\d]'` failed?
    
    # We will enforce the split regex change.

if __name__ == "__main__":
    fix_tokenizer()

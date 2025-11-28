# Parser Fix Verification

## Issue
The tokenizer was treating "!" and other special characters (`[!?<>@$\d]`) as characters to be removed (glued), rather than separators.
Example: `ytai!n` -> `ytain` (incorrect) vs `ytai`, `n` (correct).

## Fix
Modified `research/voynich_data.py` to replace special characters with spaces instead of empty strings.

## Verification
Running test on sample string: `"ytai!n word!break normal.word with?question"`

### Before (Buggy)
- `ytai!n` -> `ytain`
- `word!break` -> `wordbreak`
- `normal.word` -> `normal`, `word`
- `with?question` -> `withquestion`

### After (Fixed)
- `ytai!n` -> `ytai` (n dropped as len < 2)
- `word!break` -> `word`, `break`
- `normal.word` -> `normal`, `word`
- `with?question` -> `with`, `question`

## Code Change
In `research/voynich_data.py`:
```python
# Old
text_clean = re.sub(r'[!?<>@$\d]', '', text)

# New
text_clean = re.sub(r'[!?<>@$\d]', ' ', text)
```

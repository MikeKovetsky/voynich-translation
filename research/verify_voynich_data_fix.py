import sys
import os

# Add research to path
sys.path.append(os.path.join(os.getcwd(), 'research'))

import voynich_data as vd

# Mock get_eva_pages
def mock_get_pages(*args, **kwargs):
    return {'test_folio': {'1': 'ytai!n word!break'}}

vd.get_eva_pages = mock_get_pages

print("Testing get_all_words with fix...")
words = vd.get_all_words()
print(f"Words found: {sorted(words)}")

expected = ['break', 'word', 'ytai']
if sorted(words) == expected:
    print("SUCCESS: Parser split words correctly.")
else:
    print("FAILURE: Parser failed to split words correctly.")

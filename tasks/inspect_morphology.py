import json

with open('results/verb_morphology.json', 'r') as f:
    data = json.load(f)

print(f"Total items: {len(data)}")

# Check for "Bio" section (f75r-f84v)
bio_pages = [f"f{i}r" for i in range(75, 85)] + [f"f{i}v" for i in range(75, 85)]
bio_items = [item for item in data if item.get('page') in bio_pages]
print(f"Bio items: {len(bio_items)}")

# Check for "Recipes" section
recipes_items = [item for item in data if item.get('section') == 'Recipes']
print(f"Recipes items: {len(recipes_items)}")

# Check 'dy' occurrences in Bio
dy_suffix_count = sum(1 for item in bio_items if item.get('suffix') == 'dy')
dy_word_count = sum(1 for item in bio_items if item.get('original') == 'dy')
print(f"Bio: suffix='dy': {dy_suffix_count}, word='dy': {dy_word_count}")

# Check 'qok' prefix in Bio
qok_prefix_count = sum(1 for item in bio_items if item.get('prefix') == 'qok')
print(f"Bio: prefix='qok': {qok_prefix_count}")

# Sample a few Bio verbs (qok prefix)
bio_verbs = [item for item in bio_items if item.get('prefix') == 'qok']
print("Sample Bio verbs:", [item['original'] for item in bio_verbs[:5]])

# Sample a few sentences split by dy
# We need to see if 'dy' is a word or suffix that ends a sentence.
# Task says "Use dy ... to split".
# If 'dy' is a suffix, maybe words ending in 'dy' end sentences?
# Or if 'dy' is a separate word.

import re

text = "ytai!n example!word test!"
print(f"Original: '{text}'")

# Simulate master_dict.py logic
tokens_findall = re.findall(r"[a-zA-Z0-9]+", text)
print(f"re.findall: {tokens_findall}")

# Simulate simple split
tokens_split = text.split()
print(f"split: {tokens_split}")

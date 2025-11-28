
import re

SUBJECTS = {
    "patient", "sick", "priest", "cohen", "woman", "nymph", "bather", "attendant", "she", "he", "person",
    "olchey", "chol", "oror", "man"
}
VERBS = {
    "cook", "boil", "extract", "draw", "heat", "fire", "burn", "wash", "clean", "bathe", "drink", "eat", "take", "mix", "rub", "apply", "enter", "exit", "soak", "stand", "sit", "pour"
}
OBJECTS = {
    "mixture", "decoction", "water", "spring", "pool", "bath", "tub", "root", "herb", "plant", "oil", "ointment", "vapor", "steam", "stone", "pipe", "spout", "boil", "liquid", "honey"
}

line_content = "AND measure/portion cook/process the (+ noun) ? ? THAT preposition/conjunction finger ? Extract/Draw out the (+ noun) the/of Mixture/Decoction spring/source Conjunction (And/Then)"

def clean_token(token):
    t = token.replace("**", "").replace(":", "").lower()
    return re.split(r'[^a-z]+', t)

raw_tokens = line_content.split()
all_subtokens = []
for t in raw_tokens:
    all_subtokens.extend(clean_token(t))

tokens = [t for t in all_subtokens if t]

found_subjects = []
for t in tokens:
    if t in SUBJECTS:
        found_subjects.append(t)

print(f"Tokens: {tokens}")
print(f"Found Subjects: {found_subjects}")

# EVA to AVA Mapper
# Based on Edith Sherwood's "The Voynich Botanical Plant Names Decoded"
# Table 4: The AVA Alphabet

def to_ava(eva_text):
    """
    Convert EVA text to AVA (Sherwood's Alphabet).
    
    Mapping based on visual similarity described by Sherwood:
    EVA -> AVA
    o -> o
    a -> a
    e -> e
    i -> i
    d (8) -> b (Sherwood: "8-shaped symbol represents b")
    y (9) -> a (Sherwood: "9-shaped symbol... may also represent a")
             Note: She says it's 'a' or 'm' or 'n'. "Trial and error... may also represent a".
             Let's try 'a' as primary for now.
    l -> l
    p -> p
    s -> s
    g -> g (Sherwood: "a and g are similar", likely EVA g maps to AVA g)
    r -> r
    m -> m
    n -> n
    ch -> c (Sherwood: "c may also represent ch")
    sh -> s? (She maps EVA 'sh' to 's' in Table 1)
    ee -> e (or just keep ee?) She says "This symbol for l may also represent two l's".
    
    Let's build a char-by-char map first.
    """
    
    # Direct Character Map
    # EVA chars: o, a, y, l, r, d, s, e, i, ch, sh, k, t, p, f, m, n
    
    mapping = {
        'o': 'o',
        'a': 'a',
        'e': 'e',
        'i': 'i',
        'd': 'b',  # EVA '8' is 'd', Sherwood '8' is 'b'
        'y': 'a',  # EVA '9' is 'y', Sherwood '9' is 'a' (or 'm'/'n' sometimes)
        'l': 'l',
        'r': 'r',
        's': 's',
        'g': 'g',  # EVA 'g' is rare, but exists
        'p': 'p',
        'f': 'f',
        'k': 't',  # EVA 'k' (gallows) -> Sherwood 't'? Table 4 says 't' looks like gallows.
                   # Wait, Table 4 has a gallows for 't'. 
                   # EVA 't' (gallows) -> AVA 't'.
                   # EVA 'k' (gallows) -> AVA 't'? or 'k'? Sherwood says Italian has no K.
                   # Let's map EVA k/t to t for now.
        't': 't',
        'm': 'm',  # EVA 'm' (in 'in', 'iin')
        'n': 'n',  # EVA 'in' is often 'n'?
        'c': 'c',  # EVA 'c' (in 'ch')
        'h': 'h'   # EVA 'h' (in 'ch', 'sh')
    }
    
    # Sherwood specific digraph handling
    # She says 'ch' -> 'c' or 'ch'
    # She says 'sh' -> 's' (Table 1 shows 's' glyph is EVA 's', but what about 'sh'?)
    # Let's stick to char-by-char for now, as her anagram method allows reordering anyway.
    
    ava_chars = []
    for char in eva_text:
        if char in mapping:
            ava_chars.append(mapping[char])
        else:
            # Keep unknown chars or skip?
            # Keep for now to see what we miss
            if char.isalpha():
                ava_chars.append(char)
            # Skip punctuation
            
    return "".join(ava_chars)

def convert_file(input_path, output_path):
    with open(input_path, 'r') as f:
        text = f.read()
    
    ava_text = to_ava(text)
    
    with open(output_path, 'w') as f:
        f.write(ava_text)

if __name__ == "__main__":
    # Test string
    test_eva = "daiin chol"
    # d->b, a->a, i->i, i->i, n->n | ch->ch, o->o, l->l
    # baiin chol
    print(f"Test: {test_eva} -> {to_ava(test_eva)}")

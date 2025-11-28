
import os

output_path = "data/external_corpora/latin_medical.txt"

# Categories of Medieval Medical/Herbal Latin
plants = [
    "herba", "radix", "folium", "flos", "semen", "fructus", "cortex", "succus",
    "rosa", "lilium", "salvia", "ruta", "mentha", "betonica", "plantago",
    "artemisia", "foeniculum", "absinthium", "aloes", "myrrha", "crocus",
    "piper", "zingiber", "cinnamomum", "laurus", "oliva", "vitis", "uva",
    "ficus", "malum", "pyrum", "prunus", "cerasus", "nux", "glandes",
    "quercus", "fagus", "pinus", "abies", "cedrus", "juniperus", "cupressus",
    "populus", "salix", "tilia", "ulmus", "fraxinus", "sambucus", "ebulus",
    "hedera", "viscum", "muscus", "fungus", "boletus", "triticum", "hordeum",
    "avena", "secale", "milium", "paniculum", "faba", "pisum", "lens",
    "cicer", "lupinus", "allium", "cepa", "porrum", "brassica", "caulis",
    "rapa", "napus", "daucus", "pastinaca", "apium", "petroselinum",
    "coriandrum", "cuminum", "anethum", "carvi", "sinapis", "papaver",
    "hyoscyamus", "mandragora", "solanum", "helleborus", "aconitum",
    "cicuta", "verbena", "melissa", "lavandula", "rosmarinus", "hyssopus",
    "thymus", "origanum", "majorana", "basilicum", "satureja", "pulegium",
    "nepeta", "calamintha", "marrubium", "scordium", "chamaedrys",
    "centaurium", "hypericum", "agrimonia", "potentilla", "tormentilla",
    "fragaria", "rubus", "cynirrhodon", "spina", "carduus", "urtica",
    "rumex", "acetosa", "lapathum", "polygonum", "persicaria", "bistorta",
    "rheum", "liquiritia", "glycyrrhiza", "gentiana", "aristolochia",
    "asarum", "cyclamen", "primula", "verbascum", "digitalis", "scrophularia",
    "linaria", "antirrhinum", "euphrasia", "pedicularis", "melampyrum",
    "orobanche", "cuscuta", "convolvulus", "ipomoea", "borago", "anchusa",
    "lithospermum", "echium", "symphytum", "pulmonaria", "myosotis",
    "viola", "cheiranthus", "matthiola", "hesperis", "sisymbrium", "erysimum",
    "nasturtium", "cochlearia", "draba", "thlaspi", "iberis", "alyssum",
    "lunaria", "cardamine", "dentaria", "arabis", "turritis", "reseda"
]

anatomy = [
    "caput", "cerebrum", "oculus", "auris", "nasus", "os", "lingua", "dens",
    "collum", "humerus", "brachium", "manus", "digitus", "pectus", "cor",
    "pulmo", "stomachus", "jecur", "hepar", "splen", "ren", "intestinum",
    "viscera", "uterus", "vulva", "testiculus", "membrum", "crus", "genu",
    "pes", "cutis", "caro", "os", "ossis", "nervus", "vena", "arteria",
    "sanguis", "phlegma", "cholera", "melancholia", "spiritus", "anima",
    "corpus", "cadaver", "sceleton", "vertebra", "costa", "pelvis", "femur",
    "tibia", "fibula", "tarsus", "metatarsus", "phalanges", "cranium",
    "maxilla", "mandibula", "cartilago", "tendo", "ligamentum", "musculus",
    "adeps", "pinguedo", "medulla", "cerebellum", "nucha", "guttur",
    "fauces", "larynx", "pharynx", "esophagus", "trachea", "bronchus",
    "diaphragma", "peritoneum", "omentum", "mesenterium", "pancreas",
    "vesica", "urina", "sperma", "menstrua", "lac", "saliva", "mucus",
    "sudor", "lachryma", "pus", "sanies", "virus"
]

diseases = [
    "morbus", "aegritudo", "dolor", "febris", "pestis", "plaga", "vulnus",
    "ulcus", "tumor", "apostema", "inflammatio", "rubor", "calor", "dryas",
    "hydrops", "icterus", "lepra", "scabies", "pruritus", "tussis",
    "coryza", "catarrhus", "asthma", "dyspnoea", "phthisis", "haemoptysis",
    "pleuritis", "peripneumonia", "cardiaca", "syncope", "palpitatio",
    "anorexia", "nausea", "vomitus", "dyspepsia", "colica", "iliaca",
    "dysenteria", "lienteria", "diarrhea", "constipatio", "haemorrhoides",
    "vermes", "lumbrici", "ascarides", "calculus", "gravedo", "vertigo",
    "apoplexia", "paralysis", "spasmus", "convulsio", "epilepsia", "mania",
    "melancholia", "phrenitis", "lethargus", "coma", "vigilia", "insomnia",
    "cephalaea", "hemicrania", "migrana", "ophthalmia", "otitis", "angina"
]

actions = [
    "coque", "bibe", "misce", "fiat", "sume", "recipe", "da", "signa",
    "solve", "tere", "pulverisa", "distilla", "sublima", "calcfac", "frigida",
    "humecta", "sicca", "purga", "vomit", "laxa", "astringe", "incide",
    "attenua", "matura", "superpone", "applica", "unge", "lava", "balnea",
    "fomenta", "sacarifica", "phlebotoma", "ventosa", "cauterisa", "cura",
    "sana", "medica", "praepara", "serva", "custodi", "claude", "aperi",
    "move", "quiesce", "ambula", "dormi", "vigila", "ede", "jejuna",
    "abstine", "utere", "frui", "vive", "mori"
]

general = [
    "aqua", "ignis", "terra", "aer", "aether", "lux", "tenebrae", "sol",
    "luna", "stella", "sidus", "planet", "mundus", "caelum", "deus",
    "angelus", "diabolus", "spiritus", "materia", "forma", "substantia",
    "qualitas", "quantitas", "relatio", "actio", "passio", "locus", "tempus",
    "dies", "nox", "hora", "mensis", "annus", "aestas", "hiems", "ver",
    "autumnus", "calidus", "frigidus", "humidus", "siccus", "bonus",
    "malus", "magnus", "parvus", "longus", "brevis", "latus", "angustus",
    "altus", "profundus", "gravis", "levis", "durus", "mollis", "asper",
    "levis", "acutus", "obtusus", "dulcis", "amarus", "acidus", "acer",
    "salsus", "insipidus", "foetidus", "fragrans", "ruber", "albus",
    "niger", "viridis", "flavus", "caeruleus", "violaceus", "purpureus",
    "aureus", "argenteus", "ferreus", "plumbeus", "cupreus", "stanneus"
]

all_words = plants + anatomy + diseases + actions + general

# Add some variations/inflections implicitly by adding common suffixes if needed, 
# or just keep the base forms. For 1000 words, we can duplicate with inflections.
# Let's generate genitive/plural forms for nouns to expand the list.
expanded_words = []
for word in all_words:
    expanded_words.append(word)
    # Simple naive Latin inflection rules for expansion
    if word.endswith("a"):
        expanded_words.append(word[:-1] + "ae") # genitive/plural
        expanded_words.append(word + "m") # accusative
    elif word.endswith("us"):
        expanded_words.append(word[:-2] + "i") # genitive/plural
        expanded_words.append(word[:-2] + "um") # accusative
    elif word.endswith("um"):
        expanded_words.append(word[:-2] + "i") # genitive
        expanded_words.append(word[:-2] + "a") # plural
    elif word.endswith("o"):
        expanded_words.append(word + "nis") # some 3rd declension guess
    elif word.endswith("is"):
        expanded_words.append(word) # often same in genitive
    
    # Verb simple imperatives/infinitives
    if word in actions:
        if word.endswith("e"): # coque -> coquere
            expanded_words.append(word + "re")
        if word.endswith("a"): # sana -> sanare
            expanded_words.append(word + "re")

# Deduplicate and sort
final_corpus = sorted(list(set(expanded_words)))

print(f"Generated {len(final_corpus)} words.")

with open(output_path, "w") as f:
    for word in final_corpus:
        f.write(word + "\n")

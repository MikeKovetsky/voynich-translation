import os


absolute_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(absolute_path, "..")
library = os.path.join(root, "library")


class Paths:
    root = root
    library = library
    researcher_history = os.path.join(library, "history", "researcher")
    manager_history = os.path.join(library, "history", "manager")
    mastermind_history = os.path.join(library, "history", "mastermind")
    master_dictionary = os.path.join(library, "dictionary", "master_dictionary.json")
    usage_metadata = os.path.join(root, "usage_metadata")

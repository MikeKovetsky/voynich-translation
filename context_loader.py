import os
import glob
import json

# Paths
TRUTH_FILE = "artifacts/established_truths.md"
PROGRESS_DIR = "progress"
DICT_FILE = "results/dictionary/master_dictionary_v20.json"

def load_truths():
    if not os.path.exists(TRUTH_FILE):
        return "No established truths file found."
    with open(TRUTH_FILE, 'r') as f:
        return f.read()

def load_recent_progress(n=3):
    files = glob.glob(os.path.join(PROGRESS_DIR, "*.txt"))
    # Sort by iteration number (filename is '103.txt', etc)
    # Need to handle integer sorting
    try:
        files.sort(key=lambda x: int(os.path.basename(x).split('.')[0]))
    except:
        files.sort() # Fallback
        
    recent = files[-n:]
    output = []
    for fpath in recent:
        with open(fpath, 'r') as f:
            content = f.read()
            # Summarize? Or just dump?
            # Just dump header and content
            output.append(f"--- {os.path.basename(fpath)} ---")
            output.append(content)
            output.append("")
    return "\n".join(output)

def load_dict_stats():
    if not os.path.exists(DICT_FILE):
        return "Dictionary not found."
    
    try:
        with open(DICT_FILE, 'r') as f:
            data = json.load(f)
            
        entries = data.get('entries', {})
        total = len(entries)
        confirmed = sum(1 for k, v in entries.items() if v.get('translation_status') == 0 or v.get('confidence', 0) >= 0.9)
        
        return f"Dictionary v20: {total} entries. Confirmed Anchors: {confirmed} ({confirmed/total*100:.1f}% coverage)."
    except:
        return "Error reading dictionary."

def main():
    print("\n" + "="*50)
    print("VOYNICH MISSION BRIEFING")
    print("="*50 + "\n")
    
    print(">>> STATUS REPORT")
    print(load_dict_stats())
    print("\n")
    
    print(">>> ESTABLISHED TRUTHS (The Constitution)")
    print(load_truths())
    print("\n")
    
    print(">>> RECENT PROGRESS (Last 3 Iterations)")
    print(load_recent_progress())
    print("="*50)
    print("READY FOR COMMANDS.")

if __name__ == "__main__":
    main()

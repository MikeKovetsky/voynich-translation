import os
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_file_size(filepath):
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_python_imports(filepath):
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('import '):
                    mod = line.split()[1].split('.')[0]
                    imports.add(mod)
                elif line.startswith('from '):
                    mod = line.split()[1].split('.')[0]
                    imports.add(mod)
    except:
        pass
    return imports

def analyze_voynich_data():
    eva_path = ROOT / 'data' / 'eva_ivtff.txt'
    if not eva_path.exists():
        return None
    
    words = Counter()
    pages = set()
    text_lines = 0
    
    with open(eva_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            if line.strip():
                text_lines += 1
                # Extract page refs like <f1r>
                page_match = re.search(r'<(f\d+[rv]?)>', line)
                if page_match:
                    pages.add(page_match.group(1))
                # Extract words (EVA characters)
                tokens = re.findall(r'[a-z]+', line.lower())
                words.update(tokens)
    
    return {
        'text_lines': text_lines,
        'unique_words': len(words),
        'total_tokens': sum(words.values()),
        'pages': len(pages),
        'top_words': words.most_common(15)
    }

def analyze_results():
    results_dir = ROOT / 'results'
    if not results_dir.exists():
        return None
    
    json_files = list(results_dir.glob('*.json'))
    md_files = list(results_dir.glob('*.md'))
    
    total_json_entries = 0
    for jf in json_files:
        try:
            with open(jf, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    total_json_entries += len(data)
                elif isinstance(data, list):
                    total_json_entries += len(data)
        except:
            pass
    
    return {
        'json_files': len(json_files),
        'md_files': len(md_files),
        'total_json_entries': total_json_entries
    }

def main():
    print("=" * 60)
    print("📊 VOYNICH REPO STATISTICS")
    print("=" * 60)
    
    # Collect all files
    py_files = []
    txt_files = []
    json_files = []
    md_files = []
    img_files = []
    other_files = []
    
    all_imports = set()
    
    for root, dirs, files in os.walk(ROOT):
        # Skip hidden dirs and common ignores
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for fname in files:
            if fname.startswith('.'):
                continue
            fpath = Path(root) / fname
            
            if fname.endswith('.py'):
                py_files.append(fpath)
                all_imports.update(get_python_imports(fpath))
            elif fname.endswith('.txt'):
                txt_files.append(fpath)
            elif fname.endswith('.json'):
                json_files.append(fpath)
            elif fname.endswith('.md'):
                md_files.append(fpath)
            elif fname.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                img_files.append(fpath)
            else:
                other_files.append(fpath)
    
    # Calculate stats
    py_lines = sum(count_lines(f) for f in py_files)
    txt_lines = sum(count_lines(f) for f in txt_files)
    json_lines = sum(count_lines(f) for f in json_files)
    md_lines = sum(count_lines(f) for f in md_files)
    
    total_size = sum(get_file_size(f) for f in py_files + txt_files + json_files + md_files + img_files + other_files)
    code_size = sum(get_file_size(f) for f in py_files)
    data_size = sum(get_file_size(f) for f in txt_files + json_files)
    img_size = sum(get_file_size(f) for f in img_files)
    
    # Find largest files
    all_code_files = [(f, get_file_size(f), count_lines(f)) for f in py_files]
    all_code_files.sort(key=lambda x: x[2], reverse=True)
    
    print("\n📁 FILE COUNTS")
    print("-" * 40)
    print(f"  Python scripts:     {len(py_files):>5}")
    print(f"  Text files:         {len(txt_files):>5}")
    print(f"  JSON files:         {len(json_files):>5}")
    print(f"  Markdown files:     {len(md_files):>5}")
    print(f"  Image files:        {len(img_files):>5}")
    print(f"  Other:              {len(other_files):>5}")
    print(f"  ─────────────────────────")
    print(f"  TOTAL:              {len(py_files) + len(txt_files) + len(json_files) + len(md_files) + len(img_files) + len(other_files):>5}")
    
    print("\n📝 LINE COUNTS")
    print("-" * 40)
    print(f"  Python code:        {py_lines:>7,}")
    print(f"  Text data:          {txt_lines:>7,}")
    print(f"  JSON data:          {json_lines:>7,}")
    print(f"  Markdown docs:      {md_lines:>7,}")
    print(f"  ─────────────────────────")
    print(f"  TOTAL:              {py_lines + txt_lines + json_lines + md_lines:>7,}")
    
    print("\n💾 SIZE BREAKDOWN")
    print("-" * 40)
    print(f"  Python code:        {format_size(code_size):>10}")
    print(f"  Text/JSON data:     {format_size(data_size):>10}")
    print(f"  Images:             {format_size(img_size):>10}")
    print(f"  ─────────────────────────")
    print(f"  TOTAL:              {format_size(total_size):>10}")
    
    print("\n🔝 LARGEST PYTHON FILES (by lines)")
    print("-" * 40)
    for fpath, size, lines in all_code_files[:10]:
        name = fpath.relative_to(ROOT)
        print(f"  {lines:>5} lines  {name}")
    
    print("\n📦 DEPENDENCIES USED")
    print("-" * 40)
    stdlib = {'os', 'sys', 'json', 're', 'collections', 'pathlib', 'datetime', 
              'time', 'math', 'random', 'typing', 'functools', 'itertools',
              'string', 'copy', 'glob', 'shutil', 'subprocess', 'argparse',
              'logging', 'io', 'pickle', 'csv', 'statistics', 'unicodedata',
              'difflib', 'textwrap', 'http', 'urllib', 'concurrent'}
    
    external = sorted([i for i in all_imports if i not in stdlib and not i.startswith('_')])
    stdlib_used = sorted([i for i in all_imports if i in stdlib])
    
    print(f"  Standard library: {', '.join(stdlib_used[:12])}")
    if len(stdlib_used) > 12:
        print(f"                    {', '.join(stdlib_used[12:])}")
    print(f"  External:         {', '.join(external) if external else 'None'}")
    
    # Voynich-specific stats
    voynich = analyze_voynich_data()
    if voynich:
        print("\n📜 VOYNICH MANUSCRIPT DATA")
        print("-" * 40)
        print(f"  Transcription lines:  {voynich['text_lines']:>7,}")
        print(f"  Unique words (EVA):   {voynich['unique_words']:>7,}")
        print(f"  Total word tokens:    {voynich['total_tokens']:>7,}")
        print(f"  Pages covered:        {voynich['pages']:>7}")
        print(f"\n  Most common EVA words:")
        for word, count in voynich['top_words'][:10]:
            print(f"    {word:<15} {count:>6,} occurrences")
    
    # Results analysis
    results = analyze_results()
    if results:
        print("\n📊 RESULTS DATA")
        print("-" * 40)
        print(f"  JSON result files:    {results['json_files']:>7}")
        print(f"  Markdown reports:     {results['md_files']:>7}")
        print(f"  Total JSON entries:   {results['total_json_entries']:>7,}")
    
    # Fun stats
    print("\n🎯 FUN FACTS")
    print("-" * 40)
    avg_lines = py_lines / len(py_files) if py_files else 0
    print(f"  Avg lines per Python file:  {avg_lines:.0f}")
    
    # Count task files
    tasks_dir = ROOT / 'tasks'
    if tasks_dir.exists():
        task_count = len(list(tasks_dir.glob('*.txt')))
        print(f"  Research tasks tracked:     {task_count}")
    
    # Estimate effort
    hours_estimate = py_lines / 50  # rough: 50 lines/hour
    print(f"  Estimated dev hours:        ~{hours_estimate:.0f}")
    
    # Unique function names
    func_names = []
    for pf in py_files:
        try:
            with open(pf, 'r') as f:
                for line in f:
                    match = re.match(r'def\s+(\w+)\s*\(', line)
                    if match:
                        func_names.append(match.group(1))
        except:
            pass
    print(f"  Functions defined:          {len(func_names)}")
    print(f"  Unique function names:      {len(set(func_names))}")
    
    print("\n" + "=" * 60)
    print("🔬 Happy decoding the Voynich Manuscript!")
    print("=" * 60)

if __name__ == '__main__':
    main()

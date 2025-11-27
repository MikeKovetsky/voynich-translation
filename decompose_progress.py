import re
import os

def parse_file(filepath, pattern_name, regex):
    results = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return results

    # Split by lines to find headers
    lines = content.split('\n')
    current_id = None
    current_content = []
    
    for line in lines:
        match = re.search(regex, line)
        if match:
            if current_id is not None:
                results[current_id] = '\n'.join(current_content).strip()
            current_id = int(match.group(1))
            current_content = [line]
        elif current_id is not None:
            current_content.append(line)
            
    if current_id is not None:
        results[current_id] = '\n'.join(current_content).strip()
        
    print(f"Found {len(results)} {pattern_name}s in {filepath}")
    return results

def main():
    # Parse Steps from progress.md
    steps = parse_file('progress.md', 'Step', r'^##.*Step\s+(\d+)')
    
    # Parse Tracks from progress_summary.md
    tracks = parse_file('progress_summary.md', 'Track', r'^##.*Track\s+(\d+)')
    
    # Parse Iterations from progress_summary.md
    iterations1 = parse_file('progress_summary.md', 'Iteration', r'^##.*Iteration\s+(\d+)')
    
    # Parse Iterations from progress_summary_2.md
    iterations2 = parse_file('progress_summary_2.md', 'Iteration', r'^##.*Iteration\s+(\d+)')
    
    # Combine
    final_files = {}
    
    # Strategy:
    # 1. Use Steps 1-11 (approx)
    # 2. Use Tracks for middle ground if Steps missing? 
    #    Actually, let's check overlap.
    
    # If Steps exist, use them.
    for i, content in steps.items():
        final_files[i] = content
        
    # If Tracks exist and no file yet, use Track.
    for i, content in tracks.items():
        if i not in final_files:
            final_files[i] = content
        else:
            # Conflict? Steps usually have "Step X: Title". Tracks have "Track X: Title".
            # Step 1 in progress.md is "Research Phase". Track 1 is "Statistical Analysis".
            # Step 2 is "Statistical Analysis". So Step N ~= Track N-1?
            # Let's prefer Steps for early files as they are in the main log.
            pass

    # Iterations usually override or extend.
    # Iteration 38+ seems to be the later sequence.
    for i, content in iterations1.items():
        final_files[i] = content
        
    for i, content in iterations2.items():
        final_files[i] = content
        
    # Output stats
    print(f"Total unique files prepared: {len(final_files)}")
    print(f"Missing: {[i for i in range(1, 61) if i not in final_files]}")
    
    # Write to progress/
    os.makedirs('progress', exist_ok=True)
    for i in range(1, 61):
        if i in final_files:
            with open(f'progress/{i}.txt', 'w', encoding='utf-8') as f:
                f.write(final_files[i])
        else:
            # Placeholder if missing
            print(f"Warning: File {i} is missing content. Creating placeholder.")
            with open(f'progress/{i}.txt', 'w', encoding='utf-8') as f:
                f.write(f"Iteration {i}\n\nStatus: Missing from summaries.")

if __name__ == "__main__":
    main()

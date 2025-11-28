import os

def concatenate_progress(start_number, end_number):
    """
    Concatenates progress text files from start_number to end_number (inclusive).
    """
    progress_dir = "progress"
    separator = "\n" + "="*40 + "\n"
    
    print(f"--- Concatenating Progress Files {start_number} to {end_number} ---\n")

    for i in range(start_number, end_number + 1):
        file_path = os.path.join(progress_dir, f"{i}.txt")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"FILE: {i}.txt")
                    print(separator)
                    print(content)
                    print(separator + "\n")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"Warning: {file_path} does not exist.\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Concatenate progress files.")
    parser.add_argument("start", type=int, help="Start file number")
    parser.add_argument("end", type=int, help="End file number")
    
    args = parser.parse_args()
    
    concatenate_progress(args.start, args.end)

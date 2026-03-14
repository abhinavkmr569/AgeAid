import os

# --- CONFIGURATION ---
OUTPUT_FILE = "full_codebase1.txt"
TARGET_EXTENSIONS = {".py", ".md", ".yml", ".yaml", ".txt"}
IGNORE_DIRS = {".git", "__pycache__", "env", "venv", ".venv", ".idea", ".vscode", "alembic"}
IGNORE_FILES = {"code_consolidator.py", ".env", "root.crt", "package-lock.json"}
SPECIAL_FILENAMES = {"dockerfile"}  # lowercase for case-insensitive comparison

def is_text_file(filename):
    # Special case for files with no extension (e.g. Dockerfile)
    if filename.lower() in SPECIAL_FILENAMES:
        return True
    return os.path.splitext(filename)[1] in TARGET_EXTENSIONS

def consolidate_code():
    root_dir = os.getcwd()
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            
            for filename in filenames:
                if filename in IGNORE_FILES:
                    continue
                    
                if is_text_file(filename):
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            outfile.write("="*50 + "\n")
                            outfile.write(f"FILE: {relative_path}\n")
                            outfile.write("="*50 + "\n")
                            outfile.write(content)
                            outfile.write("\n\n")
                            print(f"✅ Added: {relative_path}")
                            
                    except Exception as e:
                        print(f"❌ Could not read {relative_path}: {e}")

    print(f"\n✨ Done! All code saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    consolidate_code()
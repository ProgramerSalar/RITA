import os
import random
import time

def rename_folder_contents(target_folder):
    # --- CONFIGURATION ---
    # Paste your folder path inside the quotes below:
    # Example: target_folder = r"C:\Users\Name\Downloads\Videos"
    # target_folder = r"YOUR_FOLDER_PATH_HERE" 
    # ---------------------

    split_base_folder = target_folder.split('/')[-1]
    # print(split_base_folder)
    

    # Check if folder exists
    if not os.path.exists(target_folder):
        print(f"Error: Folder not found: {target_folder}")
        return

    # print(f"Target Folder: {target_folder}")
    # confirm = input("Are you sure you want to rename all files to random numbers? (Type 'yes'): ")
    # if confirm.lower() != 'yes':
    #     print("Operation cancelled.")
    #     return

    # Create log file for safety
    log_file = os.path.join(target_folder, "rename_history_log.txt")
    
    files = os.listdir(target_folder)
    count = 0
    used_numbers = set()

    print("\nProcessing...")

    for filename in files:
        # Skip the log file and hidden files
        if filename == "rename_history_log.txt" or filename.startswith("."):
            continue

        old_path = os.path.join(target_folder, filename)

        if os.path.isfile(old_path):
            name, ext = os.path.splitext(filename)
            
            # Generate unique random number
            while True:
                # Generates a number like 481920
                new_num = str(random.randint(100000, 999999))
                if new_num not in used_numbers:
                    used_numbers.add(new_num)
                    break
            

            new_filename = f"{split_base_folder}_{new_num}{ext}"
            new_path = os.path.join(target_folder, new_filename)

            # Rename
            try:
                os.rename(old_path, new_path)
                
                # Write to log
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"{new_filename} <-- {filename}\n")
                
                print(f"[OK] {new_filename}")
                count += 1
            except Exception as e:
                print(f"[ERROR] Could not rename {filename}: {e}")

    print("-" * 30)
    print(f"Done! {count} files renamed.")
    print(f"History saved in: {log_file}")


if __name__ == "__main__":
    path = "../part_1"

    # rename_folder_contents(path)

    for root, dirs, files in os.walk(path):
        print(root)

        if root == path:
            pass 
        else:
            # print('not working...')
            rename_folder_contents(root)

   
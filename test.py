import re, os, glob, json
import pandas as pd 

def clean_srt_file(file_path):

    if not os.path.exists(file_path):
        print("file path does not found.")
        exit()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'^\d+$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', content)
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    full_text = ''.join(lines)
    
    return full_text
    

def generate_dataset_json(folder_path, output_json_name="../dataset_map.json"):
    """
    Scans a folder for related video files (mp4, jpg, json, srt),
    groups them by common filename, and creates a consolidated JSON file.
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found at {folder_path}")
        return

    # Dictionary to temporarily hold grouped data
    # Key = Base Filename (unique ID), Value = Dict of paths
    grouped_data = {}

    # 1. List all files
    files = os.listdir(folder_path)

    # Define suffixes to strip so we can find the "Common Name"
    # IMPORTANT: Longer suffixes must be checked first!
    # e.g., check ".info.json" before ".json"
    suffixes_map = [
        ('.info.json', 'metadata'),
        ('.json', 'metadata'),
        ('.en.srt', 'subtitle'), # specific language subs
        ('.srt', 'subtitle'),    # generic subs
        ('.jpg', 'thumbnail'),
        ('.webp', 'thumbnail'),
        ('.png', 'thumbnail'),
        ('.mp4', 'video'),
        ('.mkv', 'video'),
        ('.webm', 'video')
    ]

    print(f"Scanning {len(files)} files...")

    for filename in files:
        full_path = os.path.join(folder_path, filename)
        
        # Skip directories
        if os.path.isdir(full_path):
            continue

        # 2. Identify the "Base Name" and "File Type"
        base_name = None
        file_type = None

        for suffix, f_type in suffixes_map:
            if filename.endswith(suffix):
                # Remove the suffix to get the unique ID/Base Name
                # e.g. "Video1.info.json" -> "Video1"
                base_name = filename[:-len(suffix)] 
                file_type = f_type
                break
        
        # If we found a recognized file type
        if base_name and file_type:
            # Initialize entry if not exists
            if base_name not in grouped_data:
                grouped_data[base_name] = {
                    "id": base_name,
                    "video": None,
                    "metadata": None,
                    "Image": None,
                    "subtitle": None
                }
            
            # Store the absolute path
            grouped_data[base_name][file_type] = full_path

    # 3. Convert dictionary to a clean list
    dataset_list = list(grouped_data.values())

    # 4. Save to JSON file
    output_path = os.path.join(folder_path, output_json_name)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset_list, f, indent=4)
        print(f"Success! JSON saved at: {output_path}")
        print(f"Total complete entries found: {len(dataset_list)}")
        return dataset_list
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return []


if __name__ == "__main__":
    # --- USAGE ---
    folder_path = "./math_shorts_dataset/rational_number_math"

    # Run the function
    dataset = generate_dataset_json(folder_path)

    json_path = "/home/manish/Desktop/projects/rita/math_shorts_dataset/dataset_map.json"

    with open(json_path, 'r') as f:
        data = json.load(f)
        for file in data:

            # caption capture 
            caption_path = file['subtitle']
            capation_path = str(caption_path)
            if capation_path.endswith('.en.srt'):
                caption = clean_srt_file(capation_path)
                # print(caption)

            
            # capture json 
            json_path = file['metadata']
            json_path = str(json_path)
            if json_path.endswith('.json'):
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                    json_title = json_data['title']

            

                



        






    

    



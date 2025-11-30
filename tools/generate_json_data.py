import re, os, json, glob


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
    

def generate_dataset_json(folder_path, output_json_name = "./dataset_map.json"):
    """
    Scans a folder for related video files (mp4, jpg, json, srt),
    groups them by common filename, and creates a consolidated JSON file.
    """
    json_path = folder_path.split('/')[2]
    base_path = folder_path.split('/')[1]
    if not os.path.exists(f"{base_path}/json"):
        os.makedirs(f"{base_path}_json", exist_ok=True)

    json_path = f"./{base_path}_json/{json_path}_dataset_map.json"
    output_json_name = json_path


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
                    "subtitle": None,
                    "thumbnail": None
                  
                }
            
            # Store the absolute path
            grouped_data[base_name][file_type] = full_path

    # 3. Convert dictionary to a clean list
    dataset_list = list(grouped_data.values())

    # 4. Save to JSON file
    output_path = os.path.join(output_json_name)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset_list, f, indent=4)
        print(f"Success! JSON saved at: {output_path}")
        print(f"Total complete entries found: {len(dataset_list)}")
        return dataset_list
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return []
    
def Indent_json_data(json_path, folder_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
        json_format_list = []
        caption = ''
        json_title = ''
        for file in data:
            # print(file['subtitle'])
            # caption capture 
            caption_path = file['subtitle']
            capation_path = str(caption_path)
            if capation_path.endswith('.en.srt'):
                caption = clean_srt_file(capation_path)
                # print(caption)

            
            # capture json 
            new_json_path = file['metadata']
            new_json_path = str(new_json_path)
            if new_json_path.endswith('.info.json'):
                
                with open(new_json_path, 'r') as f:
                    try:
                        new_json_data = json.load(f)
                    except Exception as e:
                        print(f'getting the error.... {e}')

                    json_title = new_json_data['title']
            # print(json_title)

            json_format = {
                "id": file["id"],
                "video": file["video"],
                "title": json_title,
                "subtitle": caption,
                "Image": file["thumbnail"],
                "metadata": file["metadata"],
            }
            json_format_list.append(json_format)

        print(json_path)
       

        if not os.path.exists("./Indent_json"):
            os.makedirs("./Indent_json", exist_ok=True)
    
        split_dir = json_path.split("/")[2]
        split_dir = split_dir.split('.')[0]
        output_path = os.path.join(f"./Indent_json/{split_dir}_dataset.json")
    
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_format_list, f, indent=4)

        print(f"Successfully created the json: {output_path}")


def Run_Generation(folder_path):
    for root, dirs, files in os.walk(folder_path):

        if root == folder_path:
            print("Next Path..")
        else:
            folder_path = root
            generate_dataset_json(folder_path)


def Indent_Merge(folder_path):

    folder_path_json = f"{folder_path}_json"
    for root, dirs, files in os.walk(folder_path_json):
        for file in files:
            path = os.path.join(str(root), str(file)) 
            Indent_json_data(path, folder_path_json)
    

    json_path = "./Indent_json"

    json_files = glob.glob(os.path.join(json_path, "*.json"))
    json_data_list = []
    for path in json_files:
        with open(path, 'r') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"error getting {e}")
            json_data_list.extend(data)

    output_file_path = "merged_part1_data.json"
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data_list, f, indent=4)
    print(f"successfully created the json data.")



if __name__ == "__main__":
    
    # so only change the `folder_path` 
    folder_path = "./part_11"




    # for root, dirs, files in os.walk(folder_path):

    #     if root == folder_path:
    #         print("Next Path..")
    #     else:
    #         folder_path = root
    #         generate_dataset_json(folder_path)


    Run_Generation(folder_path)
    Indent_Merge(folder_path)

        
    
    print('------------------------------------------------------')
    

    # folder_path_json = f"{folder_path}_json"
    # for root, dirs, files in os.walk(folder_path_json):
    #     for file in files:
    #         path = os.path.join(str(root), str(file)) 
    #         Indent_json_data(path, folder_path_json)
    

    # json_path = "./Indent_json"

    # json_files = glob.glob(os.path.join(json_path, "*.json"))
    # json_data_list = []
    # for path in json_files:
    #     with open(path, 'r') as f:
    #         data = json.load(f)
    #         json_data_list.extend(data)

    # output_file_path = "merged_part1_data.json"
    # with open(output_file_path, 'w', encoding='utf-8') as f:
    #     json.dump(json_data_list, f, indent=4)
    # print(f"successfully created the json data.")

    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    

    

            
        


        
            
    

    
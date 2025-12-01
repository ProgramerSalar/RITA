import json 
import re 

def Filter_Json_Null_value(json_path):

    with open(json_path, 'r') as f:
        try:
            datas = json.load(f)
            matches = [
                d for d in datas 
                if d['video'] is not None
                and d['id'] 
                and d['subtitle']
                and d['Image']]
            
            new_json_data_list = []
            for m in matches:
                # print(f"Id: {m['id']}")
                # print(f"Video:", {m["video"]})
                # print(f"Subtitle: {m['subtitle']}")
                # print(f"Image: {m['Image']}")

                new_json_data = {
                    "Id": m['id'],
                    "Video": m['video'],
                    "Subtitle": m['subtitle'],
                    "Image": m['Image']
                }

                new_json_data_list.append(new_json_data)

            fine_tune_json = "./FineTune_json_data.json"

            print(new_json_data_list)
            with open(fine_tune_json, 'w', encoding='utf-8') as f:
                json.dump(new_json_data_list, f, indent=4)
        

            

        except Exception as e:
            print(f"error...... as {e}")


def Test_Filter_json(json_path):
    with open(json_path, 'r') as f:
        try:
            datas = json.load(f)
            
            unique_matches = []
            seen_ids = set()

            for d in datas:
                # 1. Get the ID
                current_id = d.get('id')

                # 2. Check if we have already seen this ID
                if current_id in seen_ids:
                    continue # Skip this loop iteration (don't add the clone)

                # 3. Validation: Check if video is NOT None, and other fields exist
                if (d.get('video') is not None 
                    and current_id 
                    and d.get('subtitle') 
                    and d.get('Image')):
                    
                    # If valid and unique, add to our list and mark ID as seen
                    unique_matches.append(d)
                    seen_ids.add(current_id)
            
            print(f"Found {len(unique_matches)} unique valid entries out of {len(datas)} total.")

            # Print the results
            for m in unique_matches:
                print("---")
                print(f"Id: {m['id']}")
                print(f"Video: {m['video']}")
                print(f"Subtitle: {m['subtitle']}")
                print(f"Image: {m['Image']}")

            # Optional: Save the clean, unique data to a new file
            # with open(output_path, 'w') as outfile:
            #     json.dump(unique_matches, outfile, indent=4)
            #     print(f"Saved unique data to {output_path}")

        except Exception as e:
            print(f"error...... as {e}")


def clean_subtitle_text(text):
    """
    Cleans subtitle text by removing brackets, noise words, and extra spaces.
    Returns an empty string if the subtitle is just noise.
    """
    if not isinstance(text, str):
        return str(text)
    
    # Remove text in brackets like [music], [Applause], [Music]
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove text in parentheses (like speaker notes)
    text = re.sub(r'\(.*?\)', '', text)
    
    # Remove the word 'foreign' (common ASR artifact)
    text = re.sub(r'\bforeign\b', '', text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and strip
    text = ' '.join(text.split())
    
    return text


def clean_text_content(text):
    """
    Cleans the subtitle text. 
    Returns None if the text is too short or invalid.
    """
    if not isinstance(text, str):
        return None
        
    # Remove 'foreign' (case insensitive)
    text = re.sub(r'\bforeign\b', '', text, flags=re.IGNORECASE)
    
    # Remove generic filler text like "thank you" if it's the ONLY thing there
    if text.strip().lower() in ['thank you', 'no', 'oh', 'he', 'you']:
        return None

    # Clean up whitespace
    text = ' '.join(text.split())
    
    # If text is too short (e.g., less than 5 characters), it's likely noise
    if len(text) < 5:
        return None
        
    return text


# matches = [
#                 d for d in datas 
#                 if d['video'] is not None
#                 and d['id'] 
#                 and d['subtitle']
#                 and d['Image']]

if __name__ == "__main__":

    # json_path = "./Json/merged_part1_data.json"
    new_json_path = "./FineTune_json_data.json"

    with open(new_json_path, 'r') as f:
        datas = json.load(f)

    unique_records = []
    seen_ids = set()

    duplicates = 0
    removed_bad_text = 0

    for d in datas:

        # 1. Get ID and ensure it exists 
        curr_id = d.get('Id')
        if not curr_id:
            continue

        # 2. Duplicate: Skip if we have seen this Id already 
        if curr_id in seen_ids:
            duplicates += 1 
            continue

        # 3. Get the text (handling 'text' or 'subtitle' keys)
        # we prefer 'text' based on your current file structure.
        raw_text = d.get('Subtitle')
        clean_sub_Text = clean_subtitle_text(raw_text)
        clean_text = clean_text_content(clean_sub_Text)
        
        if not clean_text:
            removed_bad_text += 1 
            continue

        new_record = {
            'id': curr_id,
            'video': d.get('Video'),
            'image': d.get('Image'),
            'subtitle': clean_text
        }
        unique_records.append(new_record)

    output_path = "./clean_json_data.json"
    with open(output_path, 'w') as f:
        json.dump(unique_records, f, indent=4)
    print("successfully....")

            

        
            
        


    


    

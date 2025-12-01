import json
import re

def clean_final_subtitle(text):
    if not isinstance(text, str):
        return None
    
    # 1. Remove specific noise words inside the text
    # Remove 'foreign' (common error)
    text = re.sub(r'\bforeign\b', '', text, flags=re.IGNORECASE)
    # Remove [music], [applause]
    text = re.sub(r'\[.*?\]', '', text)
    
    # 2. Clean up spaces
    text = ' '.join(text.split())
    
    # 3. Filter out "Useless" subtitles
    # If the ONLY thing in the subtitle is one of these words, delete the record.
    useless_phrases = ['thank you', 'no', 'oh', 'hey', 'so', 'music', 'applause']
    if text.lower() in useless_phrases:
        return None
        
    # 4. Length check: If left with less than 3 chars, it's garbage
    if len(text) < 3:
        return None

    return text

if __name__ == "__main__":
    input_file = "./clean_json_data.json"
    output_file = "./Final_Ready_For_FineTuning.json"

    print("Loading data...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    unique_data = []
    seen_ids = set()
    
    duplicates_removed = 0
    noise_removed = 0

    for entry in data:
        # 1. Get ID
        vid_id = entry.get('id')
        
        # 2. DEDUPLICATE: If we have seen this ID before, SKIP IT
        if vid_id in seen_ids:
            duplicates_removed += 1
            continue
            
        # 3. Clean Subtitle
        original_sub = entry.get('subtitle')
        clean_sub = clean_final_subtitle(original_sub)
        
        # If subtitle is bad/empty, skip this entry
        if not clean_sub:
            noise_removed += 1
            continue
            
        # 4. Add Valid Entry
        seen_ids.add(vid_id)
        
        # Update the entry with the cleaned subtitle
        entry['subtitle'] = clean_sub
        unique_data.append(entry)

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(unique_data, f, indent=4)

    print("-" * 30)
    print(f"Original Count:     {len(data)}")
    print(f"Duplicates Removed: {duplicates_removed}")
    print(f"Noise Removed:      {noise_removed}")
    print(f"Final Count:        {len(unique_data)}")
    print("-" * 30)
    print(f"Your perfect file is saved as: {output_file}")
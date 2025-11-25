import json
import os
import cv2

class RationalNumberDataset:
    def __init__(self, json_file_path, root_video_dir="."):
        """
        Args:
            json_file_path (str): Path to the dataset JSON file.
            root_video_dir (str): Directory prefix for video paths (if videos are in a subfolder).
        """
        self.root_video_dir = root_video_dir
        
        # Load the JSON data
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
            
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"Dataset loaded successfully. Found {len(self.data)} items.")

    def __len__(self):
        """Returns the total number of items in the dataset."""
        return len(self.data)

    def __getitem__(self, idx):
        """Returns the metadata dictionary for a specific index."""
        return self.data[idx]

    def load_video_capture(self, idx):
        """
        Loads the video capture object for a given index using OpenCV.
        
        Returns:
            cv2.VideoCapture object or None if video path is invalid/null.
        """
        item = self.data[idx]
        video_path = item.get('video')

        # specific check for null or empty paths
        if not video_path:
            print(f"[Warning] Item ID '{item.get('id')}' has no video path.")
            return None

        # Construct the full path
        full_path = os.path.join(self.root_video_dir, video_path)
        
        # normalize path for the OS (handles / vs \ issues)
        full_path = os.path.normpath(full_path)

        if not os.path.exists(full_path):
            print(f"[Error] Video file not found at: {full_path}")
            return None

        # Load video using OpenCV
        cap = cv2.VideoCapture(full_path)
        
        if not cap.isOpened():
            print(f"[Error] Could not open video file: {full_path}")
            return None
            
        return cap

# --- usage example ---

if __name__ == "__main__":
    json_file = "/home/manish/Desktop/projects/rita/rational_number_math_dataset.json"
    
    # Initialize the dataset
    # root_video_dir should be the folder where your 'math_shorts_dataset' folder resides
    dataset = RationalNumberDataset(json_file, root_video_dir=".")

    # Example: Loop through first 3 items
    for i in range(min(3, len(dataset))):
        print(f"\n--- Processing Item {i} ---")
        item_data = dataset[i]
        print(f"Title: {item_data['title']}")
        
        # Attempt to load the video
        cap = dataset.load_video_capture(i)
        
        if cap:
            # Read the first frame to prove it loaded
            ret, frame = cap.read()
            if ret:
                print(f"Success: Video loaded. Resolution: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("Failed to read frame.")
            
            # Always release the video resource
            cap.release()
        else:
            print("Skipping video load (Video missing or null).")


    
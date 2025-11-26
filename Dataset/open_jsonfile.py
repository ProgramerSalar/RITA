import json, glob, os 
from torch.utils.data import DataLoader

from video_dataset import VideoDataset






if __name__ == "__main__":

    json_path = "/home/manish/Desktop/projects/rita/testing_merged_part1_data.json"
    # out = OpenJsonFIle(json_path)

    checking_json_path = glob.glob(json_path)
    print('checking_json_path', checking_json_path)

    with open(json_path, 'r') as f:
            json_data = json.load(f)
            
            video_paths = [path['video'] for path in json_data]
            for video_path in video_paths:
    
                if video_path == None:
                    pass 
                else:
                    print(video_path)
                    checking_video_path = glob.glob(video_path)
                    print('checking_video_path: ', checking_video_path)
                     




                    # print("not None")
                    # video_dataset = VideoDataset(video_path)
                    # data = video_dataset.__getitem__(idx=0)
                    # print(data)
    
    
    
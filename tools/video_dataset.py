import torch 
from torch.utils.data import Dataset, DataLoader
import glob, os, cv2
from PIL import Image
from torchvision import transforms
from einops import rearrange

class VideoDataset(Dataset):

    def __init__(self,
                 video_files,
                 num_frames=16,
                 ):
        
        self.num_frames = num_frames
        if os.path.isfile(video_files):
            self.video_files = [video_files]
        elif os.path.isdir(video_files):
            self.video_files = glob.glob(pathname=(os.path.join(video_files, '*.mp4')))
        
        
                    

        
        

        self.transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(256),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.video_files)
    

    def _extract_frames(self, video_path):

        frames = []
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            ret, frame = cap.read()
            if not ret == True:
                os.remove(video_path)
            
            else:
                
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                if total_frames > 0:

                    # [0, 1573-1]
                    indices = torch.linspace(0, total_frames-1, self.num_frames).long()
                    
                    
                    for i in indices:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, i.item())
                        ret, frame = cap.read()
                        if ret:
                            # OpenCv reads frames in BGR format, convert to RGB 
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            # convert numpy array to PIL Image for torchvision transform 
                            frame_pil = Image.fromarray(frame_rgb)
                            frames.append(frame_pil)

                cap.release()

                # If video was shorter then num_frames, duplicate the last frame 
                while len(frames) < self.num_frames:
                    if frames:
                        frames.append(frames[-1])

                    
        return frames
    
    def __getitem__(self, idx):
        
        video_path = self.video_files[idx]
        frames = self._extract_frames(video_path)
        

        if not frames:
            return None
        
        

        
        transformed_frames = [self.transform(frame) for frame in frames]
        if len(transformed_frames) != 0:
            video_tensor = torch.stack(transformed_frames)
            video_tensor = rearrange(video_tensor, 't c h w -> c t h w')
            video_tensor = video_tensor.contiguous()
            

        return video_tensor
        

def collate_fn(batch):
    # Filter out None values
    batch = list(filter(lambda x: x is not None, batch))
    
    # If the whole batch is bad (empty), return None
    if len(batch) == 0:
        return None
        
    return torch.utils.data.dataloader.default_collate(batch)

if __name__ == "__main__":

    
    from repair_video import video_repair
    # folder_path = "./part_1"

    # for root, dirs, files in os.walk(folder_path):        
    #     video_files = glob.glob(os.path.join(root, "*.mp4"))

       
    #     for video_file in video_files:
    #         cap = cv2.VideoCapture(video_file)
    #         
    #         if cap.isOpened():
    #             ret, frame = cap.read()
    #             if not ret == True:
    #                 print(f"<<<<<<<<<<<<<<<<<<<<<{video_file}")
    #                 video_repair(video_file)
           
  

            
                
            
        
    #     dataset = VideoDataset(video_dir=root)
        
    #     train_dataloader = DataLoader(dataset=dataset,
    #                                 batch_size=1,
    #                                 num_workers=4,
    #                                 collate_fn=collate_fn)
        
    #     for i, data in enumerate(train_dataloader):
    #         if data is None:
    #             continue
    #         print(f"Index: {i} shape of data: {data.shape}")

    # print('successfully...........................................')
    # ----------------------------------------------------------------------------------------
    import json 

    json_path = "./part_5.json"

    with open(json_path, 'r') as f:
        json_datas = json.load(f)
        
        for data in json_datas:
            if not data['video'] == None:
                if os.path.exists(data['video']):
                
                    cap = cv2.VideoCapture(data['video'])
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if not ret == True:
                            video_repair(data['video'])

                    dataset = VideoDataset(video_files=data['video'])
                    train_dataloader = DataLoader(dataset=dataset, 
                                                batch_size=2,
                                                collate_fn=collate_fn)
                    
                    for video_tensor in train_dataloader:
                        print(video_tensor.shape)

        print('successfully.........................')



           
        





    
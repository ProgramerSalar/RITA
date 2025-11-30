import subprocess, os, cv2, glob 


def video_repair(video_path):


    if os.path.exists(video_path):

        # base_path = video_path.split('/')[1]
        # base_path = f"Repair_{base_path}"
        # base_file = video_path.split('/')[2:]
        
        # base_file = '/'.join(base_file)
        # output_path = f"./{base_path}/{base_file}"
        # print(output_path)

        # if not os.path.exists(f"./{base_path}"):
        #     os.makedirs(f"./{base_path}", exist_ok=True)

        # # subfolder
        # subdir = video_path.split('/')[2]
        # if not os.path.exists(f"./{base_path}/{subdir}"):
        #     os.makedirs(f"./{base_path}/{subdir}", exist_ok=True)

        base_file = video_path.split('/')[-1]
        base_path = video_path.split('/')[:-1]
        base_path = '/'.join(base_path)
        output_path = f"{base_path}/repair_{base_file}"
        
        

        try:
            cmd_method_1 = [
            "ffmpeg",
            "-y",                       # Overwrite output
            "-err_detect", "ignore_err", # Ignore decoding errors
            "-i", video_path,
            "-c:v", "libx264",          # Re-encode video
            "-preset", "ultrafast",     # Fast encoding speed
            "-crf", "28",               # Slightly lower quality to ensure stability
            "-c:a", "aac",              # Re-encode audio
            "-strict", "experimental",
            output_path
            ]

            # we supress output to keep console clean, change stderr to None to see FFmpeg logs 
            subprocess.run(cmd_method_1, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            temp_raw_file = output_path + ".h264"
            
            
        except Exception as e:
            print(e)

        
        try:
            cmd_extract_raw = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-map", "0:v",              # Select only video
                "-c:v", "copy",             # Copy stream
                "-bsf:v", "h264_mp4toannexb", # Convert to raw stream format
                temp_raw_file
            ]

            cmd_remux_raw = [
                "ffmpeg", "-y",
                "-i", temp_raw_file,
                "-c:v", "copy",
                output_path
            ]

            # Extract 
            subprocess.run(cmd_extract_raw, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Remux 
            subprocess.run(cmd_remux_raw, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # cleanup temp file 
            if os.path.exists(temp_raw_file):
                os.remove(temp_raw_file)

            # so this is the old video to delete
            if os.path.exists(video_path):
                os.remove(video_path)
                
            # currapted video are deleted.
            cap = cv2.VideoCapture(output_path)
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret == True:
                    print(f"<<<<<<<<<<<<<<<< {output_path}")
                    os.remove(output_path)
               

            

        except Exception as e:
            print(e)

        finally:
            print('working...')
            # so let's rename the output video 
            if os.path.exists(output_path):
                split_dir = output_path.split('/')[-1]
                remove_rapair_word = split_dir.replace("repair_", "")
                print(remove_rapair_word)
                rename = output_path.split('/')[:-1]
                rename = '/'.join(rename)
                remove_rapair_word = f"{rename}/{remove_rapair_word}"
                print(remove_rapair_word)
                os.rename(output_path, remove_rapair_word)



if __name__ == "__main__":
    
    folder_path = "./part_1"

    for root, dirs, files in os.walk(folder_path):        
        video_files = glob.glob(os.path.join(root, "*.mp4"))
        for video_file in video_files:
            video_repair(video_file)
    print("succesfully -------------------------------------------")

    


                

   

    
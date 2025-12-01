from pytube import YouTube

def download_video(link):
    try:
        youtubeObject = YouTube(link)
        youtubeObject = youtubeObject.streams.get_highest_resolution()
        youtubeObject.download()
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error has occurred: {e}")

# Get the YouTube video URL from the user
link = input("Enter the YouTube video URL: ")
download_video(link)

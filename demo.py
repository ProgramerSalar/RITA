import yt_dlp
import os, glob, re
import json
import csv
import time
from datetime import datetime

class YouTubeShortsDownloader:
    def __init__(self, output_base_dir="./shorts_dataset"):
        self.output_base_dir = output_base_dir
        self.metadata_file = os.path.join(output_base_dir, "metadata.csv")
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        if not os.path.exists(self.output_base_dir):
            os.makedirs(self.output_base_dir)
        
        # Initialize metadata file
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'video_id', 'title', 'channel', 'duration', 
                    'view_count', 'upload_date', 'download_date',
                    'search_query', 'file_path', 'transcript'
                ])
    
    def get_ydl_opts(self, search_query, category):
        """Get yt-dlp options"""
        category_dir = os.path.join(self.output_base_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            
        return {
            'outtmpl': os.path.join(category_dir, '%(title)s [%(id)s].%(ext)s'),
            'format': 'best[height<=720]',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en.*'],
            'subtitlesformat': 'srt',
            'writethumbnail': True,
            'writeinfojson': True,
            'ignoreerrors': True,
            'no_warnings': False,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'match_filter': self.shorts_filter,
            'postprocessors': [
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                },
                # Added: Ensure subtitles are converted to srt for easy parsing.
                {
                    'key': 'FFmpegSubtitlesConvertor',
                    'format': 'srt'
                }
            ],
            'progress_hooks': [self.progress_hook],
        }
    
    def shorts_filter(self, info):
        """Filter only Shorts (videos under 60 seconds)"""
        if info.get('duration', float('inf')) > 60:
            return 'Video is longer than 60 seconds (not a Short)'
        return None
    
    def progress_hook(self, d):
        """Progress hook for downloads"""
        if d['status'] == 'finished':
            print(f"Download completed: {d['filename']}")

    def extract_transcript(self, base_filename):

        """ 
            Helper to find the .srt file associated with the video
            and clean the text for the CSV.
        """
        # The video file usually ends in .mp4 or .mkv, subs usually replace extension .en srt 
        # we strip the extension for the video filename to find the base path
        base_path = os.path.splitext(base_filename)[0]

        # Look for any srt file starting with the base path 
        # yt-dlp names them like "title.en.srt" or 'title.en-orig.srt'
        srt_files = glob.glob(f"{glob.escape(base_path)}*.srt")

        if not srt_files:
            return ""
        
        try:
            # Take the first matching subtitle file 
            with open(srt_files[0], 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple cleanup to remove timestamps and index numbers
            # This regex looks for the SRT timestamp format (00:00:00,000 --> ...)
            clean_text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
            # Remove leftover newlines and extra spaces
            clean_text = clean_text.replace('\n', ' ').replace('\r', '').strip()
            # Remove duplicate spaces
            clean_text = re.sub(' +', ' ', clean_text)

            return clean_text
        
        except Exception as e:
            print(f"Error as {e}")

    
    def save_metadata(self, info, search_query, category):
        """Save video metadata to CSV"""
        try:

            # Get the filename where the video was saved.
            filename = info.get('_filename', '')

            # Attempt to extract transcript text 
            transcript_text = self.extract_transcript(filename)



            with open(self.metadata_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    info.get('id', ''),
                    info.get('title', '').replace(',', ' '),
                    info.get('uploader', ''),
                    info.get('duration', 0),
                    info.get('view_count', 0),
                    info.get('upload_date', ''),
                    datetime.now().strftime('%Y%m%d'),
                    search_query,
                    filename,
                    transcript_text
                ])
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def download_from_search(self, search_query, max_results=50, category="general"):
        """Download Shorts from search results"""
        search_url = f"ytsearch{max_results}:{search_query}"
        
        ydl_opts = self.get_ydl_opts(search_query, category)
        
        try:
            print(f"\n=== Searching for: '{search_query}' (max: {max_results} results) ===")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info without downloading first
                info_dict = ydl.extract_info(search_url, download=False)
                
                if not info_dict or 'entries' not in info_dict:
                    print("No results found")
                    return
                
                # Filter only Shorts
                shorts_entries = []
                for entry in info_dict['entries']:
                    if entry and entry.get('duration', 61) <= 60:
                        shorts_entries.append(entry)
                
                print(f"Found {len(shorts_entries)} Shorts out of {len(info_dict['entries'])} total results")
                
                # Download each Short
                for i, entry in enumerate(shorts_entries, 1):
                    if not entry:
                        continue
                        
                    print(f"\n[{i}/{len(shorts_entries)}] Downloading: {entry.get('title', 'Unknown')}")
                    try:
                        # Download the video
                        ydl.download([entry['webpage_url']])

                        # re-extract info to get the exact filepath where it landed (crucial) for finding the SRT
                        result_info = ydl.extract_info(entry['webpage_url'], download=False)
                        
                        # Save metadata
                        self.save_metadata(result_info, search_query, category)
                        
                    except Exception as e:
                        print(f"Error downloading {entry.get('title', 'Unknown')}: {e}")
                    
                    # Be polite - add delay between downloads
                    time.sleep(1)
                        
        except Exception as e:
            print(f"Error processing search '{search_query}': {e}")
    
    def batch_download(self, search_queries, results_per_query=20):
        """Batch download from multiple search queries"""
        for i, query in enumerate(search_queries, 1):
            print(f"\n{'='*50}")
            print(f"Processing query {i}/{len(search_queries)}: {query}")
            print(f"{'='*50}")
            
            self.download_from_search(
                search_query=query,
                max_results=results_per_query,
                category=query.replace(' ', '_')[:20]
            )
            
            # Longer delay between different searches
            time.sleep(5)

# Usage Example
if __name__ == "__main__":
    downloader = YouTubeShortsDownloader("./math_shorts_dataset")
    
    

    math_search_queries = [
    "elementary math shorts",
    "middle school math shorts",
    "high school math shorts",
    "college math shorts",
    "GCSE maths shorts",
    "SAT math shorts",
    "ACT math shorts",
    "CBSE maths shorts",
    "rational number maths",
     "mathematics shorts",
     "math tricks shorts",
     "algebra math shorts",
     "geometry math shorts", 
     "calculus shorts",
     "probability math shorts",
     "statistics math shorts",
     "trigonometry shorts",
     "fractions math shorts"
]
    
    # Start batch download
    downloader.batch_download(
        search_queries=math_search_queries,
        results_per_query=30  # Increase for larger dataset
    )

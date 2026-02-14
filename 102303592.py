
import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment

# 🔥 Set ffmpeg path (Windows)
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-2026-02-09-git-9bfa1635ae-essentials_build\bin"


# -----------------------------
# Argument Validation
# -----------------------------
def validate_arguments():
    if len(sys.argv) != 5:
        print("Usage: python 102303592.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer_name = sys.argv[1]

    try:
        num_videos = int(sys.argv[2])
    except ValueError:
        print("Error: NumberOfVideos must be an integer.")
        sys.exit(1)

    try:
        duration = int(sys.argv[3])
    except ValueError:
        print("Error: AudioDuration must be an integer.")
        sys.exit(1)

    output_file = sys.argv[4]

    if num_videos <= 10:
        print("Error: NumberOfVideos must be greater than 10.")
        sys.exit(1)

    if duration <= 20:
        print("Error: AudioDuration must be greater than 20 seconds.")
        sys.exit(1)

    if not output_file.endswith(".mp3"):
        print("Error: Output file must be an .mp3 file.")
        sys.exit(1)

    return singer_name, num_videos, duration, output_file


# -----------------------------
# Create Directories
# -----------------------------
def create_directories():
    folders = ["downloads", "trimmed", "output"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


# -----------------------------
# Search URLs
# -----------------------------
def get_video_urls(singer_name, num_videos):
    search_query = (
        f"ytsearch{num_videos * 5}:"
        f"{singer_name} official audio -live -concert -mix -jukebox"
    )

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'no_warnings': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        urls = [entry['url'] for entry in info['entries']]

    return urls


# -----------------------------
# Download Audio Only
# -----------------------------
def download_single_video(video_url, index):
    ydl_opts = {
        'format': 'bestaudio[ext=webm]/bestaudio',
        'outtmpl': f'downloads/video_{index}.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    for file in os.listdir("downloads"):
        if file.startswith(f"video_{index}") and not file.endswith(".part"):
            return os.path.join("downloads", file)

    return None


# -----------------------------
# Trim Audio
# -----------------------------
def process_video(video_path, duration, index):
    audio = AudioSegment.from_file(video_path)
    trimmed_audio = audio[:duration * 1000]

    output_path = os.path.join("trimmed", f"file_{index}.mp3")
    trimmed_audio.export(output_path, format="mp3")

    os.remove(video_path)

    return output_path


# -----------------------------
# Merge Files
# -----------------------------
def merge_files(output_filename):
    merged = AudioSegment.empty()

    files = sorted(os.listdir("trimmed"))

    for file in files:
        if file.endswith(".mp3"):
            file_path = os.path.join("trimmed", file)
            audio = AudioSegment.from_file(file_path)
            merged += audio

    output_path = os.path.join("output", output_filename)
    merged.export(output_path, format="mp3")

    # 🔥 Delete trimmed files after merge
    for file in files:
        if file.endswith(".mp3"):
            os.remove(os.path.join("trimmed", file))

    return output_path



# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    singer, n, y, output_file = validate_arguments()

    create_directories()

    print("Fetching video URLs...")
    video_urls = get_video_urls(singer, n)

    trimmed_files = []
    index = 1

    for url in video_urls:
        if len(trimmed_files) == n:
            break

        print(f"Processing video {index}/{n}")

        downloaded_file = download_single_video(url, index)

        if downloaded_file is None:
            print("Download failed. Skipping.")
            continue

        trimmed_file = process_video(downloaded_file, y, index)
        trimmed_files.append(trimmed_file)

        index += 1

    print("Merging files...")
    final_path = merge_files(output_file)

    print(f"\nMashup created successfully: {final_path}")

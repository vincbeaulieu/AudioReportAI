
from pytube import YouTube

from ..header import input_dir, workspace


def download_from_youtube(link, save_path=""):
    try:
        # Fetch and download the YouTube object
        youtubeObject = YouTube(link)#.streams.first().download(save_path)
        youtubeObject = youtubeObject.streams.get_highest_resolution()
        youtubeObject.download(save_path)

        # Obtain the name of the downloaded file
        filename = youtubeObject.default_filename
    except:
        print("An error has occurred")
        exit()
    
    print("Download completed")

    # Return the filename of the downloaded file
    return filename


if __name__ == "__main__":
    # Prompt user for the YouTube URL
    url = input("Paste the YouTube URL here: ")

    # Download the video file to the "input/" directory
    source_file = download_from_youtube(url, input_dir)

# Reference: https://www.freecodecamp.org/news/python-program-to-download-youtube-videos/


# Youtube Downloader using tkinter and youtube-dl

Prerequisites:

1. Install Python 3
2. Install youtube-dl using pip
3. Install ffmpeg/avconv and ffprobe/avprobe using pip

Usage:

1. open command terminal and type > python YoutubeDownloader.py
2. Following GUI opens up

![image](https://user-images.githubusercontent.com/8674169/158995384-391b17b4-fa80-48fb-8e13-bf60910e4fe0.png)

GUI

1. Select output directory
2. Copy any youtube url and paste in the Youtube URL field
3. Click Get Video Info to display video title and formats available
4. Video Audio section where both are available. Select resoluton and file sizes
5. Click extract audio to create audio file in selected extension.
6. Download to download the video file and save it in output directory
7. Video Only section has only video, but no audio
8. Audio Only section has only audio, but no video
9. Merge section will merge the video and audio after downloading both and save it in selected extension
10. Keep each file is an option to keep the original files downloaded. If off, the files are deleted after merge
11. Bottom text window displays the info/error messages and download progress.

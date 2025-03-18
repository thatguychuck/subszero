# subszero
A python command line script to scan for video files and attempt to check for a corresponding subtitle file, both external and embedded. A list of videos not matched to a subtitle is exported as a txt file.

## Why?
Personally, I was looking for an easy way to generate a txt file of videos without subtitles so I could feed it into [https://github.com/absadiki/subsai](https://github.com/absadiki/subsai), 
which is a project that uses a local whisper/ai model to generate subtitles for videos.

## Requirements:
**python3** (this script was only tested on debian 12 bookworm).

**ffmpeg** as this script calls ffprobe to check for embedded subtitles.

### Optional:
**tqdm** for facy progress bars, falls back to a file counter if not installed.

# Limitations:
**I am not a programmer,** just a hobbiest/tinkerer. When it comes to python, I am a novice, probably even less than. This script relied heavily on google/chatgpt/hope to come into existance. But I had a need and this filled it,
so I put it here in case it can help someone else. The testing I did on my own revealed many pitfalls that I tried to mitigate through checks and sanitizing of paths, and as a result the script seems overly large for what it does. 

At any rate here are a few things of note:
- No language detection. Only attempts to see if subtitles are present or not.
- The subtitle files it searches for are hard coded and limited, see "usage" below for the list.
- Matching `awesome.video.mkv` to `awesome.video.srt` is relatively straight forward, but matching `awesome.video.mkv` to other conventions proved troublesome (`awesome.video.eng.srt`, `awesome.video.sdh.eng.srt`, or even `Awesome.Video.srt`). The logic in this script takes the video name without extention, and checks if the subtitle file contains that name with both sets switched to lower case. This proved accurate (as far as I can tell) in my own testing. However if there is a error in matching it is probably occuring here. 
- Uses the file command to check mime type for "video" to find the video files.
- ffprobe is used to check if subtitles are present in a video container.

## Usage:
**Scanning a large library can take some time, it is reccomended to test on smaller folders first and utilize screen or tmux**
`./subszero.py /path/to/media/files/`

`./subszero.py -h` Will display the following:
```
usage: subszero.py [-h] [--version] source_directory

Scans a directory and subdirectories for video files.
Attempts to match video files with subtitle files, and also checks for embedded subitiles.
A list of videos with no match are exported as a text file.

Requires: ffmpeg (uses ffprobe to check for embedded subtitles).
Optional: tqdm (for fancy progress bars, uses basic counter if not available).

Supported external subtitle formats:
- .srt (SubRip)
- .sub (MicroDVD)
- .vtt (WebVTT)
- .ass (Advanced SubStation Alpha)
- .ssa (SubStation Alpha)

The output file will be named based on the directory and timestamp.

positional arguments:
  source_directory  Path to the source directory

options:
  -h, --help        show this help message and exit
  --version         show program's version number and exit

```

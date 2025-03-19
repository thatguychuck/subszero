# subszero
A python command line script to scan for video files that also attempts to check for a corresponding subtitle file, both external and embedded. By default a list of videos, not matched to a subtitle, is exported as a txt file. Other file lists can be exported using command line options.

## Why?
Personally, I was looking for an easy way to generate a txt file of videos without subtitles so I could feed it into [https://github.com/absadiki/subsai](https://github.com/absadiki/subsai), 
a project that uses a local whisper/ai model to generate subtitles for videos.

## Requirements:
**python3** (this script was only tested on debian 12 bookworm).

**ffmpeg** as this script calls ffprobe to check for embedded subtitles.

### Optional:
**tqdm** for fancy progress bars, falls back to a file counter if not installed.

# Limitations:
**I am not a programmer,** just a hobbyst/tinkerer. When it comes to python, I am a novice, probably even less than. This script relied heavily on google/chatgpt/hope to come into existence. But I had a need and this filled it,
so I put it here in case it can help someone else. 

#### At any rate here are a few things of note:
- Currently, nothing is optomized as far as parallelization, it's slower than it probably could be. Did I mention I am not really a programmer?
- No language detection. Only attempts to see if subtitles are present or not.
- No detection of "burned in" subtitles which are present in the video images themselves.
- The external subtitle files for the search are hard coded and limited, see "usage" below for the list. However the script can be modified to search for others if needed.
- Matching `awesome.video.mkv` to `awesome.video.srt` is relatively straight forward, but matching `awesome.video.mkv` to other conventions proved troublesome (`awesome.video.eng.srt`, `awesome.video.sdh.eng.srt`, or even `Awesome.Video.srt`). The logic in this script takes the video name without extention, and checks if the subtitle name contains the video name, with both sets switched to lower case. This proved accurate (as far as I can tell) in my own testing. However if there is a error in matching it is probably occurring here. 
- Uses the `file` command to check mime type for "video" to find the video files.
- `ffprobe` is used to check if subtitles are present in a video container.
- **BLOAT:** As I am also using this as a learning exercise, this script conatins way more than it actually needs. The testing I did revealed many pitfalls that I tried to mitigate through checks and sanitizing of paths. As a result the script is overly complicated for what it does. Did I mention I am not really a programmer?
  
#### Performance
This script was ran agains a 30TB(ish) collection of media, connected over SAMBA, and produced the following results. Smaller data sets do not take nearly as long.
```
=== Summary of Results ===
Total Files Scanned: 156147
Total Video Files Found: 19891
Total Subtitle Files Found: 7969
Total Videos with Embedded Subtitles: 6037
Total Videos with Matching External Subtitles: 6464
Total Videos with Subtitles (External + Embedded): 11965
Total Videos Without Subtitles: 7926


=== Script Execution Complete ===
Total time elapsed: 01:49:54.439 (hh:mm:ss.ms)
```

## Usage:
**Scanning a large library can take some time, it is recomended to test on smaller folders first and utilize `screen` or `tmux`**

`./subszero.py /path/to/media/files/`

`./subszero.py -h` Will display the following:
```
usage: subszero.py [-h] [--version] [-r] [-a] [-s] [-m] [-e] source_directory

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
  source_directory     Path to the source directory

options:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  -r, --reverse        Also export a list of video files that have subtitles or embedded subtitles, if any.
  -a, --all-videos     Also export a list of all video files found, if any.
  -s, --all-subtitles  Also export a list of all subtitle files found, if any.
  -m, --all-embedded   Also export a list of all videos with embedded subtitles.
  -e, --everything     Enable all export options.


```

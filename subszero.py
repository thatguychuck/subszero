#!/usr/bin/env python3

import os
import subprocess
import json
import sys
import datetime
import argparse
import time

__version__ = "0.0.26"

start_time = time.time() # Begin timer to track script completion

# Set up argument parser
parser = argparse.ArgumentParser(
    description=(
        "Scans a directory and subdirectories for video files.\n"
        "Attempts to match video files with subtitle files, and also checks for embedded subtitles.\n"
        "A list of videos with no match are exported as a text file.\n\n"
        "Requires: ffmpeg (uses ffprobe to check for embedded subtitles).\n"
        "Optional: tqdm (for fancy progress bars, uses basic counter if not available).\n\n"
        "Supported external subtitle formats:\n"
        "- .srt (SubRip)\n"
        "- .sub (MicroDVD)\n"
        "- .vtt (WebVTT)\n"
        "- .ass (Advanced SubStation Alpha)\n"
        "- .ssa (SubStation Alpha)\n\n"
        "The output file will be named based on the directory and timestamp."
    ),
    formatter_class=argparse.RawTextHelpFormatter  # Ensures newlines are preserved
)
# Required arguments
parser.add_argument("source_directory", type=str, help="Path to the source directory")
# Optional arguments
parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

# Define export options separately
export_options = [
    ("-r", "--reverse", "Also export a list of video files that have subtitles or embedded subtitles, if any."),
    ("-a", "--all-videos", "Also export a list of all video files found, if any."),
    ("-s", "--all-subtitles", "Also export a list of all subtitle files found, if any."),
    ("-m", "--all-embedded", "Also export a list of all videos with embedded subtitles."),
    ("-e", "--everything", "Enable all export options."),
]

# Add options to the parser
for short, long, desc in export_options:
    parser.add_argument(short, long, action="store_true", help=desc)

# Parse arguments
args = parser.parse_args()

# If --everything is enabled, enable all other export options
if args.everything:
    for short, long, _ in export_options[:-1]:  # Exclude "--everything" itself
        vars(args)[long.lstrip("--").replace("-", "_")] = True  # Safer way to modify argparse namespace

# Normalize and clean the directory path
source_dir = os.path.abspath(args.source_directory.strip())

# Ensure the provided directory exists
if not os.path.isdir(source_dir):
    print(f"Error: The directory '{source_dir}' does not exist.")
    sys.exit(1)

# Ensure the script has read access to the directory
if not os.access(source_dir, os.R_OK):
    print(f"Error: No read access to the directory '{source_dir}'. Please check permissions.")
    sys.exit(1)

# Check write access to current directory to be able to export results
if not os.access(os.getcwd(), os.W_OK):
    print(f"Error: No write access to the current directory. Cannot export results. Exiting.")
    sys.exit(1)

# Try to import tqdm, set fallback mode if not installed
try:
    from tqdm import tqdm
    use_tqdm = True
except ImportError:
    use_tqdm = False

# Function to check if ffmpeg/ffprobe is installed
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subprocess.run(["ffprobe", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Ensure ffmpeg is installed before proceeding
if not check_ffmpeg():
    print("Error: ffmpeg/ffprobe is not installed or not in the system PATH.")
    print("Please install ffmpeg before running this script.")
    sys.exit(1)

filetypes = ("video",)
subtitle_types = (".srt", ".sub", ".vtt", ".ass", ".ssa")

video_files = []
subtitle_files = []

print(f"\nScanning '{source_dir}' for video and subtitle files...")

# Get all files for progress tracking
all_files = [os.path.join(root, name) for root, _, files in os.walk(source_dir) for name in files]
total_files = len(all_files)

# Use tqdm if available, otherwise show progress on one line
if use_tqdm:
    file_iterator = tqdm(all_files, desc="Processing files", unit="file")
else:
    file_iterator = all_files

# Scan for video and subtitle files
for i, file in enumerate(file_iterator, start=1):
    name = os.path.basename(file)

    # Update single-line progress if tqdm is not available
    if not use_tqdm:
        percentage = (i / total_files) * 100
        sys.stdout.write(f"\rProcessed {i}/{total_files} files ({percentage:.2f}%)")
        sys.stdout.flush()

    # Check if it's a subtitle file
    if name.lower().endswith(subtitle_types):
        subtitle_files.append(file)
        continue

    # Check if it's a video using MIME type
    try:
        ftype = subprocess.check_output(['file', '--mime-type', '-b', file]).decode('utf-8', errors='ignore').strip()
        if ftype.split("/")[0] in filetypes:
            video_files.append(file)
    except subprocess.CalledProcessError:
        print(f"\nError processing file: {file}")

print("\nScanning complete.")
print(f"Total Video Files Found: {len(video_files)}")
print(f"Total Subtitle Files Found: {len(subtitle_files)}")

# Normalize filenames (strip extensions, convert to lowercase)
video_basenames = {os.path.splitext(os.path.basename(video))[0].lower() for video in video_files}
subtitle_basenames = [os.path.splitext(os.path.basename(sub))[0].lower() for sub in subtitle_files]

# Find matching subtitles (allow exact matches and minor suffixes)
subtitle_set = {sub for sub in subtitle_basenames} # Convert subtitle basenames to a set
subtitle_matches = {video for video in video_basenames if any(sub.startswith(video) for sub in subtitle_set)}


def has_embedded_subtitles(video_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_streams', '-print_format', 'json', video_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        streams = json.loads(result.stdout).get("streams", [])
        return any(stream.get("codec_type") == "subtitle" for stream in streams)
    except Exception as e:
        print(f"\nError checking subtitles for {video_path}: {e}")
        return False

videos_without_subtitles = []
total_videos = len(video_files)

embedded_subtitles = []

print("\nChecking for embedded subtitles and filtering videos without subtitles...")

videos_without_subtitles = []
embedded_subtitles = []

# Define video_iterator properly
if use_tqdm:
    video_iterator = tqdm(video_files, desc="Checking videos", unit="video")
else:
    video_iterator = video_files

for index, vid in enumerate(video_iterator, start=1):
    has_embedded = has_embedded_subtitles(vid)
    if has_embedded:
        embedded_subtitles.append(vid)

    video_base = os.path.splitext(os.path.basename(vid))[0].lower()
    if video_base not in subtitle_matches and vid not in embedded_subtitles:
        videos_without_subtitles.append(vid)

    if not use_tqdm:
        percentage = (index / total_videos) * 100
        sys.stdout.write(f"\rChecking videos: {index}/{total_videos} ({percentage:.2f}%)")
        sys.stdout.flush()

print("\nEmbedded subtitle check and filtering complete.")

def export_file(file_list, prefix, source_dir):
    """Exports a list of files to a timestamped text file if the list is not empty."""
    if not file_list:
        print(f"\n{prefix.replace('_', ' ')} list empty. No export needed.\n")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_path = os.path.basename(source_dir).replace(":", "").replace(" ", "-")
    file_name = f"{prefix}_{safe_path}_{timestamp}.txt"

    print(f"\n--- Exporting {prefix.replace('_', ' ')} ---\n")  # Add a separator before exporting

    try:
        with open(file_name, "w") as f:
            total = len(file_list)

            # Use tqdm if available, otherwise show progress manually
            if use_tqdm:
                for item in tqdm(file_list, desc=f"Exporting {prefix}", unit="item"):
                    f.write(item + "\n")

            else:
                for i, item in enumerate(file_list, start=1):
                    f.write(item + "\n")
                    percentage = (i / total) * 100
                    sys.stdout.write(f"\rExporting {prefix}: {i}/{total} files ({percentage:.2f}%)")
                    sys.stdout.flush()

        print(f"\nExported {prefix.replace('_', ' ')} to {file_name}\n")  # Add spacing after export
    except Exception as e:
        print(f"\nError exporting {prefix.replace('_', ' ')}: {e}\n")
        if os.path.exists(file_name):
            os.remove(file_name)

# Export based on conditions
all_subtitles_combined = subtitle_files + embedded_subtitles  # Merge subtitles (external + embedded)

# Define export conditions compactly
export_items = [
    (video_files, "all_videos", args.all_videos),
    (subtitle_files, "all_subtitles", args.all_subtitles),
    (embedded_subtitles, "all_embedded_subtitles", args.all_embedded),
    (videos_without_subtitles, "no_subtitles", True),  # Always attempt to export if not empty
]

# Execute exports
for file_list, prefix, condition in export_items:
    if condition or args.everything:
        export_file(file_list, prefix, source_dir)

elapsed_time = time.time() - start_time # Track time for script ending.
formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) # Format time into a better format
milliseconds = int((elapsed_time % 1) * 1000)

# Determine videos with external subtitles by matching video base names with subtitle_matches.
videos_with_external_subtitles = [
    vid for vid in video_files
    if os.path.splitext(os.path.basename(vid))[0].lower() in subtitle_matches
]

# Combine external and embedded subtitle videos ensuring each video is only counted once.
videos_with_subtitles = set(videos_with_external_subtitles) | set(embedded_subtitles)
total_videos_with_subtitles = len(videos_with_subtitles)

print("\n=== Summary of Results ===")
print(f"Total Files Scanned: {total_files}")
print(f"Total Video Files Found: {len(video_files)}")
print(f"Total Subtitle Files Found: {len(subtitle_files)}")
print(f"Total Videos with Embedded Subtitles: {len(embedded_subtitles)}")
print(f"Total Videos with Matching External Subtitles: {len(subtitle_matches)}")
print(f"Total Videos with Subtitles (External + Embedded): {total_videos_with_subtitles}")
print(f"Total Videos Without Subtitles: {len(videos_without_subtitles)}\n")
print(f"\n=== Script Execution Complete ===")
print(f"Total time elapsed: {formatted_time}.{milliseconds:03d} (hh:mm:ss.ms)\n")

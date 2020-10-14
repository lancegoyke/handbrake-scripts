#!/usr/bin/env python3
"""
## Overview

This is a script to run Handbrake on a series of bluray ripped "backup"
folders from MakeMKV,. Encodes and names them in a sequence of files like a
television season, increasing the episode number for each video title.

## Requirements

- HandBrakeCLI.exe installed and in your PATH.
- Source directories from which to pull.
- Source directories must be a bluray backup, not a series of video files.

## Helpful Info

Here's a link for info on installing HandBrake. At the time of writing,
you will find the "Command Line Version" on the Downloads page.
https://handbrake.fr/docs/en/latest/get-handbrake/download-and-install.html

Here's a link to MakeMKV.
https://www.makemkv.com/

Note: this script was written on a Windows computer.

## How It Works

User must supply:
- `input_file_paths` - a list of video source input directories
- `output_file_directory` - destination directory
- `output_file_prefix` - destination file name; designates season
- `episode_num` - first episode number of season being processed
- `output_file_extension` - type of video file container
- `title_min_duration` - the minimum length of a video title in your source
- `preset_file_full_path` - absolute path of HandBrake GUI preset file export
- `preset_name` - name of HandBrake GUI preset

Handbrake scans the folder and finds the tracks. The script must specify
the minimum duration of the title. Recommendation is to use the HandBrake
GUI to read the disc and visually look for a cutoff duration that makes
sense.

This version of the script runs with a HandBrake preset in JSON format.
Recommendation is to use the GUI to designate all desired settings, then
export to JSON file and link the absolute path in this script.

## Example HandBrakeCLI Commands

To scan each item in `input_file_paths`:
- `HandBrakeCLI \
    --input C:\MakeMKV\Video\backup\Series_S1_D1 \
    --title 0 \
    --min-duration 2400`

To transcode a source title:
- `HandBrakeCLI \
    --preset-import-gui "C:\Media\Presets\special-handbrake-preset.json" \
    -Z "Special HandBrake Preset Name" \
    --input "C:\MakeMKV\Video\backup\Series_S1_D1" \
    --title 68 \
    --output C:\Media\TV Shows\Series\Season 1\s01e01.mkv`

## Metadata

Author: Lance Goyke
URL: lancegoyke.com
"""

from pathlib import Path
import re
import subprocess
import sys
from typing import List
import winsound


# A list of input source folders containing MakeMKV bluray backup
# Do not include trailing slash
input_file_paths = [
    'M:\\Video\\COSMOS_01',
    'M:\\Video\\COSMOS_02',
    'M:\\Video\\COSMOS_03',
    'M:\\Video\\COSMOS_04',
    'M:\\Video\\COSMOS_05',
    'M:\\Video\\COSMOS_06',
    'M:\\Video\\COSMOS_07',
]
output_file_directory = 'S:\\media\\TV Shows\\Cosmos (2014)\\Season 1\\'
output_file_prefix = "s01e"
episode_num = 1
output_file_extension = ".mkv"
title_min_duration = 2520  # 42 minutes in seconds
preset_file_full_path = 'S:\\media\\test-transcoding\\presets\\CPU-20RF-slow.json'
preset_name = "H.265 20 RF with metadata"


def scan_for_titles(scan_folder: str) -> List[str]:
    """Scan the track and grab the numbers representing the titles longer than
    the specified min-duration."""

    scan_commands = [
        "HandBrakeCLI",
        "--input", f'{scan_folder}',  # HandBrakeCLI does not like quoted folder
        "--title", "0",  # 0 means scan all titles, must be a string
        "--min-duration", f'{title_min_duration}',
    ]

    try:
        print(">>> Running HandBrakeCLI scan.")
        print(f'\t {" ".join(scan_commands)}')
        scan = subprocess.run(
            " ".join(scan_commands),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        ).stderr
    except subprocess.SubprocessError:
        print("Something went wrong with the track scan. Exiting.")
        sys.exit()

    scan = scan.decode("utf-8", "ignore")  # turn bytes-like object into string

    # return a list of captured strings
    titles = re.findall(r'\n\+ title (\d+):', scan)
    return titles


def main():
    # These commands should stay the same for each video being transcoded
    base_transcode_commands = [
        "HandBrakeCLI",
        '--preset-import-gui', f'"{preset_file_full_path}"',
        '-Z', f'"{preset_name}"',
    ]
    global episode_num

    # Make the output folder if necessary
    o = Path(output_file_directory)
    if not o.exists():
        o.mkdir()

    # For transcoding whole folders backed up from MakeMKV, we will have many
    # titles.
    for input_file_path in input_file_paths:
        p = Path(input_file_path)

        # Handle files
        if p.is_file():
            print(f"{input_file_path}")
            print("This path is a file.")
            print("This script scans input folders for multiple titles.")
            print("Skipping.\n")
            pass

        # Handle directories
        elif p.is_dir():
            print(f"\n[HANDBRAKE] INPUT > {input_file_path}")

            # get the titles longer than min-duration
            print("\n[HANDBRAKE] SCAN STARTING")
            titles = scan_for_titles(input_file_path)  # a list of strings
            print(f"[HANDBRAKE] titles: {titles}")
            print("[HANDBRAKE] SCAN FINISHED")

            # run HandBrake on each title
            for title in titles:
                commands = []
                commands.extend(base_transcode_commands)
                output_file_name = f"{output_file_prefix}{episode_num:0>2d}{output_file_extension}"
                commands.extend(['--input', f'"{input_file_path}"'])
                commands.extend(['--title', title])
                commands.extend(['--output', f'"{output_file_directory}{output_file_name}"'])
                print("\n[HANDBRAKE] Running command")
                print("\n\t".join(commands))
                # subprocess.run(" ".join(commands), shell=True)
                episode_num += 1

        # Handle unknowns
        else:
            print("[ERROR] Could not identify file path. Exiting.")
            print(f"path = {input_file_path}")
            sys.exit()

    # End gracefully
    print("\n[HANDBRAKE] Finished!")
    print(f'[HANDBRAKE] Last file output: "{output_file_directory}{output_file_name}"')
    print(f"[HANDBRAKE] Next episode would be #{episode_num}")
    winsound.Beep(1000, 100)


if __name__ == "__main__":
    main()

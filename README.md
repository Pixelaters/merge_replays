# Merge Replays - MP4/M4A Combiner

A GUI application to merge matching MP4 and M4A files into a single file with two separate audio tracks.

## Features

✅ **GUI Window** - Easy-to-use graphical interface  
✅ **Progress Bar** - Visual feedback during processing  
✅ **Drag & Drop** - Drop folders directly into the app  
✅ **Auto-delete Originals** - Optionally remove source files after merge  

## Requirements

- **Python 3.7+**
- **FFmpeg** - Must be installed and available in your PATH

### Installing FFmpeg

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract and add the `bin` folder to your system PATH
3. Verify installation by running `ffmpeg -version` in Command Prompt

**Alternative (Windows):**
- Use Chocolatey: `choco install ffmpeg`
- Use winget: `winget install ffmpeg`

## Installation

### Option 1: Run from Source

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Note: `tkinterdnd2` is optional. The app will work without it.

2. Run the application:
```bash
python merge_replays.py
```

### Option 2: Use Pre-built Executable

A standalone `.exe` file is available in the `dist` folder. Simply run `MergeReplays.exe` - no Python installation required!

**Note:** FFmpeg must still be installed and in your PATH for the executable to work.

### Building Your Own Executable

To build the executable yourself:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build script:
```bash
build.bat
```

Or manually:
```bash
python -m PyInstaller --onefile --windowed --name "MergeReplays" merge_replays.py
```

The executable will be created in the `dist` folder.

## Usage

1. Run the application:
```bash
python merge_replays.py
```

2. Select source folder (contains your MP4 and M4A files)
3. Select destination folder (where merged files will be saved)
4. (Optional) Check "Delete original files after merge"
5. Click "Start Merging"

### How It Works

The application will:
- Find all matching file pairs (e.g., `unknown_replay_2026.01.12-16.44.mp4` and `unknown_replay_2026.01.12-16.44.m4a`)
- Merge them into a single MP4 file with:
  - Video track from the MP4 file
  - Audio track 1 from the MP4 file (default)
  - Audio track 2 from the M4A file
- Save the merged file to the destination folder
- Optionally delete the original files

### Output Format

The merged file will have two audio tracks that you can switch between in most video players:
- **Track 1 (Default)**: Audio from the original MP4 file
- **Track 2**: Audio from the M4A file

## Troubleshooting

**"FFmpeg not found" error:**
- Make sure FFmpeg is installed and added to your system PATH
- Restart the application after installing FFmpeg

**Drag & Drop not working:**
- Install `tkinterdnd2`: `pip install tkinterdnd2`
- Restart the application

**Files not merging:**
- Check that file names match exactly (except extension)
- Ensure both MP4 and M4A files exist in the source folder
- Check the status log for detailed error messages

## License

Free to use and modify.


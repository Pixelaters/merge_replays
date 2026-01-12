@echo off
echo Building Merge Replays executable...
python -m PyInstaller --onefile --windowed --name "MergeReplays" merge_replays.py
echo.
echo Build complete! Executable is in the 'dist' folder.
pause

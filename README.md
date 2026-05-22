# 📁 Bulk File Organizer & Renamer (Task 8)

A powerful CLI-based Python automation script designed to rename multiple files in bulk and automatically organize them into folders based on file type, extension, size, or creation date.

## 🚀 Features
* **File Renaming:** Add custom prefixes, suffixes, replace specific words, or apply auto-numbering (e.g., `file_1`, `file_2`).
* **Smart Organization:** Automatically sorts files into structured folders (`Images`, `PDFs`, `Videos`, `Audio`, etc.).
* **Preview System:** Displays a safe before/after preview of changes before execution.
* **Logging System:** Records every single operation with timestamps in both `rename_log.txt` and `rename_log.csv`.
* **Undo System:** Single-click operation (`Option 6`) to instantly reverse the last batch of rename or move actions.

## 🛠️ Advanced Requirements Met
* Built entirely using standard library modules (`os`, `shutil`, `csv`, `json`).
* Robust error handling for `PermissionError` and `FileNotFoundError`.
* Prevents file overwriting.

## 💻 How to Run
1. Open terminal/cmd in the project directory.
2. Run the script using:
   ```bash
   python "Task 8 Bulk file renamer.py"

   ## 🎥 Demo Video Walkthrough
A complete end-to-end working demonstration of this project is uploaded directly in this repository as:
`Task 8 Bulk file renamer demo video.mp4`

The video showcases:
1. **Target Directory Selection** (`Option 1`)
2. **Bulk File Renaming with Auto-Numbering** (`Option 2`)
3. **Automated Structural Sorting/Organization** (`Option 3`)
4. **Real-time Log Generation** (`Option 5`)
5. **Full Execution Reversal (Undo Feature)** (`Option 6`)

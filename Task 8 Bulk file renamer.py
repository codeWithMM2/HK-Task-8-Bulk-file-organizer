import os
import shutil
import csv
import json
from datetime import datetime

# file names for logs and undo history
log_txt = "rename_log.txt"
log_csv = "rename_log.csv"
undo_file = "undo_history.json"

# folder categories for organizing by file type
type_map = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "PDFs": [".pdf"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audio": [".mp3", ".wav", ".aac"],
    "Documents": [".docx", ".doc", ".txt", ".pptx", ".xlsx"],
    "Archives": [".zip", ".rar", ".tar", ".gz"],
}

# ask user for folder path and check if it exists
def get_folder():
    path = input("Enter folder path: ").strip()
    if not os.path.isdir(path):
        print("Invalid folder.")
        return None
    return path

# return list of files only (skip subfolders)
def list_files(folder):
    try:
        return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    except PermissionError:
        # no access to read this folder
        print("Permission denied: cannot read this folder.")
        return []
    except FileNotFoundError:
        # folder was deleted or moved after selection
        print("Folder not found.")
        return []

# save every rename action to txt and csv log
def save_log(old, new):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_txt, "a") as f:
        f.write(f"{t} | {old} -> {new}\n")
    exists = os.path.isfile(log_csv)
    with open(log_csv, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["Time", "Old Name", "New Name"])
        w.writerow([t, old, new])

# add current batch of operations to undo history json
def push_undo(ops):
    history = json.load(open(undo_file)) if os.path.isfile(undo_file) else []
    history.append(ops)
    json.dump(history, open(undo_file, "w"))

# reverse the last batch of rename or move operations
def undo_last():
    if not os.path.isfile(undo_file):
        print("Nothing to undo.")
        return
    history = json.load(open(undo_file))
    if not history:
        print("Nothing to undo.")
        return
    last_ops = history.pop()
    count = 0
    for old_path, new_path in reversed(last_ops):
        # only undo if new file exists and old path is free
        if os.path.exists(new_path) and not os.path.exists(old_path):
            os.rename(new_path, old_path)
            save_log(os.path.basename(new_path), os.path.basename(old_path))
            count += 1
        else:
            print(f"  Cannot undo: {os.path.basename(new_path)}")
    json.dump(history, open(undo_file, "w"))
    print(f"Undone {count} operation(s).")

# rename a file safely and catch permission or missing file errors
def safe_rename(folder, old, new):
    old_path = os.path.join(folder, old)
    new_path = os.path.join(folder, new)
    if os.path.exists(new_path):
        print(f"  Skipped (already exists): {new}")
        return None
    try:
        os.rename(old_path, new_path)
        save_log(old, new)
        # return both paths so undo can reverse this later
        return (old_path, new_path)
    except PermissionError:
        # file is open or locked by another program
        print(f"  Permission denied: {old}")
        return None
    except FileNotFoundError:
        # file was deleted between listing and renaming
        print(f"  File not found: {old}")
        return None

# show before/after names and ask user to confirm
def confirm_preview(change_list):
    print("\n--- Preview ---")
    for old, new in change_list:
        print(f"  {old}  ->  {new}")
    return input("\nApply? (y/n): ").strip().lower() == "y"

# bonus: let user define their own naming pattern using tokens
def custom_pattern_rename(all_files):
    print("Available tokens: {name} {ext} {date} {num}")
    pattern = input("Enter pattern (e.g. work_{date}_{num}): ").strip()
    today = datetime.now().strftime("%Y%m%d")
    change_list = []
    for i, file_name in enumerate(all_files, 1):
        name, ext = os.path.splitext(file_name)
        # replace each token with actual value
        new = pattern.replace("{name}", name).replace("{ext}", ext.lstrip("."))
        new = new.replace("{date}", today).replace("{num}", str(i))
        # add original extension if user forgot to include {ext}
        if not new.endswith(ext):
            new += ext
        change_list.append((file_name, new))
    return change_list

# handle all renaming options including bonus custom pattern
def rename_files(folder):
    files = list_files(folder)
    if not files:
        print("No files found.")
        return
    print("\n1.Prefix  2.Suffix  3.Replace Word  4.Auto Number  5.Custom Pattern")
    choice = input("Choose: ").strip()
    change_list = []
    if choice == "1":
        p = input("Prefix: ").strip()
        for f in files:
            change_list.append((f, p + f))
    elif choice == "2":
        s = input("Suffix (before extension): ").strip()
        for f in files:
            n, e = os.path.splitext(f)
            change_list.append((f, n + s + e))
    elif choice == "3":
        ow = input("Word to replace: ").strip()
        nw = input("Replace with: ").strip()
        for f in files:
            if ow in f:
                change_list.append((f, f.replace(ow, nw)))
    elif choice == "4":
        base = input("Base name (e.g. file): ").strip()
        for i, f in enumerate(files, 1):
            _, e = os.path.splitext(f)
            change_list.append((f, f"{base}_{i}{e}"))
    elif choice == "5":
        # bonus: custom naming rule
        change_list = custom_pattern_rename(files)
    else:
        print("Invalid option.")
        return
    if not change_list:
        print("Nothing to rename.")
        return
    if confirm_preview(change_list):
        # apply renames and collect successful ones for undo
        ops = [r for old, new in change_list for r in [safe_rename(folder, old, new)] if r]
        if ops:
            push_undo(ops)
        print(f"\nRenamed {len(ops)} file(s).")
    else:
        print("Cancelled.")

# organize files into subfolders by type, extension, date or size
def organize_files(folder):
    files = list_files(folder)
    if not files:
        print("No files found.")
        return
    print("\n1.By Type  2.By Extension  3.By Date  4.By File Size")
    choice = input("Choose: ").strip()
    moved = 0
    ops = []
    for file_name in files:
        file_path = os.path.join(folder, file_name)
        _, ext = os.path.splitext(file_name)
        ext_lower = ext.lower()
        if choice == "1":
            dest = "Others"
            for bucket, exts in type_map.items():
                if ext_lower in exts:
                    dest = bucket
                    break
        elif choice == "2":
            dest = ext_lower.replace(".", "").upper() if ext_lower else "NO_EXT"
        elif choice == "3":
            mt = os.path.getmtime(file_path)
            dest = datetime.fromtimestamp(mt).strftime("%Y-%m")
        elif choice == "4":
            # bonus: sort files into size buckets
            kb = os.path.getsize(file_path) / 1024
            if kb < 100:
                dest = "Small_under100KB"
            elif kb < 1024:
                dest = "Medium_100KB_to_1MB"
            elif kb < 10240:
                dest = "Large_1MB_to_10MB"
            else:
                dest = "Huge_above10MB"
        else:
            print("Invalid option.")
            return
        dest_folder = os.path.join(folder, dest)
        # create destination subfolder if it doesnt exist
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, file_name)
        if os.path.exists(dest_path):
            print(f"  Skipped (exists): {file_name}")
            continue
        try:
            shutil.move(file_path, dest_path)
            save_log(file_name, os.path.join(dest, file_name))
            ops.append((file_path, dest_path))
            moved += 1
        except PermissionError:
            # file is locked or in use by another program
            print(f"  Permission denied: {file_name}")
        except FileNotFoundError:
            # file disappeared before we could move it
            print(f"  File not found: {file_name}")
    if ops:
        push_undo(ops)
    print(f"\nOrganized {moved} file(s).")

# show all files in selected folder with their size
def preview_folder(folder):
    files = list_files(folder)
    if not files:
        print("Folder is empty.")
        return
    print(f"\nFiles in '{folder}':")
    for i, f in enumerate(files, 1):
        kb = os.path.getsize(os.path.join(folder, f)) / 1024
        print(f"  {i}. {f}  [{kb:.1f} KB]")

# read and print log file contents
def view_logs():
    print("\n1. TXT Log  2. CSV Log")
    lf = log_txt if input("Choose: ").strip() == "1" else log_csv
    if not os.path.isfile(lf):
        print("No log found yet.")
        return
    with open(lf, "r") as f:
        print("\n" + f.read())

# main loop with menu
def run():
    folder = None
    while True:
        print("\n====== Bulk File Organizer ======")
        print("1.Select Folder  2.Rename  3.Organize")
        print("4.Preview  5.Logs  6.Undo Last  7.Exit")
        c = input("Choose: ").strip()
        if c == "1":
            folder = get_folder()
            if folder:
                print(f"Selected: {folder}")
        elif c in ("2", "3", "4"):
            if not folder:
                print("Select a folder first (Option 1).")
            elif c == "2":
                rename_files(folder)
            elif c == "3":
                organize_files(folder)
            elif c == "4":
                preview_folder(folder)
        elif c == "5":
            view_logs()
        elif c == "6":
            # bonus: undo the last rename or organize batch
            undo_last()
        elif c == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

run()
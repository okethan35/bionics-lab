import os
import shutil
import re
from datetime import datetime
import pandas as pd

def extract_timestamp(filename):
    """Extracts and converts timestamp from filename to a datetime object."""
    match = re.search(r'(\d{2})_(\d{2})_(\d{4})_(\d{2})_(\d{2})_(\d{2})', filename)
    if match:
        month, day, year, hour, minute, second = map(int, match.groups())
        return datetime(year, month, day, hour, minute, second)
    return None

''' 
    Renames and organizes CSV files from a source directory based on subject ID, 
    tendency, FMA number, score, and trial number.
    Files are copied to a new destination directory, organized into FMA subfolders.
    
    Parameters:
        source_dir (str): Path to the source directory.
        destination_dir (str): Path to the destination directory.
        subjects (list): List of subject IDs to process. Passing an
        empty list or false value will default to processing all 
        data in the source directory
'''
def hs_rename_files(source_dir, destination_dir, subjects=[], overwrite_file=True,
                    tasks_to_run=["FMA17", "FMA18", "FMA19", "FMA20", "FMA21", 
                                  "FMA22", "FMA23"], tasks_to_skip=[],
                    subjects_to_skip=[]):
    if len(subjects) == 0:
        subject_dirs = [dir for dir in os.listdir(source_dir) if 
                        os.path.isdir(os.path.join(source_dir, dir))
                        and dir[0:2] not in subjects_to_skip]
    else:
        subject_dirs = [dir for dir in os.listdir(source_dir) if 
                        os.path.isdir(os.path.join(source_dir, dir)) and 
                        dir[0:2] in subjects]
    
    tasks = list(set(tasks_to_run) - set(tasks_to_skip))

    # Prepare destination directory
    if not os.path.isdir(os.path.join(destination_dir, "HS_data")):
        os.makedirs(os.path.join(destination_dir, "HS_data"))

    # Extract subject_id from dir name and create destination path
    for subject_dir in subject_dirs:
        subject_dir_path = os.path.join(source_dir, subject_dir)
        subject_id = subject_dir[0:2]
        new_subject_dir = os.path.join(destination_dir, "HS_data", subject_id)

        # Create destination folder if it does not exist
        if not os.path.isdir(new_subject_dir):
            os.makedirs(new_subject_dir)
        for task in tasks:  # Create FMA folders
            if not os.path.isdir(os.path.join(new_subject_dir, task)):
                os.makedirs(os.path.join(new_subject_dir, task))

        print(f"SUBJECT: {subject_dir}")
        score_dirs = os.listdir(subject_dir_path)
        for score_dir in score_dirs:
            
            fma_files = {}
            
            numbers = re.findall(r'\d+', score_dir) # Extract score from dir name
            score = int(numbers[-1]) if numbers else None
            score_dir_path = os.path.join(subject_dir_path, score_dir)

            if not os.path.isdir(score_dir_path):
                continue

            csv_files = [file for file in sorted(os.listdir(score_dir_path)) if file.endswith('.csv')]
            
            for file in csv_files:
                new_filename_parts = file.split("_")
                fma_num = new_filename_parts[0][0:5]
                
                if fma_num not in tasks:
                    continue

                if not fma_num[3:5].isdigit():
                    continue  # Skip files that don't have the FMA num

                timestamp = extract_timestamp(file)

                if not timestamp:
                    continue

                new_filename_parts.insert(0, subject_id)
                new_filename_parts.insert(3, "Tendency")
                new_filename_parts.insert(4, f"FT{str(int(fma_num[3:5]) + 7)}=S{score}")

                new_filename = "_".join(new_filename_parts)
                if fma_num not in fma_files:
                    fma_files[fma_num] = []
                fma_files[fma_num].append((timestamp, file, score_dir_path, new_filename))

            for fma_num, files in fma_files.items():
                
                sorted_files = sorted(files, key=lambda x: x[0])

                for trial_num, (_, file, from_dir, filename) in enumerate(sorted_files, start=1):
                    new_filename_parts = filename.split("_")
                    new_filename_parts.insert(5, f"Trial{trial_num}")
                    new_filename = "_".join(new_filename_parts)
                    print(f"File: {file}")
                    if not os.path.exists(os.path.join(new_subject_dir, fma_num, new_filename)) or overwrite_file:
                        shutil.copy(os.path.join(from_dir, file), 
                                os.path.join(new_subject_dir, fma_num, new_filename))

''' 
    Renames and organizes CSV files from a source directory based on subject ID, 
    Affection, left or right hand, score, and trial number.
    Files are copied to a new destination directory, organized into FMA subfolders.
    
    Parameters:
        source_dir (str): Path to the source directory.
        destination_dir (str): Path to the destination directory.
        subjects (list): List of subject IDs to process. Passing an
        empty list or false value will default to processing all 
        data in the source directory
'''
def sp_rename_files(source_dir, destination_dir, subjects=[], overwrite_file=True,
                    tasks_to_run=["FMA17", "FMA18", "FMA19", "FMA20", "FMA21", 
                                  "FMA22", "FMA23"], tasks_to_skip=[],
                    subjects_to_skip=[]):
    if len(subjects) == 0:
        subject_dirs = [dir for dir in os.listdir(source_dir) if 
                        os.path.isdir(os.path.join(source_dir, dir))
                        and dir not in subjects_to_skip]
    else:
        subject_dirs = [dir for dir in os.listdir(source_dir) if 
                        os.path.isdir(os.path.join(source_dir, dir)) and 
                        dir in subjects]
    
    tasks = list(set(tasks_to_run) - set(tasks_to_skip))

    # Prepare destination directory
    if not os.path.isdir(os.path.join(destination_dir, "SP_data")):
        os.makedirs(os.path.join(destination_dir, "SP_data"))
    
    # Extract subject_id from dir name and create destination path
    for subject_dir in subject_dirs:
        subject_dir_path = os.path.join(source_dir, subject_dir, 
                                        f"{subject_dir}_FMA_HAND",
                                        f"{subject_dir}_FMA_VR_HAND")
        if not os.path.isdir(subject_dir_path):
            continue
        
        # Extract FMA Scores from excel file
        fma_score_file = None
        for file in os.listdir(os.path.join(source_dir, subject_dir)):
            if file.endswith('.xlsx') and 'FMA_SCORE' in file:
                fma_score_file = os.path.join(source_dir, subject_dir, file)
                break
        if not os.path.exists(fma_score_file):
            continue
        df = pd.read_excel(fma_score_file)
        lefthand = {}
        righthand = {}
        if df.iloc[3, 1] == "Left":
            for row in range(28, 35):
                lefthand[df.iloc[row,0][0:5]] = df.iloc[row, 1]
                righthand[df.iloc[row,0][0:5]] = df.iloc[row, 3]
        elif df.iloc[3, 1] == "Right":
            for row in range(28, 35):
                righthand[df.iloc[row,0][0:5]] = df.iloc[row, 1]
                lefthand[df.iloc[row,0][0:5]] = df.iloc[row, 3]
        fma_scores = {"lefthand": lefthand, "righthand": righthand}


        # Create destination folder if it does not exist
        new_subject_dir = os.path.join(destination_dir, "SP_data", subject_dir)

        if not os.path.isdir(new_subject_dir):
            os.makedirs(new_subject_dir)
        for task in tasks:  # Create FMA folders
            if not os.path.isdir(os.path.join(new_subject_dir, task)):
                os.makedirs(os.path.join(new_subject_dir, task))

        print(f"SUBJECT: {subject_dir}")
        hand_dirs = os.listdir(subject_dir_path)
        for hand_dir in hand_dirs:
            
            fma_files = {}
            
            hand_dir_path = os.path.join(subject_dir_path, hand_dir)
            if not os.path.isdir(hand_dir_path):
                continue
            
            hand_dir_parts = hand_dir.split("_")
            affection = "Affected" if "Affected" in hand_dir_parts else "Unaffected" # Extract affection from dir name
            side = "lefthand" if "LeftHand" in hand_dir_parts else "righthand"
            
            csv_files = [file for file in sorted(os.listdir(hand_dir_path)) 
                         if file.endswith('.csv')]
            
            for file in csv_files:
                new_filename_parts = file.split("_")
                fma_num = new_filename_parts[0][0:5]

                if fma_num not in tasks:
                    continue

                if not fma_num[3:5].isdigit():
                    continue  # Skip files that don't have the FMA num

                timestamp = extract_timestamp(file)

                if not timestamp:
                    continue

                new_filename_parts.insert(0, subject_dir)
                new_filename_parts.insert(2, affection)
                new_filename_parts.insert(4, f"FT{str(int(fma_num[3:5]) + 7)}=S{fma_scores[side][fma_num]}")

                new_filename = "_".join(new_filename_parts)
                
                if fma_num not in fma_files:
                    fma_files[fma_num] = []
                fma_files[fma_num].append((timestamp, file, hand_dir_path, new_filename))

            for fma_num, files in fma_files.items():
                sorted_files = sorted(files, key=lambda x: x[0])

                for trial_num, (_, file, from_dir, filename) in enumerate(sorted_files, start=1):
                    new_filename_parts = filename.split("_")
                    new_filename_parts.insert(-6, f"Trial{trial_num}")
                    new_filename = "_".join(new_filename_parts)
                    print(f"File: {file}")
                    if not os.path.exists(os.path.join(new_subject_dir, fma_num, new_filename)) or overwrite_file:
                        shutil.copy(os.path.join(from_dir, file), 
                                os.path.join(new_subject_dir, fma_num, new_filename))
        
if __name__ == '__main__':

    # ==Configurations==
    DATA_TYPE = ["SP"] # "HS" and/or "SP" ; "HS" means healthy subjects - tendency data
                            # AND "SP" means Stroke Patients - actual experiment data 
               # ["HS"]
    overwrite_file = False  # Setting to overwrite files with new file if they already exist
                            # By default, function automatically overwrites files

    # Specifies which tasks (FMA17-23) to run. If parameter isn't passed, all tasks are run 
    tasks_to_run = ["FMA17", "FMA18", "FMA19", "FMA20" "FMA21", "FMA22", "FMA23"]

    # Specifies any tasks (FMA17-23) to skip. If parameter isn't passed, none are skipped
    tasks_to_skip = []

    # ===HS=== 
    # original input source directory   
    source_hs = r'c:\Users\FireF\Box\FMA_Experiment_Share\FMAhand-sensor\HS-tendency-data'
    subjects_hs = ["VV"]    # Specifies subjects to run. If parameter isn't passed, all subjects are run
    
    # ===SP===
    source_sp = r'C:\Users\FireF\Box\FMA_Experiment_Share\SP'
    subjects_sp = ["ID12-DBML-E250212"]    # Specifies subjects to run. If parameter isn't passed, all subjects are run

    # output directory 
    destination = r'c:\Users\FireF\Box\FMA_Experiment_Share\FMAhand-sensor\data_for_processing'
    
    if "HS" in DATA_TYPE:
        hs_rename_files(source_hs, destination)
    if "SP" in DATA_TYPE:
        sp_rename_files(source_sp, destination)
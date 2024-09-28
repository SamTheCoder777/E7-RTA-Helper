import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import hashlib
import shutil

def get_file_hash(file_path):
    """Calculate the SHA256 hash of the file's content."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in chunks of 64KB
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def file_exists_with_same_content(file_path, destination_folder):
    """Check if there is a file with the same content in the destination folder."""
    src_file_hash = get_file_hash(file_path)

    for root, _, files in os.walk(destination_folder):
        for file in files:
            dest_file_path = os.path.join(root, file)
            if get_file_hash(dest_file_path) == src_file_hash:
                return True
    return False

def copy_file_if_unique(src_file, dest_folder):
    """Copy the file to the destination folder if it's unique (name or content)."""
    base_name = os.path.basename(src_file)
    dest_file = os.path.join(dest_folder, base_name)

    # Ensure destination directory exists
    os.makedirs(dest_folder, exist_ok=True)

    # Check for files with the same content
    if file_exists_with_same_content(src_file, dest_folder):
        print(f"A file with the same content already exists. Skipping copy.")
        return

    # If file name exists, append a number to avoid overwriting
    counter = 1
    base_name_no_ext, ext = os.path.splitext(base_name)
    while os.path.exists(dest_file):
        dest_file = os.path.join(dest_folder, f"{base_name_no_ext}_{counter}{ext}")
        counter += 1

    # Copy the file
    shutil.copy2(src_file, dest_file)
    print(f"File copied to: {dest_file}")

def merge(csv_files):
    merged_csv = pd.DataFrame()
    max_match_number = 0
    
    for csv_file in csv_files:
        # Read the current CSV file
        current_csv = pd.read_csv(csv_file)
        
        # Adjust match numbers to avoid duplicates
        current_csv['Match Number'] += max_match_number
        
        # Update the max match number for the next iteration
        max_match_number = current_csv['Match Number'].max()
        
        # Concatenate the current CSV to the merged DataFrame
        merged_csv = pd.concat([merged_csv, current_csv], ignore_index=True)

    # Group by 'Match Number' and remove duplicates
    grouped = merged_csv.groupby('Match Number')[['Pick Order', 'Match Result', 'Team', 'Hero', 'First Pick']].agg(tuple)
    is_duplicated = grouped.duplicated(keep="first")
    
    # Get only the non-duplicated 'Match Number' values
    unique_match_numbers = grouped[~is_duplicated].index
    
    # Filter the original DataFrame to retain only the non-duplicated 'Match Number' groups
    merged_csv = merged_csv[merged_csv['Match Number'].isin(unique_match_numbers)]
    
    # Re-factorize the 'Match Number' to be sequential
    merged_csv.loc[:, 'Match Number'] = pd.factorize(merged_csv['Match Number'])[0] + 1
    return merged_csv

copy_file_if_unique('data/epic7_match_history.csv', 'match_histories')

# Get files from the folder
csvs = [join('match_histories', f) for f in listdir('match_histories') if isfile(join('match_histories', f))]
print(csvs)

# Merge all CSVs
final_csv = merge(csvs)

# Save the merged DataFrame to a new CSV
final_csv.to_csv('data/epic7_match_history.csv', index=False)
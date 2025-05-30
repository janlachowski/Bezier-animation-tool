from pathlib import Path

# Define the base folder
base_path = Path(__file__).parent
animation_folder = base_path / "animation"

# Check if the folder exists
if animation_folder.exists() and animation_folder.is_dir():
    # Iterate over all files in the folder
    for file in animation_folder.iterdir():
        # Check if it's a file (skip directories)
        if file.name != "frame0.png":
            try:
                file.unlink()  # Delete the file
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")
else:
    print(f"Folder {animation_folder} does not exist or is not a directory.")
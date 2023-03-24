import os
import toml


def create_directories(dir_structure: dict, start_path: str = "."):
    for directory, subdirectories in dir_structure.items():
        os.makedirs(os.path.join(start_path, directory), exist_ok=True)
        if isinstance(subdirectories, dict):
            create_directories(subdirectories, os.path.join(start_path, directory))
        elif isinstance(subdirectories, set):
            for subdirectory in subdirectories:
                os.makedirs(os.path.join(start_path, directory, subdirectory), exist_ok=True)


def create_directories_and_settings(directory_structure: dict, settings: dict, start_path: str = ".", force=False):
    if os.path.exists(start_path) and os.listdir(start_path) is not None and not force:
        return False
    create_directories(directory_structure, start_path)
    with open(os.path.join(start_path, 'settings.toml'), 'w') as f:
        toml.dump(settings, f)
    return True

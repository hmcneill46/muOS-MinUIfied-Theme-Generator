import os
from pathlib import Path
import shutil
import sys


def find_base_dirs() -> tuple[Path, Path]:
    frozen: bool = getattr(sys, "frozen", False)
    mei_pass: str = getattr(sys, "_MEIPASS", "")
    executable: str = getattr(sys, "executable", "")

    if frozen and mei_pass:
        # The application is running as a bundle
        BASE_DIR = Path(executable).parent
        RESOURCES_DIR = Path(mei_pass)  # type: ignore[attr-defined]
    else:
        # the application is running in a normal Python environment
        BASE_DIR = Path()
        RESOURCES_DIR = BASE_DIR

    return BASE_DIR, RESOURCES_DIR


def copy_contents(src: Path, dst: Path):
    if not dst.exists():
        os.makedirs(dst)

    for item in os.listdir(src):
        src_path = src / item
        dst_path = dst / item

        if src_path.is_dir():
            if not dst_path.exists():
                shutil.copytree(src_path, dst_path)
            else:
                copy_contents(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


def ensure_folder_exists(folder_path: Path):
    if not folder_path.exists():
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"Error creating folder {folder_path}: {e}")


def delete_folder(folder_path: Path):
    if folder_path.exists():
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            print(f"Error deleting folder {folder_path}: {e}")
    else:
        raise FileNotFoundError(f"Folder {folder_path} does not exist")


def delete_file(file_path: Path):
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    else:
        raise FileNotFoundError(f"File {file_path} does not exist")


def rename_file(src: Path, dst: Path):
    if src.exists():
        try:
            os.rename(src, dst)
        except Exception as e:
            print(f"Error renaming file {src} to {dst}: {e}")
    else:
        raise FileNotFoundError(f"File {src} does not exist")

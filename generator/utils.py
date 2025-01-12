from pathlib import Path
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
        BASE_DIR = Path(__file__).resolve().parent
        RESOURCES_DIR = BASE_DIR

    return BASE_DIR, RESOURCES_DIR

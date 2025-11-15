import glob
import os


def get_sub_dir_path(
    top_dir:  str,
    root_dir: str = "/eos/experiment/sndlhc/convertedData/physics"
):
    """
    Return a list of full paths to subdirectories named `top_dir`,
    starting from `root_path`.
    """

    matchingDirs = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        if os.path.basename(dirpath) == top_dir:
            matchingDirs.append(dirpath)
    return matchingDirs

def get_all_files(input_dir: str, files: str) -> list:
    """
    Get list of all files matching pattern in a directory.

    Args:
        inputDir: Directory path to search in
        files: File pattern to match

    Returns:
        list: List of files matching the pattern
    """
    return glob.glob(f"{input_dir}/{files}")

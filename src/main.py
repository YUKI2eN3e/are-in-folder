#!/usr/bin/env python3.11
from . import *
import argparse
import hashlib
from typing import List
from os import scandir, getcwd, DirEntry
from sys import platform
from rich.progress import track


def get_opts() -> argparse.Namespace:
    """Get program args/opts

    Returns:
            argparse.Namespace: files_in, dest_folder
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--files-in",
        help="Folder with subset of files in dest folder.",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dest-folder",
        help="Dest folder that might contain the subset of files.",
        required=True,
    )
    return parser.parse_args()


def get_hash(file_name: str) -> str:
    with open(file_name, "br", buffering=0) as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def list_files(dir: str) -> List[DirEntry[str]]:
    """Get a list of files in the directory 'dir'

    Args:
        dir (str): the directory to check

    Returns:
        List[DirEntry[str]]: list of files in 'dir'
    """
    if (("\\" not in dir) if platform == "win32" else ("/" not in dir)) or ".." in dir[
        :2
    ]:
        if platform == "win32":
            dir = "{}\\{}".format(getcwd(), dir)
        else:
            dir = "{}/{}".format(getcwd(), dir)
    dir_entries = scandir(dir)
    files: List[str] = []
    for entry in dir_entries:
        if entry.is_file():
            files.append(entry)
    return files


def run():
    opts = get_opts()
    file_subset = list_files(opts.files_in)
    file_passes = list(range(len(file_subset)))
    for i in track(range(len(file_subset)), "Checking Hashes..."):
        try:
            dest_hash = get_hash(
                "{}\\{}".format(opts.dest_folder, file_subset[i].name)
                if platform == "win32"
                else "{}/{}".format(opts.dest_folder, file_subset[i].name)
            )
            if get_hash(file_subset[i].path) == dest_hash:
                file_passes[i] = True
            else:
                file_passes[i] = False
        except FileNotFoundError:
            file_passes[i] = False
    if False not in file_passes:
        console.print("[green]All files passed![/green]")
    else:
        for i in range(len(file_passes)):
            if not file_passes[i]:
                console.print(
                    "[red][bold]Failed:\t[/bold]{}[/red]".format(file_subset[i].name)
                )


if __name__ == "__main__":
    run()

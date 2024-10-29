import argparse
import pathlib

def safe_copy(source, destination):
    print(f"Copying {source} -> {destination}")

def main():
    parser = argparse.ArgumentParser(description="Tool to train the parameters of the cryptodec")
    parser.add_argument("--source", required=True, help="The source directory to copy from")
    parser.add_argument("--destination", required=True, help="The destination to copy to")

    args = parser.parse_args()

    safe_copy(pathlib.Path(args.source), pathlib.Path(args.destination))
import pathlib
import sys

import matplotlib.pyplot as plt

from modules.fileio import read_csv


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file> ...")
        sys.exit(1)

    files = sys.argv[1:]
    n = len(sys.argv) - 1
    for i in range(n):
        label, arr = read_csv(pathlib.Path(files[i]).resolve())
        plt.plot(arr, label=f"{files[i]}", alpha=1/n)

    plt.xlabel("Time")
    plt.ylabel("Output")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()

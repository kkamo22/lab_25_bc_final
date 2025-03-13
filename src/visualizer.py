import pathlib
import sys

import matplotlib.pyplot as plt

from modules.fileio import read_csv


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file1> <csv_file2>")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]
    label1, data1 = read_csv(pathlib.Path(file1).resolve())
    label2, data2 = read_csv(pathlib.Path(file2).resolve())

    if label1 != label2:
        print("Error: CSV files must have the same label in the first row.")
        sys.exit(1)

    plt.plot(data1, label=f"{file1}", alpha=0.5)
    plt.plot(data2, label=f"{file2}", alpha=0.5)
    plt.xlabel("Time")
    plt.ylabel(label1)
    plt.legend()
    plt.title(f"Visualization of {label1}")
    plt.show()


if __name__ == "__main__":
    main()

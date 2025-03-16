import csv
import pathlib
import sys

import matplotlib.pyplot as plt


def read_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        label = next(reader)[0]  # 1行目のラベル
        data = [float(row[0]) for row in reader]  # 2行目以降のデータ
    return label, data


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

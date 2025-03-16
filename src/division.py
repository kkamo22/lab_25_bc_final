import sys
import csv

import matplotlib.pyplot as plt


def read_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        label = next(reader)[0]  # 1行目のラベル
        data = [float(row[0]) for row in reader]  # 2行目以降のデータ
    return label, data


def plot_data(data, label, N, t, n):
    start = n*t
    end = n*t + N
    sampled_data = data[start:end]
    indices = list(range(len(data)))
    sampled_indices = indices[start:end]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(indices, data)
    ax.plot(sampled_indices, sampled_data)
    ax.set_xlabel("Time (sampled every {} steps)".format(t))
    ax.set_ylabel(label)
    ax.set_ylim(0, 1024)
    ax.set_title(f"Visualization of {label} (N={N}, t={t})")
    plt.show()


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <csv_file> <N> <t>")
        sys.exit(1)
    
    file = sys.argv[1]
    try:
        N = int(sys.argv[2])
        t = int(sys.argv[3])
    except ValueError:
        print("Error: N and t must be integers.")
        sys.exit(1)
    
    label, data = read_csv(file)
    for i in range((len(data) - N) // t):
        plot_data(data, label, N, t, i)


if __name__ == "__main__":
    main()

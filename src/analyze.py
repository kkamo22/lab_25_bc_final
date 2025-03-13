import pathlib
import sys

import matplotlib.pyplot as plt
import numpy as np

from modules.fileio import read_csv


BITS = 10
VCC = 3.3
GAIN = 1009


def calc_emg(data):
    emg = ((np.array(data) / 2**BITS) - 1/2) * VCC * 1000 / GAIN
    return emg


def calc_ema(arr, rho):
    ems = [arr[0]]
    for val in arr[1:]:
        ems.append(rho*ems[-1] + (1 - rho)*val)
    return np.array(ems)


if __name__ == "__main__":
    filename = sys.argv[1]
    label, data = read_csv(pathlib.Path(filename).resolve())

    emg = calc_emg(data)
    emg = np.abs(emg)

    # EMS を計算
    ema1 = calc_ema(emg, 0.9)
    ema2 = calc_ema(emg, 0.95)
    ema3 = calc_ema(emg, 0.99)

    # グラフを表示
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(emg, alpha=0.25, label="EMG")
    ax.plot(ema1, alpha=0.25, label="EMA (ρ = 0.9)")
    ax.plot(ema2, alpha=0.25, label="EMA (ρ = 0.95)")
    ax.plot(ema3, alpha=0.25, label="EMA (ρ = 0.99)")
    ax.legend()
    ax.set_xlabel("Index")
    ax.set_ylabel("Output")
    ax.set_ylim(0.0, 1.0)
    plt.show()

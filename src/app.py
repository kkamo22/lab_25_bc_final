import sys
import time

import bitalino
import matplotlib.pyplot as plt

from modules.device import get_device, calc_emg


MAC_ADDRESS = "98:D3:91:FE:44:E9"

EMG_PIN = 1
ACC_PIN = 0

SAMPLING_RATE = 1000  # Hz
N_SAMPLES = 100

BITS = 10
VCC = 3.3
GAIN = 1009


if __name__ == "__main__":
    # デバイスの取得
    device = get_device(MAC_ADDRESS)
    if type(device) !=  bitalino.BITalino:
        print("ERROR: Could not get the device.", file=sys.stderr)
        exit(1)

    # 計測準備
    device.start(SAMPLING_RATE, [ACC_PIN])

    # データ計測
    start_time = 0.0
    update_time = 0.5

    fig = plt.figure()
    ax = fig.add_subplot(111)

    emgs = []
    emgs_ema = []
    rho = 0.95
    while True:
        data = device.read(N_SAMPLES)
        emg = calc_emg(data[:, 5][0], BITS, VCC, GAIN)
        #emg = abs(emg)
        emgs.append(emg)
        emgs_ema.append(
            rho*emgs_ema[-1] + (1 - rho)*emg
                if len(emgs_ema) > 0
                else emg)
        if len(emgs) > 100:
            emgs = emgs[-100:]
            emgs_ema = emgs_ema[-100:]

        current_time = time.time()
        if current_time - start_time > update_time:
            start_time = current_time
            ax.cla()
            ax.plot(emgs)
            ax.plot(emgs_ema)
            ax.set_xlabel("Index")
            ax.set_ylabel("EMG / ms")
            ax.set_ylim(-1.0, 1.0)
            plt.draw()
            plt.pause(0.1)

import sys
import time

import bitalino
import matplotlib.pyplot as plt

from modules.device import get_device


MAC_ADDRESS = "98:D3:91:FE:44:E9"

SAMPLING_RATE = 1000  # Hz
N_SAMPLES = 100


if __name__ == "__main__":
    # デバイスの取得
    device = get_device(MAC_ADDRESS)
    if type(device) !=  bitalino.BITalino:
        print("ERROR: Could not get the device.", file=sys.stderr)
        exit(1)

    # 計測準備
    device.start(SAMPLING_RATE, [0])

    # データ計測
    start_time = time.time()
    running_time = 10.0
    y = []
    while True:
        data = device.read(N_SAMPLES)
        data_a1 = data[:, 5]

        y.extend(data_a1)

        if time.time() - start_time > running_time:
            break
    plt.plot(y)
    plt.show()

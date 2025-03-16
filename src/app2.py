import sys
import threading
import time

import bitalino
import matplotlib.pyplot as plt


MAC_ADDRESS = "98:D3:91:FE:44:E9"

ACC_PIN = 0
EMG_PIN = 1

SAMPLING_RATE = 1000  # Hz
N_SAMPLES = 100

BITS = 10
VCC = 3.3
GAIN = 1009

MAX_LEN = 100
EMGS_EMA_RHO = 0.925

SMILE_THRES = 0.08  # mV


# マルチスレッド用
stop_event = threading.Event()


def get_device(mac_address):
    device = None
    try:
        device = bitalino.BITalino(mac_address)
    except Exception as e:
        print("ERROR: The MAC address or serial port for the device is "
              "invalid.", file=sys.stderr)
    return device


def calc_emg(data, bits, vcc, gain):
    emg = ((data / 2**bits) - 1/2) * vcc * 1000 / gain
    return emg


def calc_ema(old, new, rho):
    return rho*old + (1 - rho)*new


def add_ema(ema_list, new, rho):
    if len(ema_list) > 0:
        ema = calc_ema(ema_list[-1], new, rho)
    else:
        ema = new
    ema_list.append(ema)


def sampling(device, accs, emgs, emgs_ema):
    while not stop_event.is_set():
        # データ取得
        data = device.read(N_SAMPLES)
        acc = data[:, 5+ACC_PIN][0]
        emg = calc_emg(data[:, 5+EMG_PIN][0], BITS, VCC, GAIN)

        # データ追加・廃棄
        accs.append(acc)
        if len(accs) > MAX_LEN:
            del accs[:-MAX_LEN]

        emgs.append(emg)
        add_ema(emgs_ema, abs(emg), EMGS_EMA_RHO)
        if len(emgs) > MAX_LEN:
            del emgs[:-MAX_LEN]
            del emgs_ema[:-MAX_LEN]


def mainloop(accs, emgs, emgs_ema):
    #fig = plt.figure()
    #ax = fig.add_subplot(111)

    smiling = False

    start_time = 0.0
    update_time = 0.5
    while not stop_event.is_set():
        current_time = time.time()
        if current_time - start_time > update_time:
            # グラフ更新
            """
            ax.cla()
            ax.plot(emgs)
            ax.plot(emgs_ema)
            ax.set_xlabel("Index")
            ax.set_ylabel("EMG / ms")
            #ax.set_ylim(-1.0, 1.0)
            plt.draw()
            plt.pause(0.1)"""

            if len(emgs_ema) > 0:
                print(emgs_ema[-1])
                if emgs_ema[-1] > SMILE_THRES:
                    if not smiling:
                        smiling = True
                        print("Smile!")
                else:
                    if smiling:
                        smiling = False
                        print("No smile...")

            start_time = current_time


if __name__ == "__main__":
    # デバイスの取得
    device = get_device(MAC_ADDRESS)
    if type(device) !=  bitalino.BITalino:
        print("ERROR: Could not get the device.", file=sys.stderr)
        exit(1)

    # 計測準備
    device.start(SAMPLING_RATE, [ACC_PIN, EMG_PIN])

    # スレッド・共有資源の用意
    accs = []
    emgs = []
    emgs_ema = []

    sample_t = threading.Thread(
        target=sampling, args=[device, accs, emgs, emgs_ema])
    main_t = threading.Thread(
        target=mainloop, args=[accs, emgs, emgs_ema])

    # 処理
    sample_t.start()
    main_t.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
        sample_t.join()
        main_t.join()

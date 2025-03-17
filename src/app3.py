import math
import os
import sys
import threading
import time

import bitalino
import numpy as np
import pygame
import pygame.locals


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")


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

MAX_HC = 126


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


def make_honeycomb_pos_list(center, d, n):
    pos_list = []
    hor = math.sqrt(3) / 2
    offsets = np.array([
        ( hor*d,  d/2),
        ( hor*d, -d/2),
        (     0, -d  ),
        (-hor*d, -d/2),
        (-hor*d,  d/2),
        (     0,  d  ),
    ])
    steps = np.array([
        (     0, -d  ),
        (-hor*d, -d/2),
        (-hor*d,  d/2),
        (     0,  d  ),
        ( hor*d,  d/2),
        ( hor*d, -d/2),
    ])
    i = 0
    count = 0
    layer = 1
    while i <= n:
        i += 1
        count += 1
        if count > 6 * layer:
            count = 1
            layer += 1
        l = (count - 1) // layer
        m = (count - 1) % layer
        pos = center + layer*offsets[l] + m*steps[l]
        pos_list.append(pos)
    return pos_list


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


def mainloop(screen, accs, emgs, emgs_ema):
    smiling = False
    num_of_honeycombs = 0
    hc_pos_list = make_honeycomb_pos_list(np.array([200, 200]), 38, MAX_HC)

    # データが取得されるまで待機
    while len(emgs_ema) == 0:
        time.sleep(0.1)

    hc_img = pygame.image.load(os.path.join(IMG_DIR, "honeycomb1.png"))
    hc_img.convert()
    hc_img = pygame.transform.scale(hc_img, (50, 50))
    hc_img = pygame.transform.rotate(hc_img, 90)

    start_time = 0.0
    update_time = 0.5
    while not stop_event.is_set():
        # 描画
        screen.fill(color=(200, 200, 200))
        screen.blit(hc_img, (175, 175))

        for i in range(num_of_honeycombs):
            pos = hc_pos_list[i]
            #pygame.draw.circle(screen, (255, 255, 0), pos, 5)
            screen.blit(hc_img, pos - np.array([50, 50])/2)

        pygame.display.update()

        # 笑顔の判定
        print(f"EMG: {emgs_ema[-1]:.5f} mV  {num_of_honeycombs}",
              file=sys.stderr)
        if emgs_ema[-1] > SMILE_THRES:
            if not smiling:
                smiling = True
                print("Smile!", file=sys.stderr)
        else:
            if smiling:
                smiling = False
                print("No smile...", file=sys.stderr)

        # ハニカム増減
        current_time = time.time()
        if smiling:
            if current_time - start_time > update_time:
                if num_of_honeycombs <= MAX_HC:
                    num_of_honeycombs += 1
                    start_time = current_time
        else:
            if current_time - start_time > update_time:
                if num_of_honeycombs > 0:
                    num_of_honeycombs -= 1
                    start_time = current_time

        time.sleep(0.01)


if __name__ == "__main__":
    # pygame 立ち上げ
    pygame.init()
    screen = pygame.display.set_mode(size=(400, 400))

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
        target=mainloop, args=[screen, accs, emgs, emgs_ema])

    # メインルーチン
    sample_t.start()
    main_t.start()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    pygame.quit()
                    raise KeyboardInterrupt
    except KeyboardInterrupt:
        stop_event.set()
        sample_t.join()
        main_t.join()

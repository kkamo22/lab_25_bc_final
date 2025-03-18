import os
import sys
import threading
import time

import bitalino
import numpy as np
import pygame
import pygame.locals

from modules.device import (
    get_device,
    start_device,
    sample_data,
)
from modules.honeycomb import (
    HC_BASE,
    HC_STRONG,
    HC_NORMAL,
    HC_WEAK,
    hc_imgs,
    load_hc_imgs,
    make_hc_pos_list,
    make_hc_surface,
)


# ファイルパス
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")

# デバイス関連
MAC_ADDRESS = "98:D3:91:FE:44:E9"

# 画面の設定
SCREEN_W = 400
SCREEN_H = 400

# その他
SMILE_THRES = 0.08  # mV

MAX_HC = 126


# マルチスレッド用
stop_event = threading.Event()


def sample_t_func(device, accs, emgs, emgs_ema):
    """サンプリング用スレッドの関数."""
    while not stop_event.is_set():
        sample_data(device, accs, emgs, emgs_ema)


def main_t_func(screen, accs, emgs, emgs_ema):
    smiling = False
    num_of_honeycombs = 0

    # データが取得されるまで待機
    while len(emgs_ema) == 0:
        time.sleep(0.1)

    start_time = 0.0
    update_time = 0.5
    while not stop_event.is_set():
        # 描画
        screen.fill(color=(200, 200, 200))
        hc_surface = make_hc_surface(
            np.array([SCREEN_W, SCREEN_H]), num_of_honeycombs)
        screen.blit(hc_surface, (0, 0))

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
    # pygame 初期化
    pygame.init()
    screen = pygame.display.set_mode(size=(400, 400))

    # ハニカム準備
    load_hc_imgs(IMG_DIR)
    make_hc_pos_list(np.array([SCREEN_W, SCREEN_H]) / 2, 38, MAX_HC)

    # デバイスの取得
    while True:
        device = get_device(MAC_ADDRESS)
        if type(device) == bitalino.BITalino:
            break
        print("ERROR: Could not get the device.", file=sys.stderr)

    # 計測準備
    start_device(device)

    # スレッド・共有資源の用意
    accs = []
    emgs = []
    emgs_ema = []

    sample_t = threading.Thread(
        target=sample_t_func, args=[device, accs, emgs, emgs_ema])
    main_t = threading.Thread(
        target=main_t_func, args=[screen, accs, emgs, emgs_ema])

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

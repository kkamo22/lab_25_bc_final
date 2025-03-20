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
from modules.facial import (
    calibrate,
    detect_smile,
    make_gauge_surface,
)
from modules.honeycomb import (
    FIELD_1,
    load_hc_imgs,
    make_field_info,
    activate_honeycomb,
    deactivate_honeycomb,
    make_hc_surface,
)


# ファイルパス
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")

# デバイス関連
MAC_ADDRESS = "98:D3:91:FE:44:E9"

# 画面の設定
SCREEN_W = 720
SCREEN_H = 600
SCREEN_SIZE = np.array([SCREEN_W, SCREEN_H])

SCREEN_CENTER = np.array([SCREEN_W, SCREEN_H]) / 2

# その他
SMILE_THRES = 0.08  # mV

MAX_HC = 126


# マルチスレッド用
stop_event = threading.Event()


def sample_t_func(device, accs, emgs, emgs_ema):
    """サンプリング用スレッドの関数."""
    while not stop_event.is_set():
        sample_data(device, accs, emgs, emgs_ema)


def render_t_func(surfaces, field_info, emgs_ema):
    """描画用スレッドの関数."""
    while not stop_event.is_set():
        hc_surface = make_hc_surface(SCREEN_SIZE, field_info)
        gauge_surface = make_gauge_surface(SCREEN_SIZE, emgs_ema[-1])
        surfaces["hc"] = hc_surface
        surfaces["gauge"] = gauge_surface


def main_t_func(device, screen, accs, emgs, emgs_ema):
    smiling = False
    num_of_honeycombs = 0

    # フィールド読み込み
    field_info = make_field_info(FIELD_1, SCREEN_CENTER)

    # データが取得されるまで待機
    while len(emgs_ema) == 0:
        time.sleep(0.1)

    calibrate(device, screen, emgs_ema)

    # 描画用スレッドの準備
    surfaces = {
        "hc": make_hc_surface(SCREEN_SIZE, field_info),
        "gauge": make_gauge_surface(SCREEN_SIZE, emgs_ema[-1]),
    }
    render_t = threading.Thread(
        target=render_t_func, args=[surfaces, field_info, emgs_ema])
    render_t.start()

    start_time = 0.0
    update_time = 0.5
    while not stop_event.is_set():
        #sample_data(device, accs, emgs, emgs_ema)

        # 描画
        screen.fill(color=(200, 200, 200))
        screen.blit(surfaces["hc"], (0, 0))
        screen.blit(surfaces["gauge"], (0, 0))

        pygame.display.update()

        if num_of_honeycombs >= field_info["num_of_hcs"]:
            break

        # 笑顔の判定
        #print(emgs_ema[-1])
        if detect_smile(emgs_ema[-1]):
            if not smiling:
                smiling = True
        else:
            if smiling:
                smiling = False

        # ハニカム増減
        current_time = time.time()
        if smiling:
            if current_time - start_time > update_time:
                if num_of_honeycombs <= MAX_HC:
                    num_of_honeycombs += 1
                    activate_honeycomb(field_info, num_of_honeycombs)
                    start_time = current_time
        else:
            if current_time - start_time > update_time:
                if num_of_honeycombs > 0:
                    deactivate_honeycomb(field_info, num_of_honeycombs)
                    num_of_honeycombs -= 1
                    start_time = current_time

        #time.sleep(0.01)

    raise KeyboardInterrupt


if __name__ == "__main__":
    # pygame 初期化
    pygame.init()
    screen = pygame.display.set_mode(size=(SCREEN_W, SCREEN_H))

    # ハニカム準備
    load_hc_imgs(IMG_DIR)

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
        target=main_t_func, args=[device, screen, accs, emgs, emgs_ema])

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

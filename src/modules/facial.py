import csv
import datetime
import os
import statistics
import sys
import time

import pygame

from modules.device import (
    sample_data,
)


# ファイル
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
LOG_DIR = os.path.join(ROOT_DIR, "log", "calibration")

# 閾値
SMILE_THD = 0.08  # mV
SMILE_MAX = 0.10  # mV

THD_RATE = 0.8

criteria = {}

# サーフェイスの設定
COLORKEY = (0, 255, 0)

# ゲージ関連
GAUGE_X = 8
GAUGE_Y = 16
GAUGE_W = 120
GAUGE_H = 40

BAR_X = GAUGE_X + GAUGE_W*SMILE_THD/SMILE_MAX - 1
BAR_Y = GAUGE_Y - 2
BAR_W = 2
BAR_H = GAUGE_H + 4

GAUGE_COLOR_EMPTY = (128, 64, 0)
GAUGE_COLOR_FULL = (210, 210, 0)
GAUGE_COLOR_BAR = (32, 32, 32)

# 画面
BG_COLOR = (200, 200, 200)

# キャリブレーション
CAL_TITLE_SIZE = 64
CAL_DESCR_SIZE = 32

CAL_TITLE_POS = (16, 16)
CAL_DESCR_POS = (16, 72)

CAL_FONT_COLOR = (32, 32, 32)

CAL_COOL_TIME = 6.0

CAL_DURATION = 5.0


def countdown_for_mes(screen, title, description):
    """測定前のカウントダウン."""
    font1 = pygame.font.SysFont(None, CAL_TITLE_SIZE)
    font2 = pygame.font.SysFont(None, CAL_DESCR_SIZE)
    screen.fill(color=BG_COLOR)
    screen.blit(font1.render(title, True, CAL_FONT_COLOR), CAL_TITLE_POS)
    screen.blit(font2.render(description, True, CAL_FONT_COLOR), CAL_DESCR_POS)
    pygame.display.update()
    start_time = time.time()
    while time.time() - start_time < CAL_COOL_TIME:
        time.sleep(0.05)
    start_time = 0.0
    count = 4
    while count > 0:
        current_time = time.time()
        if current_time - start_time > 1.0:
            count -= 1
            start_time = current_time
            if count <= 0:
                break
            screen.fill(color=BG_COLOR)
            screen.blit(
                font1.render(str(count), True, CAL_FONT_COLOR), CAL_TITLE_POS)
            pygame.display.update()
    screen.fill(color=BG_COLOR)
    screen.blit(font1.render("Go!", True, CAL_FONT_COLOR), CAL_TITLE_POS)
    pygame.display.update()
    start_time = time.time()
    while time.time() - start_time < 1.0:
        time.sleep(0.05)
    screen.fill(color=BG_COLOR)
    pygame.display.update()


def make_filename(description):
    """ログファイル名の生成."""
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{dt_str}_{description}"
    return filename


def measure_baseline(emgs):
    """ベースライン電圧の測定."""
    emg_data = []
    time_data = []
    start_time = time.time()
    while time.time() - start_time < CAL_DURATION:
        time_data.append(time.time() - start_time)
        emg_data.append(emgs[-1])
        time.sleep(0.01)
    filename = make_filename("baseline.csv")
    with open(os.path.join(LOG_DIR, filename), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(
            [["time", "img"]] + [list(i) for i in zip(time_data, emg_data)])
    ave = statistics.mean(emg_data)
    criteria["baseline_ave"] = ave
    print("AVERAGE:", criteria["baseline_ave"], "mV", file=sys.stderr)


def measure_smiling(device, emgs):
    """笑顔時の電圧の測定."""
    emg_data = []
    time_data = []
    start_time = time.time()
    while time.time() - start_time < CAL_DURATION:
        #sample_data(device, [], [], emgs)
        time_data.append(time.time() - start_time)
        emg_data.append(emgs[-1])
        time.sleep(0.01)
    #filename = make_filename("smiling.csv")
    #with open(os.path.join(LOG_DIR, filename), "w", newline="") as f:
    #    writer = csv.writer(f)
    #    writer.writerows(
    #        [["time", "img"]] + [list(i) for i in zip(time_data, emg_data)])
    ave = statistics.mean(emg_data)
    criteria["smiling_ave"] = ave
    print("AVERAGE:", criteria["smiling_ave"], "mV", file=sys.stderr)


def calibrate(device, screen, emgs):
    """電圧値をキャリブレーションする."""
    countdown_for_mes(
        screen,
        "Measurement",
        "Please keep smiling "
        f"for {CAL_DURATION} seconds.")
    measure_smiling(device, emgs)


def detect_smile(emg):
    """笑顔を検知する."""
    return emg > criteria["smiling_ave"] * THD_RATE


def render_gauge(surface, emg):
    """ゲージを描画する."""
    pygame.draw.rect(
        surface, GAUGE_COLOR_EMPTY, (GAUGE_X, GAUGE_Y, GAUGE_W, GAUGE_H))
    pygame.draw.rect(
        surface, GAUGE_COLOR_FULL, (
            GAUGE_X,
            GAUGE_Y,
            min(GAUGE_W * emg / criteria["smiling_ave"], GAUGE_W),
            GAUGE_H))
    bar_x = GAUGE_W*THD_RATE - 1
    pygame.draw.rect(
        surface, GAUGE_COLOR_BAR, (bar_x, BAR_Y, BAR_W, BAR_H))


def make_gauge_surface(screen_size, emg):
    """ゲージを描画したサーフェイスを生成する."""
    surface = pygame.surface.Surface(screen_size)
    surface.fill(COLORKEY)
    surface.set_colorkey(COLORKEY)
    render_gauge(surface, emg)
    return surface

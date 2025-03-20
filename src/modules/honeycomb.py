import itertools
import math
import os
import random
import sys
import time

import numpy as np
import pygame


# 画像ラベル
HC_IMG_BASE = "hc_base.png"
HC_IMG_1 = "hc1.png"
HC_IMG_2 = "hc2.png"
HC_IMG_3 = "hc3.png"
HC_IMG_4 = "hc4.png"

HC_INACTIVE_1 = "hc_inactive_1.png"
HC_INACTIVE_2 = "hc_inactive_2.png"

hc_imgs = {}

# ハニカムの設定
HC_SIZE = 65

HC_DIST = 50
HC_DIST_HOR = HC_DIST * math.sqrt(3) / 2
HC_DIST_VER = HC_DIST

HC_OFFSET = -np.array([1, 1]) * HC_SIZE / 2

hc_pos_list = []

HC_STATE_INACTIVE = 0
HC_STATE_ACTIVE = 1

# フィールドの設定
FIELD_W = 2*5 + 1
FIELD_H = 2*5 + 1

BASE = 0

FIELD_TMP = [
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, BASE, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
]

FIELD_0 = [
    [None, None, None, None,   62,   61,   90, None, None, None, None],
    [None, None,   64,   63,   38,   37,   60,   89,   88, None, None],
    [  66,   65,   40,   39,   20,   19,   36,   59,   58,   87,   86],
    [  67,   41,   22,   21,    8,    7,   18,   35,   34,   57,   85],
    [  68,   42,   23,    9,    2,    1,    6,   17,   33,   56,   84],
    [  69,   43,   24,   10,    3, BASE,    5,   16,   32,   55,   83],
    [  70,   44,   25,   11,   12,    4,   14,   15,   31,   54,   82],
    [  71,   45,   46,   26,   27,   13,   29,   30,   52,   53,   81],
    [None,   72,   73,   47,   48,   28,   50,   51,   79,   80, None],
    [None, None, None,   74,   75,   49,   77,   78, None, None, None],
    [None, None, None, None, None,   76, None, None, None, None, None],
]

FIELD_1 = [
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None,   20,   19,   36, None, None, None, None],
    [None, None,   22,   21,    8,    7,   18,   35,   34, None, None],
    [None, None,   23,    9,    2,    1,    6,   17,   33, None, None],
    [None, None,   24,   10,    3, BASE,    5,   16,   32, None, None],
    [None, None,   25,   11,   12,    4,   14,   15,   31, None, None],
    [None, None, None,   26,   27,   13,   29,   30, None, None, None],
    [None, None, None, None, None,   28, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
]

# サーフェイスの設定
COLORKEY = (200, 200, 200)


class Honeycomb:
    def __init__(self, pos, label):
        self.pos = pos
        self.label = label
        self.state = HC_STATE_ACTIVE if self.label == HC_IMG_BASE \
                     else HC_STATE_INACTIVE

        self.anim_last_time = 0.0
        self.anim_duration = 1.0
        self.anim_count = 1
        self.anim_label = self.label

    def activate(self, label):
        self.state = HC_STATE_ACTIVE
        self.label = label

    def deactivate(self):
        self.state = HC_STATE_INACTIVE

    def render(self, surface):
        """ハニカムを描画する."""
        if self.state == HC_STATE_INACTIVE:
            current_time = time.time()
            if current_time - self.anim_last_time > self.anim_duration:
                self.anim_last_time = current_time
                self.anim_count = 1 if self.anim_count == 0 else 0
                self.anim_label = [
                    HC_INACTIVE_1, HC_INACTIVE_2][self.anim_count]
        elif self.state == HC_STATE_ACTIVE:
            self.anim_label = self.label
        surface.blit(hc_imgs[self.anim_label], self.pos)


def load_hc_imgs(img_dir):
    """ハニカムの画像をロードする.

    この関数はアプリの初期化段階で呼び出す必要がある.
    """
    labels = [
        HC_IMG_BASE,
        HC_IMG_1,
        HC_IMG_2,
        HC_IMG_3,
        HC_IMG_4,
        HC_INACTIVE_1,
        HC_INACTIVE_2
    ]
    for label in labels:
        img = pygame.image.load(os.path.join(img_dir, label))
        img.convert()
        img = pygame.transform.scale(img, (HC_SIZE, HC_SIZE))
        hc_imgs[label] = img


def calc_hc_pos(field_f, target, screen_center):
    """フィールドの位置から座標を計算する."""
    try:
        index = field_f.index(target)
    except ValueError:
        print(f"ERROR: Could not find '{target}' from the field.",
              file=sys.stderr)
        sys.exit(1)
    row = index//FIELD_W - FIELD_W//2
    col = index%FIELD_W - FIELD_H//2
    x = col * HC_DIST_HOR
    y = (row + 1/2*(col % 2)) * HC_DIST_VER
    return np.array([x, y]) + screen_center + HC_OFFSET


def make_field_info(field, screen_center):
    """フィールドの情報を生成する."""
    field_info = {}
    field_f = list(itertools.chain.from_iterable(field))
    num_of_hcs = max([i for i in field_f if isinstance(i, int)])
    field_info["num_of_hcs"] = num_of_hcs
    pos_list = [calc_hc_pos(field_f, BASE, screen_center)]
    hcs = [Honeycomb(pos_list[0], HC_IMG_BASE)]
    for i in range(1, num_of_hcs + 1):
        pos = calc_hc_pos(field_f, i, screen_center)
        pos_list.append(pos)
        hcs.append(Honeycomb(pos, HC_IMG_1))
    field_info["pos_list"] = pos_list
    field_info["hcs"] = hcs
    return field_info


def activate_honeycomb(field_info, n):
    """ハニカムを 1 つ指定してアクティブ化する."""
    hc = field_info["hcs"][n]
    labels = [HC_IMG_1, HC_IMG_2, HC_IMG_3, HC_IMG_1]
    hc.activate(random.choice(labels))


def deactivate_honeycomb(field_info, n):
    """ハニカムを 1 つ指定して非アクティブ化する."""
    hc = field_info["hcs"][n]
    hc.deactivate()


def make_hc_surface(screen_size, field_info):
    """ハニカムを描画したレイヤを生成する."""
    surface = pygame.surface.Surface(screen_size)
    surface.convert()
    surface.fill(COLORKEY)
    surface.set_colorkey(COLORKEY)

    for hc in field_info["hcs"]:
        hc.render(surface)

    return surface

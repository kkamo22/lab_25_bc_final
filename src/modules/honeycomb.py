import math
import os

import numpy as np
import pygame


# 画像ラベル
HC_BASE = "honeycomb4.png"
HC_STRONG = "honeycomb2.png"
HC_NORMAL = "honeycomb1.png"
HC_WEAK = "honeycomb3.png"

hc_imgs = {}

# ハニカムの設定
HC_SIZE = 50
HC_DIST = 38

hc_pos_list = []


def load_hc_imgs(img_dir):
    """ハニカムの画像をロードする.

    この関数はアプリの初期化段階で呼び出す必要がある.
    """
    labels = [HC_BASE, HC_STRONG, HC_NORMAL, HC_WEAK]
    for label in labels:
        img = pygame.image.load(os.path.join(img_dir, label))
        img.convert()
        img = pygame.transform.scale(img, (HC_SIZE, HC_SIZE))
        img = pygame.transform.rotate(img, 90)
        hc_imgs[label] = img


def make_hc_pos_list(center, d, n):
    """ハニカムの座標のリストを生成する."""
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
        hc_pos_list.append(pos)


def make_hc_surface(screen_size, num_of_honeycombs):
    """ハニカムを描画したレイヤを生成する."""
    surface = pygame.surface.Surface(screen_size)
    surface.convert()
    center = np.array(screen_size) / 2
    offset = -np.array([1, 1]) * HC_SIZE / 2
    surface.blit(hc_imgs[HC_BASE], center + offset)
    for i in range(num_of_honeycombs):
        pos = hc_pos_list[i]
        surface.blit(hc_imgs[HC_NORMAL], pos + offset)
    return surface

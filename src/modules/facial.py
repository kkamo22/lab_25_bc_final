import pygame


# 閾値
SMILE_THD = 0.08  # mV
SMILE_MAX = 0.10  # mV

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


def detect_smile(emg):
    """笑顔を検知する."""
    return emg > SMILE_THD


def render_gauge(surface, emg):
    """ゲージを描画する."""
    pygame.draw.rect(
        surface, GAUGE_COLOR_EMPTY, (GAUGE_X, GAUGE_Y, GAUGE_W, GAUGE_H))
    pygame.draw.rect(
        surface, GAUGE_COLOR_FULL, (
            GAUGE_X,
            GAUGE_Y,
            GAUGE_W * emg / SMILE_MAX,
            GAUGE_H))
    pygame.draw.rect(
        surface, GAUGE_COLOR_BAR, (BAR_X, BAR_Y, BAR_W, BAR_H))


def make_gauge_surface(screen_size, emg):
    """ゲージを描画したサーフェイスを生成する."""
    surface = pygame.surface.Surface(screen_size)
    surface.fill(COLORKEY)
    surface.set_colorkey(COLORKEY)
    render_gauge(surface, emg)
    return surface

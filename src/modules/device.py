import sys

import bitalino


# デバイス設定
SAMPLING_RATE = 1000  # Hz

ACC_PIN = 0
EMG_PIN = 1

N_SAMPLES = 100

BITS = 10
VCC = 3.3
GAIN = 1009

# 計測
MAX_DATA_LEN = 100

EMGS_EMA_RHO = 0.925


def get_device(mac_address):
    """BITalino デバイスと接続する."""
    device = None
    try:
        device = bitalino.BITalino(mac_address)
    except Exception as e:
        print("ERROR: The MAC address or serial port for the device is "
              "invalid.", file=sys.stderr)
    return device


def start_device(device):
    """BITalino デバイスによる計測を開始する."""
    device.start(SAMPLING_RATE, [ACC_PIN, EMG_PIN])


def calc_emg(data, bits, vcc, gain):
    """信号から EMG の電圧値 (mV) を計算する."""
    emg = ((data / 2**bits) - 1/2) * vcc * 1000 / gain
    return emg


def calc_ema(old, new, rho):
    """指数移動平均 (EMA) を計算する."""
    return rho*old + (1 - rho)*new


def add_ema(ema_list, new, rho):
    """指数移動平均 (EMA) を計算し, リストに追加する."""
    if len(ema_list) > 0:
        ema = calc_ema(ema_list[-1], new, rho)
    else:
        ema = new
    ema_list.append(ema)


def sample_data(device, accs, emgs, emgs_ema):
    """生体データをサンプリングする."""
    # データ取得
    data = device.read(N_SAMPLES)
    acc = data[:, 5+ACC_PIN][0]
    emg = calc_emg(data[:, 5+EMG_PIN][0], BITS, VCC, GAIN)

    # データ追加・廃棄
    accs.append(acc)
    if len(accs) > MAX_DATA_LEN:
        del accs[:-MAX_DATA_LEN]

    emgs.append(emg)
    add_ema(emgs_ema, abs(emg), EMGS_EMA_RHO)
    if len(emgs) > MAX_DATA_LEN:
        del emgs[:-MAX_DATA_LEN]
        del emgs_ema[:-MAX_DATA_LEN]

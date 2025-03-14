import sys

import bitalino


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

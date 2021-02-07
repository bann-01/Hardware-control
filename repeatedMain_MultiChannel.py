# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 12:33:33 2019

@author: Guy Mcbride (Keysight)
@author: B.Ann (TU-Delft)
"""

import os
import json
import numpy as np
import logging.config
import matplotlib.pyplot as plt
import AWG_multi as awg
import digitizer as dig
import hvi
import time

CHASSIS = 0
DIGITIZER_SLOT = 3
DIGITIZER_CHANNEL_I = 3
DIGITIZER_CHANNEL_Q = 4
AWG_SLOT = 2
AWG_CHANNEL = 3

AWG_DELAYS = 0
DIGITIZER_DELAY = 0e-9

PULSE_WIDTH = 5E-06
CAPTURE_WIDTH = 10E-06
CARRIER_FREQUENCIES = [10E+06,10E+6]
PRI = 50.0E-6
NUMBER_OF_PULSES = 1000
NUMBER_OF_AVG    = 10
log = logging.getLogger('Main')

def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def hertz_to_rad(hertz: float):
    return hertz * 2 * np.pi

def timebase(start, stop, sample_rate):
    start_sample = int(start * sample_rate)
    stop_sample = int (stop * sample_rate)
    timebase = np.arange(start_sample, stop_sample)
    timebase = timebase / sample_rate
    return(timebase)

if (__name__ == '__main__'):
    setup_logging()

    #Create a simple pulse of carrier
    t = timebase(0, PULSE_WIDTH, 1e+09)
    waves = []
    for carrier in CARRIER_FREQUENCIES:
        wave = np.sin(hertz_to_rad(carrier) * t)
        wave = np.concatenate([wave, np.zeros(100)])
        waves.append(wave)
    
    awg_h = awg.open(CHASSIS, AWG_SLOT)
    dig_h = dig.open(CHASSIS, DIGITIZER_SLOT, DIGITIZER_CHANNEL_I, DIGITIZER_CHANNEL_Q, CAPTURE_WIDTH)

    awg.Waveform_memory_flush()
    awg.open_channel(channel=2, amp=1.0)
    awg.open_channel(channel=3, amp=1.0)
    awg.WaveformLoad(waves)
    awg.WaveformQueue(waves, AWG_DELAYS, number_of_channel=len(channel_list), channel_list=[2,3], number_of_cycle=1)
    dig.digitize(DIGITIZER_DELAY, NUMBER_OF_PULSES*NUMBER_OF_AVG)

    hvi_path = os.getcwd() + '\\SyncStartRepeated.hvi'
    hvi_mapping = {'AWG': awg_h, 'DIG': dig_h}
    hvi.init(hvi_path, hvi_mapping)

    for i in range(NUMBER_OF_AVG):
        hvi.start(NUMBER_OF_PULSES, PRI)
        
        time.sleep(1)   # This shows the 1024 cycles limit bug
        log.info("Reading Waveforms....")
    
        plt.xlabel("us")
        for ii in range(NUMBER_OF_PULSES):
            samples = dig.get_data_I()
            if len(samples) == 0:
                log.error("Reading appears to have timed out after {} pulses".format(ii))
                break
            if ii < 2: # do not plot too many waves
                plt.plot(dig.timeStamps / 1e-06, samples)
                plt.show()
    
    hvi.close()
    dig.close()
    awg.close_channel(2)
    awg.close_channel(3)
    awg.close()
    
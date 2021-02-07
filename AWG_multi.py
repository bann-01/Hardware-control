# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 12:32:15 2019

@author: Guy Mcbride (Keysight)
@author: B.Ann (TU-Delft)
"""

import sys
import time
import random
import numpy as np
import logging
#import matplotlib.pyplot as plt

sys.path.append(r'C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
import keysightSD1 as key

log = logging.getLogger(__name__)

# globals to this module (essentially this is a singleton class)
__awg = key.SD_AOU()
# Queue constants
SINGLE_CYCLE = 1
INFINITE_CYCLES = 0
WAVE_PRESCALER = 0

def open(chassis, slot):
    log.info("Configuring AWG in slot {}...".format(slot))
    error = __awg.openWithSlotCompatibility('', chassis, slot, key.SD_Compatibility.KEYSIGHT)
    if error < 0:
        log.info("Error Opening - {}".format(error))
    error = __awg.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_OUT)
    if error < 0:
        log.info("Error Setting Trigger to output - {}".format(error))
    log.info("Finished setting up AWG in slot {}...".format(slot))
    return __awg

def open_channel(channel, amp=1.0):
    error=__awg.AWGflush(channel)
    if error < 0:
        log.info("Error Flushing AWG - {}".format(error))
    error = __awg.channelWaveShape(channel, key.SD_Waveshapes.AOU_AWG)
    if error < 0:
        log.info("Error Setting Waveshape - {}".format(error))
    error = __awg.channelAmplitude(channel, amp)
    if error < 0:
        log.info("Error Setting Amplitude - {}".format(error))
    log.info("Setting front panel trigger to Output...")

def WaveformLoad(waveforms):
    wave = key.SD_Wave()
    WaveidList=range(len(waveforms))
    for waveform,waveId in zip(waveforms,WaveidList):
        error = wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, waveform)
        if error < 0:
            log.info("Error Creating Wave - {}".format(error))
        error = __awg.waveformLoad(wave, waveId)
        if error < 0:
            log.info("Error Loading Wave - {}".format(error))

def WaveformQueue(waveforms, start_delay, number_of_channel, channel_list, number_of_cycle ):
    WaveidList=range(len(waveforms))
    for waveId in WaveidList:
        i = waveId % number_of_channel
        log.info("Queueing waveforms in channel {}".format(channel_list[i]))
        error = __awg.AWGqueueWaveform(channel_list[i], waveId, key.SD_TriggerModes.SWHVITRIG, start_delay, number_of_cycle , WAVE_PRESCALER)
        if error < 0:
            log.info("Queueing waveform failed! - {}".format(error))
        error = __awg.AWGqueueConfig(channel_list[i], key.SD_QueueMode.CYCLIC)
        if error < 0:
            log.info("Configure cyclic mode failed! - {}".format(error))
        error = __awg.AWGstart(channel_list[i])
        if error < 0:
            log.info("Starting AWG failed! - {}".format(error))
        log.info("Finished Loading waveform")


def Waveform_memory_flush():
    error=__awg.waveformFlush()
    if error < 0:
        log.info("Error Flushing waveforms - {}".format(error))

def close_channel(channel):
    log.info("Stopping AWG channel {}".format(channel))
    error = __awg.AWGstop(channel)
    if error < 0:
        log.info("Stopping AWG failed! - {}".format(error))
    error = __awg.channelWaveShape(channel, key.SD_Waveshapes.AOU_HIZ)
    if error < 0:
        log.info("Putting AWG into HiZ failed! - {}".format(error))

def close():     
    __awg.close()
    log.info("Finished stopping and closing AWG")

if (__name__ == '__main__'):

    print("WARNING - YOU ARE RUNNING TEST CODE")
    
    import simpleMain
    
    t = simpleMain.timebase(0, 100e-6, 1e9)
    wave = np.sin(simpleMain.hertz_to_rad(20E+06) * t)
    
    open(1, 2, 1)
    loadWaveform(wave, 0)
    __awg.AWGtrigger(_channel)

    time.sleep(10)
    close()
    
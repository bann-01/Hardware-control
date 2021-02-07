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

# Queue constants
SINGLE_CYCLE = 1
INFINITE_CYCLES = 0
WAVE_PRESCALER = 0

def open(chassis, slot):
	__awg = key.SD_AOU()
    log.info("Configuring AWG in slot {}...".format(slot))
    error = __awg.openWithSlotCompatibility('', chassis, slot, key.SD_Compatibility.KEYSIGHT)
    if error < 0:
        log.info("Error Opening - {}".format(error))
    error = __awg.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_OUT)
    if error < 0:
        log.info("Error Setting Trigger to output - {}".format(error))
    log.info("Finished setting up AWG in slot {}...".format(slot))
    return __awg

def open_channel(awg, channel, amp=1.0):
    error=	awg.AWGflush(channel)
    if error < 0:
        log.info("Error Flushing AWG - {}".format(error))
    error = awg.channelWaveShape(channel, key.SD_Waveshapes.AOU_AWG)
    if error < 0:
        log.info("Error Setting Waveshape - {}".format(error))
    error = awg.channelAmplitude(channel, amp)
    if error < 0:
        log.info("Error Setting Amplitude - {}".format(error))
    log.info("Setting front panel trigger to Output...")

def WaveformLoad(awg, waveforms):
    wave = key.SD_Wave()
    WaveidList=range(len(waveforms))
    for waveform,waveId in zip(waveforms,WaveidList):
        error = wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, waveform)
        if error < 0:
            log.info("Error Creating Wave - {}".format(error))
        error = awg.waveformLoad(wave, waveId)
        if error < 0:
            log.info("Error Loading Wave - {}".format(error))

def WaveformQueue(awg, waveforms, start_delay, number_of_channel, channel_list, number_of_cycle ):
    WaveidList = range(len(waveforms))
    for waveId in WaveidList:
        i = waveId % number_of_channel
        log.info("Queueing waveforms in channel {}".format(channel_list[i]))
        error = awg.AWGqueueWaveform(channel_list[i], waveId, key.SD_TriggerModes.SWHVITRIG, start_delay, number_of_cycle , WAVE_PRESCALER)
        if error < 0:
            log.info("Queueing waveform failed! - {}".format(error))
        error = awg.AWGqueueConfig(channel_list[i], key.SD_QueueMode.CYCLIC)
        if error < 0:
            log.info("Configure cyclic mode failed! - {}".format(error))
        error = awg.AWGstart(channel_list[i])
        if error < 0:
            log.info("Starting AWG failed! - {}".format(error))
        log.info("Finished Loading waveform")


def Waveform_memory_flush(awg):
    error = awg.waveformFlush()
    if error < 0:
        log.info("Error Flushing waveforms - {}".format(error))

def close_channel(awg,channel):
    log.info("Stopping AWG channel {}".format(channel))
    error = awg.AWGstop(channel)
    if error < 0:
        log.info("Stopping AWG failed! - {}".format(error))
    error = awg.channelWaveShape(channel, key.SD_Waveshapes.AOU_HIZ)
    if error < 0:
        log.info("Putting AWG into HiZ failed! - {}".format(error))

def close(awg):     
    awg.close()
    log.info("Finished stopping and closing AWG")
    
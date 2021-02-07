# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 12:32:15 2019

@author: Guy Mcbride (Keysight)
@author: B.Ann (TU-Delft)
"""

import sys
import numpy as np
import logging
import matplotlib.pyplot as plt

log = logging.getLogger(__name__)

sys.path.append(r'C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
import keysightSD1 as key

# globals to this module (essentially this is a singleton class)
__dig = key.SD_AIN()
# _channel = 1
_pointsPerCycle = 0
timeStamps = []
_SAMPLE_RATE = 500E+06

def timebase(start, stop, sample_rate):
    start_sample = int(start * sample_rate)
    stop_sample = int (stop * sample_rate)
    timebase = np.arange(start_sample, stop_sample)
    timebase = timebase / sample_rate
    return(timebase)

def open(chassis, slot, channel_I, channel_Q, captureTime):
    log.info("Configuring Digitizer...")
    global timeStamps, _pointsPerCycle, _channel_I, _channel_Q
    _channel_I = channel_I
    _channel_Q = channel_Q
    timeStamps = timebase(0, captureTime, _SAMPLE_RATE)
    _pointsPerCycle = len(timeStamps)
    error = __dig.openWithSlotCompatibility('', chassis, slot, key.SD_Compatibility.KEYSIGHT)
    if error < 0:
        log.info("Error Opening digitizer in slot #{}".format(slot))
    error = __dig.DAQflush(_channel_I)
    if error < 0:
        log.info("Error Flushing")
    error = __dig.DAQflush(_channel_Q)
    if error < 0:
        log.info("Error Flushing")
    error = __dig.channelInputConfig(_channel_I, 2.0, key.AIN_Impedance.AIN_IMPEDANCE_50, 
                             key.AIN_Coupling.AIN_COUPLING_DC)
    if error < 0:
        log.info("Error Configuring channel")
    error = __dig.channelInputConfig(_channel_Q, 2.0, key.AIN_Impedance.AIN_IMPEDANCE_50, 
                             key.AIN_Coupling.AIN_COUPLING_DC)
    if error < 0:
        log.info("Error Configuring channel")
    return (__dig)

def digitize(trigger_delay, number_of_pulses = 1):
    trigger_delay = trigger_delay * _SAMPLE_RATE # expressed in samples
    trigger_delay = int(np.round(trigger_delay))
    error = __dig.DAQconfig(_channel_I, _pointsPerCycle, number_of_pulses, trigger_delay, key.SD_TriggerModes.SWHVITRIG)
    if error < 0:
        log.info("Error Configuring Acquisition")
    error = __dig.DAQstart(_channel_I)
    if error < 0:
        log.info("Error Starting Digitizer")
    error = __dig.DAQconfig(_channel_Q, _pointsPerCycle, number_of_pulses, trigger_delay, key.SD_TriggerModes.SWHVITRIG)
    if error < 0:
        log.info("Error Configuring Acquisition")
    error = __dig.DAQstart(_channel_Q)
    if error < 0:
        log.info("Error Starting Digitizer")
    
def get_data_I():
    _channel=_channel_I
    TIMEOUT = 10000
    LSB = 1/ 2**14
    dataRead = __dig.DAQread(_channel, _pointsPerCycle, TIMEOUT)
    if len(dataRead) != _pointsPerCycle:
        log.warn("Attempted to Read {} samples, actually read {} samples".format(_pointsPerCycle, len(dataRead)))
    return(dataRead * LSB)
    
def get_data_Q():
    _channel=_channel_Q
    TIMEOUT = 10000
    LSB = 1/ 2**14
    dataRead = __dig.DAQread(_channel, _pointsPerCycle, TIMEOUT)
    if len(dataRead) != _pointsPerCycle:
        log.warn("Attempted to Read {} samples, actually read {} samples".format(_pointsPerCycle, len(dataRead)))
    return(dataRead * LSB)

def flush():
    error = __dig.DAQflush(_channel_I)
    if error < 0:
        log.info("Error Flushing")
    error = __dig.DAQflush(_channel_Q)
    if error < 0:
        log.info("Error Flushing")

def close():
    __dig.close()
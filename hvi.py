# -*- coding: utf-8 -*-
"""
Created on Thu May 23 09:46:33 2019

@author: Guy Mcbride (Keysight)
@author: B.Ann (TU-Delft)
"""

import logging
import sys
import time
sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
import keysightSD1 as key

__log = logging.getLogger(__name__)

__hvi = key.SD_HVI()

class HviError(Exception):
    """Basic exception for errors raised by HVI"""
    _error = None
    _message = None
    def __init__(self, error, msg=None):
        if msg is None:
            msg = "An error occured with HVI: {}".format(key.SD_Error.getErrorMessage(error))
        super(HviError, self).__init__(msg)
        self._error = error
    @property
    def error_message(self):
        return key.SD_Error.getErrorMessage(self._error)

def __compile_download():
    __log.info("Compiling HVI...")
    cmpID = __hvi.compile()
    if cmpID != 0:
        error = "HVI compile failed : {}".format(key.SD_Error.getErrorMessage(cmpID))
        __log.error(error)
        raise HviError(cmpID, error)
    __log.info("Loading HVI...")
    cmpID = __hvi.load()
    if cmpID == -8038:
        __log.debug("HVI contains Demo Module. Please make sure you do an assignHW()")
    elif cmpID != 0:
        error = "HVI load failed : {}".format(key.SD_Error.getErrorMessage(cmpID))
        __log.error(error)
        raise HviError(cmpID, error)
        
def init(hviFileName, mapping):
    __log.info("Opening HVI file: {}".format(hviFileName))
    hviID = __hvi.open(hviFileName)
    if hviID ==  key.SD_Error.RESOURCE_NOT_READY: #Only for old library
        __log.debug("No Critical Error - {}: {}".format(hviID, key.SD_Error.getErrorMessage(hviID)))
        __log.debug("Using old library -> Need to compile HVI...")
    elif hviID == key.SD_Error.DEMO_MODULE: #Only for old library
        __log.debug("No Critical Error - {} {}".format(hviID, key.SD_Error.getErrorMessage(hviID)))
        __log.debug("Using old library -> need to assigning HW modules...")
    elif hviID < 0:
        __log.error("Opening HVI - {}: {}".format(hviID, key.SD_Error.getErrorMessage(hviID)))
        raise HviError(hviID, "Opening HVI - {}: {}".format(hviID, key.SD_Error.getErrorMessage(hviID)))
        
    error  = __hvi.releaseHW()
    if (error < 0):
        __log.error("Releasing HW - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))

    for (module_name, module_id) in mapping.items():
        __log.info("Assigning {} to {} in slot {}".format(module_name, module_id.getProductName(), module_id.getSlot()))
        error = __hvi.assignHardwareWithUserNameAndModuleID(module_name, module_id)
        if error == -8069:
            __log.debug("Assigning HVI {}, Spurious Error- {}: {}".format(module_name, error, key.SD_Error.getErrorMessage(error)))
            __log.info("HVI HW assigned for {}, {} in slot {}".format(module_name, module_id.getProductName(), module_id.getSlot()))
        elif error < 0:
            error_msg = "HVI assign HW AOU Failed for: {}, {}: {}".format(
                    module_name, 
                    module_id,
                    key.SD_Error.getErrorMessage(error))
            __log.error(error_msg)
            raise HviError(error, error_msg)
        else:
            __log.info("HVI HW assigned for {}, {} in slot {}".format(module_name, module_id.getProductName(), module_id.getSlot()))
    # if the last module assigned has this error then it is more serious
    if error == -8069:
        __log.error("Assigning HVI - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))
#        raise HviError(error)
    __compile_download()
            
def start(number_pulses = 1, pri = 0):
    __log.info("Starting HVI...")
    # There is 140ns of intrinsic 'gap' in the HVI loop.
    gap = pri - 140e-09
    if gap < 0: gap = 0
    error = __hvi.writeDoubleConstantWithUserName('AWG', 'GapTime', gap, 's')
    if (error < 0):
        __log.error("Writing AWG gapTime - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))

    error = __hvi.writeDoubleConstantWithUserName('DIG', 'GapTime', gap, 's')
    if (error < 0):
        __log.error("Writing DIG gapTime - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))

    error = __hvi.writeIntegerConstantWithUserName('AWG', 'number of pulses', number_pulses)
    if (error < 0):
        __log.error("Writing AWG number of pulses - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))

    error = __hvi.writeIntegerConstantWithUserName('DIG', 'number of pulses', number_pulses)
    if (error < 0):
        __log.error("Writing DIG number of pulses - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))
    
    [error, digNumPulses] = __hvi.readIntegerConstantWithUserName('DIG', 'number of pulses')
    if (error < 0):
        __log.error("Reading DIG number of pulses - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))
    else:
        __log.info("DIG number of pulses Register = {}".format(digNumPulses))

    __compile_download()    # This necessary when Constants are changed
    error = __hvi.start()
    if (error < 0):
        __log.error("Starting HVI- {}: {}".format(error, key.SD_Error.getErrorMessage(error)))
        
def close():
    error  = __hvi.releaseHW()
    if (error < 0):
        __log.error("Releasing HW - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))
    error = __hvi.close()
    if (error < 0):
        __log.error("Closing HVI - {}: {}".format(error, key.SD_Error.getErrorMessage(error)))

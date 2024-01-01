"""
CCS200.py
---------
A Python module for controlling the CCS200 Spectrometer.

This module provides a class 'Spectrometer' with methods to interface with the CCS200 Spectrometer.
It encapsulates the functionality required to initialize, control, and retrieve data from the spectrometer.

Author: [Your Name]
Date: [Creation Date]
"""

from ctypes import *
import numpy as np
import os

class Spectrometer:
    """
    A class to represent and control a CCS200 Spectrometer.

    ...

    Attributes
    ----------
    lib : CDLL
        A ctypes CDLL instance to interact with the spectrometer's DLL.
    ccs_handle : c_int
        A ctypes c_int to store the spectrometer's handle.
    ...

    Methods
    -------
    __init__(self):
        Initializes the Spectrometer class.

    _load_library(self):
        Internal method to load the spectrometer's DLL.

    _initialize_device(self):
        Internal method to initialize the spectrometer device.

    set_integration_time(self, time_in_seconds):
        Sets the integration time for the spectrometer.

    start_scan(self):
        Initiates a scan on the spectrometer.

    get_scan_data(self):
        Retrieves the scan data from the spectrometer.

    close(self):
        Closes the connection to the spectrometer.
    """

    def __init__(self):
        """
        Initializes the Spectrometer class.

        This method initializes the DLL and the spectrometer device.
        """
        self.lib = None
        self.ccs_handle = c_int(0)
        self._load_library()
        self._initialize_device()

    def _load_library(self):
        """
        Internal method to load the spectrometer's DLL.
        """
        try:
            os.chdir(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin")
            self.lib = cdll.LoadLibrary("TLCCS_64.dll")
        except Exception as e:
            raise RuntimeError("Failed to load spectrometer DLL: " + str(e))

    def _initialize_device(self):
        """
        Internal method to initialize the spectrometer device.
        """
        try:
            self.lib.tlccs_init(b"USB0::0x1313::0x8089::M00912624::RAW", 1, 1, byref(self.ccs_handle))
        except Exception as e:
            raise RuntimeError("Failed to initialize spectrometer: " + str(e))

    def set_integration_time(self, time_in_seconds):
        """
        Sets the integration time for the spectrometer.

        Parameters
        ----------
        time_in_seconds : float
            The integration time in seconds.
        """
        try:
            integration_time = c_double(time_in_seconds)
            self.lib.tlccs_setIntegrationTime(self.ccs_handle, integration_time)
        except Exception as e:
            raise RuntimeError("Failed to set integration time: " + str(e))

    def start_scan(self):
        """
        Initiates a scan on the spectrometer.
        """
        try:
            self.lib.tlccs_startScan(self.ccs_handle)
        except Exception as e:
            raise RuntimeError("Failed to start scan: " + str(e))

    def get_scan_data(self):
        """
        Retrieves the scan data from the spectrometer.

        Returns
        -------
        tuple of numpy.ndarray
            A tuple containing the wavelengths and intensities as numpy arrays.
        """
        try:
            wavelengths = (c_double * 3648)()
            self.lib.tlccs_getWavelengthData(self.ccs_handle, 0, byref(wavelengths), c_void_p(None), c_void_p(None))

            data_array = (c_double * 3648)()
            self.lib.tlccs_getScanData(self.ccs_handle, byref(data_array))

            wavelengths_np = np.ctypeslib.as_array(wavelengths)
            data_array_np = np.ctypeslib.as_array(data_array)

            return wavelengths_np, data_array_np
        except Exception as e:
            raise RuntimeError("Failed to retrieve scan data: " + str(e))

    def close(self):
        """
        Closes the connection to the spectrometer.
        """
        try:
            self.lib.tlccs_close(self.ccs_handle)
        except Exception as e:
            raise RuntimeError("Failed to close spectrometer: " + str(e))

# Import standard library modules.
import uasyncio

# Import SWC-IRFL library modules.
import usbcdc
import harpsync
import picopinout as pinout
from picodevice import Pico

SYCN_CALIBRATION = 1000000 - 240  # Stores the calibration
# factor to align to a standard (Atmel's ATxmega) core
# implementation of HARP.

# Instance the hardware interfaces.
stream = usbcdc.usbcdc(1)
sync = harpsync.harpsync(0, calib=SYCN_CALIBRATION)

statusled = pinout.statusled
spis = pinout.spis
gpio = pinout.gpio

# Instance the device object and launch its application.
theDevice = Pico(stream,
                 sync,
                 statusled,
                 spis,
                 gpio,
                 trace=False)

uasyncio.run(theDevice.main())

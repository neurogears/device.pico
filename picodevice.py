"""General IO device class."""
from micropython import const

from microharp.device import HarpDevice
from microharp.types import HarpTypes
from microharp.register import ReadWriteReg, OperationalCtrlReg

from picoregisters import AdcRegister, AnalogStreamStateRegister
from picoregisters import (PwmDutycycleRegister, PwmFreqRegister,
                           PwmStartRegister, PwmStopRegister)
from picoregisters import (Set_HarpDigitalOutputArrayRegister,
                           Clear_HarpDigitalOutputArrayRegister,
                           Toggle_HarpDigitalOutputArrayRegister)
from picoregisters import HarpDigitalInputArrayRegister

from picoevent import HarpDigitalInputArrayEvent, AdcEvent


class Pico(HarpDevice):
    """Pico device."""

    # Digital Inputs
    R_DIGITAL_INPUT =           const(32)  # U8    Reflects the state of DI digital lines # noqa: E501 E224
    # Digital Outputs
    R_DIGITAL_OUTPUT_SET =		const(38)  # U8    Sets the correspondent output # noqa: E501 E224
    R_DIGITAL_OUTPUT_CLEAR =	const(39)  # U8    Clears the correspondent output # noqa: E501 E224
    R_DIGITAL_OUTPUT_TOGGLE =	const(40)  # U8    Toggles the correspondent output # noqa: E501 E224

    # Analog
    R_ANALOG_PIN = 				const(44)  # U16    Voltage at ADC input # noqa: E501 E224
    R_ANALOG_STREAM_STATE = 	const(33)  # U8     Enables the analog stream # noqa: E501 E224
    # PMW
    R_PWM0_DUTYCYCLE =			const(64)  # U8     Dutycycle of the output [0 : 99] # noqa: E501 E224
    R_PWM0_FREQ =				const(60)  # U16    Frequency of PWM output >10Hz # noqa: E501 E224
    R_PWM0_START =				const(68)  # U8     Start the PWM output on the selected output # noqa: E501 E224
    R_PWM0_STOP =				const(69)  # U8     Stop the PWM output on the selected output # noqa: E501 E224

    # PMW
    R_PWM1_DUTYCYCLE =			const(65)  # U8     Dutycycle of the output [0 : 99] # noqa: E501 E224
    R_PWM1_FREQ =				const(61)  # U16    Frequency of PWM output >10Hz # noqa: E501 E224
    R_PWM1_START =				const(70)  # U8     Start the PWM output on the selected output # noqa: E501 E224
    R_PWM1_STOP =				const(71)  # U8     Stop the PWM output on the selected output # noqa: E501 E224

    def __init__(self, stream, sync, led, spis, gpio, trace=False):
        """Constructor.

        Connects the logical device to its physical interfaces, creates the drives and register map.
        """
        super().__init__(stream, sync, led, trace=trace)

        registers = {
            # Core
            HarpDevice.R_DEVICE_NAME        : ReadWriteReg(HarpTypes.U8, tuple(b'picoharp')),  # noqa: E501
            HarpDevice.R_WHO_AM_I           : (HarpTypes.U16, (123456,)),  # noqa: E501

            # Digital Input
            Pico.R_DIGITAL_INPUT            : HarpDigitalInputArrayRegister(gpio["DigitalInput"]),  # noqa: E501

            # Digital Output
            Pico.R_DIGITAL_OUTPUT_SET       : Set_HarpDigitalOutputArrayRegister(gpio["DigitalOutput"]),  # noqa: E501
            Pico.R_DIGITAL_OUTPUT_CLEAR     : Clear_HarpDigitalOutputArrayRegister(gpio["DigitalOutput"]),  # noqa: E501
            Pico.R_DIGITAL_OUTPUT_TOGGLE    : Toggle_HarpDigitalOutputArrayRegister(gpio["DigitalOutput"]),  # noqa: E501

            # Analog Input
            Pico.R_ANALOG_PIN               : AdcRegister(gpio["ADC"]),  # noqa: E501
            Pico.R_ANALOG_STREAM_STATE      : AnalogStreamStateRegister(self),  # noqa: E501

            # PWM
            Pico.R_PWM0_DUTYCYCLE           : PwmDutycycleRegister(gpio["PWM"][0]),  # noqa: E501
            Pico.R_PWM1_DUTYCYCLE           : PwmDutycycleRegister(gpio["PWM"][1]),  # noqa: E501
            Pico.R_PWM0_FREQ                : PwmFreqRegister(gpio["PWM"][0]),  # noqa: E501
            Pico.R_PWM1_FREQ                : PwmFreqRegister(gpio["PWM"][1]),  # noqa: E501
            Pico.R_PWM0_START               : PwmStartRegister(gpio["PWM"][0]),  # noqa: E501
            Pico.R_PWM1_START               : PwmStartRegister(gpio["PWM"][1]),  # noqa: E501
            Pico.R_PWM0_STOP                : PwmStopRegister(gpio["PWM"][0]),  # noqa: E501
            Pico.R_PWM1_STOP                : PwmStopRegister(gpio["PWM"][1]),  # noqa: E501
        }

        self.registers.update(registers)

        # Define Events
        self.digital_input_event = HarpDigitalInputArrayEvent(
            Pico.R_DIGITAL_INPUT, self.registers[Pico.R_DIGITAL_INPUT],
            self.sync, self.txMessages)

        self.adc_event = AdcEvent(Pico.R_ANALOG_PIN,
                                  self.registers[Pico.R_ANALOG_PIN],
                                  self.sync, self.txMessages, period=10)

    def _ctrl_hook(self):
        """Private member function.

        Control register write hook, updates device state.
        """
        super()._ctrl_hook()

        if self.registers[HarpDevice.R_OPERATION_CTRL].OP_MODE != OperationalCtrlReg.STANDBY_MODE:
            self.digital_input_event.enable()
        else:
            self.digital_input_event.disable()
            self.adc_event.disable()

            #Disable PWMs if the control register is off
            if self.registers[Pico.R_PWM0_STOP].harpPWM.enabled is True:
                self.registers[Pico.R_PWM0_STOP].harpPWM.stop()
            if self.registers[Pico.R_PWM1_STOP].harpPWM.enabled is True:
                self.registers[Pico.R_PWM1_STOP].harpPWM.stop()

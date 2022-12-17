from machine import PWM, Pin


class HarpDigitalInputPin():
    '''
    Implements an abstract class to interface with the Pin class.
    Specifically, it generates callbacks to all subscribers when an interrupt
    is generated (trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING) and the 'self.value'
    updated.
    '''

    def __init__(self, gpio_pin, idx_id):
        self._gpio_pin = gpio_pin
        self._callbacks = []
        self._pin_port_id = idx_id
        self.Pin = Pin(gpio_pin, mode=Pin.IN, pull=Pin.PULL_DOWN)
        self.Pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                     handler=self.__iqr_callback)
        self._value = self.Pin.value()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        # triggers a callback to all subscribers when the
        # value is changed (e.g. by the iqr)
        self._value = new_value
        self._notify_subscribers(new_value)

    def _notify_subscribers(self, new_value):
        # Notify all registered subscribers and also
        # emit to identifier to the callback
        for subscriber in self._callbacks:
            subscriber(new_value, self._pin_port_id)

    def add_callback(self, observer):
        self._callbacks.append(observer)

    def remove_callback(self, idx):
        self._callbacks.pop(idx)

    def __iqr_callback(self, pin):
        # iqr triggers a pin read since we need to establish
        # if it was a rising or falling edge
        self.value = pin.value()


class HarpDigitalInputArray():
    '''
    Implements a digital input port of several pins (<8).
    Each pin is implemented through the HarpDigitalInputPin
    class.
    On an update of any of the pins (HarpDigitalInputPin._notify_subscribers),
    it will trigger the input callback function.
    '''
    def __init__(self, gpio_pin_tuple):
        if len(gpio_pin_tuple) > 8:
            raise ValueError("Input tuple must be of max size 8.")

        self._callbacks = []
        self._gpio_pins = gpio_pin_tuple
        self._n_pins = len(self._gpio_pins)
        self._max_val = self._state_to_dec((True,) * self._n_pins)

        self.pin_array = [HarpDigitalInputPin(pin, idx) for
                          (idx, pin) in enumerate(self._gpio_pins)]
        for pin in self.pin_array:
            pin.add_callback(self._update_port_state)
        self._state = self._init_state()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        for callback in self._callbacks:
            callback(self._state)

    def _init_state(self):
        return self._state_to_dec([pin.value == 1 for pin in self.pin_array])

    def _update_port_state(self, ret_state, ret_pin_idx):
        # update the state of the port
        self.state = \
            (self.state & ~(1 << ret_pin_idx)) | \
                (ret_state << ret_pin_idx)

    def add_callback(self, observer):
        self._callbacks.append(observer)

    def remove_callback(self, idx):
        self._callbacks.pop(idx)

    @staticmethod
    def _state_to_dec(arr):
        return sum([1 << idx for (idx, bit) in enumerate(arr) if bit])


class HarpDigitalOutputArray():
    '''
    Implements a digital output port of several pins (<8).
    The state is updated via self.change_state. An optional
    binary mask can be passed to update several pins at once.
    '''
    toggle_lookup = (1, 0)

    def __init__(self, gpio_pin_tuple):
        if len(gpio_pin_tuple) > 8:
            raise ValueError("Input tuple must be of max size 8.")
        self._gpio_pins = gpio_pin_tuple
        self.pin_array = [Pin(pin, Pin.OUT) for pin in self._gpio_pins]
        self._n_pins = len(self._gpio_pins)
        self.clear_state(mask=None)
        self.current_state = [pin.value() for pin in self.pin_array]

    def change_state(self, state, mask=None):
        if (state not in (0, 1)):
            raise ValueError('Invalid input value.')
        if mask is not None:  # only change the relevant values
            [(pin.value(state)) for idx, pin
             in enumerate(self.pin_array) if ((mask >> idx) & 1 == 1)]
        else:
            [(pin.value(state)) for idx, pin
             in enumerate(self.pin_array)]
        self.update_current_state()

    def set_state(self, mask=None):
        self.change_state(1, mask)

    def clear_state(self, mask=None):
        self.change_state(0, mask)

    def toggle_state(self, mask=None):
        if mask is not None:  # only change the relevant values
            [
                pin.value(
                    HarpDigitalOutputArray.toggle_lookup[
                        self.current_state[idx]
                        ])
                for (idx, pin) in enumerate(self.pin_array) if ((mask >> idx) & 1 == 1)
                ]
        else:
            [
                pin.value(
                    HarpDigitalOutputArray.toggle_lookup[
                        self.current_state[idx]
                        ])
                for (idx, pin) in enumerate(self.pin_array)
                ]
        self.update_current_state()

    def update_current_state(self):
        self.current_state = [pin.value() for pin in self.pin_array]


class HarpPwm():
    '''
    Implements an abstract PWM class to use in the PicoHarp board
    '''
    MinFrequency = 10
    MinDutyCycle = 0

    def __init__(self, pin, frequency=MinFrequency, dutycyle=MinDutyCycle):
        self._pin = self.pin = Pin(pin)
        self._frequency = self.frequency = frequency
        self._dutycyle = self.dutycyle = dutycyle
        self.pwm = None
        self.enabled = False

    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        self._pin = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if (value >= HarpPwm.MinFrequency):
            self._frequency = value

    @property
    def dutycyle(self):
        return self._dutycyle

    @dutycyle.setter
    def dutycyle(self, value):
        if ((value >= 0) and (value <= 100)):
            self._dutycyle = value

    def start(self):
        dutycycle_u16 = int((self.dutycyle/100.0) * 65535.0)
        self.pwm = PWM(self.pin)
        self.pwm.freq(self.frequency)
        self.pwm.duty_u16(dutycycle_u16)
        self.enable()

    def stop(self):
        self.pwm.deinit()
        self.disable()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
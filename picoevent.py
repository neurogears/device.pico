from microharp.event import HarpEvent, PeriodicEvent


class HarpDigitalInputArrayEvent(HarpEvent):
    """Digital input port event.

    Triggers a read of register at address,
    generating an event message, on a pin event.
    """
    def __init__(self, address, register, sync, queue):
        super().__init__(address, register, sync, queue)
        register.harp_digital_input_array.add_callback(self._callback)


class AdcEvent(PeriodicEvent):
    """ADC input event.
    Periodically riggers a read of register at address,
    generating an event message.
    """
    def __init__(self, address, register, sync, queue, period):
        super().__init__(address, register, sync, queue, period)
        self.disable()
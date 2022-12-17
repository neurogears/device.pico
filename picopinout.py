from machine import Pin, ADC
from picofunction import HarpPwm, HarpDigitalOutputArray, HarpDigitalInputArray

statusled = Pin(25, Pin.OUT)

spis = ()

gpio = {
    "DigitalInput": HarpDigitalInputArray((6, 7, 8, 9)),
    "ADC": ADC(26),
    "DigitalOutput": HarpDigitalOutputArray((10, 11, 12, 13)),
    "PWM": (HarpPwm(14), HarpPwm(15))
}

# CLK_OUT       => GP0
# CLK_IN        => GP1

# UART_TX       => GP4
# UART_RX       => GP5

# DIN0          => GP6
# DIN1          => GP7
# DIN2          => GP8
# DIN3          => GP9

# DOUT0         => GP10
# DOUT1         => GP11
# DOUT2         => GP12
# DOUT3         => GP13

# PWM0          => GP14
# PWM1          => GP15

# SPI_RX        => GP16
# SPI_CS        => GP17
# SPI_CSK       => GP18
# SPI_TX        => GP19

# I2C_SDA       => GP20
# I2C_SCL       => GP21

# ADC           => GP26
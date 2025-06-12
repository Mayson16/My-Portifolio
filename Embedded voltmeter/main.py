from machine import Pin, ADC, Timer
import math
import time
import utime
import machine

#######################################
# Pin and constant definitions
#######################################
button = Pin(16, Pin.IN, Pin.PULL_DOWN)
adc = ADC(Pin(26))
segment_pins = [
    Pin(0, Pin.OUT),  # Segment A
    Pin(1, Pin.OUT),  # Segment B
    Pin(2, Pin.OUT),  # Segment C
    Pin(3, Pin.OUT),  # Segment D
    Pin(4, Pin.OUT),  # Segment E
    Pin(5, Pin.OUT),  # Segment F
    Pin(6, Pin.OUT)   # Segment G
]
dp = Pin(7, Pin.OUT)
digit_pins = [
    Pin(8, Pin.OUT),  # Digit 1
    Pin(9, Pin.OUT),  # Digit 2
    Pin(10, Pin.OUT),  # Digit 3
    Pin(11, Pin.OUT)   # Digit 4
]

hex_numbers = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
#######################################
# Global variables
#######################################
display_value = 0
display_timer = Timer()
button_is_pressed = 0
last_time = 0
debounce = 200
display_digits = [0, 0, 0, 0]
dp_position = 3
current_digit = -1
#######################################
# Function definitions
#######################################

# Function to read the ADC pin and
# to convert the digital value to a voltage level in the 0-3.3V range
# This function updates the value of the display_value global variable
def read_analogue_voltage(Pin=None):
    analog_value = adc.read_u16()
    voltage = (analog_value * 3.3) / 65535
    return voltage

# Function to disable timer that triggers scanning 7 segment displays
def disable_display_timer():
    global display_timer
    display_timer.deinit()

# Function to enable timer that triggers scanning 7 segment displays
def enable_display_timer():
    global display_timer
    display_timer.init(period=30, mode=Timer.PERIODIC, callback=scan_display)

# Function to handle scanning 7 segment displays
# Display the value stored in the display_value global variable
# on available 7-segment displays
def scan_display(timer_int):
    global current_digit
    current_digit = (current_digit + 1) % 4
    display_digit(current_digit, display_digits[current_digit], current_digit == dp_position)

# Function display the given value on the display with the specified index
# dp_enable specifies if the decimal pooint should be on or off
def display_digit(digit_index, digit_value, dp_enable=False):
    for dpin in digit_pins:
        dpin.value(1)
    mask = 0 if digit_value is None else hex_numbers[digit_value]
    for i, seg in enumerate(segment_pins):
        seg.value((mask >> i) & 1)
    dp.value(1 if dp_enable else 0)
    digit_pins[digit_index].value(0)

# Function to test avaiable 7-segment displays
def display_value_test():
    enable_display_timer()  # Start the display timer
    for num in range(10):
        display_digits[0] = None
        display_digits[1] = None
        display_digits[2] = None
        display_digits[3] = num
        time.sleep(0.5)  # Show each digit for half a second
    disable_display_timer()  # Stop the display timer after the test

# Function to handle the button interrupt
def button_pressed(pin):
    global button_is_pressed
    global last_time
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_time) > debounce:
        button_is_pressed = 1
        last_time = current_time

# Function to setup GPIO/ADC pins, timers and interrupts
def setup():
    global button_is_pressed
    global display_digits
    global dp_position
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)
    enable_display_timer()
    voltage = 0.0
    s = "0.00"

    while True:
        if button_is_pressed == 1:
            voltage = read_analogue_voltage()
            s = '{:.2f}'.format(voltage)
            integer_part = int(voltage) 
            decimal_part = int(round((voltage - integer_part) * 100))
            
            display_digits[0] = 0 
            display_digits[1] = decimal_part % 10 
            display_digits[2] = decimal_part // 10 
            display_digits[3] = integer_part 
            
            dp_position = 3  
            
            button_is_pressed = 0
            


if __name__ == '__main__':
    setup()
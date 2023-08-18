import busio
import board
import digitalio
import time
import canio
import struct
import analogio
import pwmio
import shift_light_v2
from digitalio import DigitalInOut, Direction

# Constants
MSG_START = b'\xff\xff'
ECU_CAN_ID = 0x600

# Shift light
# SETUP
END = 8600
STEP = 150

# Make sure the leds are off
shift_light_v2.leds_off()

# Screen backlight brightness control
backlight = pwmio.PWMOut(board.D10, frequency=5000, duty_cycle=0)

# Light sensor
ADC = analogio.AnalogIn(board.A1)
def is_dark():
    a_val = ADC.value
    # print(a_val)
    if a_val < 6000:
        return True
    else:
        return False

# Dimmer
def dimmer(value):
    global led_br
    # Dark
    if value is True:
        backlight.duty_cycle = 30_000
        led_br = 10
    # Bright
    else:
        backlight.duty_cycle = 0
        led_br = 80

# Run at startup
dimmer(is_dark())

uart = busio.UART(board.TX, board.RX, baudrate=576_000, timeout=.5)

relay = DigitalInOut(board.D6)
relay.direction = Direction.OUTPUT
relay.value = True

# CAN BUS
# The CAN transceiver has a standby pin, bring it out of standby mode
if hasattr(board, 'CAN_STANDBY'):
    standby = digitalio.DigitalInOut(board.CAN_STANDBY)
    standby.switch_to_output(False)

# The CAN transceiver is powered by a boost converter, turn on its supply
if hasattr(board, 'BOOST_ENABLE'):
    boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
    boost_enable.switch_to_output(True)

# Can Bus pins
can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=500_000, auto_restart=True)

# CAN listener 0x400-0x407 and 0x600-0x607
listener = can.listen(matches=[canio.Match(id=0x607, mask=0x5F8)], timeout=.5)

# Variables
old_bus_state = None
fail_safe = 0
counter = 0
counter_start = False
old_dark = is_dark()
dim_counter = 0
t1 = time.monotonic()
shift_light_off = False
rpm = 0

# Debug
# rpm = 7999

while True:
    """
    # Debug
    # id = struct.pack("H", 0x600)
    id = 0x600
    data = struct.pack("<HBbHH", rpm, 0, 25, 100, 50)
    # time.sleep(.01)
    """

    # CAN BUS
    # Bus state information
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
    message = listener.receive()

    # Turn off when needed
    if message is None:
        print("No message received within timeout")
        serial_read = uart.read(1)
        # Shutdown message from Raspberry pi
        if serial_read == b'\xff':
            counter_start = True
            print("Counter start")
        if counter_start is True:
            counter += 1
        # Failsafe if message receiving failed
        fail_safe += 1
        if counter > 10 or fail_safe > 60:
            print("Shutting down")
            relay.value = False
        continue

    counter = 0
    fail_safe = 0
    counter_start = False

    id = message.id
    data = message.data

    # Reading rpm for shift light
    if id == ECU_CAN_ID:
        # Unpack message
        message = struct.unpack("<HBbHH", data)
        rpm = message[0]

    # print("Received a message with id:", (hex(id)))
    id_packed = struct.pack("H", id)

    # ECU_CAN_ID + 1 message not needed
    if id != ECU_CAN_ID + 1:
        # Send start message, id and message
        uart.write(MSG_START)
        uart.write(id_packed)
        uart.write(data)

    # Shift light
    if rpm > END - STEP * 5:
        shift_light_v2.action(rpm, STEP, END, led_br)
        shift_light_off = False
        # Make sure all leds are off
    else:
        if shift_light_off is False:
            shift_light_v2.leds_off()
            shift_light_off = True

    # Dimmer
    dark = is_dark()

    # If ambient light hasn't changed: reset timer
    if dark is old_dark:
        t1 = time.monotonic()

    # If timer hasn't been reseted in 4 seconds: change brightness
    if time.monotonic() > t1 + 4:
        dimmer(dark)
        old_dark = dark

   """
    # Debug
    # print("rpm =", rpm)
    rpm = int(rpm)
    if rpm < 8000:
        rise_rpm = True
    elif rpm > 9300:
        rise_rpm = False

    if rise_rpm is True:
        rpm += 1
    else:
        rpm -= 1
    time.sleep(.00625)
    """


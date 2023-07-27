import pygame
import time
import serial
import struct
import os

# Uart setup
uart = serial.Serial("/dev/ttyAMA0", baudrate=576_000, timeout=1,
                     parity=serial.PARITY_ODD)

# PyGame
size = width, height = (800, 480)
pygame.init()
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

# Read needed files
path = "/home/valtteri/EMUB/"
units_memory = open(path + "units_memory.txt", "r")
units = units_memory.read().splitlines()
units_memory.close()
odometer_memory = open(path + "odometer_memory.txt", "r")
odometer = int(odometer_memory.readline())
odometer_memory.close()

# Variables
start_up = True
timeout_counter = 0
rpm = 0
speed = 0
gear = 0
out_temp = 0
fuel_level = None
raw_fuel_level = 0
batt_v = 0
left_blinker = False
right_blinker = False
high_beam = False
errors = 0
speed_sum = 0
speed_sum_counter = 0
distance_timer = time.monotonic()
old_rpm = None
old_gear = None
old_speed = None
old_out_temp = None
old_odometer = None
old_clock = None
old_error_list = None
old_refuel = None
old_right_blinker = None
old_left_blinker = None
old_high_beam = None
old_values = [None, None, None, None, None, None]
values = [0, 0, 0, 0, 0, 0]
old_values_2 = [None, None, None, None, None, None]
values_2 = [0, 0, 0, 0, 0, 0]
clear = True
loop = True
touch = False
start = True
timeout_counter = 0
filter_counter = 0
filter_sum = 0
countdown = 10
buffer_empty = True
update = time.monotonic()

# CONSTANTS
CENTER_X, CENTER_Y = (width / 2, height / 2)
RIGHT_SIDE = width - 180
RED = (155, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
ECU_CAN_ID = 0x600
FUEL_MAX = 197
FUEL_MIN = 37

def menu():
    screen.fill((60, 60, 60))
    font_20 = pygame.font.SysFont("dejavusans", 20)

    # Constants
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def create_rect(x, y, text):
        pygame.draw.rect(screen, BLACK, [x, y, 190, 70], border_radius=10)
        name = font_20.render(text, True, WHITE)
        screen.blit(name, (x + 15, y + 20))
        return pygame.Rect(x, y, 190, 70)

    # Coordinates
    coordinates_x = []
    coordinates_y = []
    coordinate_y = 5
    coordinate_x = 5
    for x in range(6):
        coordinates_y.append(coordinate_y)
        coordinate_y += 80
    for x in range(4):
        coordinates_x.append(coordinate_x)
        coordinate_x += 200

    touch = False

    # Buttons
    rpm_button = create_rect(coordinates_x[0], coordinates_y[0], "RPM")
    tps_button = create_rect(coordinates_x[1], coordinates_y[0], "TPS")
    iat_button = create_rect(coordinates_x[2], coordinates_y[0], "IAT")
    map_button = create_rect(coordinates_x[3], coordinates_y[0], "MAP")
    inj_pw_button = create_rect(coordinates_x[0], coordinates_y[1], "Inj pw.")
    oil_t_button = create_rect(coordinates_x[1], coordinates_y[1], "Oil temp.")
    oil_p_button = create_rect(coordinates_x[2], coordinates_y[1], "Oil pressure")
    fuel_p_button = create_rect(coordinates_x[3], coordinates_y[1], "Fuel pressure")
    clt_t_button = create_rect(coordinates_x[0], coordinates_y[2], "Coolant temp.")
    ign_ang_button = create_rect(coordinates_x[1], coordinates_y[2], "Ignition angle")
    dwell_button = create_rect(coordinates_x[2], coordinates_y[2], "Dwell time")
    lambda_button = create_rect(coordinates_x[3], coordinates_y[2], "Lambda")
    lambda_corr_button = create_rect(coordinates_x[0], coordinates_y[3], "Lambda corr.")
    egt_1_button = create_rect(coordinates_x[1], coordinates_y[3], "EGT 1")
    egt_2_button = create_rect(coordinates_x[2], coordinates_y[3], "EGT 2")
    batt_button = create_rect(coordinates_x[3], coordinates_y[3], "Battery voltage")
    ethanol_ctnt_button = create_rect(coordinates_x[0], coordinates_y[4], "Ethanol content")
    dbw_pos_button = create_rect(coordinates_x[1], coordinates_y[4], "Dbw position")
    boost_t_button = create_rect(coordinates_x[2], coordinates_y[4], "Boost target")
    dsg_m_button = create_rect(coordinates_x[3], coordinates_y[4], "DSG Mode")
    lambda_t_button = create_rect(coordinates_x[0], coordinates_y[5], "Lambda target")
    fuel_used_button = create_rect(coordinates_x[1], coordinates_y[5], "Fuel used")
    fuel_level_button = create_rect(coordinates_x[2], coordinates_y[5], "Fuel level")
    empty_button = create_rect(coordinates_x[3], coordinates_y[5], "")

    # Display refresh
    pygame.display.flip()

    loop = True
    while loop:
        time.sleep(.01)
        # Press any key to interrupt
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.KEYDOWN:
                loop = False
                pygame.quit()
            # Unit selection
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touch = True
                pos = event.pos

        if touch:
            if pygame.Rect.collidepoint(rpm_button, pos):
                return "RPM"
            elif pygame.Rect.collidepoint(tps_button, pos):
                return  "TPS                 %"
            elif pygame.Rect.collidepoint(iat_button, pos):
                return  "IAT                 °C"
            elif pygame.Rect.collidepoint(map_button, pos):
                return  "MAP              kPa"
            elif pygame.Rect.collidepoint(inj_pw_button, pos):
                return  "Inj pw.           ms"
            elif pygame.Rect.collidepoint(oil_t_button, pos):
                return  "Oil temp.       °C"
            elif pygame.Rect.collidepoint(oil_p_button, pos):
                return  "Oil press.      bar"
            elif pygame.Rect.collidepoint(fuel_p_button, pos):
                return  "Fuel press.    bar"
            elif pygame.Rect.collidepoint(clt_t_button, pos):
                return  "Clt temp.       °C"
            elif pygame.Rect.collidepoint(ign_ang_button, pos):
                return  "Ign angle  °btdc"
            elif pygame.Rect.collidepoint(dwell_button, pos):
                return  "Dwell time    ms"
            elif pygame.Rect.collidepoint(lambda_button, pos):
                return  "Lambda"
            elif pygame.Rect.collidepoint(lambda_corr_button, pos):
                return  "Lambda corr.  %"
            elif pygame.Rect.collidepoint(egt_1_button, pos):
                return  "EGT 1             °C"
            elif pygame.Rect.collidepoint(egt_2_button, pos):
                return  "EGT 2             °C"
            elif pygame.Rect.collidepoint(ethanol_ctnt_button, pos):
                return  "Ethanol           %"
            elif pygame.Rect.collidepoint(batt_button, pos):
                return  "Battery  voltage"
            elif pygame.Rect.collidepoint(dbw_pos_button, pos):
                return  "Dbw position  %"
            elif pygame.Rect.collidepoint(boost_t_button, pos):
                return  "Boost target  kPa"
            elif pygame.Rect.collidepoint(dsg_m_button, pos):
                return  "DSG mode"
            elif pygame.Rect.collidepoint(lambda_t_button, pos):
                return  "Lambda target"
            elif pygame.Rect.collidepoint(fuel_used_button, pos):
                return  "Fuel used         L"
            elif pygame.Rect.collidepoint(fuel_level_button, pos):
                return  "Fuel level        %"
            touch = False

# Return CPU temperature as a character string
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("'C\n", ""))

# DSG mode dictionery
dsg_mode_return = {0: "0", 2 : "P", 3 : "R", 4 : "N", 5 : "D", 6 : "S", 7 : "M", 15 : "Fault"}

# Fonts
font_20 = pygame.font.SysFont("dejavusans", 20)
font_30 = pygame.font.SysFont("dejavusans", 30)
font_60 = pygame.font.SysFont("dejavusans", 60)
font_80 = pygame.font.SysFont("dejavusans", 80)

# Text box sizes
kmh_30 = font_30.size("km/h")
one_digit_60 = font_60.size("0")
three_digit_60 = font_60.size("000")
one_letter_60 = font_60.size("N")
digits_80 = [font_80.size("0"), font_80.size("00"), font_80.size("000")]

# Renders
CELSIUS_20 = font_20.render("°C", True, WHITE, BLACK)
KMH_TEXT = font_30.render("km/h", True, WHITE, BLACK)
NO_CAN_BUS_R = font_20.render("No Can Bus communication", True, WHITE, BLACK)
# RPM bar numbers
rpm_list = [font_60.render(str(x), True, WHITE) for x in range(1, 10)]

# Title texts
def title_text(text):
    return font_20.render(text, True, WHITE, BLACK)

# Images
HIGH_BEAM_BLUE = pygame.image.load(path + "High_beam_blue.png")
HIGH_BEAM_BLACK = pygame.image.load(path + "High_beam_black.png")
FUEL_PUMP_YELLOW = pygame.image.load(path + "Fuel_pump_yellow.png")
FUEL_PUMP_BLACK = pygame.image.load(path + "Fuel_pump_black.png")

# Buttons
unit_0_button = pygame.Rect(0, 95, 180, 100)
unit_1_button = pygame.Rect(0, 210, 180, 100)
unit_2_button = pygame.Rect(0, 325, 180, 100)
unit_3_button = pygame.Rect(RIGHT_SIDE, 95, 180, 100)
unit_4_button = pygame.Rect(RIGHT_SIDE, 210, 180, 100)
unit_5_button = pygame.Rect(RIGHT_SIDE, 325, 180, 100)

# Emu Black error flags
ERRORFLAGS = ("", "OILP", "EWG", "DSG", "DIFFCTRL", "FPR", "DBW", "FF_SENSOR",
              "KNOCKING", "EGT_ALARM", "EGT2", "EGT1", "WBO", "MAP", "IAT", "CLT")

def error_flags(number):
    # Convert to bit list
    bit_list = [True if x == "1" else False for x in "{:016b}".format(number)]
    # Get the errors that are on
    errors_on = []
    for x in range(len(bit_list)):
        if bit_list[x] is True:
            errors_on.append(ERRORFLAGS[x])
    return errors_on

# Reading 3 bit bitfield from Can extension board (message 0x610)
def bitfield_3_return(number):
    # Convert to bit list
    bit_list = [True if x == "1" else False for x in "{:03b}".format(number)]
    return bit_list

# Creating title texts
unit_0 = title_text(units[0])
unit_1 = title_text(units[1])
unit_2 = title_text(units[2])
unit_3 = title_text(units[3])
unit_4 = title_text(units[4])
unit_5 = title_text(units[5])

# Clear input buffer
uart.reset_input_buffer()

while loop:
    # Clearing screen
    if clear is True:
        screen.fill((60, 60, 60))
        values = [0, 0, 0, 0, 0, 0]

    # Press any key to interrupt
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            loop = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            touch = True
            pos = event.pos
    # Read uart message id and message
    id = None

    # If Uart buffer is empty
    if uart.in_waiting == 0:
        time.sleep(.01)
        buffer_empty = True
        timeout_counter += 1
    else:
        buffer_empty = False
        data = uart.read(1)
        countdown = 10
        timeout_counter = 0

    # Shutdown if there is no Can Bus communication
    if timeout_counter > 100:
        clear = True
        data = uart.read(1)
        if data == b'':
            countdown -= 1
            pygame.draw.rect(screen, BLACK, [CENTER_X - 150, 180, 300, 150], border_radius=10)
            screen.blit(NO_CAN_BUS_R, (CENTER_X - 140, CENTER_Y - 10))
            shutdown = font_20.render("Shutting down in: " + str(countdown) + " s", True, WHITE, BLACK)
            screen.blit(shutdown, (CENTER_X - 140, CENTER_Y + 15))
            pygame.display.flip()
        if countdown == 0:
            # Send message to Feather to turn off the power
            uart.write(b'\xff')
            print("Shutdown")
            os.system("sudo shutdown -h now")
        if loop is True:
            continue
    if buffer_empty is True and loop is True:
        continue

    # Reading message start
    if data == b'\xff':
        data = uart.read(1)
        if data == b'\xff':
            id = uart.read(2)
            id = struct.unpack("H", id)[0]

    if id == 0x400:
        data = uart.read(3)
        message = struct.unpack("<BBb", data)
        bit_list_3 = bitfield_3_return(message[0])
        # High beam input is inverted
        high_beam = not bit_list_3[0]
        right_blinker = bit_list_3[1]
        left_blinker = bit_list_3[2]
        raw_fuel_level = message[1]
        out_temp = message[2]
        # Fuel level filtering
        if filter_counter < 499:
            filter_sum += raw_fuel_level
            filter_counter += 1
            filter_ready = False
        else:
            fuel_level = int(filter_sum / filter_counter)
            filter_sum = 0
            filter_counter = 0
            filter_ready = True
        # If filtering not ready
        if start_up is True:
            fuel_level = raw_fuel_level
        # Scaling
        if filter_ready is True or start_up is True:
            if fuel_level > FUEL_MAX:
                fuel_level = FUEL_MAX
            if fuel_level < FUEL_MIN:
                fuel_level = FUEL_MIN
            fuel_level = int((fuel_level - 37) / 1.6 - 100)
            if fuel_level != 0:
                fuel_level = fuel_level * -1
            start_up = False
        if "Fuel level        %" in units:
            values[units.index("Fuel level        %")] = fuel_level

    elif id is not None:
        data = uart.read(8)

    if id == ECU_CAN_ID:
        # Unpack message
        message = struct.unpack("<HBbHH", data)
        rpm = message[0]
        if "RPM" in units:
            values[units.index("RPM")] = rpm
        if "TPS                 %" in units:
            values[units.index("TPS                 %")] = int(message[1] * 0.5)
        if "IAT                 °C" in units:
            values[units.index("IAT                 °C")] = message[2]
        if "MAP              kPa" in units:
            values[units.index("MAP              kPa")] = message[3]
        if "Inj pw.           ms" in units:
            values[units.index("Inj pw.           ms")] = round(message[4] * 0.016129, 1)

    elif id == ECU_CAN_ID + 2:
        message = struct.unpack("<HBBBBh", data)
        speed = message[0]
        # Calculating travelled distance
        speed_sum += speed
        speed_sum_counter += 1
        if speed_sum_counter >= 1000:
            average_speed = (speed_sum / 1000) * 0.27777778
            timer = time.monotonic() - distance_timer
            distance = (average_speed * timer) / 1000
            distance_timer = time.monotonic()
            odometer = odometer + distance
            speed_sum = 0
            speed_sum_counter = 0
            # Saving to memory
            odometer_memory = open(path + "odometer_memory.txt", "w")
            odometer_memory.write(str(int(odometer)))
            odometer_memory.close()
        if "Oil temp.       °C" in units:
            values[units.index("Oil temp.       °C")] = message[2]
        if "Oil press.      bar" in units:
            values[units.index("Oil press.      bar")] = round(message[3] * 0.0625, 1)
        if "Fuel press.    bar" in units:
            values[units.index("Fuel press.    bar")] = round(message[4] * 0.0625, 1)
        if "Clt temp.       °C" in units:
            values[units.index("Clt temp.       °C")] = message[5]

    elif id == ECU_CAN_ID + 3:
        message = struct.unpack("<bBBBHH", data)
        if "Ign angle  °btdc" in units:
            values[units.index("Ign angle  °btdc")] = message[0] * 0.5
        if "Dwell time    ms" in units:
            values[units.index("Dwell time    ms")] = round(message[1] * 0.05, 1)
        if "Lambda" in units:
            values[units.index("Lambda")] = round(message[2] * 0.0078125, 2)
        if "Lambda corr.  %" in units:
            values[units.index("Lambda corr.  %")] = int(message[3] * 0.5)
        if "EGT 1             °C" in units:
            values[units.index("EGT 1             °C")] = message[4]
        if "EGT 2             °C" in units:
            values[units.index("EGT 2             °C")] = message[5]

    elif id == ECU_CAN_ID + 4:
        message = struct.unpack("<BbHHBB", data)
        gear = message[0]
        batt_v = round(message[2] * 0.027, 1)
        if "Battery  voltage" in units:
            values[units.index("Battery  voltage")] = batt_v
        # Error flags
        errors = message[3]
        if "Ethanol           %" in units:
            values[units.index("Ethanol           %")] = message[5]

    elif id == ECU_CAN_ID + 5:
        message = struct.unpack("<BBhHBB", data)
        if "Dbw position  %" in units:
            values[units.index("Dbw position  %")] = int(message[0] * 0.5)

    elif id == ECU_CAN_ID + 7:
        message = struct.unpack("<HBBBBH", data)
        if "Boost target  %" in units:
            values[units.index("Boost target  kPA")] = message[0]
        if "DSG mode" in units:
            values[units.index("DSG mode")] = dsg_mode_return[message[2]]
        if "Lambda target" in units:
            values[units.index("Lambda target")] = round(message[3] * 0.01, 2)
        if "Fuel used         L" in units:
            values[units.index("Fuel used         L")] = round(message[5] * 0.01, 1)

    # Clearing old values, when needed
    values_2[0] = len(str(values[0]))
    if values_2[0] != old_values_2[0] or clear is True:
        old_values_2[0] = values_2[0]
        pygame.draw.rect(screen, BLACK, [0, 95, 180, 100], border_radius=10)
        screen.blit(unit_0, (10, 100))

    values_2[1] = len(str(values[1]))
    if values_2[1] != old_values_2[1] or clear is True:
        old_values_2[1] = values_2[1]
        pygame.draw.rect(screen, BLACK, [0, 210, 180, 100], border_radius=10)
        screen.blit(unit_1, (10, 215))

    values_2[2] = len(str(values[2]))
    if values_2[2] != old_values_2[2] or clear is True:
        old_values_2[2] = values_2[2]
        pygame.draw.rect(screen, BLACK, [0, 325, 180, 100], border_radius=10)
        screen.blit(unit_2, (10, 330))

    values_2[3] = len(str(values[3]))
    if values_2[3] != old_values_2[3] or clear is True:
        old_values_2[3] = values_2[3]
        pygame.draw.rect(screen, BLACK, [RIGHT_SIDE, 95, 180, 100], border_radius=10)
        screen.blit(unit_3, (RIGHT_SIDE + 10, 100))

    values_2[4] = len(str(values[4]))
    if values_2[4] != old_values_2[4] or clear is True:
        old_values_2[4] = values_2[4]
        pygame.draw.rect(screen, BLACK, [RIGHT_SIDE, 210, 180, 100], border_radius=10)
        screen.blit(unit_4, (RIGHT_SIDE + 10, 215))

    values_2[5] = len(str(values[5]))
    if values_2[5] != old_values_2[5] or clear is True:
        old_values_2[5] = values_2[5]
        pygame.draw.rect(screen, BLACK, [RIGHT_SIDE, 325, 180, 100], border_radius=10)
        screen.blit(unit_5, (RIGHT_SIDE + 10, 330))

    new_speed = len(str(speed))
    if new_speed != old_speed or clear is True:
        old_speed = new_speed
        pygame.draw.rect(screen, BLACK, [CENTER_X - 110, 180, 220, 150], border_radius=10)
        screen.blit(KMH_TEXT, (CENTER_X - kmh_30[0] / 2, 285))

    # Update values, when needed
    # Top left value update
    if values[0] != old_values[0] or clear is True:
        old_values[0] = values[0]
        value_0_r = font_60.render(str(values[0]), True, WHITE, BLACK)
        screen.blit(value_0_r, (10, 125))
    # Center left value update
    if values[1] != old_values[1] or clear is True:
        old_values[1] = values[1]
        value_1_r = font_60.render(str(values[1]), True, WHITE, BLACK)
        screen.blit(value_1_r, (10, 240))
    # Bottom left value update
    if values[2] != old_values[2] or clear is True:
        old_values[2] = values[2]
        value_2_r = font_60.render(str(values[2]), True, WHITE, BLACK)
        screen.blit(value_2_r, (10, 355))
    # Top right value update
    if values[3] != old_values[3] or clear is True:
        old_values[3] = values[3]
        value_3_r = font_60.render(str(values[3]), True, WHITE, BLACK)
        screen.blit(value_3_r, (RIGHT_SIDE + 10, 125))
    # Center right value update
    if values[4] != old_values[4] or clear is True:
        old_values[4] = values[4]
        value_4_r = font_60.render(str(values[4]), True, WHITE, BLACK)
        screen.blit(value_4_r, (RIGHT_SIDE + 10, 240))
    # Bottom right value update
    if values[5] != old_values[5] or clear is True:
        old_values[5] = values[5]
        value_5_r = font_60.render(str(values[5]), True, WHITE, BLACK)
        screen.blit(value_5_r, (RIGHT_SIDE + 10, 355))
    # Gear update
    if gear != old_gear or clear is True:
        pygame.draw.rect(screen, BLACK, [CENTER_X - 40, 90, 80, 80], border_radius=10)
        old_gear = gear
        if gear == 0:
            gear = "N"
        gear_r = font_60.render(str(gear), True, WHITE, BLACK)
        if gear == "N":
            screen.blit(gear_r, (CENTER_X - one_letter_60[0] / 2, 95))
        else:
            screen.blit(gear_r, (CENTER_X - one_digit_60[0] / 2, 95))
    # Speed update
    if speed != old_speed or clear is True:
        old_speed = speed
        speed_r = font_80.render(str(speed), True, WHITE, BLACK)
        screen.blit(speed_r, (CENTER_X - digits_80[len(str(speed)) - 1][0] / 2, CENTER_Y - digits_80[0][1] / 2))

    clock = time.strftime("%H:%M")
    if clock != old_clock or out_temp != old_out_temp or odometer != old_odometer or clear is True:
        pygame.draw.rect(screen, BLACK, [CENTER_X - 110, 340, 220, 80], border_radius=10)
        screen.blit(CELSIUS_20, (CENTER_X + 75, 350))
        # Clock update
        old_clock = clock
        clock_r = font_30.render(clock, True, WHITE, BLACK)
        screen.blit(clock_r, (CENTER_X - 100, 343))
        # Out temp update
        old_out_temp = out_temp
        out_temp_r = font_30.render(str(out_temp), True, WHITE, BLACK)
        screen.blit(out_temp_r, (CENTER_X + 35, 343))
        # Odometer update
        old_odometer = odometer
        odometer_r = font_30.render(str(int(odometer)) + " km", True, WHITE, BLACK)
        screen.blit(odometer_r, (CENTER_X - 100, 383))

    # RPM Bar
    if rpm != old_rpm or clear is True:
        rpm_bar = int(rpm * 0.08)
        pygame.draw.rect(screen, BLACK, (0, 0, 800, 80))
        pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, rpm_bar, 80))
        for x in range(len(rpm_list)):
            screen.blit(rpm_list[x], (width / 10 * (x + 1) - one_digit_60[0] / 2, 40 - one_digit_60[1] / 2))
        old_rpm = rpm

    # Blinker left
    if old_left_blinker != left_blinker or clear is True:
        if left_blinker is True:
            blinker_colour = GREEN
        else:
            blinker_colour = BLACK
        bl = [210, 150]
        pygame.draw.polygon(screen, blinker_colour, [[bl[0], bl[1]], [bl[0] + 16, bl[1] - 16], [bl[0] + 16, bl[1] + 16]])
        pygame.draw.rect(screen, blinker_colour, (bl[0] + 16, bl[1] - 8, 16, 16))
        old_left_blinker = left_blinker

    if old_right_blinker != right_blinker or clear is True:
        if right_blinker is True:
            blinker_colour = GREEN
        else:
            blinker_colour = BLACK
        # Blinker right
        br = [590, 150]
        pygame.draw.polygon(screen, blinker_colour, [[br[0], br[1]], [br[0] - 16, br[1] - 16], [br[0] - 16, br[1] + 16]])
        pygame.draw.rect(screen, blinker_colour, (br[0] - 32, br[1] - 8, 16, 16))
        old_right_blinker = right_blinker

    if old_high_beam != high_beam or clear is True:
        if high_beam is True:
            screen.blit(HIGH_BEAM_BLUE, (205, 350))
        else:
            screen.blit(HIGH_BEAM_BLACK, (205, 350))
        old_high_beam = high_beam

    # Fuel level warning
    # print(fuel_level)
    if fuel_level is not None and fuel_level < 6:
        refuel = True
    else:
        refuel = False

    if refuel != old_refuel or clear is True:
        if refuel is False:
            screen.blit(FUEL_PUMP_BLACK, (545, 350))
        else:
            screen.blit(FUEL_PUMP_YELLOW, (545, 350))
        old_refuel = refuel

    # Errors
    error_list = []
    if errors != 0:
        error_list = error_flags(errors)

    # Battery voltage low warning
    if batt_v < 11.3 or batt_v < 13 and rpm > 0:
        error_list.append("Battery " + str(batt_v) + "V")

    if error_list != old_error_list or update < time.monotonic() or clear is True:
        update = time.monotonic() + 1
        if len(error_list) == 0:
            pygame.draw.rect(screen, LIGHT_BLUE, (0, 440, 800, 40))
            cpu_temp = getCPUtemperature()
            cpu_temp_text = font_30.render("Cpu " + cpu_temp, True, WHITE, LIGHT_BLUE)
            screen.blit(cpu_temp_text, (0, 443))
        else:
            errors_text = font_30.render("Errors " + str(len(error_list)) + ": ", True, WHITE, RED)
            errors_r = font_30.render(", ".join(error_list), True, WHITE, RED)
            pygame.draw.rect(screen, RED, (0, 440, 800, 40))
            screen.blit(errors_text, (0, 443))
            screen.blit(errors_r, (135, 443))
        old_error_list = error_list
        clear = False

    # Unit change
    if touch:
        if pygame.Rect.collidepoint(unit_0_button, pos):
            units[0] = menu()
            unit_0 = title_text(units[0])
        elif pygame.Rect.collidepoint(unit_1_button, pos):
            units[1] = menu()
            unit_1 = title_text(units[1])
        elif pygame.Rect.collidepoint(unit_2_button, pos):
            units[2] = menu()
            unit_2 = title_text(units[2])
        elif pygame.Rect.collidepoint(unit_3_button, pos):
            units[3] = menu()
            unit_3 = title_text(units[3])
        elif pygame.Rect.collidepoint(unit_4_button, pos):
            units[4] = menu()
            unit_4 = title_text(units[4])
        elif pygame.Rect.collidepoint(unit_5_button, pos):
            units[5] = menu()
            unit_5 = title_text(units[5])

        touch = False
        clear = True
        # Clear serial buffer because of interrupt
        uart.reset_input_buffer()

        # Saving to memory
        units_memory = open(path + "units_memory.txt", "w")
        for x in range(len(units)):
            units_memory.write(str(units[x]) + "\n")
        units_memory.close()

    # Update screen
    pygame.display.flip()

    # Close the program
    if loop is False:
        pygame.quit()


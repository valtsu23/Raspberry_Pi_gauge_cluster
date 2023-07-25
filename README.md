# Raspberry_pi_gauge_cluster
### Technical specs:
- Raspberry Pi 4 Model B 4GB
- 5" sunlight readable display with touchscreen from Makerplane:
  - https://store.makerplane.org/5-sunlight-readable-touchscreen-hdmi-display-for-raspberry-pi/
- DIY PCB inside the enclosure controls power for all devices and receives Can Bus messages and sends them over UART to Raspberry pi
  - DC-DC converter
  - Adafruit Feather M4 CAN Express with ATSAME51
  - Adafruit DS3231 Precision RTC - STEMMA QT
  - Screen brighness control
  - Adafruit Neopixel shiftlight control
  - Small relay for power

### Software specs
- Raspberry Pi OS Lite 64bit (bullseye)
  - X server: X.Org
  - Window manager: Openbox
  - Gauge cluster software is based on Pygame graphics library
    - There is 6 sensors data (3 left and 3 right) that you can choose to display with touscreen

### Can bus data
- Most of the data needed is read from Ecumaster Emu Black can stream
- There is also DIY can bus device sending message id 0x400, which contains
  - turn signals
  - high beam
  - fuel level

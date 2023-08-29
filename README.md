# Raspberry_Pi_gauge_cluster

![image1](/Pictures/IMG_20230724_183946.jpg)

Video: https://youtu.be/ISC5q4k9wDg

### Updates
30.8.2023 display_v2.py released (more info on the file)


### How it works
Adafruit Feather receives messages from Can Bus and picks rpm signal for shift light. Feather sends same can bus data bytes over Uart to Raspberry pi. 
Feather reads the amount of ambient light from photodiode and controls screeen brightness with pwm. 
Device needs switched 12V and continous 12v from battery to work correctly. Switched power wakes up the device and Raspberry pi starts booting. When Can Bus stream is lost Raspberry pi automatically starts shutdown process and sends message to Feather. After specified time the Feather turns off the relay connected to continous 12v and cuts power from the device. The device doesn't consume any power after shutdown. 

### Something to improve
- More testing needed
- Display code still needs some optimizing
- Adding Raspberry pi setup guide
- Shortening the start up time (about 25 seconds now)

### Technical specs:
- Raspberry Pi 4 Model B 4GB
- SanDisk Extreme Pro UHS-I U3 64GB microSD
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
### Graphic software functions
- There is 6 sensors data (3 left and 3 right) that you can choose to display with touscreen
- bar on the bottom of the screen in normal situation is blue and shows Raspberry pi CPU temperature
- If there is some error detected by ECU or battery voltage is low. Error flags are shown on the bottom of the screen and the bar is red
  
### Can bus data
- Most of the data needed is read from Ecumaster Emu Black can stream
- There is also DIY can bus device sending message id 0x400, which contains
  - Turn signals
  - High beam on
  - Fuel level
  - Ambient temperature

### Case
- Designed with FreeCAD
- Filament is PETG
- M3x6 machine screws 2 pcs
- M4 thread insert 1 pcs
- M4x8 machine screw 1pcs
- M4x20 machine screw 2pcs
- M4 nut 2pcs

![image1](/Pictures/Raspi_Feather2.png)

### Part list for PCB:
#### From www.partco.fi
  - PCH2596S DC-DC converter (LM2596S)
  - 3A diode 
  - 1A diode 2pcs
  - FTR-F3AA005V (small 5V relay)
  - BPW42 3mm phototransistor or similar
  - 2N3904 NPN transistor or similar
  - B3F-31XX Omron switch or SKH KKK 2 from partco.fi
  - 2k2 0,6w resistor
  - 1M 0,6w resistor 
  - 2x13 male pin header with long pins (20mm total length)
  - 2x13 female smd pin header (soldered to display pcb)
  - 1x40 female pin header
  - 1x40 male pin header
  - 0,22mm2 - 0,5mm2 wires (0,5mm2 recommended for power and ground)
#### From Berrybase.de
  - NeoPixel Stick mit 8 WS2812 5050 RGB LEDs (Copy of Adafruit's product. Dimensions won't match)
#### From www.adafruit.com
  - Adafruit DS3231 Precision RTC - STEMMA QT
  - Adafruit Feather M4 CAN Express with ATSAME51
#### From www.ebay.com
  - 5pin JST-SM connector pair

![Image1](/Pictures/DSC_0969.JPG)

![Image1](/Pictures/DSC_0965.JPG)

![Image1](/Pictures/DSC_0927.JPG)

![Image1](/Pictures/DSC_0938.JPG)

![Image1](/Pictures/DSC_0955.JPG)

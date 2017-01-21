#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import logging
import sys, serial
from time import *
import datetime, string

def enum(**enums):
    return type('Enum', (), enums)

Status = enum(ERR='ERROR', OK=['OK', 'ready', 'no change'], BUSY='busy')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# modified code from: http://www.instructables.com/id/Easy-ESP8266-WiFi-Debugging-with-Python/step2/Software/
def send_cmd(sCmd, waitTm=1, retry=5):
    lp = 0
    ret = ""

    logging.info("Sending command: %s" % sCmd)

    for i in range(retry):
        ser.flushInput()
        ser.write(sCmd + "\r\n")
        ret = []
        ret.append(ser.readline().strip("\r\r\n"))  # Eat echo of command.
        sleep(0.2)
        while (lp < waitTm or Status.BUSY in ret[-1]):
            while (ser.inWaiting()):
                ret.append(ser.readline().strip("\r\n"))
                logging.debug(ret[-1])
                lp = 0
            if (ret in Status.OK): break
            # if( ret == 'ready' ): break
            if (ret == Status.ERR): break
            sleep(1)
            lp += 1

        sleep(1)
        if (ret[-1] in Status.OK): break

    logging.info("Command result: %s" % ret)
    return ret

if len(sys.argv) != 5:
    print "Usage: esp8266test.py port baud_rate ssid password"
    sys.exit()

port = sys.argv[1]
# Baud rate should be: 9600 or 115200
speed = sys.argv[2]
ssid = sys.argv[3]
pwd = sys.argv[4]

ser = serial.Serial(port, speed)
try:
    if ser.isOpen():
        ser.close()
    ser.open()
    ser.isOpen()

    send_cmd("AT")
    # send_cmd( "AT+RST", 5 ) # NOTE: seems to cause problems that require manually reset (pulling down the RST pin)
    # sleep(3)
    current_ap = send_cmd("AT+CWJAP?")[1]
    print current_ap
    if ssid not in current_ap:
        send_cmd("AT+CWMODE=1")  # set device mode (1=client, 2=AP, 3=both)
        # The mode will be changed on Olimex MOD-WIFI-ESP8266-DEV only after a reset
        # The command below will reset the device
        send_cmd("AT+RST");
        send_cmd("AT+CWLAP", 10)  # scan for WiFi hotspots
        send_cmd("AT+CWJAP=\"" + ssid + "\",\"" + pwd + "\"", 5)  # connect

    addr = send_cmd("AT+CIFSR", 5)  # check IP address

finally:
    ser.close()

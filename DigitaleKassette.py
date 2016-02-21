#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pygame
import config
import threading
import time
import logging

from miranda import upnp, msearch, host
from UPNPController import UPNPController
from RFIDReader import RFIDReader
from JukeBox import JukeBox
from ActionData import ActionData
from WebApp import WebApp
from Wifi import Wifi

class DigitaleKassette(threading.Thread):

    def __init__(self):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.mediaRendererModelName = config.general['mediaRendererModelName'] 
        self.lastRFIDCard = ''
        self.initializeWifi = False
        
        # Set up logging       
        self.logger = logging.getLogger('DigitaleKassette')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
        
        os.system('gmediarender start &')
        time.sleep(5)
        
        # Initialize UPnP connection and discover devices
        self.uPNPController = UPNPController()
        self.uPNPController.discoverDevices()
        self.uPNPController.getDeviceInformation()
        self.uPNPController.getDeviceByModelName('MediaRenderer', self.mediaRendererModelName)
        self.uPNPController.getDevicesByDeviceType('urn:schemas-upnp-org:device:MediaServer:1', 'MediaServer')
        
        # Initialize ActionDB
        self.actionData = ActionData()

        # Initialize RFID-Reader
        self.reader = RFIDReader(True)
        
        # Initialize JukeBox
        self.jb = JukeBox(self.uPNPController, self.actionData)
        
        # Initalize Wifi
        self.wifi = Wifi() 
        if not self.wifi.isConnected():
            self.initializeWifi = True
            self.wifi.startAccessPoint()
        
        # Initialize WebApp
        self.webApp = WebApp(self.uPNPController, self.actionData, self, self.wifi, self.initializeWifi)          

    def onNewConnection(self):
        os.system('gmediarender start &')
        time.sleep(5)
        self.uPNPController.discoverDevices()
        self.uPNPController.getDeviceInformation()
        self.uPNPController.getDeviceByModelName('MediaRenderer', self.mediaRendererModelName)
        self.uPNPController.getDevicesByDeviceType('urn:schemas-upnp-org:device:MediaServer:1', 'MediaServer')
       
        #os.system('sudo fuser -k 80/tcp')
        #self.webApp = WebApp(self.uPNPController, self.actionData, self, self.wifi, False)
        
        #Ready: make some noise
        os.system('mpg321 audio/beep.mp3 &')
        
    def lockRFID(self):
        if(self.jb.rfidIsLocked == False):
            
            self.jb.rfidIsLocked = True
            
            time.sleep(self.jb.rfidLockIntervall)
            self.jb.rfidIsLocked = False
            
            #hide last card from Jukebox
            self.reader.lastID = '' 
            
            return True
        else:
            self.logger.error('RFIDReader is already locked...')  
            return False
        #pause
        
if __name__ == '__main__':
    
    #os.system('cat /sys/class/net/wlan0/carrier')
    
    dk = DigitaleKassette()
    dk.logger.debug('DigitaleKassette is up running...')  
   
    #Ready: make some noise
    os.system('mpg321 audio/beep.mp3 &')
    
    while True:
        dk.logger.debug('Main loop...') 
        
        # perform action on new rfid event
        if dk.lastRFIDCard != dk.reader.lastID and dk.jb.rfidIsLocked == False:
            dk.lastRFIDCard = dk.reader.lastID
            dk.jb.play(dk.reader.lastID) 
        if dk.wifi.hasNewConnection == True:
            dk.onNewConnection() 
            dk.wifi.hasNewConnection = False
                
        time.sleep(1)

			

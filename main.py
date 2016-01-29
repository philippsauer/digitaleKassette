#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import config
import threading
import time
import serial
import logging

from miranda import upnp, msearch, host

class DigitaleKassette(threading.Thread):

    def __init__(self):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.actionDataSource = config.general['actionDataSource']
        self.mediaRendererModelName = config.general['mediaRendererModelName'] 
        self.deviceSearchTimeout = config.general['deviceSearchTimeout'] 
        self.latestRFIDCard = ''
        self.mediaRendererIndex = ''
         
        # Set up logging       
        self.logger = logging.getLogger('DigitaleKassette')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
   
        # Set up dedicated thread for RFID-Reader
        RFIDthread = threading.Thread(target=self.readRFID, args=())
        RFIDthread.daemon = True
        RFIDthread.start()
        self.logger.debug('RFIDthread started')
        
        # Set up UPnP connection
        self.conn = upnp(False,False,None,None)
        self.conn.UNIQ = True
        self.conn.VERBOSE = True
        self.conn.TIMEOUT = self.deviceSearchTimeout 

        # Set up thread for device discovery
        deviceDiscoveryThread = threading.Thread(target=self.discoverDevice, args=(self.mediaRendererModelName,))
        deviceDiscoveryThread.daemon = True
        deviceDiscoveryThread.start()      
        self.logger.debug('device discovery thread started')

    def readRFID(self):
    # endlessly run RFID scanner
        sleepTime = config.rfid['sleepTime']
        startFlag = '\x02'
        endFlag = '\x03'   
        
        UART = serial.Serial('/dev/ttyAMA0', 9600)
        UART.close()
        UART.open() 
        
        while True:
            ID = ''
            Zeichen = UART.read()
            if Zeichen == startFlag:
                for Counter in range(13):
                    Zeichen = UART.read()
                    ID = ID + str(Zeichen)
                ID = ID.replace(endFlag, '')              
                if  ID != self.latestRFIDCard:  
                    self.setNewRFIDCard (ID)
                time.sleep(sleepTime)    
               
    def setNewRFIDCard(self, ID): 
    # set latest RFID card ID
        self.latestRFIDCard = ID
        self.logger.debug('New RFID-Card detected: '+ID)
        action = self.getAction(ID)
        self.runAction(action)
      
    def getAction(self, id):
    # Get designated action for a given RFID-Chip-ID   
        f = open(self.actionDataSource, 'r')
        try:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == id:
                    return row
                    break
        except ValueError:
            self.logger.error( 'Could not read file: '+self.actionDataSource)
        finally:
            f.close()
    
    def runAction(self, action):
    # run designated action for current RFID card ID
        if action[2] == 'play':
            self.logger.debug('Performing action: '+action[2])
            #host(6,[0, 'send', self.mediaRendererIndex, 'MediaRenderer', 'AVTransport', 'SetAVTransportURI'], self.conn)
            self.sendAction('set', 'MediaRenderer', 'AVTransport', 'SetAVTransportURI')
            self.sendAction('play', 'MediaRenderer', 'AVTransport', 'Play')
            
        elif action[2] == 'pause':
            self.logger.debug('Performing action: '+action[2])
        elif action[2] == 'next':
            self.logger.debug('Performing action: '+action[2])
        else:
            self.logger.error( 'No action given for: '+action)
      
    def discoverDevice(self, modelName):
    
        self.logger.debug('Searching for devices...')
        msearch(0, 0, self.conn)
        
        self.logger.debug('Getting device information...')
        for index in self.conn.ENUM_HOSTS:
            hostInfo = self.conn.ENUM_HOSTS[index]
            if hostInfo['dataComplete'] == False:
                xmlHeaders, xmlData = self.conn.getXML(hostInfo['xmlFile'])
                self.conn.getHostInfo(xmlData,xmlHeaders,index)
        
        self.logger.debug('Searching for gmediarenderer...')
        for index in self.conn.ENUM_HOSTS:        
            if hostInfo['dataComplete'] == True:
                try:
                    if self.conn.ENUM_HOSTS[index]['deviceList']['MediaRenderer']['modelName'] == modelName:
                        self.logger.debug('gmediarender found ...')  
                        self.logger.debug('index: '+str(index)) 
                        self.mediaRendererIndex = str(index)
                        
                except KeyError:
                    pass

    
    def sendAction(self, action, deviceName, serviceName, actionName):
    
        index = False
        actionArgs = False
        sendArgs = {}
        retTags = []
        controlURL = False
        fullServiceName = False
        
        try:
            hostInfo = self.conn.ENUM_HOSTS[int(self.mediaRendererIndex)]
        except:
            self.logger.debug('Indexing failed') 
            return False

		#Get the service control URL and full service name
        try:
            controlURL = hostInfo['proto'] + hostInfo['name']
            controlURL2 = hostInfo['deviceList'][deviceName]['services'][serviceName]['controlURL']
            if not controlURL.endswith('/') and not controlURL2.startswith('/'):
                controlURL += '/'
            controlURL += controlURL2
        except Exception,e:
            self.logger.debug('Getting service control URL failed') 
            return False

        #Get action info
        try:
            actionArgs = hostInfo['deviceList'][deviceName]['services'][serviceName]['actions'][actionName]['arguments']
            fullServiceName = hostInfo['deviceList'][deviceName]['services'][serviceName]['fullName']
        except Exception,e:
            self.logger.debug('Getting action info failed') 
            return False

        if action == 'set':
            self.logger.debug('Performing action SET') 
            for argName,argVals in actionArgs.iteritems():
                print argName
                if argName == 'InstanceID':
                    actionStateVar = argVals['relatedStateVariable']
                    stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]			                    
                    sendArgs[argName] = ('self.mediaRendererIndex',stateVar['dataType'])
                if argName == 'CurrentURIMetaData':
                    actionStateVar = argVals['relatedStateVariable']
                    stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]			                    
                    sendArgs[argName] = ('http://192.168.2.135:10243/WMPNSSv4/2601510775/1_NC0xNDQ1OA.mp3',stateVar['dataType'])
                if argName == 'CurrentURI':
                    actionStateVar = argVals['relatedStateVariable']
                    stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]			                    
                    sendArgs[argName] = ('http://192.168.2.135:10243/WMPNSSv4/2601510775/1_NC0xNDQ1OA.mp3',stateVar['dataType'])                   

        if action == 'play':
            self.logger.debug('Performing action PLAY') 
            for argName,argVals in actionArgs.iteritems():
                print argName
                if argName == 'InstanceID':
                    actionStateVar = argVals['relatedStateVariable']
                    stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]			                    
                    sendArgs[argName] = ('self.mediaRendererIndex',stateVar['dataType'])	    
                if argName == 'Speed':
                    actionStateVar = argVals['relatedStateVariable']
                    stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]			                    
                    sendArgs[argName] = (1,stateVar['dataType'])	    

		soapResponse = self.conn.sendSOAP(hostInfo['name'],fullServiceName,controlURL,actionName,sendArgs)
		if soapResponse != False:
			#It's easier to just parse this ourselves...
			for (tag,dataType) in retTags:
				tagValue = self.conn.extractSingleTag(soapResponse,tag)
				if dataType == 'bin.base64' and tagValue != None:
					tagValue = base64.decodestring(tagValue)            
                    
                    
if __name__ == '__main__':

    digitaleKassette = DigitaleKassette()
    digitaleKassette.logger.debug('digitaleKassette is running...')   

    while True:
        digitaleKassette.logger.debug('Main loop...')   
        time.sleep(1)

			
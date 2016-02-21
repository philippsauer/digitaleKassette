import sys
import csv
import config
import threading
import time
import logging
from miranda import upnp, msearch, host

class UPNPController:

    def __init__(self):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.deviceSearchTimeout = config.general['deviceSearchTimeout'] 
        self.mediaRendererIndex = ''
        self.myDevices = []
         
        # Set up logging       
        self.logger = logging.getLogger('UPNPController')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
        
        # Set up UPnP connection
        self.conn = upnp(False,False,None,None)
        self.conn.UNIQ = True
        self.conn.VERBOSE = True
        self.conn.TIMEOUT = self.deviceSearchTimeout 

    
    def discoverDevices(self):   
        self.logger.debug('Searching for devices...')
        msearch(0, 0, self.conn)
        
    def getDeviceInformation(self):       
        self.logger.debug('Getting device information...')
        for index in self.conn.ENUM_HOSTS:
            hostInfo = self.conn.ENUM_HOSTS[index]
            if hostInfo['dataComplete'] == False:
                # skip external devices
                if "192.168." in hostInfo['xmlFile']:   
                    xmlHeaders, xmlData = self.conn.getXML(hostInfo['xmlFile'])
                    self.conn.getHostInfo(xmlData,xmlHeaders,index)
    
    def getDeviceByModelName(self, deviceType, modelName):  
        # deviceType = {MediaRenderer, MediaServer, etc..}
        # modelName ~ friendly name
        self.logger.debug('Searching for device...'+modelName)
        for index in self.conn.ENUM_HOSTS:      
            hostInfo = self.conn.ENUM_HOSTS[index]
            if hostInfo['dataComplete'] == True:
                try:
                    if self.conn.ENUM_HOSTS[index]['deviceList'][deviceType]['modelName'] == modelName:
                        self.logger.debug('Found device:'+modelName+' with index '+str(index))  
                        self.mediaRendererIndex = str(index)                      
                except KeyError:
                    pass
                    
    def getDevicesByDeviceType(self, uPnPdeviceType, deviceType): 
        # deviceType = {MediaRenderer, MediaServer, etc..}
        # uPnPdeviceType = {urn:schemas-upnp-org:device:MediaServer:1, ...}
        self.logger.debug('Searching for device...'+uPnPdeviceType)
        for index in self.conn.ENUM_HOSTS:  
            hostInfo = self.conn.ENUM_HOSTS[index]
            if hostInfo['dataComplete'] == True:
                try:
                    if hostInfo['deviceList'][deviceType]['fullName'] == uPnPdeviceType:
                        self.logger.debug('Found device:'+uPnPdeviceType+' with index '+str(index))  
                        self.myDevices.append(str([index, hostInfo['deviceList'][deviceType]['modelName']]))
                except KeyError:
                    pass

    def getAudioData(self, index): 
        self.logger.debug('Browsing audio data @hostIndex '+index) 
        data = self.sendAction(['browse'], 'MediaServer', 'ContentDirectory', 'Browse', index)
        return data           
    
    def sendAction(self, action, deviceName, serviceName, actionName, hostIndex):
    
        index = False
        actionArgs = False
        sendArgs = {}
        retTags = []
        controlURL = False
        fullServiceName = False
        
        try:
            hostInfo = self.conn.ENUM_HOSTS[int(hostIndex)]
        except:
            self.logger.debug('Indexing failed. hostIndex: '+str(hostIndex)) 
            
            return False

        try:
            controlURL = hostInfo['proto'] + hostInfo['name']
            controlURL2 = hostInfo['deviceList'][deviceName]['services'][serviceName]['controlURL']
            if not controlURL.endswith('/') and not controlURL2.startswith('/'):
                controlURL += '/'
            controlURL += controlURL2
        except Exception,e:
            self.logger.debug('Getting service control URL failed') 
            print "Getting service control URL failed"
            return False

        #Get action info
        try:
            actionArgs = hostInfo['deviceList'][deviceName]['services'][serviceName]['actions'][actionName]['arguments']
            fullServiceName = hostInfo['deviceList'][deviceName]['services'][serviceName]['fullName']
        except Exception,e:
            self.logger.debug('Getting action info failed') 
            print "Getting action info failed"
            return False

        if action[0] == 'set':
            for argName,argVals in actionArgs.iteritems():
                actionStateVar = argVals['relatedStateVariable']
                stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar] 
                if argName == 'InstanceID':                               
                    sendArgs[argName] = (hostIndex,stateVar['dataType'])
                elif argName == 'CurrentURIMetaData':                               
                    sendArgs[argName] = ('',stateVar['dataType'])
                elif argName == 'CurrentURI':                              
                    sendArgs[argName] = (action[1],stateVar['dataType'])   
                else:
                    retTags.append((argName,stateVar['dataType']))                    
        
        elif action[0] == 'play':
            for argName,argVals in actionArgs.iteritems():
               actionStateVar = argVals['relatedStateVariable']
               stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]   
               if argName == 'InstanceID':                             
                    sendArgs[argName] = (hostIndex,stateVar['dataType'])        
               elif argName == 'Speed':                               
                    sendArgs[argName] = (1,stateVar['dataType'])
               else:
                    retTags.append((argName,stateVar['dataType']))  
        
        elif action[0] == 'stop':
            for argName,argVals in actionArgs.iteritems():
               actionStateVar = argVals['relatedStateVariable']
               stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]   
               if argName == 'InstanceID':                             
                    sendArgs[argName] = (hostIndex,stateVar['dataType'])        
               else:
                    retTags.append((argName,stateVar['dataType']))   

        elif action[0] == 'pause':
            for argName,argVals in actionArgs.iteritems():
               actionStateVar = argVals['relatedStateVariable']
               stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]   
               if argName == 'InstanceID':                             
                    sendArgs[argName] = (hostIndex,stateVar['dataType'])        
               else:
                    retTags.append((argName,stateVar['dataType']))                                       
        
        elif action[0] == 'browse':
            for argName,argVals in actionArgs.iteritems():
                actionStateVar = argVals['relatedStateVariable']
                stateVar = hostInfo['deviceList'][deviceName]['services'][serviceName]['serviceStateVariables'][actionStateVar]
                if argName == 'ObjectID':                                                  
                    sendArgs[argName] = ('/external/audio/media',stateVar['dataType'])        
                elif argName == 'BrowseFlag':                                                   
                    sendArgs[argName] = ('BrowseDirectChildren',stateVar['dataType'])
                elif argName == 'Filter':      
                    sendArgs[argName] = ('*',stateVar['dataType'])        
                elif argName == 'RequestedCount':                            
                    sendArgs[argName] = (10,stateVar['dataType'])
                elif argName == 'StartingIndex':                                
                    sendArgs[argName] = (0,stateVar['dataType'])  
                elif argName == 'SortCriteria':                                
                    sendArgs[argName] = ('',stateVar['dataType'])  
                else:
                    retTags.append((argName,stateVar['dataType']))
        
        # send and parse SOAP
        soapResponse = self.conn.sendSOAP(hostInfo['name'],fullServiceName,controlURL,actionName,sendArgs)
        if soapResponse != False:
            for (tag,dataType) in retTags:
                tagValue = self.conn.extractSingleTag(soapResponse,tag)
                if dataType == 'bin.base64' and tagValue != None:
                    tagValue = base64.decodestring(tagValue)  
                if tag == 'Result':
                    if  tagValue != None:
                        return unicode(tagValue, 'utf-8')
                    else:
                        return False
                
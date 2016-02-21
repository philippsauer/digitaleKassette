import os
import config
import serial
import logging

from miranda import upnp, msearch, host

class JukeBox():

    def __init__(self, uPNPController, actionData):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.actionDataSource = config.general['actionDataSource']
        self.mediaRendererModelName = config.general['mediaRendererModelName'] 
        self.deviceSearchTimeout = config.general['deviceSearchTimeout'] 
        self.rfidLockIntervall = config.general['rfidLockIntervall']
        self.rfidIsLocked = False

        # Set up logging       
        self.logger = logging.getLogger('JukeBox')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
   
        # Set up reference to actionData
        self.actionData = actionData
        
        # Set up reference to UPnP controller
        self.uPNPController = uPNPController
    
    def runAction(self, action):
    # run action for current RFID card ID
        if not self.rfidIsLocked:
            if action == None:
                self.logger.error( 'action == None')
                os.system('mpg321 audio/error.mp3 &')
            elif action[2] == 'play':
                self.uPNPController.sendAction(['stop'], 'MediaRenderer', 'AVTransport', 'Stop', self.uPNPController.mediaRendererIndex)
                self.uPNPController.sendAction(['set',action[1]], 'MediaRenderer', 'AVTransport', 'SetAVTransportURI', self.uPNPController.mediaRendererIndex)
                self.uPNPController.sendAction(['play'], 'MediaRenderer', 'AVTransport', 'Play', self.uPNPController.mediaRendererIndex)          
            elif action[2] == 'pause':
                self.uPNPController.sendAction(['pause'], 'MediaRenderer', 'AVTransport', 'Pause', self.uPNPController.mediaRendererIndex)
            elif action[2] == 'next':
                self.logger.debug( 'action == next')
            elif action[2] == 'stop':
                self.uPNPController.sendAction(['stop'], 'MediaRenderer', 'AVTransport', 'Stop', self.uPNPController.mediaRendererIndex)
            else:
                self.logger.error( 'undefined action: ' +str(action))
                os.system('mpg321 audio/error.mp3 &')
      
    #if __name__ == '__main__':   
    def play(self, id):
        action = self.actionData.getActionData(id)
        self.runAction(action)            

			
import config
import time
import serial
import logging
import threading
import os

class RFIDReader(threading.Thread):

    def __init__(self, runForever):
              
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.status = None
        self.lastID = ''
         
        # Set up logging       
        self.logger = logging.getLogger('RFIDReader')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
   
        # Set up dedicated thread for listening to the serial interface
        self.RFIDthread = threading.Thread(target=self.read, args=(runForever,))
        self.RFIDthread.daemon = True
        self.RFIDthread.start()

   
    def __enter__(self):
        if self.status != 'open':
            self.status = 'open'
        return self 

    def close(self):
        if self.status != 'closed':
            self.status = 'closed'
    
    def __exit__(self, *err):
        self.close()
        
    # run RFID scanner 
    def read(self, runForever):
        sleepTime = config.rfid['sleepTime']
        startFlag = '\x02'
        endFlag = '\x03' 
        run = True
        
        uart = serial.Serial('/dev/ttyAMA0', 9600)
        uart.close()
        uart.open() 
        
        while run:
            id = ''
            char = uart.read()
            if char == startFlag:
                for counter in range(13):
                    char = uart.read()
                    id = id + str(char)
                id = id.replace(endFlag, '')              
                self.logger.debug('RFIDReader: '+id) 
                if  id != self.lastID :  
                    self.lastID = id
                    os.system('mpg321 audio/beep.mp3 &')
                    
                    #skip scanning 
                    if runForever == False:
                        run = False             
            
            #time.sleep(sleepTime)   
            

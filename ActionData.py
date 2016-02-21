import config
import logging

class ActionData():

    def __init__(self):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.actionDataSource = config.general['actionDataSource']

        # Set up logging       
        self.logger = logging.getLogger('Database')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
      
    def getActionData(self, id):
    # Get designated action for a given RFID-Chip-ID  
        try:
            f = open(self.actionDataSource,"r")
            lines = f.readlines()
            f.close()          
            for line in lines:
                line = line.strip("\n") 
                line = line.split(",")                
                if line[0] == id:
                    return line
                    
        except ValueError:
            self.logger.error( 'Could not read file: '+self.actionDataSource)
        finally:
            f.close()
    
    def setActionData(self, id, uri, action):
        try:
            #read data
            f = open(self.actionDataSource,"r")
            lines = f.readlines()
            f.close()
            
            #create new dataset
            newData = id+','+str(uri)+','+action+'\n'
            
            #write new data back to file
            f = open(self.actionDataSource,"w")
            for line in lines:
                line = line.split(",")
                if line[0] != id:
                    line = ','.join(line)
                    f.write(line)
            f.write(newData)
            f.close()
            
        except ValueError:
            self.logger.error( 'Could not read file: '+self.actionDataSource)
        finally:
            f.close()       
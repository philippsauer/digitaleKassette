import config
import threading
import time
import commands
import logging
import sys
import os

class Wifi(threading.Thread):

    def __init__(self):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']
        self.wpa_conf_file = config.wifi['wpa_conf_file']
        self.interface_file = config.wifi['interface_file']
        self.formatter = config.general['logging_formatter']
        self.hasNewConnection = False
        
        # Set up logging       
        self.logger = logging.getLogger('Wifi')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
        
    def startAccessPoint(self):  
        
        # /etc/network/interfaces
        interface = '''
        auto lo
        iface lo inet loopback
        iface eth0 inet dhcp         
        allow-hotplug wlan0
        iface wlan0 inet static
        address 192.168.10.1
        netmask 255.255.255.0'''
                        
        self.dataToFile(interface, self.interface_file)

        self.logger.debug('Starting wlan0') 
        time.sleep(5)
	os.system('sudo ifdown wlan0')                    
        os.system('sudo ifup wlan0')
	os.system('sudo ifdown wlan0')
        os.system('sudo ifup wlan0')
	time.sleep(1)
	os.system('sudo service isc-dhcp-server start')
        time.sleep(1)
        os.system('sudo hostapd /etc/hostapd/hostapd.conf &')        

    def joinWifi(self, ssid, psk, delay):     

        # wait for webapp to deliver response
        time.sleep(delay)
        
        if ssid and psk:
            self.logger.debug('Shutting down wlan0') 
            os.system('sudo ifdown wlan0')
            
            # /etc/wpa_supplicant/wpa_supplicant.conf
            wpa_conf = '''
            ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
            update_config=1
            network={
                ssid="'''+ssid+'''"
                psk="'''+psk+'''"
            }'''                       
             
            self.dataToFile(wpa_conf, self.wpa_conf_file)
             
            # /etc/network/interfaces
            interface = '''
            auto lo
            iface lo inet loopback
            iface eth0 inet dhcp         
            allow-hotplug wlan0
            iface wlan0 inet manual
            wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf'''
            
            self.dataToFile(interface, self.interface_file)
            self.logger.debug('Starting wlan0') 
            os.system('sudo ifup wlan0')  
            self.hasNewConnection = True           

    def isConnected(self):

        connection = commands.getstatusoutput('iwgetid -r')
        
        if connection[1] == "digitalekassette":
            self.logger.debug('Connected to AP: '+str(connection)) 
            return False
	elif connection[1]:
            self.logger.debug('Connected to foreign wifi')
	    return True
        else:
            self.logger.debug('wlan0 is not connected: '+str(connection)) 
            return False
        
    def dataToFile(self, data, file):
        
        f = open(file,"w")
        for line in data:
            f.write(line)
        f.close()
    







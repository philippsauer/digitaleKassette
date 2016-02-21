import time
import config
import logging
import validators
import threading

from xml.sax.saxutils import unescape
from xml.dom.minidom import parse, parseString
from flask import Flask, url_for, render_template, request, jsonify
from flask.ext.classy import FlaskView, route

app = Flask(__name__)

class WebApp(FlaskView, threading.Thread):

    def __init__(self, uPNPController, actionData, dk, wifi, init):
        
        # Load configuration values & initialize class variables
        self.disableLogging = config.general['disableLogging']

        # Set up logging       
        self.logger = logging.getLogger('WebApp')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.disabled = self.disableLogging
        
        # run WebApp thread
        self.webAppThread = threading.Thread(target=self.runApp, args=())
        self.webAppThread.daemon = True
        self.webAppThread.start()
        
        # put object references into Flask config
        app.config['UPNPCONTROLLER'] = uPNPController
        app.config['DIGITALEKASSETTE'] = dk
        app.config['ACTIONDATA'] = actionData
        app.config['WIFI'] = wifi
        app.config['INIT'] = init

    def runApp(self):
        host =  config.app['host']
        port =  config.app['port']
        app.debug = config.app['debug']  
        app.run(host=host, port=port)

        
@app.route("/")
@app.route("/home")
def main():
    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')
    output = output+ '<div id="content">'
    output = output+'<h1>Willkommen</h1>'
    
    init = app.config['INIT']
    if init:
        output = output+'<p class="error">No Wifi Connection found. Please configure Wifi</p>'
    else:
        output = output+'<p style="color:green">Digitale Kassette is bereit.</p>'  
        
    output = output+'</div></body></html>'
    return output
    
@app.route("/rescan")
def rescan():
    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')
    output = output+ '<div id="content">'
    
    init = app.config['INIT']
    if init:
        output = output+'<p class="error">No Wifi Connection found. Please configure Wifi</p>'
    else:
        app.config['UPNPCONTROLLER'].discoverDevices()
        app.config['UPNPCONTROLLER'].getDeviceInformation()
        app.config['UPNPCONTROLLER'].getDeviceByModelName('MediaRenderer', 'gmediarender')
        app.config['UPNPCONTROLLER'].getDevicesByDeviceType('urn:schemas-upnp-org:device:MediaServer:1', 'MediaServer')
        output = output+'<p style="color:green">Rescan successful.</p>'  
        
    output = output+'</div></body></html>'
    return output

    
@app.route('/music')
def music():    
    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')
    output = output+'<div id="content">'  
    output = output+"<h1>Datentraeger-Konfiguration</h1>"
        
    try:
        init = app.config['INIT']
    except ValueError:       
        output = output+'<p class="error">Failed getting initialization state.</p>'
        output = output+'</div></body></html>'
        return output
    
    if init:
        output = output+'<p class="error">Please configure Wifi first</p>'
        output = output+'</div></body></html>'
        return output
    
    output = output+"<h2>Step 1: Choose MediaServer</h2>"
    
    try:
        servers = app.config['UPNPCONTROLLER'].myDevices
    except ValueError:       
        output = output+'<p class="error">No MediaServers available in your local network.</p>'
        output = output+'</div></body></html>'
        return output

    if len(servers) < 1:
        output = output+'<p class="error">No MediaServers available in your local network. Are you connected?</p>'
        output = output+'<p><a href="rescan">Rescan</a></p>'
        output = output+'</div></body></html>'       
        return output

    else:
        output = output+'<form action="music2">'
        output = output+'<select name="serverID" style="width: 400px" size="5">'
        
        for device in servers:
            id = device.strip("[]")
            id = id.split(",")           
            output = output+'<option value="'
            output = output+str(id[0])
            output = output+'">'
            output = output+device
            output = output+'</option>'
            
        output = output+'</select>'
        output = output+'<br><input type="submit" style="width: 400px">'
        output = output+'</form>'
        output = output+'<p><a href="rescan">Rescan</a></p>'
        output = output+'</div></body></html>'
        return output
           
    output = output+'</div></body></html>'
    return output
    

@app.route('/music2')
def music2():

    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')
    output = output+'<div id="content">'    
    output = output+"<h1>Datentraeger-Konfiguration</h1>"
    
    init = app.config['INIT']
    if init:
        output = output+'<p class="error">Please configure Wifi first</p>'
        output = output+'</div></body></html>'
        return output
    
    output = output+"<h2>Step 2: Choose Audio-Item</h2>"    
    
    serverID = request.args.get('serverID')
    
    if isInvalidServerID(serverID ):
        output = output+'<p class="error">Invalid ServerID. Please return to the previous page.</p>'
        output = output+'</div></body></html>'
        return output
    else:       
        xmlString = app.config['UPNPCONTROLLER'].getAudioData(serverID)
        if xmlString:
        
            output = output+'<form action="music3">'
            output = output+'<select name="trackURL" style="width: 400px" size="10">'            
            
            # prepare for minidom parser
            xmlString = unescape(xmlString)
            xmlString = xmlString.encode('utf-8')
            
            dom = parseString(xmlString)
            for node in dom.getElementsByTagName('item'):
                title = ''
                artist = ''
                url = ''
                
                # get metadata for each item
                for child in node.childNodes:
                    if child.nodeName == ('dc:title'):
                        title = child.firstChild.nodeValue
                    elif child.nodeName == ('upnp:artist'):
                        artist = child.firstChild.nodeValue
                    elif child.nodeName == ('res'):
                        url = child.firstChild.nodeValue
                
                # print option value
                output = output+'<option value="'  
                output = output+url
                output = output+'">'+artist+' - '+title
                output = output+'</option>'
                
            output = output+'</select>'          
            output = output+"<h2>Step 3: Place RFID-Card on scanner</h2>"         
            output = output+'<br><input type="submit" value="Speichern" style="width:400px; height:50px" >'
            output = output+'</form>'
            output = output+'</div></body></html>'
            return output  
            
        else:
            output = output+'<p class="error">No data to received. Please return to the previous page.</p>'
            output = output+'</div></body></html>'
            return output  

            
@app.route('/music3')
def music3():
    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')
    output = output+ '<div id="content">'
    output = output+"<h1>Datentraeger-Konfiguration</h1>"
    
    init = app.config['INIT']
    if init:
        output = output+'<p class="error">Please configure Wifi first</p>'
        output = output+'</div></body></html>'
        return output
    
    

    # get url
    trackURL = request.args.get('trackURL')   
    if not validators.url(trackURL):
        output = output+'<p class="error">URL not valid.</p>'
        output = output+'</div></body></html>'
        return output  
        
    # get rfid id
    try:
        dk = app.config['DIGITALEKASSETTE']
    except ValueError:       
        output = output+'<p class="error">Could not reference DigitaleKassette. Please reboot</p>'
        output = output+'</div></body></html>'
        return output
    
    # hide scanning from JukeBox
    dk.lockRFID()
    time.sleep(6)
        
    rfidCard = dk.lastRFIDCard
    if rfidCard == "":
        output = output+'<p class="error">No RFID-Card detected.</p>'
        output = output+'</div></body></html>'
        return output    

    try:
        actionData = app.config['ACTIONDATA']
        actionData.setActionData (str(rfidCard),str(trackURL),'play') 
    except ValueError:       
        output = output+'<p class="error">Failed by referencing ActionData.</p>'
        output = output+'</div></body></html>'
        return output    

    output = output+'<h1 style="color:green">Erfolgreich</h1>'        
    output = output+'</div></body></html>'
    return output  
 
 
@app.route('/wifi')
def wifi():
    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')  
    output = output+ '<div id="content">'
    output = output+"<h1>Wifi-Konfiguration</h1>"    
    output = output+'<form action="wifi2">'
    output = output+ 'SSID*:<br>'
    output = output+ '<input type="text" name="ssid">'
    output = output+ '<br><br>'
    output = output+ 'Passphrase*:<br>'
    output = output+ '<input type="text" name="passw">'   
    output = output+'<br><input type="submit" value="Absenden">'
    output = output+'</form>'
    output = output+'</div></body></html>'
    return output  
  
@app.route('/wifi2')
def wifi2():
    output = ""
    output = output+render_template('head.html')
    output = output+render_template('nav.html')  
    output = output+ '<div id="content">'
    output = output+"<h1>Wifi-Konfiguration</h1>"  
    
    ssid = request.args.get('ssid')
    passw = request.args.get('passw')
    
    try:
        wifi = app.config['WIFI']
    except ValueError:       
        output = output+'<p class="error">Failed to connect to wifi. Please retry.</p>'
        output = output+'</div></body></html>'
        return output
        
    if ssid and passw: 
        wifiThread = threading.Thread(target=wifi.joinWifi, args=(ssid, passw, 4,))
        wifiThread.daemon = True
        wifiThread.start()
        output = output+"<p>Reconnecting to new wifi... Please close this page.</p>"
        app.config['INIT'] = False
    else:
        output = output+"<p>Connecting to new wifi failed. SSID & Passphrase correct?</p>"
          
    output = output+'</div></body></html>'
    return output 

def isInvalidServerID(serverID):
    if serverID is None:
        return True
    elif serverID.isnumeric():
        return False
    else:
        return True
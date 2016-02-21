# Digitale Kassette

## Ziel & Aufgabenstellung

Ziel war die Entwicklung eines Abspielgerätes mit der Haptik früherer Musikträger, da "Touch"-basierte Interaktion nicht immer für jüngere oder ältere Personen geeignet ist. Hierzu wurde ein neuer Musikträger in Form von RFID-Karten geschaffen. Zusätzlich musste eine Administrations-Oberfläche bereitgestellt werden, welche die Zuordnung des RFID-Chips mit der jeweiligen Ressource ermöglicht. 

## Überblick

Die Software gliedert sich in zwei Hauptbestandteile, dem Administrationsinterface mit Webserver, sowie einem Teil namens "JukeBox", welcher das Abspielen der Musik übernimmt

### 1 - Administrations-Interface



### 2 - Digitale Kassette

## Zusätzlich eingesetzte Software

* MediaRenderer: gmediarender http://gmrender.nongnu.org/
* Python UPnP Framework: miranda-upnp https://github.com/0x90/miranda-upnp
* Python Webserver & Webapp Framework: flask http://flask.pocoo.org/

## Weitere Baustellen

Aktuell können Musikstücke in Form von *.mp3 Dateien abgespielt und einer RFID-Card hinterlegt werden. Eine Sinnvolle Erweiterung wäre der Support von ganzen Playlists. Daran anknüpfend müssen weitere RFID-Action-Typen (Next/Previous) eingeführt werden.

Die Lautstärke muss aktuell über einen externen ControlPoint angepasst werden, welcher auf den internen MediaPlayer (gmediarenderer) zugreift, hierzu eignet sich beispielsweise BubbleUPNP. Für die Einführung der Lautstärkesteuerung mittels RFID-Cards müssen die beiden RFID-Action Typen 'Volume+' und 'Volume-' eingeführt werden.





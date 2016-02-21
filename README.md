# Digitale Kassette

## Ziel & Aufgabenstellung

Ziel war die Entwicklung eines Abspielgerätes mit der Haptik früherer Musikträger, da "Touch"-basierte Interaktion nicht immer für jüngere oder ältere Personen geeignet ist. Hierzu wurde ein neuer Musikträger in Form von RFID-Karten geschaffen. Zusätzlich musste eine Administrations-Oberfläche bereitgestellt werden, welche die Zuordnung des RFID-Chips mit der jeweiligen Ressource ermöglicht. 

## Bestandteile

Die Software gliedert sich in zwei Hauptbestandteile, dem Administrationsinterface mit Webserver, sowie einem Teil namens `Jukebox` welcher das Abspielen der Musik übernimmt. Herzstück stellt die zentrale Conroller-Klasse `DigitaleKassette` dar. Diese stellt die zentralen Ressourcen und Objekte für andere Programmbestandteile bereit und initiiert diese. 

Hauptfunktionen des Programms wurden in Klassen ausgelagert welche zentral instanziiert werden. Dazu gehören:
* `ActionData`: Diese Klasse übernimmt lesende und schreibende Operationen auf die Datei `actionData.csv`, welche Action-Typen (Play, Stop), sowie Webserver-Ressource mit der jeweiligen RFID-Card verknüpft.
* `RFID-Reader`: Diese Klasse ist die Verbindung zum RFID-Lesegerät an der seriellen Schnittstelle
* `UPNP-Controller`: Die Digitale Kassette verwendet das Tool 'miranda-upnp' zur UPnP Kommunikation. Dieses wird initial über die Kommandozeile genutzt. `UPNP-Controller.py` verwendet und erweitert einige Methoden aus 'miranda-upnp' und der darin enthaltenen Klasse 'upnp' um die UPnP-Steuerung programmintern und ohne Kommandozeilen-Interaktion zu ermöglichen. 
* `Wifi`


Von der Conroller-Klasse `DigitaleKassette` wird zuerst die Erkennung der UPnP Geräte getriggert. 

### Administrations-Interface

Das Administrations-Interface stellt für den Nutzer 2 zentrale Funktionen bereit:
* Das Einrichten einer WLAN-Verbindung
* Das Hinzufügen von Musikträgern



Zum Einsatz kam das in Python geschriebene Web-Application-Framework Flask.

### JukeBox



### Eingesetzte Software

* MediaRenderer: gmediarender http://gmrender.nongnu.org/
* Python UPnP Framework: miranda-upnp https://github.com/0x90/miranda-upnp
* Python Webserver & Webapp Framework: flask http://flask.pocoo.org/

## Weitere Baustellen

Aktuell können Musikstücke in Form von *.mp3 Dateien abgespielt und einer RFID-Card hinterlegt werden. Eine Sinnvolle Erweiterung wäre der Support von ganzen Playlists. Daran anknüpfend müssen weitere RFID-Action-Typen (Next/Previous) eingeführt werden.

Die Lautstärke muss aktuell über einen externen ControlPoint angepasst werden, welcher auf den internen MediaPlayer (gmediarenderer) zugreift, hierzu eignet sich beispielsweise BubbleUPNP. Für die Einführung der Lautstärkesteuerung mittels RFID-Cards müssen die beiden RFID-Action Typen 'Volume+' und 'Volume-' eingeführt werden.





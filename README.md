# Digitale Kassette

## Ziel & Aufgabenstellung

Ziel war die Entwicklung eines Abspielgerätes mit der Haptik früherer Musikträger, da "Touch"-basierte Interaktion nicht immer für jüngere oder ältere Personen geeignet ist. Hierzu wurde ein neuer Musikträger in Form von RFID-Karten geschaffen. Zusätzlich musste eine Administrations-Oberfläche bereitgestellt werden, welche die Zuordnung des RFID-Chips mit der jeweiligen Ressource ermöglicht. 

## Überblick

Herzstück stellt die zentrale Conroller-Klasse `DigitaleKassette` dar. Diese stellt die zentralen Ressourcen und Objekte für andere Programmbestandteile bereit und instanziiert diese. Die Hauptbestandteile sind das Administrationsinterface mit Webserver (`WebApp.py`), sowie ein Teil namens Jukebox (`JukeBox.py`) welcher die Steuerung zum Abspielen der Musik übernimmt. 

### Administrations-Interface

Das Administrations-Interface stellt für den Nutzer zwei zentrale Funktionen bereit:
* Das Einrichten einer WLAN-Verbindung
* Das Hinzufügen von Musikträgern

Zum Einsatz kam das in Python geschriebene Web-Application-Framework Flask (siehe `Webapp.py`). Die einzelnen auszuliefernden HTML-Dokumente werden mit Hilfe sog. App-Routes (z.B. `@app.route("/home")`) erstellt und definiert.

### JukeBox

Ermittelt die auszuführende Aktion für die jeweilige RFID-Karte und steuert dessen Ausführung. (z.B. Abspielen einer bestimmten Ressource, oder Stop des aktuellen Titels) 

### Weitere Programmbestandteile

Weitere wichtige Funktionen des Programms wurden in eigene Klassen ausgelagert welche durch `DigitaleKassette.py` zentral instanziiert werden. Dazu gehören:
* `ActionData`: Diese Klasse übernimmt lesende und schreibende Operationen auf die Datei `actionData.csv`, welche Action-Typen (Play, Stop), sowie Webserver-Ressource mit der jeweiligen RFID-Card verknüpft.
* `RFID-Reader`: Diese Klasse ist die Verbindung zum RFID-Lesegerät an der seriellen Schnittstelle
* `UPNP-Controller`: Die Digitale Kassette verwendet das Tool 'miranda-upnp' zur UPnP Kommunikation. Dieses wird initial über die Kommandozeile genutzt. `UPNP-Controller.py` verwendet und erweitert einige Methoden aus 'miranda-upnp' und der darin enthaltenen Klasse 'upnp' um die UPnP-Steuerung programmintern und ohne Kommandozeilen-Interaktion zu ermöglichen. 
* `Wifi`: Diese Klasse kann den Betriebsmodus zwischen 'Accesspoint' und 'einfacher WLAN-Teilnehmer' steuern. Hierzu müssen relevante Konfigurations-Dateien im System überschrieben, sowie der Wlan-Adapter hoch- und runtergefahren werden können.

### Eingesetzte Software

* MediaRenderer: gmediarender http://gmrender.nongnu.org/
* Python UPnP Framework: miranda-upnp https://github.com/0x90/miranda-upnp
* Python Webserver & Webapp Framework: flask http://flask.pocoo.org/

### Sonstige Dateien

* `audio/` - Enthält Systemsounds (error.mp3 im Fehlerfall, beep.mp3 im Erfolgsfall)
* `static/` - Statische Ressourcen (Bilder, Styles) der Flask-WebApp
* `templates/` - HTML-Templates (HTML-Header und Navigationselemente) der Flask-WebApp
* `actionData.csv` - Datentabelle, welche Action-Typen (Play, Stop) und Webserver-Ressource mit der jeweiligen RFID-Card verknüpft
* `config.py` - Enthält zentrale Konfigurations-Einstellungen in Form von Python-Dictionaries

### Autostart

Zum Systemstart wird ein Cronjob ausgeführt. Dieser initiiert den Start der Digitalen Kassette. Hierzu wurde mittels `crontab -e`folgender Cronjob für den Nutzer Pi eingerichtet: 

`@reboot cd /home/pi/kassette/ && sudo /usr/bin/python DigitaleKassette.py > /home/pi/kassette/out.log 2>&1`

Sofern das Logging in der Datei `config.py` eingeschaltet ist, werden sämtliche Debug-Ausgaben in die Datei `out.log` geschrieben

## Weitere Baustellen

Aktuell können Musikstücke in Form von *.mp3 Dateien abgespielt und einer RFID-Card hinterlegt werden. Eine sinnvolle Erweiterung wäre der Support von ganzen Playlists. Daran anknüpfend müssen weitere RFID-Action-Typen (Next/Previous) mit zugehörigen UPnP-Aktionen (`UPNP-Controller.py`) eingeführt werden.

Die Lautstärke muss aktuell über einen externen ControlPoint angepasst werden, welcher auf den internen MediaPlayer (gmediarenderer) zugreift, hierzu eignet sich beispielsweise BubbleUPNP. Für die Einführung der Lautstärkesteuerung mittels RFID-Cards müssen die beiden RFID-Action Typen 'Volume+' und 'Volume-' eingeführt werden.

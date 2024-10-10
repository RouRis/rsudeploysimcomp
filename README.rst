================
RSUDeploySimComp
================

.. image:: https://github.com/RouRis/rsudeploysimcomp/actions/workflows/testing.yml/badge.svg
   :target: https://github.com/RouRis/rsudeploysimcomp/actions/workflows/testing.yml


.. image:: https://img.shields.io/pypi/v/rsudeploysimcomp.svg
        :target: https://pypi.python.org/pypi/rsudeploysimcomp


Simulation-Based Comparative Analysis of Roadside Unit Deployment Strategies

* Free software: 3-clause BSD license
* Documentation: (COMING SOON!) https://RouRis.github.io/rsudeploysimcomp.

Features
--------

# Projektname

Dies ist eine kurze Beschreibung des Projekts und seiner Funktionalität. Hier kannst du angeben, was der Code macht und welchen Zweck er erfüllt.

## Voraussetzungen

- **Python**: Stelle sicher, dass Python installiert ist.
- **Weitere Abhängigkeiten**: Installiere die benötigten Pakete, falls vorhanden (z. B. `pip install -r requirements.txt`).

## Installation

1. **Code herunterladen**  
   Lade den gesamten Code aus dem Repository herunter. Entweder klone das Repository oder lade es als ZIP-Datei herunter und entpacke sie.

   ```bash
   git clone <URL-des-Repositories>

## Konfigurationsdatei anpassen

Im Hauptverzeichnis des Projekts befindet sich eine Konfigurationsdatei (z. B. `config.json` oder `.yaml`), die wichtige Parameter enthält, die an die spezifischen Bedürfnisse des Nutzers angepasst werden sollten. 

### Schritte zur Anpassung der Konfigurationsdatei:

1. **Öffne die Konfigurationsdatei**  
   Die Datei kann mit einem Texteditor geöffnet und bearbeitet werden.

2. **Parameter anpassen**  
   Ändere die Werte in der Konfigurationsdatei entsprechend deiner Anforderungen. Zu den möglichen Parametern gehören:
   - Pfade zu den benötigten Komponenten (z. B. Disolv, Prep-Disolv)
   - Konfigurationswerte wie Anzahl der Iterationen, Speicherort für Ausgabedateien, usw.
   
3. **Speichern und Schließen**  
   Sobald alle Änderungen vorgenommen wurden, speichere die Datei und schließe den Editor.

### Hinweis:
Die Pfade in der Konfigurationsdatei sollten den Verzeichnissen entsprechen, in denen die zusätzlichen Komponenten abgelegt wurden. Dadurch wird sichergestellt, dass der Code die benötigten Ressourcen korrekt findet und verwendet.


## Benötigte Code-Komponenten herunterladen

Um das Projekt vollständig nutzen zu können, sind zusätzliche Code-Komponenten erforderlich. Lade diese Bausteine herunter und lege sie in den entsprechenden Verzeichnissen ab, wie es in der Konfigurationsdatei angegeben ist.

### Benötigte Komponenten:

1. **Disolv**  
   Lade die Disolv-Komponente herunter und platziere sie im dafür vorgesehenen Verzeichnis.

2. **Prep-Disolv**  
   Lade auch die Prep-Disolv-Komponente herunter und speichere sie im entsprechenden Verzeichnis.

### Hinweise:

- Stelle sicher, dass die Verzeichnisse, in denen die Komponenten gespeichert werden, mit den Pfaden in der Konfigurationsdatei übereinstimmen.
- Diese Komponenten sind für die vollständige Funktionalität des Projekts erforderlich, da sie spezifische Datenvorbereitungs- und Verarbeitungsaufgaben übernehmen.

Sobald die Komponenten heruntergeladen und an den richtigen Stellen abgelegt wurden, ist das Projekt bereit für die Ausführung.

## Verzeichnisstruktur

Um sicherzustellen, dass der Code korrekt ausgeführt werden kann, ist die folgende Verzeichnisstruktur erforderlich. Diese Struktur hilft, alle Ressourcen an den richtigen Orten abzulegen.

```plaintext
/home/
   Projects/
      Python/
         prep-disolv/
         rsudeploysimcomp/
      Rust/
         disolv/
    
   Workspace/
       configs/
       input/
       output/
       raw/




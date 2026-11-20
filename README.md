## CASHPOOR BROKER

### Abstract und Zusammenfassung:

Die eigenen Finanzen sind ein wichtiges Thema, Anlagestrategien werden von Kleinanleger:innen aber oft nicht ausreichend erprobt und getestet. Privatpersonen fehlt der Bezug zur Aktienkursentwicklung und genau hier setzt der Cashpoor Broker an. Durch die Website „CASHPOOR“ wird dem:der Kleinanleger:in ein gamifiziertes Erleben beim Investieren in Finanzprodukte ermöglicht, indem die Webseite durch API-Schnittstellen echte Kursentwicklungen sichtbar macht und ein Depot mit Spielgeld bereithält. Beim Cashpoor Broker sind keine echten Transaktionen möglich und auch keine Ein- oder Auszahlungen in Echtgeld, es wird lediglich mit virtuellem Spielgeld in der Währung des US-Dollars gehandelt. Durch die Webseite und vor allem aber auch das Leaderboard (und speziell das Klettern auf der Rangliste dort) werden Anreize zum nachhaltigen Investieren geschaffen, aber auch Badges und Awards als Belohnungen warten auf, sowie die Möglichkeit den Gesamtdepotwert mit denen der Mitstreiter:innen zu vergleichen. Auf Seiten des Backends wird die Anwendung durch das Python-Framework Flask und SQLite und eine API betrieben, auf Seiten des Frontends wird die Darstellung mit HTML, CSS, JavaScript und auch der JavaScript-Alternative Jinja realisiert. Es handelt sich bei diesem Projekt um ein fiktives / theoretisches Studienprojekt im Rahmen des Moduls "Webprogrammierung" im dualen Studium der Informatik.

### Setup der Flask Web Application auf Windows:
<details>
<summary>Hier eine Schritt-für-Schritt-Anleitung für Windows, die für das Setup auszuführen ist.</summary>

Die Befehle sind im Terminal auszuführen:

1. Schritt - Wechsel in den Ordner "challenge" mit cd:
```bash
cd cashpoor
```

2. Schritt - Aufsetzen der Umgebungsvariable "venv" mit:
```bash
py -m venv venv
venv\Scripts\activate
set FLASK_APP=app.py  
```

3. Schritt - Lokale Installation der "requirements.txt" mit pip install:
```bash
python.exe -m pip install --upgrade pip   
py -m pip install -r requirements.txt
```

4. Schritt - Lokaler Start der Webapplikation mit "flask run":
```bash
flask run
```

5. Schritt - Öffnen der angezeigten URL mit der IP-Adresse und dem Port im Browser:
```bash
http://127.0.0.1:5000/
```
</details>

### Setup der Flask Web Application auf macOS:
<details>
<summary>Hier eine Schritt-für-Schritt-Anleitung für macOS, die für das Setup auszuführen ist.</summary>

Die Befehle sind im Terminal auszuführen:

1. Schritt - Wechsel in den Ordner "challenge" mit cd:
```bash
cd cashpoor
```

2. Schritt - Lokale Installation der "requirements.txt" mit pip install:
```bash
python3 -m pip install -r requirements.txt
```

3. Schritt - Aufsetzen der Umgebungsvariable "venv" mit:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Schritt - Lokaler Start der Webapplikation mit "flask run":
```bash
flask run
```

5. Schritt - Öffnen der angezeigten URL mit der IP-Adresse und dem Port im Browser:
```bash
http://127.0.0.1:5000/
```
</details>

### Die Inspiration für dieses Projekt:

Dieses Projekt basiert **abgewandelt** auf der Aufgabe "Finance" der Kursreihe CS50x (Harvard University).

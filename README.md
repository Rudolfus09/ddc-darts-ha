# DDC Darts – Home Assistant Integration

Steuert Philips Hue (und andere) Lichter automatisch bei Live-Darts-Events auf [darts-drinks.de](https://darts-drinks.de).

## Features

- Lichter leuchten in der Farbe des Gewinners bei Match-Sieg
- Reagiert auf Events wie 180er, High Finishes, Checkouts
- Farben werden von der Website geliefert (inkl. individuelle Spielerfarben)
- Konfiguration komplett über die HA-UI — kein YAML nötig

## Installation über HACS

1. HACS öffnen → Integrationen → ⋮ → Benutzerdefinierte Repositories
2. Repository-URL einfügen und Kategorie "Integration" wählen
3. "DDC Darts" installieren
4. Home Assistant neu starten

## Einrichtung

1. Einstellungen → Geräte & Dienste → Integration hinzufügen → "DDC Darts"
2. Verbindungscode eingeben (findest du auf darts-drinks.de → Live-Regeln → Home Assistant)
3. Lichter auswählen, die bei Events reagieren sollen
4. Effektdauer einstellen (Standard: 10 Sekunden)

## Funktionsweise

Die Integration pollt die darts-drinks.de API alle 3 Sekunden. Wenn ein Darts-Event erkannt wird (z.B. Match gewonnen), werden die ausgewählten Lichter für die konfigurierte Dauer in der Spielerfarbe angesteuert und danach automatisch auf den vorherigen Zustand zurückgesetzt.

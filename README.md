## Routes:

`/plan` - Aktueller Vertretungsplan

#### Examle Response:

```json
{
  "Dienstag": [
    {
      "art": "Klausur",
      "fach": "pw6",
      "hinweis": "PoWi",
      "klasse": "Q1Q2",
      "lehrkraft": "",
      "raum": "A111",
      "raum_alt": "",
      "stunde": "1 - 2"
    }
  ],
  "Montag": []
}
```

---

`/classes` - Aktuelle Hausaufgaben

_(Hausaufgaben werden als erledigt gekennzeichnet, wenn diese route aufgerufen wird)_

#### Examle Response:

```json
[
  {
    "class": "Deutsch",
    "content": "Verfassern Sie eine Dialoganalyse zur Szene 20."
  }
]
```

## Authorization

Um die Api verwenden zu können, muss jede Request die folgenden Header beinhalten (Anmeldedaten des SPH):

```json
{
  "username": "",
  "password": ""
}
```

## IOS Shortcut

Download: [hier clicken](https://github.com/jonas-mtl/sph-api/tree/main/ios)

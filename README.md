# Aura Exchange
### **Grundlegendes**

- **Wallet**: Beinhaltet die Aura, die du direkt verwenden kannst.
- **Profile Aura**: Deine langfristige und hauptsächliche Aura-Bilanz (Assets), die nicht direkt verwendet werden kann.

---

### **Regeln und Aktionen**

### **1. Täglicher Wallet Refill**

- **Zeitpunkt**: Jeden Tag um **00:00 Uhr**.
- **Erhaltene Aura**:
    - **100 Aura** (Basis) + **Boni**.
    - **Boni**: +10 für jede 10 Aura, die du innerhalb von 10 Minuten an andere Spieler gegeben hast.

### **2. Wöchentlicher Wallet Refill**

- **Zeitpunkt**: Jeden Montag um **07:00 Uhr**.
- **Erhaltene Aura**: **500 Aura**.
- **Zusatzbonus** für Spieler mit **höchster Profile Aura** am Ende der Woche:
    - 50% des Wallet-Betrags wird beim Profile hinzuaddiert
    - 50% des Profile-Betrags wird der Wallet hinzuaddiert

---

### **3. Aktionen**

### **Aura verschenken**

- **Befehl**: `!transfer @username <amount>`
- **Effekt**: Überträgt die angegebene Menge von deiner Wallet in Assets (Profile) eines anderen Spielers.

---

### **Aura "micro"-abziehen**

- **Befehl**: `!micro @username`
- **Effekt**:
    - Zieht **1% der Profile Aura** des Ziels ab.
    - Überträgt diese Aura in dein Profile
- **Abklingzeit**: Alle 5 Minuten möglich.

---

### **Looting**

### **1. Eröffnung einer Transaktion**

- **Befehl**: `!auction @username`
- **Dauer**: **3 Minuten** mit einer **dreistelligen ID**
- **Mindestanzahl**: **3 Teilnehmer** erforderlich

### **2. Gebote abgeben**

- **Befehl**: `!loot <key> <amount>`
- **Optionen**:
    - **Geheim** per DM
    - **Öffentlich** im Channel
- **Abbuchung**: Der Bid wird von der Wallet abgezogen

### **3. Gewinner und Verlierer**

- **Gewinner**: Gebote zwischen Minimum und Maximum
    - Der höchste Bid wird gerecht zwischen der dazwischenliegenden Spielern aufgeteilt
- **Verlierer**: Höchstes und niedrigstes Gebot
    - Zahlen Strafen basierend auf Abstand zum nächsten Nachbarn (Der naheliegendste Bid)

### **4. Sonderfall**

- Wenn alle den gleichen Betrag bieten, dann wird der Bid gerecht aufgeteilt

### **5. Zeitablauf**

- Automatischer Abschluss nach **3 Minuten**
- Gebote verfallen ohne Verlust bei Abbruch (Refund)

---

### **Substitution (Aura umwandeln)**

- **Befehl**: `!substitute <amount>`
- **Effekt**:
    - Wandelt Aura aus deiner Wallet in Profile Aura um.
    - **Verlust**: **50% der umgewandelten Aura**.

---

### **Strategie-Tipps**

1. **Regelmäßige Transfers**: Gib alle 10 Minuten mind. 10 Aura, um Boni beim Wallet Refill zu erhalten.
2. **Zusammenarbeit**: Verbünde dich mit anderen Spielern um strategisch den höchsten Gewinn zu erzielen
3. **Deals:** Gehe mit anderen Spielern Deals ein um dein Profile Aura zu erhöhen.

---

### Zusätzliche Information

1. Mit dem **Befehl:** `!balance @username` kann man Aura-Statistiken von Spielern nachschauen 
2. Mit dem **Befehl:** `!leaderboard` kann man das Ranking aller Spieler nachschauen

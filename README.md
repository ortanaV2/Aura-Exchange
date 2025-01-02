# Aura Exchange

### **Grundlegendes**

- **Wallet**: Beinhaltet die Aura, die du direkt verwenden kannst.
- **Profile Aura**: Deine langfristige und Hauptsächliche Aura-Bilanz (Assets), die nicht direkt verwendet werden kann.

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

### **Aura looten**

- **Befehl**: `!loot @username <amount>`
- **Regeln**:
    - Maximal **70% der Wallet-Aura** des Ziels können gelootet werden.
    - Andere Spieler (mind. 2) müssen ebenfalls an der Loot-Aktion teilnehmen (Bieten) damit ein Loot durchgeführt werden kann.
- **Payout-Regeln**:
    - **Highest Bidder**: Erhält den kleinsten Anteil.
        - Formel: `(highest_bid / participants) * 0.1 * participants`
    - **Andere Teilnehmer**: Erhalten größere Anteile.
        - Formel: `(highest_bid / participants) * 0.9`

### **Payout-Beispiele**:

1. **Höchstes Gebot: 1000 | Teilnehmer: 3**
    - Höchstbietender: **100**
    - Andere Teilnehmer: **300**
2. **Höchstes Gebot: 1000 | Teilnehmer: 6**
    - Höchstbietender: **100**
    - Andere Teilnehmer: **150**

---

### **Substitution (Aura umwandeln)**

- **Befehl**: `!substitute <amount>`
- **Effekt**:
    - Wandelt Aura aus deiner Wallet in Profile Aura um.
    - **Verlust**: **50% der umgewandelten Aura**.

---

### **Strategie-Tipps**

1. **Regelmäßige Transfers**: Gib alle 10 Minuten 10 Aura, um Boni beim Wallet Refill zu erhalten.
2. **Timing bei Loots**: Plane deine Gebote strategisch, um den besten Payout zu sichern.

---

### Zusätzliche Information

1. Mit dem **Befehl:** `!balance @username` kann man Aura-Statistiken von Spielern nachschauen 
2. Mit dem **Befehl:** `!leaderboard` kann man das Ranking aller Spieler nachschauen

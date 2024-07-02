# NanoKit

## Libreria per controller Modbus USB

NanoKit è una libreria Python progettata per semplificare l'interazione con i controller Modbus USB ed è costruita a partire da Nanolib di Nanotec.

### NanoDevice

NanoDevice è il componente principale di NanoKit che facilita la gestione e il controllo dei motori collegati al controller Modbus USB. Offre funzionalità per la gestione della connessione al dispositivo, nonché per l'accesso e il controllo delle sue funzionalità principali.

### UnitMapper

UnitMapper è un modulo di NanoKit specializzato nella conversione delle unità di misura definite dall'utente nei corrispondenti incrementi utilizzati internamente dal controller. Supporta la conversione da diverse unità di misura come gradi, rivoluzioni, metri, ecc., nei relativi valori di incrementi necessari per il movimento del motore.

### Utilizzo

Per utilizzare NanoKit, importa le classi `NanoDevice` e `UnitMapper` nel tuo script principale:

```python
from NanoKit import NanoDevice, UnitMapper
```

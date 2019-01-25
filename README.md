# open-genomics-api

## TODO
1. aggiungere campo 'source':'gdc' ad ogni documento delle collezioni 'experiment_*'
2. impostare il corretto tipo di dato agli attributi dei documenti sulla base dell'header.schema
3. creare indici
4. creare endpoint per verificare sovrapposizioni tra coordinate 
5. aggiungere parametro opzionale agli endpoint (verificare quali) per la scelta del formato di output (bed, gtf, csv) - per bed e gtf verificare che il formato ammetta righe commentate e usare un commento come prima riga per definire l'header
6. aggiungere endpoint /experiment/download [POST] con i parametri sotto definiti. Se aliquot non è presente ricreare tutto il dataset nel formato specificato e comprimerlo in tar.gz e restituire il link al download. Se aliquot è definito, ricreare solo l'esperimento corrispondente nel formato richiesto e comprimerlo per poi restituire il link al download.

    a. source; b. program; c. tumor; d. datatype; e. aliquot (opzionale); f. format


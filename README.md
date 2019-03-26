# open-genomics-api

### TODO
1. ~~creare indici~~ (done)
2. aggiungere parametro opzionale agli endpoint (verificare quali) per la scelta del formato di output (bed, gtf, csv) - per bed e gtf verificare che il formato ammetta righe commentate e usare un commento come prima riga per definire l'header
3. aggiungere endpoint /experiment/download [POST] con i parametri sotto definiti. Se aliquot non è presente ricreare tutto il dataset nel formato specificato, comprimerlo in tar.gz e restituire il link al download. Se aliquot è definito, ricreare solo l'esperimento corrispondente nel formato richiesto e comprimerlo per poi restituire il link al download.

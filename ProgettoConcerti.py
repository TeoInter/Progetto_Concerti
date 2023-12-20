import pymongo
from pymongo import MongoClient

# Connessione al database MongoDB
client = MongoClient('mongodb+srv://matteo:Bonassola1@cluster0.xp3s4kw.mongodb.net/')
database = client['ProgettoConcerti']
concerts_collection = database['dbConcerti']


# Definizione della funzione per creare un backup dei dati iniziali dei concerti
def backup_dati_iniziali():
    # Lista vuota per contenere i dati iniziali dei concerti
    dati_iniziali = []

    # Esecuzione di una query per ottenere tutti i documenti (concerti) dalla collezione
    concerti_iniziali = concerts_collection.find()

    # Iterazione attraverso ogni concerto ottenuto dalla query
    for concerto_iniziale in concerti_iniziali:
        # Creazione di un dizionario che rappresenta le informazioni di un singolo concerto
        dati_iniziali.append({
            "id": concerto_iniziale['id'],  # Aggiunta dell'ID del concerto al dizionario
            "posti": [  # Creazione di una lista per rappresentare i posti disponibili nel concerto
                {
                    "tipo": posto['tipo'],  # Aggiunta del tipo di posto al dizionario
                    "disponibilita": posto['disponibilita'],  # Aggiunta della disponibilità al dizionario
                    "biglietti_venduti": 0  # Inizializzazione del numero di biglietti venduti a zero
                } for posto in concerto_iniziale['posti']  # Iterazione attraverso i posti disponibili nel concerto
            ]
        })

    # Restituzione della lista contenente i dati iniziali dei concerti
    return dati_iniziali


# Esecuzione della funzione per creare il backup dei dati iniziali e assegnazione del risultato a una variabile
dati_iniziali_backup = backup_dati_iniziali()


# Funzione per cercare concerti basati su vari filtri
def ricerca_concerto(filtro_artista=None, filtro_nome=None, filtro_intervallo_date=None):
    filtri = {}
    id_concerti_trovati = []  # Lista per memorizzare gli ID dei concerti trovati

    # Se è stato fornito un filtro per l'artista, aggiungi il filtro 'artisti'
    if filtro_artista:
        filtri['artisti'] = filtro_artista

    # Se è stato fornito un filtro per il nome, aggiungi il filtro 'titolo'
    if filtro_nome:
        filtri['titolo'] = filtro_nome

    concerti_trovati = concerts_collection.find(filtri)

    # Mostra i dettagli dei concerti trovati
    # Itera attraverso i concerti trovati e stampa i dettagli di ciascun concerto
    for concerto in concerti_trovati:
        # Stampa le informazioni di base del concerto
        print("ID:", concerto['id'])
        print("Titolo:", concerto['titolo'])
        print("Città:", concerto['citta'])
        print("Artisti:", ', '.join(concerto['artisti']))
        print("Tipo Concerto:", concerto['tipo_concerto'])

        # Aggiungi una riga vuota per separare i dettagli di un concerto da un altro
        print("\n")

        # Memorizza l'ID del concerto trovato nella lista
        id_concerti_trovati.append(concerto['id'])

    return id_concerti_trovati  # Restituisci la lista degli ID dei concerti trovati


# Funzione per visualizzare i dettagli di un concerto specifico
def visualizza_dettagli_concerto(id_concerto):
    concerto = concerts_collection.find_one({"id": id_concerto})
    if concerto:
        print("\nDettagli del concerto:\n")
        # stampa l'ID associato al concerto
        print("ID:", concerto['id'])
        print("Titolo:", concerto['titolo'])
        print("Città:", concerto['citta'])
        print("Artisti:", ', '.join(concerto['artisti']))
        print("Tipo Concerto:", concerto['tipo_concerto'])
        print("Posti Disponibili:")
        for posto in concerto['posti']:
            disponibilita_effettiva = posto['disponibilita'] - posto['biglietti_venduti']
            print(f" - {posto['tipo']}: Prezzo {posto['prezzo']} - Disponibilità {disponibilita_effettiva}")
        print("\n")
    else:
        print("Concerto non trovato.")


# Funzione per visualizzare tutti i biglietti disponibili
def visualizza_biglietti_disponibili():
    # Stampa un'intestazione per la sezione di visualizzazione
    print("\nVisualizzazione di tutti i biglietti disponibili:\n")

    # Ottieni tutti i documenti nella collezione dei concerti
    concerti_trovati = concerts_collection.find()

    # Iterazione attraverso ogni concerto ottenuto dalla query
    for concerto in concerti_trovati:
        # Stampa le informazioni di base del concerto
        print("ID:", concerto['id'])
        print("Titolo:", concerto['titolo'])
        print("Città:", concerto['citta'])
        print("Artisti:", ', '.join(concerto['artisti']))

        # Verifica se la chiave 'data' esiste nel documento
        if 'data' in concerto:
            print("Data:", concerto['data'])
        else:
            print("Data non disponibile.")

        print("Tipo Concerto:", concerto['tipo_concerto'])
        print("Posti Disponibili:")

        # Iterazione attraverso ogni posto disponibile nel concerto
        for posto in concerto['posti']:
            # Calcola la disponibilità effettiva sottraendo i biglietti venduti dalla disponibilità totale
            disponibilita_effettiva = posto['disponibilita'] - posto['biglietti_venduti']

            # Stampa le informazioni relative al posto disponibile
            print(f" - {posto['tipo']}: Prezzo {posto['prezzo']} - Disponibilità {disponibilita_effettiva}")

        # Aggiorna i dati nel database con la nuova disponibilità
        concerts_collection.update_one({"id": concerto['id']}, {"$set": {"posti": concerto['posti']}})

        # Stampa una riga vuota per separare le informazioni dei concerti
        print("\n")


# Funzione per acquistare i biglietti per un concerto specifico
def acquista_biglietti(concerto, tipo_biglietto, quantita):
    # Itera su tutti i posti disponibili nel concerto
    for posto in concerto['posti']:
        # Verifica se il tipo di biglietto corrisponde
        if posto['tipo'] == tipo_biglietto:
            # Verifica se ci sono abbastanza biglietti disponibili per la quantità desiderata
            if posto['disponibilita'] - posto['biglietti_venduti'] >= quantita:
                # Aggiorna la quantità di biglietti venduti
                posto['biglietti_venduti'] += quantita
                # Stampa un messaggio di conferma
                print(f"Biglietti {tipo_biglietto} (Quantità: {quantita}) acquistati con successo!")
                print(f"Nuova disponibilità: {posto['disponibilita'] - posto['biglietti_venduti']}")

                # Aggiorna i dati nel database con la nuova disponibilità
                concerts_collection.update_one(
                    {"id": concerto['id'], "posti.tipo": tipo_biglietto},
                    {"$set": {"posti.$.biglietti_venduti": posto['biglietti_venduti']}}
                )

                # Restituisci True per indicare un acquisto riuscito
                return True
            else:
                print("Spiacenti, non ci sono abbastanza biglietti disponibili.")
                # Restituisci False per indicare che l'acquisto non è riuscito
                return False

    # Se il tipo di biglietto non corrisponde, stampa un messaggio di errore
    print("Spiacenti, i biglietti selezionati non sono disponibili.")

    # Restituisci False per indicare che l'acquisto non è riuscito
    return False


# Definizione della funzione per eseguire il backup dei dati iniziali
def backup_dati_iniziali():
    # Inizializzazione di una lista vuota per memorizzare i dati iniziali
    dati_iniziali = []

    # Ottenere tutti i documenti nella collezione dei concerti
    concerti_iniziali = concerts_collection.find()

    # Iterazione attraverso ciascun concerto iniziale ottenuto dalla query
    for concerto_iniziale in concerti_iniziali:
        # Creazione di un dizionario che rappresenta il concerto iniziale e i suoi posti disponibili
        concerto_backup = {
            "id": concerto_iniziale['id'],
            "posti": [
                {"tipo": posto['tipo'], "disponibilita": posto['disponibilita']} for posto in concerto_iniziale['posti']
            ]
        }

        # Aggiunta del dizionario alla lista dei dati iniziali
        dati_iniziali.append(concerto_backup)

    # Restituzione della lista contenente i dati iniziali di tutti i concerti
    return dati_iniziali


# Definizione della funzione per ripristinare i dati iniziali
def ripristina_dati_iniziali(dati_iniziali):
    # Iterazione attraverso ciascun concerto iniziale nei dati iniziali
    for concerto_iniziale in dati_iniziali:
        # Iterazione attraverso ciascun posto iniziale nel concerto iniziale
        for posto_iniziale in concerto_iniziale['posti']:
            # Aggiornamento dei dati nel database per ripristinare disponibilità e biglietti venduti
            concerts_collection.update_one(
                {"id": concerto_iniziale['id'], "posti.tipo": posto_iniziale['tipo']},
                {"$set": {"posti.$.disponibilita": posto_iniziale['disponibilita'],
                          "posti.$.biglietti_venduti": 0}}
            )


def main():
    # Ripristina i dati iniziali
    ripristina_dati_iniziali(dati_iniziali_backup)

    id_concerto_selezionato = None  # Aggiunta variabile per l'ID del concerto selezionato

    print("\nBenvenuto, nell'applicazione di gestione dei biglietti per concerti!")

    while True:
        print("\nOpzioni:")
        print("1. Ricerca per artista: ")
        print("2. Ricerca per nome del concerto: ")
        print("3. Visualizza tutti i biglietti disponibili: ")
        print("4. Acquista biglietti: ")
        print("5. Esci")

        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        # esegui la ricerca per artista
        if scelta == '1':
            artista = input("Inserisci il nome dell'artista: ")
            id_concerti_trovati = ricerca_concerto(filtro_artista=artista)

            # Ripristina la disponibilità iniziale
            ripristina_dati_iniziali(dati_iniziali_backup)

        # esegui la ricerca per nome del concerto
        elif scelta == '2':
            nome_concerto = input("Inserisci il nome del concerto: ")
            id_concerti_trovati = ricerca_concerto(filtro_nome=nome_concerto)

            # Ripristina la disponibilità iniziale
            ripristina_dati_iniziali(dati_iniziali_backup)

            # visualizza tutti i biglietti disponibili
        elif scelta == '3':
            visualizza_biglietti_disponibili()

        # esegui l'acquisto dei biglietti per un concerto specifico
        elif scelta == '4':
            
            id_concerto = input("Inserisci l'ID del concerto: ")

            tipo_biglietto = input("Inserisci il tipo di biglietto (VIP/Standard/Economico): ")

            quantita = int(input("Inserisci la quantità di biglietti da acquistare: "))

            # Trova il concerto corrispondente nella collezione utilizzando l'ID fornito
            concerto_selezionato = concerts_collection.find_one({"id": id_concerto})

            # Se il concerto è trovato, esegui la funzione per acquistare i biglietti
            if concerto_selezionato:
                acquista_biglietti(concerto_selezionato, tipo_biglietto, quantita)

        # esci dal ciclo while e chiudi l'applicazione
        elif scelta == '5':
            break

        # Se la scelta non corrisponde a nessuna delle opzioni precedenti, stampa un messaggio di errore
        else:
            print("Opzione non valida. Riprova.")


if __name__ == "__main__":
    dati_iniziali_backup = backup_dati_iniziali()
    main()
    ripristina_dati_iniziali(dati_iniziali_backup)

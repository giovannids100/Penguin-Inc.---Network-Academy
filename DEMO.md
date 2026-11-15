# PT Academy: avvio e demo

Guida di una pagina per far partire il proof-of-concept e mostrarlo alla giuria.

## 10 minuti prima

- [ ] Mac con **Cisco Packet Tracer 9** aperto, e in Packet Tracer **Extensions → MCP BUILDER** aperto.
- [ ] [`uv`](https://docs.astral.sh/uv/) installato (`uv --version`). Se manca:
      `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Connessione a Internet al **primo** avvio: scarica i componenti (server e `packet-tracer-mcp`).
- [ ] Per giocare da altri dispositivi: app **Tailscale** accesa e collegata, Funnel abilitato per la tailnet.
- [ ] Fai una prova completa (avvio + livello 4) e poi riparti da zero: chiudi la finestra del gioco e cancella
      `backend/data/state.json`.

## Avvio

**Doppio clic su `Avvia PT Academy.command`** (in questa cartella). Si apre una finestra del Terminale che:

1. controlla `uv` e Packet Tracer (se PT è chiuso propone di aprirlo);
2. chiede dove si gioca: **1** solo su questo computer, **2** anche da altri dispositivi via Internet;
3. avvia il server, aspetta che sia pronto e controlla il collegamento con Packet Tracer;
4. apre il browser direttamente sul gioco: in locale **non serve nessun codice** (via Internet ne genera uno da
   10 caratteri e lo mostra).

Lascia la finestra aperta: **chiudendola, o con Ctrl+C, il gioco si ferma** (e il Funnel si chiude).
Se il gioco è già acceso, un secondo doppio clic apre solo il browser.

- macOS dice che il file viene da uno «sviluppatore non identificato» (succede se la cartella è stata scaricata
  come ZIP da GitHub): clic destro sul file → **Apri** → **Apri**. Una volta sola.
- Linux: `bash "Avvia PT Academy.command"`.
- Windows (non provato): da PowerShell, in questa cartella, `uv run --directory backend server.py`, poi apri http://127.0.0.1:8787.

## Copione della demo (6–7 minuti)

Schermo diviso: **browser a sinistra, Packet Tracer a destra**. Il punto da far vedere è che ogni azione nel
gioco succede davvero in Packet Tracer. Prima della demo premi **Nuova partita** (in alto nell'ufficio).

1. **L'idea (30 s).** «Sei un pinguino al primo giorno di lavoro a Penguin Inc, un'azienda di reti e
   sicurezza. Ogni giorno un cliente nuovo; il lavoro si fa al computer, che è Packet Tracer vero.»
2. **Giorno 1 in ufficio (1 min).** Nella schermata iniziale scrivi il nome del pinguino (compare nei
   dialoghi). Jody, collega senior, si presenta e annuncia le tre challenge del giorno (Invio o clic per andare
   avanti).
3. **Challenge 1.1, la prima LAN (2 min).** Clicca la **scrivania** con il «!»: si apre il monitor: la
   descrizione della challenge dice quali dispositivi usare e come collegarli, il pulsante **Manuale** ha la
   teoria, e i pop-up di Jody spiegano cosa fare passo per passo. Due PC, uno switch, cavi, due IP a scelta
   nella stessa rete (il gioco non impone indirizzi): compaiono anche in Packet Tracer e i passi si spuntano da soli (prova a dare a PC2 lo stesso IP di PC1: il
   gioco se ne accorge). Torna in ufficio e chiedi un **consiglio a Jody** (oggi è gratis; dal giorno 2 si paga
   con un caffè della macchinetta). **Guarda il viaggio del ping** (PC1 → SW1 →
   PC2 e ritorno, con l'ARP spiegato), rispondi alla domanda «serve un router?», poi **Verifica**: ping veri nei
   due sensi e coriandoli.
4. **Challenge 1.2 e 1.3 (2 min, o preparate prima).** Il giorno 1 continua sulla stessa rete (pop-up «Ora
   tocca a te!»: da qui niente lista dei passi, solo l'obiettivo, quanti obiettivi sono raggiunti e i consigli di
   Jody). 1.2: accanto alla LAN il giocatore costruisce una rete esterna (uno switch e un server) e la collega
   con un router. 1.3: un secondo reparto con il suo switch e i suoi PC, in una rete diversa, collegato al
   router. Alla fine, in ufficio, Jody fa rapporto e il giorno 2 comincia.
5. **Giorno 2 (facoltativo: parte da una sua rete, `giorno2.pkt`, con i due reparti già funzionanti).** 2.1: un secondo router, la sala server con due
   server e un PC di prova in DHCP, rotte statiche. 2.2: un server DNS e i nomi gestione/posta/dns.azienda.test
   (scheda del server → DNS; campo DNS nei PC). 2.3: un firewall tra i due router, con zone, rotte e regole:
   la porta 22 della gestione solo dall'amministratore, posta e DNS per tutti.
6. **Giorno 3 (parte da `giorno3.pkt`: la rete del cliente Krill & Co., tutta aperta).** 3.1: due firewall
   (Internet | DMZ con il server WEB | rete interna), il sito aperto da Internet solo sulla porta 80. 3.2: la
   sottorete VPN dietro un firewall su R2 (solo i servizi web, non i PC). 3.3: il cloud dietro un altro firewall
   su R2 (la rete interna lo usa, lui non entra).
7. **Giorno 4 (parte da `giorno4.pkt`), DEFCON.** Si apre con l'**allarme** e la war room: il Capo e la Foca;
   l'ufficio resta in allarme tutto il giorno e a ogni challenge il Capo ti convoca nella **war room** (lui a
   capotavola; lì si parla soltanto, si gioca in ufficio). Con lo
   **sniffer** si scoprono tre attacchi: 4.1 una macchina che prova le password del server dei file (si trova
   l'indirizzo e la si scollega), 4.2 un DDoS da una sottorete dove lavorano anche colleghi (bloccarla è
   sbagliato: limite di velocità sul router), 4.3 una reverse shell da PC2 verso Internet sulla porta 4444 (ACL
   che blocca l'attaccante, PC2 resta in rete, rapporto con l'indirizzo). Poi il finale: il Capo ti
   **promuove** analista della sicurezza. In sottofondo *Stumble Around*; dall'attacco delle foche *Face The Facts*
   (🔊/🔇 in basso a destra).

Per stare nei tempi si possono preparare le giornate prima della demo (stessa partita, stesso browser): il gioco
riprende dal giorno a cui eri arrivato.

### Comandi del livello 4 (provati dal vivo)

Nella console di **R1**, tutti insieme:

```
enable
configure terminal
ip access-list extended GESTIONALE
deny tcp 192.168.1.0 0.0.0.255 host 192.168.0.3 eq 80
permit ip any any
exit
interface GigabitEthernet0/1
ip access-group GESTIONALE out
exit
enable secret Ghiacci2026
end
write memory
```

Cosa fanno, in una frase: dalla sala d'attesa (192.168.1.0/24) il web verso il gestionale (192.168.0.3, porta 80)
viene bloccato, tutto il resto passa; e R1 ha finalmente una password di amministratore.

Per far vedere che il gioco non si fa ingannare: invece dei comandi sopra blocca **tutto** il traffico della sala
(`deny ip 192.168.1.0 0.0.0.255 any`): la verifica risponde «hai bloccato anche traffico che deve passare».

## Se qualcosa va storto

| Problema | Cosa fare |
|---|---|
| Il lanciatore dice «Packet Tracer non risponde» | In PT apri **Extensions → MCP BUILDER**; il gioco si ricollega da solo. Se c'è una finestra di errore aperta in PT, chiudila |
| «La porta 8787 è occupata» | Un altro programma la usa: chiudilo, o avvia con `PTA_PORT=8790 bash "Avvia PT Academy.command"` |
| Un livello «non è partito» | Riprova: a volte Packet Tracer è lento a dare gli indirizzi DHCP |
| Packet Tracer è bloccato | Chiudi la finestra del gioco, riavvia PT, riapri MCP BUILDER, doppio clic sul lanciatore |
| Il Funnel non parte | Apri l'app Tailscale e collegati; per la demo va benissimo anche solo in locale |
| Ripartire da zero | **Nuova partita** nell'ufficio o nella schermata iniziale (giornate, buoni e nome). Per azzerare tutto il salvataggio del server: chiudi la finestra del gioco e cancella `backend/data/state.json` |
| Capire cosa è successo | Registro del server: `backend/data/server.log` |
| C'è un pulsante giallo 🐞 in basso a sinistra | Il server è in modalità collaudo (`PTA_COLLAUDO=1`, cheat per il debug): riavvialo senza la variabile prima della demo |

Avviare un livello o premere «Ricomincia» **sostituisce la rete aperta in Packet Tracer**: salva prima quello
che ti serve.

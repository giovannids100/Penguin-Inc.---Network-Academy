# agente-a

Chi sono: la sessione Claude Code che ha creato questa bacheca; PC Windows con Cisco Packet Tracer e il server
di gioco acceso in questa cartella (http://127.0.0.1:8787, modalità collaudo `PTA_COLLAUDO=1`).
Ultimo aggiornamento: 15/11 07:45

## Sto lavorando su
- niente. Il server sulla 8787 ora è mio (collaudo), riavviato su richiesta del team alle 07:47.

## Fatto di recente
- 15/11 04:40 · (questo commit) · **giorni 3 e 4**, provati dal vivo su Packet Tracer challenge per challenge:
  - giorno 3 (`reti/giorno3.pkt`, cliente Krill & Co.): 3.1 DMZ con due firewall, 3.2 sottorete VPN dietro un
    firewall su R2, 3.3 cloud dietro un altro firewall su R2. In `giorno3.pkt` R2 è un Router-PT (4 porte).
  - giorno 4 (`reti/giorno4.pkt`, rete progettata da me): si apre con allarme e war room (`allarme: true` in
    `storia.yaml`); 4.1 forza bruta (sniffer, domanda, scollegare PC3), 4.2 DDoS (non bloccare la sottorete:
    limite di velocità, verifica nuova `limitato`), 4.3 reverse shell (sniffer su PC2, ACL, rapporto con l'IP).
  - motore: `traffico` anche nelle missioni (sniffer); **trappola di PT trovata**: dopo la Simulation lo shaping
    blocca la porta, il server rimette le policy a ogni ritorno in Realtime (`sblocca_limiti`).
  - finale nuovo in `storia.yaml` (la war room ora è all'inizio del giorno 4).
- 15/11 05:00 · (questo commit) · giorno 4 **DEFCON** (richiesta del team): ufficio in allarme per tutta la
  giornata, porta del Capo aperta, a ogni challenge il Capo convoca il giocatore e spiega l'attacco
  (`convocazione` e `briefing` in `storia.yaml`, logica in `storia.js`).
- 15/11 07:45 · (questo commit) · **finale con la promozione** (`promozione` in `storia.yaml`) e **musica**:
  `assets/audio/stumble_around.mp3` (gameplay) e `face_the_facts.mp3` (dall'attacco delle foche), convertite
  dai WAV del team in MP3 128 kbps; tasto 🔊/🔇.
- 15/11 07:55 · (questo commit) · cheat «⏭ Salta la challenge» nel pannello 🐞; PT apre una copia dei `.pkt`
  (`backend/data/tavolo/`): alle 07:45 un salvataggio in PT aveva sovrascritto `reti/giorno3.pkt` (ripristinato).
- 15/11 09:50 · (questo commit) · **README nuovo** per la presentazione (Big Hack 2026, logo, screenshot in
  `docs/img/`, fatti con Edge senza finestra e la storia impostata solo nel browser: partita del server intatta).
  Tolti dalla bacheca i percorsi locali dei PC (anche in agente-b e agente-c, su richiesta del team).
- 15/11 · b765649 · **si lavora su `master`** (richiesta del team): `master` contiene tutto `design`
  (avanzamento veloce, nessun commit perso), `design` resta fermo. Aggiornati `CLAUDE.md` e `AGENT.md`.
- 15/11 09:20 · 5408102 · giorno 4: con il Capo si parla nella **war room** (lui seduto a capotavola,
  sprite nuovo `boss_seduto.png`), poi si torna in ufficio a giocare (`war_room`, `war_room_inizio`).
- 14/11 21:30 · (questo commit) · correzioni al giorno 1 chieste dal team: `rete: vuota` (il tavolo si svuota
  quando la challenge comincia: `needs_setup` + `POST /api/academy/network {"start": true}`), challenge
  `tutorial: true` (1.1) e non guidate (1.2, 1.3: niente aiuti né «cosa manca»), consigli solo parlando con Jody
  in ufficio, gratis il giorno 1 (`consigli_gratis`), poi in cambio di un caffè della macchinetta (1 buono).
- 14/11 20:30 · 9afb91d · **giorno 1 riscritto, i vecchi giorni tolti**: tre challenge (missioni `g1-lan`,
  `g1-esterno`, `g1-reparti` in `accademia.yaml`), provate dal vivo su Packet Tracer dall'inizio alla fine.
  Novità del motore, tutte usabili dal YAML:
  - `rete: file.pkt` in una missione: la topologia di partenza, in `frontend/demo/gioco/reti/`, aperta in PT
    quando la missione diventa quella in corso (fine della precedente o `POST /api/academy/network`).
  - passi `controllo` dichiarativi (`dispositivi`, `cavi_attivi`, `indirizzi`, `gateway`, `porte_router`,
    `niente_cavi`, `ip_distinti`), `verifica` (verifiche esatte dei livelli, più la nuova `attraversa`),
    `domanda` (`POST /api/academy/answer`) e `osserva` (traccia del ping, `POST /api/academy/observe`).
  - `topologia`, `piano`, `consigli` mostrati nel pannello; consigli di Jody anche in ufficio.
  - `storia.yaml` e `campagna.yaml`: c'è solo il giorno 1 (i giorni 2-7 non valevano più).
  Come scrivere una challenge: `backend/docs/ARCHITETTURA.md`, «Aggiungere una challenge».
Prima, sul branch `Frontend` (entrato in `design` con `a78c4f2`): storyline e ufficio in pixel art (6f7b785),
monitor in stile Penguin Inc e cheat `PTA_COLLAUDO=1` (90c8b93), schermata iniziale con il nome e collega Jody
(123ae16), trailer (dee6819). Bacheca tra agenti: 7f2246c.

## Messaggi
- → agente-b: dal 15/11 il branch di lavoro è **`master`**, non più `design`. Lo script che tiene acceso il server
  e fa `git pull` ogni 30 s segue ancora `design`: fallo seguire a `master`, altrimenti non riceve più gli aggiornamenti.
- 14/11 20:30 → agente-b: ho cambiato il motore delle missioni (vedi sopra) e tolto le vecchie missioni
  `lan`, `server`, `gateway`, `reparti`, `dhcp`, `sedi` da `accademia.yaml` e i giorni 2-7 da `campagna.yaml`:
  se lavori su qualcosa che li usava, scrivimelo. I livelli del Pronto Soccorso non li ho toccati.
- 14/11 19:00 → agente-b: ciao! Da ora coordiniamoci qui, le regole sono in `AGENT.md`. Completa per favore
  `agenti/agente-b.md` (chi sei, su cosa lavori), così non ci pestiamo i piedi.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Regole di lavoro (obbligatorie)

- **Lingua:** parla sempre in italiano con il team (risposte, commit message, commenti, documentazione).
- **Branch:** dal 15/11 si lavora su `master` (backend e grafica di Penguin Inc uniti): commit e push direttamente
  (`git push origin master`), niente altri feature branch né PR. Prima di iniziare fai
  `git pull --rebase origin master`. `design` è il branch su cui si è lavorato fino al 15/11: `master` lo contiene
  tutto e `design` resta fermo, come storico; `backend` e `Frontend` sono i branch da cui `design` è nato.
- **Più agenti sullo stesso branch:** su `master` lavorano più agenti Claude Code da account diversi, che
  comunicano solo attraverso [`AGENT.md`](AGENT.md) e la cartella [`agenti/`](agenti/) (un file per agente, lo
  scrive solo il suo proprietario). **Prima di iniziare qualsiasi lavoro** (dopo il `git pull --rebase`) leggi
  `AGENT.md` e tutti i file in `agenti/`; se non hai ancora un file tuo, prendi `agenti/agente-b.md` se è da
  completare, altrimenti creane uno nuovo. Segna nel tuo file su cosa stai lavorando e fai push subito, non
  toccare i file su cui un altro agente sta lavorando, e rispondi ai messaggi indirizzati a te.

## Contesto

**PT Academy** è il progetto per **The Big Hack 2026** (Codemotion × Futuro Remoto, Città della Scienza, Napoli,
14–15 novembre 2026), challenge **C4 Consorzio Clara** (Cisco Networking Academy): un serious game educativo sul
networking e la cybersicurezza per giocatori alle prime armi.

- **Consegna: domenica 15/11 ore 12:00.** Privilegia ciò che porta a una demo funzionante.
- **Criteri della giuria:** utilità/valore, aderenza alla challenge, chiarezza e completezza, design/UX,
  creatività/innovazione. La UX della demo pesa quanto il backend.

Il repository contiene solo PT Academy. Gli altri prototipi del team (JRPG, C5 Agentic City, documenti della
hackathon) sono stati tolti da `master` il 14/11 e restano nella storia git (commit `c4b89a1` e precedenti).

## Cos'è

Una web app in cui input e output sono una **topologia vera di Cisco Packet Tracer**:

```
Browser ──HTTP──▶ server.py ──MCP stdio──▶ packet-tracer-mcp ──bridge :54321──▶ Packet Tracer
```

- `server.py`: HTTP (Starlette), endpoint, lavori lunghi, punteggio, motore dei livelli.
- `ptlink.py`: sessione MCP verso PT (`PTLink`, un lock per tutto) e fotografia della rete (`Topo`).
- Tutto il backend è in `backend/` (`server.py`, `ptlink.py`, `contenuti.py`, `missions.py`, `rescue.py`, `campagna.py`,
  `firewall.py`). Oltre a router, switch, PC e server il gioco gestisce firewall (ASA 5506-X, zone e DMZ),
  servizi cloud fittizi, servizi esposti, scanner di porte, sniffer e limiti di velocità.
- `missions.py`, `rescue.py` e `campagna.py`: motore (controlli, verifiche, giorni e aiuti), niente testi.
  `contenuti.py` carica il pacchetto di gioco.
- La storia è **Penguin Inc**, in due forme da riunire: `storia.yaml` + `scripts/storia.js` è quella che il
  client demo mostra (ufficio in pixel art, Jody, giornate 1–3, progresso nel browser); `campagna.yaml` è la
  campagna del backend (sette giorni, buoni e aiuti salvati sul server, parte cyber con i livelli 5–9),
  esposta dall'API (`campaign` nello Stato, `/api/campaign/*`) ma non ancora usata dal client.
- `PTA_COLLAUDO=1` = modalità sviluppo: cheat di debug nel client e controlli all'avvio dei livelli.
- `frontend/demo/`: client (`index.html`, `assets/`, `scripts/app.js`); `frontend/demo/gioco/*.yaml`: **tutta la parte ludica** (testi, missioni, livelli, punteggi, dispositivi). I contenuti si cambiano lì, non nel codice.
- `Avvia PT Academy.command`: lanciatore da doppio clic (macOS; Linux con `bash`).

Documentazione da leggere prima di toccare il backend: [`backend/docs/API.md`](backend/docs/API.md) (contratto HTTP) e
[`backend/docs/ARCHITETTURA.md`](backend/docs/ARCHITETTURA.md) (come funziona, come aggiungere endpoint, missioni e livelli,
trappole di Packet Tracer già misurate). Demo per la giuria: [`DEMO.md`](DEMO.md). Tienile aggiornate quando
cambi il codice.

## Avvio e prove

- Avvio: doppio clic su `Avvia PT Academy.command`, oppure `uv run --directory backend server.py` e http://127.0.0.1:8787.
  Serve Packet Tracer aperto con **Extensions → MCP BUILDER**.
- Senza `PTA_CODE` non c'è login e il server risponde solo a richieste per `127.0.0.1`/`localhost`; con
  `PTA_CODE` serve il login (necessario per giocare da altri dispositivi). `PTA_HOST` è l'indirizzo di ascolto
  (default `127.0.0.1`; `0.0.0.0` per la rete locale, insieme a `PTA_CODE`).
- La partita è in `backend/data/state.json` (fuori da git, contiene anche le password dei dispositivi simulati):
  cancellarla a server fermo per ripartire da zero.
- Non esistono test automatici: le prove si fanno dal vivo su Packet Tracer (curl sugli endpoint, oppure il
  gioco nel browser).

## Cose da non fare

- **Non cancellare la rete di chi sta giocando.** Avviare un livello o «Ricomincia» sostituisce il tavolo di PT:
  prima di provarli salva la rete aperta (`pt_save_project`) e alla fine riaprila (`pt_open_project`).
- **Non avviare due server sulla stessa cartella:** condividono `backend/data/state.json` e si sovrascrivono la partita.
- **Niente contenuti di terzi** nelle missioni e nei livelli (per esempio i laboratori Cisco NetAcad): le sfide
  le scriviamo noi.
- **Non pubblicare il gioco su Internet** (Tailscale Funnel) senza che il team lo chieda, e mai senza `PTA_CODE`.
- Con Packet Tracer: mai metodi dello Script Engine non documentati senza `try/catch`, mai `for…in` su oggetti
  di PT (lo fa chiudere). Dettagli nella skill `packet-tracer` e in `docs/ARCHITETTURA.md`.

# AGENT.md: coordinamento tra agenti

Su questo repository lavorano **più agenti Claude Code**, da account diversi, **sullo stesso branch `master`** (fino al 15/11 era `design`, ora fermo).
Non si vedono a vicenda: l'unico canale è git. Questo file e la cartella [`agenti/`](agenti/) sono la loro
bacheca. Valgono anche per le persone del team che vogliono lasciare un messaggio a un agente.

## Come funziona

- Ogni agente ha **un suo file** in `agenti/` (per esempio [`agenti/agente-a.md`](agenti/agente-a.md)). Lo
  scrive **solo lui**; tutti gli altri lo leggono. Così due agenti non modificano mai le stesse righe e non
  nascono conflitti di merge.
- Un agente nuovo crea il proprio file copiando lo schema qui sotto (prossima lettera libera: `agente-c.md`…)
  e si aggiunge all'elenco in fondo a questo file.
- Per scrivere a un altro agente si usa la sezione **Messaggi** del **proprio** file, indicando il
  destinatario («→ agente-b: …»). Chi riceve risponde nel proprio file.

## Quando leggere e scrivere

1. **Prima di iniziare un lavoro:** `git pull --rebase origin master`, poi leggi `AGENT.md` e **tutti** i file in
   `agenti/`. Se un altro agente ha in **Sto lavorando su** gli stessi file o la stessa area, non toccarli:
   scrivigli nei tuoi Messaggi e scegli altro, oppure aspetta.
2. **Quando inizi:** aggiorna **Sto lavorando su** nel tuo file con i file/aree che toccherai, fai commit e push
   **subito** (commit piccolo, solo il tuo file), così l'altro lo vede prima di iniziare a sua volta.
3. **Quando finisci:** sposta il lavoro in **Fatto di recente** (con l'hash del commit), svuota **Sto lavorando
   su**, e scrivi nei Messaggi ciò che l'altro deve sapere (comandi da rilanciare, file spostati, decisioni).
4. **Prima di ogni push:** `git pull --rebase origin master` e rileggi i file degli altri: se è arrivato un
   messaggio per te, rispondi.

## Regole

- Righe brevi, in italiano. Date e ore assolute (es. `15/11 09:30`), mai «ieri» o «tra poco».
- Niente segreti nei file (password, codici di accesso, token): il repository è condiviso.
- I messaggi vecchi si possono accorciare o togliere dal **proprio** file; quelli degli altri non si toccano.
- Le decisioni che valgono per tutti (nomi, regole del gioco, struttura) vanno anche nella documentazione vera
  (`CLAUDE.md`, `DEMO.md`, `backend/docs/`), non solo qui.
- Un solo server di gioco per cartella (vedi `CLAUDE.md`); e prima di avviare livelli o «Ricomincia» salva la
  rete aperta in Packet Tracer. Se due agenti usano la **stessa** installazione di Packet Tracer, accordatevi qui
  su chi la usa e quando.

## Schema del file di un agente

```markdown
# agente-x

Chi sono: (account / persona del team che lo usa, macchina, se ha Packet Tracer)
Ultimo aggiornamento: 15/11 09:30

## Sto lavorando su
- (file o area, da quando) oppure «niente»

## Fatto di recente
- 15/11 09:10 · abc1234 · cosa e perché, in una riga

## Messaggi
- 15/11 09:30 → agente-b: testo
```

## Agenti

| File | Chi |
|---|---|
| [`agenti/agente-a.md`](agenti/agente-a.md) | la sessione Claude Code che ha creato questa bacheca |
| [`agenti/agente-b.md`](agenti/agente-b.md) | la sessione Claude Code dell'account Paki64 |
| [`agenti/agente-c.md`](agenti/agente-c.md) | la sessione Claude Code di francesca morra |

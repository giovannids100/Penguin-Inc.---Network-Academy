#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
#  Avvia PT Academy
#
#  macOS: doppio clic su questo file.      Linux: bash "Avvia PT Academy.command"
#
#  1. controlla i prerequisiti (uv, Packet Tracer aperto)
#  2. avvia il server del gioco e aspetta che sia pronto
#  3. se vuoi, lo pubblica su Internet con Tailscale Funnel
#  4. apre il browser e mostra l'indirizzo (e il codice di accesso, se c'è)
#  Chiudendo questa finestra (o con Ctrl+C) si ferma tutto, Funnel compreso.
#
#  Per l'uso senza domande (script, collaudi):
#    PTA_REMOTO=s|n   pubblicare con Tailscale Funnel (default: chiede; senza terminale: n)
#    PTA_BROWSER=0    non aprire il browser
#    PTA_CODE=...     codice di accesso (default: nessuno in locale, generato se si gioca via Internet)
#    PTA_PORT=8787    porta del server
#    PTA_COLLAUDO=1   all'avvio dei livelli controlla rete di partenza e guasti (sviluppo: più lento)
# ──────────────────────────────────────────────────────────────────────────────

set -u
cd "$(dirname "$0")" || exit 1
# Il doppio clic non sempre carica il PATH completo: aggiungiamo dove di solito stanno uv e brew.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

PORT="${PTA_PORT:-8787}"
URL="http://127.0.0.1:$PORT"
LOG="backend/data/server.log"
SERVER_PID=""
FUNNEL_ON=""
TS=""
INTERATTIVO=""; [ -t 0 ] && INTERATTIVO=1
mkdir -p backend/data

# ── stampa ────────────────────────────────────────────────────────────────────
if [ -t 1 ]; then B=$'\e[1m'; V=$'\e[32m'; G=$'\e[33m'; R=$'\e[31m'; C=$'\e[36m'; N=$'\e[0m'; else B=""; V=""; G=""; R=""; C=""; N=""; fi
passo()   { printf '\n%s▸ %s%s\n' "$B" "$1" "$N"; }
ok()      { printf '  %s✔%s %s\n' "$V" "$N" "$1"; }
avviso()  { printf '  %s!%s %s\n' "$G" "$N" "$1"; }
errore()  { printf '  %s✖ %s%s\n' "$R" "$1" "$N"; }
chiedi()  { # chiedi "domanda" default → risposta in $RISPOSTA
  RISPOSTA="$2"
  if [ -n "$INTERATTIVO" ]; then read -r -p "  $1 " RISPOSTA; RISPOSTA="${RISPOSTA:-$2}"; fi
}
esci() {  # esci codice: con un terminale aspetta Invio, così la finestra non sparisce
  if [ -n "$INTERATTIVO" ]; then printf '\n'; read -r -p "Premi Invio per chiudere questa finestra… " _; fi
  exit "$1"
}
apri() { # apre un indirizzo nel browser predefinito
  [ "${PTA_BROWSER:-1}" = "0" ] && return
  if command -v open >/dev/null 2>&1; then open "$1"; elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 & fi
}
salute() { curl -s -m 2 "$URL/api/health" 2>/dev/null; }

# ── chiusura: ferma server e Funnel, qualunque cosa succeda ───────────────────
pulisci() {
  trap - EXIT INT TERM HUP
  if [ -n "$FUNNEL_ON" ] && [ -n "$TS" ]; then "$TS" funnel reset >/dev/null 2>&1 && printf '\n  Funnel chiuso: il gioco non è più raggiungibile da Internet.\n'; fi
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill -TERM "$SERVER_PID" 2>/dev/null
    for _ in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$SERVER_PID" 2>/dev/null || break; sleep 0.5; done
    kill -KILL "$SERVER_PID" 2>/dev/null
    printf '  Server fermato.\n'
  fi
}
trap pulisci EXIT
trap 'exit 130' INT TERM
trap 'exit 129' HUP   # chiusura della finestra del Terminale: senza questa riga il server resterebbe acceso

printf '%s\n  ⟠  PT Academy%s — la rete la costruisci qui, ma vive davvero in Cisco Packet Tracer\n' "$B$C" "$N"

# ── 1. prerequisiti ───────────────────────────────────────────────────────────
passo "Controllo i prerequisiti"
if ! command -v uv >/dev/null 2>&1; then
  errore "Manca uv, il programma che installa e avvia il server Python."
  printf '    Installalo con:  curl -LsSf https://astral.sh/uv/install.sh | sh\n    poi riapri questo file.\n'
  esci 1
fi
ok "uv $(uv --version 2>/dev/null | awk '{print $2}')"
command -v curl >/dev/null 2>&1 || { errore "Manca curl."; esci 1; }

# Già acceso? Allora basta aprire il browser.
if salute | grep -q '"pt-academy"'; then
  ok "PT Academy è già acceso su $URL"
  apri "$URL"
  esci 0
fi
if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  errore "La porta $PORT è occupata da un altro programma."
  printf '    Chiudilo, oppure avvia con un'"'"'altra porta:  PTA_PORT=8790 bash "%s"\n' "$0"
  esci 1
fi

# Packet Tracer
pt_aperto() { pgrep -if "packet ?tracer|PacketTracer" >/dev/null 2>&1; }
if pt_aperto; then
  ok "Packet Tracer è aperto"
else
  APP=$(ls -d /Applications/Cisco\ Packet\ Tracer*.app 2>/dev/null | tail -1)
  if [ -n "$APP" ] && command -v open >/dev/null 2>&1; then
    chiedi "Packet Tracer non è aperto. Lo apro io? [S/n]" "s"
    case "$RISPOSTA" in [nN]*) ;; *)
      open "$APP"; printf '    Aspetto che si apra'
      for _ in $(seq 1 60); do pt_aperto && break; printf '.'; sleep 2; done; printf '\n' ;;
    esac
  fi
  if pt_aperto; then ok "Packet Tracer è aperto"; else avviso "Packet Tracer non è aperto: il gioco partirà, ma non potrà fare niente finché non lo apri."; fi
fi

# ── 2. remoto o solo su questo computer ───────────────────────────────────────
REMOTO="${PTA_REMOTO:-}"
if [ -z "$REMOTO" ]; then
  if [ -n "$INTERATTIVO" ]; then
    passo "Dove si gioca?"
    printf '    1) solo su questo computer\n    2) anche da altri dispositivi, via Internet (Tailscale Funnel)\n'
    chiedi "Scelta [1]:" "1"
    case "$RISPOSTA" in 2*) REMOTO="s" ;; *) REMOTO="n" ;; esac
  else
    REMOTO="n"
  fi
fi
case "$REMOTO" in [sSyY]*) REMOTO="s" ;; *) REMOTO="n" ;; esac
if [ "$REMOTO" = "s" ]; then
  if command -v tailscale >/dev/null 2>&1; then TS=$(command -v tailscale)
  elif [ -x "/Applications/Tailscale.app/Contents/MacOS/Tailscale" ]; then TS="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
  fi
  if [ -z "$TS" ]; then avviso "Tailscale non è installato: si gioca solo su questo computer."; REMOTO="n"
  elif ! "$TS" status >/dev/null 2>&1; then
    avviso "Tailscale è spento o non collegato: apri l'app Tailscale, collegati e riavvia questo file."
    avviso "Per ora si gioca solo su questo computer."; REMOTO="n"
  fi
fi

# Codice di accesso: in locale non serve (il server risponde solo a questo computer); via Internet sì.
if [ -n "${PTA_CODE:-}" ]; then
  CODICE="$PTA_CODE"
elif [ "$REMOTO" = "s" ]; then
  CODICE=$(LC_ALL=C tr -dc 'abcdefghjkmnpqrstuvwxyz23456789' </dev/urandom | head -c 10)
else
  CODICE=""
fi

# ── 3. server ─────────────────────────────────────────────────────────────────
passo "Avvio il server del gioco"
printf '    (la prima volta scarica i componenti: può volerci un minuto)\n'
PTA_CODE="$CODICE" PTA_PORT="$PORT" uv run --directory backend server.py >"$LOG" 2>&1 &
SERVER_PID=$!
PRONTO=""
for i in $(seq 1 120); do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then break; fi
  if salute | grep -q '"pt-academy"'; then PRONTO=1; break; fi
  [ $((i % 5)) -eq 0 ] && printf '    …%ss\n' "$i"
  sleep 1
done
if [ -z "$PRONTO" ]; then
  errore "Il server non è partito. Ultime righe del registro ($LOG):"
  tail -n 15 "$LOG" | sed 's/^/      /'
  esci 1
fi
ok "Server acceso su $URL"
if salute | grep -q '"pt": {"ok": true\|"pt":{"ok":true'; then
  ok "Packet Tracer collegato"
else
  avviso "Packet Tracer non risponde ancora: apri ${B}Extensions → MCP BUILDER${N}. Il gioco si ricollega da solo."
fi

# ── 4. Funnel ─────────────────────────────────────────────────────────────────
INDIRIZZO_REMOTO=""
if [ "$REMOTO" = "s" ]; then
  passo "Pubblico il gioco con Tailscale Funnel"
  if "$TS" funnel --bg "$PORT" >>"$LOG" 2>&1; then
    FUNNEL_ON=1
    INDIRIZZO_REMOTO=$("$TS" funnel status 2>/dev/null | grep -o 'https://[^ ]*' | head -1)
    ok "Funnel attivo${INDIRIZZO_REMOTO:+: $INDIRIZZO_REMOTO}"
  else
    avviso "Il Funnel non è partito (è abilitato per la tua tailnet? sei collegato a Tailscale?). Dettagli in $LOG."
    avviso "Si gioca solo su questo computer."
  fi
fi

# ── 5. pronti ─────────────────────────────────────────────────────────────────
apri "$URL"
printf '\n%s  ┌──────────────────────────────────────────────────────────┐%s\n' "$C" "$N"
printf '%s  │%s  Gioca su:  %s%-45s%s%s│%s\n' "$C" "$N" "$B" "$URL" "$N" "$C" "$N"
[ -n "$INDIRIZZO_REMOTO" ] && printf '%s  │%s  Da fuori:  %s%-45s%s%s│%s\n' "$C" "$N" "$B" "$INDIRIZZO_REMOTO" "$N" "$C" "$N"
printf '%s  │%s  Codice:    %s%-45s%s%s│%s\n' "$C" "$N" "$B" "${CODICE:-nessuno, entri direttamente}" "$N" "$C" "$N"
printf '%s  └──────────────────────────────────────────────────────────┘%s\n' "$C" "$N"
printf '\n  Lascia aperta questa finestra: chiudendola, o con Ctrl+C, il gioco si ferma.\n'
printf '  Registro del server: %s\n' "$LOG"

wait "$SERVER_PID"
STATO=$?
SERVER_PID=""
if [ "$STATO" -ne 0 ] && [ "$STATO" -ne 130 ] && [ "$STATO" -ne 143 ]; then
  errore "Il server si è fermato (codice $STATO). Ultime righe del registro:"
  tail -n 15 "$LOG" | sed 's/^/      /'
  esci 1
fi

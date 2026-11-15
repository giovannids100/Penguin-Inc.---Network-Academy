"""Collegamento a Packet Tracer: un client MCP verso `packet-tracer-mcp` e una fotografia veloce del tavolo.

Browser ──HTTP──▶ server.py ──MCP stdio──▶ packet-tracer-mcp ──bridge :54321──▶ Packet Tracer

- PTLink: la sessione MCP. Ogni chiamata a PT passa da un unico lock asyncio: PT esegue uno script alla volta.
- Topo: la fotografia della rete (dispositivi, porte, cavi) con le funzioni per interrogarla.

Riferimento completo: docs/ARCHITETTURA.md, «Il collegamento a Packet Tracer».
"""
from __future__ import annotations

import asyncio
import ipaddress
import json
import os
import re
import time
from contextlib import AsyncExitStack
from dataclasses import dataclass, field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Fotografia in sola lettura del tavolo, eseguita nello Script Engine di PT. Testo fisso, mai input dell'utente.
# Solo metodi del riferimento Script Engine della skill packet-tracer o provati dal vivo, ognuno dentro
# try/catch (un errore non gestito apre una finestra modale che blocca PT). Mai for…in su oggetti di PT.
SNAPSHOT_JS = r"""
try{var net=ipc.network();var names=getDevices("");var devs=[];var links={};
for(var i=0;i<names.length;i++){var d=net.getDevice(names[i]);if(!d)continue;
 var t=-1;try{t=d.getType();}catch(e){}if(t===45)continue;
 var ps=[];try{ps=d.getPorts();}catch(e){}var ports=[];
 for(var j=0;j<ps.length;j++){var pn=ps[j];
  if(pn.indexOf("Bluetooth")===0||pn.indexOf("Vlan")===0||pn.indexOf("Wireless")===0)continue;
  var p=d.getPort(pn);if(!p)continue;
  var o={n:pn,ip:"",mask:"",up:false,on:true,link:false,vlan:null};
  try{o.ip=String(p.getIpAddress()||"");}catch(e){}
  try{o.mask=String(p.getSubnetMask()||"");}catch(e){}
  try{o.up=!!p.isPortUp();}catch(e){}
  try{o.on=!!p.isPowerOn();}catch(e){}
  if(t===1||t===16){try{o.vlan=p.isAccessPort()?Number(p.getAccessVlan()):"trunk";}catch(e){}
   try{o.psec=!!p.getPortSecurity();}catch(e){}}
  if(t===0){try{o.acl_in=String(p.getAclInID()||"");o.acl_out=String(p.getAclOutID()||"");}catch(e){}}
  var l=null;try{l=p.getLink();}catch(e){}
  if(l){o.link=true;try{var a=l.getPort1(),b=l.getPort2();
   var ka=a.getOwnerDevice().getName()+"|"+a.getName(),kb=b.getOwnerDevice().getName()+"|"+b.getName();
   var k=ka<kb?ka+"#"+kb:kb+"#"+ka;links[k]=String(l.getConnectionType());}catch(e){}}
  ports.push(o);}
 var o2={name:d.getName(),model:"",type:t,x:0,y:0,power:true,ports:ports};
 try{o2.model=String(d.getModel());}catch(e){}
 try{o2.x=d.getXCoordinate();o2.y=d.getYCoordinate();}catch(e){}
 try{o2.power=!!d.getPower();}catch(e){}
 if(t===27){try{var rc=d.enterCommand("show running-config","enable");o2.asa=String(rc.second||"");}catch(e){}}
 if(t===8||t===9){try{o2.gw=String(d.getProcess("HostIpProcess").getDefaultGateway()||"");}catch(e){}
  try{o2.dhcp=!!d.getDhcpFlag();}catch(e){}
  try{o2.dns=String(d.getProcess("DnsClientProcess").getServerIp()||"");}catch(e){}}
 if(t===0){var rs=[];try{var rt=d.getProcess("RoutingProcess").getRoutingTable();var nw=rt.routingNetworks||[];
   for(var a1=0;a1<nw.length;a1++){var en=nw[a1].routingEntries||[];
    for(var b1=0;b1<en.length;b1++){var e1=en[b1];
     rs.push({net:String(e1.networkId),mask:String(e1.subnetMask),via:String(e1.nextHop||""),
              port:String(e1.portName||""),proto:String.fromCharCode(e1.typeOfProtocol)});}}}catch(e){}
  o2.routes=rs;
  var pools=[];try{var ds=d.getProcess("DhcpServerProcess");var pc=ds.getPoolCount();
   for(var q=0;q<pc&&q<20;q++){var pl=ds.getPoolAt(q);var po={name:"",net:"",mask:"",gw:""};
    try{po.name=String(pl.getDhcpPoolName());}catch(e){}
    try{po.net=String(pl.getNetworkAddress());}catch(e){}
    try{po.mask=String(pl.getSubnetMask());}catch(e){}
    try{po.gw=String(pl.getDefaultRouter());}catch(e){}
    try{po.dns=String(pl.getDnsServerIp());}catch(e){}
    pools.push(po);}}catch(e){}
  o2.pools=pools;
  var acls=[];try{var ap=d.getProcess("AclProcess");var na=ap.getAclCount();
   for(var ai=0;ai<na&&ai<50;ai++){var a=ap.getAclAt(ai);if(!a)continue;var cm=[];var cc=0;
    try{cc=a.getCommandCount();}catch(e){}
    for(var cj=0;cj<cc&&cj<100;cj++){try{cm.push(String(a.getCommandAt(cj)));}catch(e){}}
    var ao={id:"",extended:null,rules:cm};try{ao.id=String(a.getAclId());}catch(e){}
    try{ao.extended=!!a.isExtended();}catch(e){}acls.push(ao);}}catch(e){}
  o2.acls=acls;}
 devs.push(o2);}
var ls=[];for(var k2 in links){var s=k2.split("#");var A=s[0].split("|"),B=s[1].split("|");
 ls.push({a:A[0],pa:A[1],b:B[0],pb:B[1],cable:links[k2]});}
reportResult(JSON.stringify({devices:devs,links:ls}));}catch(e){reportResult(JSON.stringify({error:String(e)}));}
"""

# Codice getType() di Packet Tracer → tipo usato dal gioco. Tutto il resto diventa "other".
KIND_BY_TYPE = {0: "router", 1: "switch", 16: "switch", 8: "pc", 9: "server", 27: "firewall"}
ZERO = ("", "0.0.0.0")  # valori che PT usa per "nessun indirizzo"


def parse_asa(text: str) -> dict:
    """La configurazione di un ASA (show running-config) → zone, ACL e assegnazioni.

    zones: [{"port", "nameif", "level"}] solo per le porte con un nome di zona;
    acls: {nome: [righe dopo «access-list NOME extended»]}; groups: {zona: nome ACL applicata in ingresso};
    routes: [{"zone", "net", "mask", "via"}] le rotte statiche («route zona rete maschera via»).
    """
    zones, acls, groups, routes, cur = [], {}, {}, [], None
    for line in text.splitlines():
        m = re.match(r"^interface (\S+)", line)
        if m:
            cur = {"port": m.group(1), "nameif": "", "level": None}
            zones.append(cur)
            continue
        if line.startswith(" ") and cur is not None:
            m = re.match(r"^\s+nameif (\S+)", line)
            if m:
                cur["nameif"] = m.group(1)
            m = re.match(r"^\s+security-level (\d+)", line)
            if m:
                cur["level"] = int(m.group(1))
            continue
        cur = None
        m = re.match(r"^access-list (\S+) extended (.+)$", line)
        if m:
            acls.setdefault(m.group(1), []).append(m.group(2).strip())
        m = re.match(r"^access-group (\S+) in interface (\S+)", line)
        if m:
            groups[m.group(2)] = m.group(1)
        m = re.match(r"^route (\S+) ([\d.]+) ([\d.]+) ([\d.]+)", line)
        if m:
            routes.append({"zone": m.group(1), "net": m.group(2), "mask": m.group(3), "via": m.group(4)})
    return {"zones": [z for z in zones if z["nameif"]], "acls": acls, "groups": groups, "routes": routes}


def short_port(name: str) -> str:
    """Nome corto di una porta, come in IOS: GigabitEthernet0/1 → Gi0/1, FastEthernet0 → Fa0."""
    for long, short in (("GigabitEthernet", "Gi"), ("FastEthernet", "Fa"), ("Serial", "Se"), ("Ethernet", "Eth")):
        if name.startswith(long):
            return short + name[len(long):]
    return name


@dataclass
class Topo:
    """La fotografia della rete, con le funzioni che servono a missioni e livelli.

    devices e links hanno lo stesso formato del campo «topology» dell'API (docs/API.md), più «kind».
    """
    devices: list[dict] = field(default_factory=list)
    links: list[dict] = field(default_factory=list)

    @classmethod
    def parse(cls, data: dict) -> "Topo":
        """Costruisce la Topo dal JSON dello snapshot, aggiungendo «kind» a ogni dispositivo."""
        for d in data["devices"]:
            d["kind"] = KIND_BY_TYPE.get(d["type"], "other")
            if d["kind"] == "firewall":
                d["fw"] = parse_asa(d.pop("asa", ""))
        return cls(data["devices"], data["links"])

    def dev(self, name: str) -> dict | None:
        """Il dispositivo con quel nome, o None."""
        return next((d for d in self.devices if d["name"] == name), None)

    def of(self, kind: str) -> list[dict]:
        """Tutti i dispositivi di un tipo (router, switch, pc, server)."""
        return [d for d in self.devices if d["kind"] == kind]

    def hosts(self) -> list[dict]:
        """Tutti i PC e i server."""
        return [d for d in self.devices if d["kind"] in ("pc", "server")]

    @staticmethod
    def port(d: dict, name: str) -> dict | None:
        """La porta con quel nome (completo) del dispositivo d, o None."""
        return next((p for p in d["ports"] if p["n"] == name), None)

    @staticmethod
    def iface(d: dict) -> ipaddress.IPv4Interface | None:
        """Il primo IPv4 configurato di un host (169.254.x.x vuol dire che il DHCP non ha risposto: nessun indirizzo)."""
        for p in d["ports"]:
            if p["ip"] not in ZERO and p["mask"] not in ZERO and not p["ip"].startswith("169.254."):
                try:
                    return ipaddress.IPv4Interface(f"{p['ip']}/{p['mask']}")
                except ValueError:
                    return None
        return None

    @staticmethod
    def port_iface(p: dict) -> ipaddress.IPv4Interface | None:
        """L'IPv4 di una porta (indirizzo + maschera), o None."""
        if p["ip"] in ZERO or p["mask"] in ZERO:
            return None
        try:
            return ipaddress.IPv4Interface(f"{p['ip']}/{p['mask']}")
        except ValueError:
            return None

    def neighbors(self, name: str) -> list[tuple[str, str, str]]:
        """(mia_porta, vicino, porta_del_vicino) per ogni cavo del dispositivo."""
        out = []
        for l in self.links:
            if l["a"] == name:
                out.append((l["pa"], l["b"], l["pb"]))
            elif l["b"] == name:
                out.append((l["pb"], l["a"], l["pa"]))
        return out

    def switch_of(self, host: str) -> str | None:
        """Lo switch a cui è collegato l'host, o None."""
        for _, peer, _ in self.neighbors(host):
            d = self.dev(peer)
            if d and d["kind"] == "switch":
                return peer
        return None

    def hosts_on(self, switch: str) -> list[dict]:
        """Gli host collegati direttamente allo switch."""
        return [d for d in self.hosts() if self.switch_of(d["name"]) == switch]

    def router_ports(self, kind_filter: str | None = None) -> list[tuple[dict, dict, ipaddress.IPv4Interface | None, str | None]]:
        """(router, porta, interfaccia IPv4 o None, vicino o None) per ogni porta di ogni router.

        Con kind_filter restituisce solo le porte cablate verso un dispositivo di quel tipo.
        """
        out = []
        for r in self.of("router"):
            peers = {mp: peer for mp, peer, _ in self.neighbors(r["name"])}
            for p in r["ports"]:
                peer = peers.get(p["n"])
                if kind_filter:
                    pd = self.dev(peer) if peer else None
                    if not pd or pd["kind"] != kind_filter:
                        continue
                out.append((r, p, self.port_iface(p), peer))
        return out

    def free_port(self, d: dict, peer_kind: str) -> str | None:
        """La prima porta libera di d adatta a collegare un dispositivo di tipo peer_kind (sottointerfacce escluse).

        Switch: Gigabit verso router e switch, FastEthernet verso gli host. Router: Gigabit, poi Fast, poi seriali.
        """
        if d["kind"] == "switch":
            fams = ["GigabitEthernet", "FastEthernet"] if peer_kind in ("router", "switch") else ["FastEthernet", "GigabitEthernet"]
        elif d["kind"] == "router":
            fams = ["GigabitEthernet", "FastEthernet", "Serial"]
        elif d["kind"] == "firewall":
            fams = ["GigabitEthernet"]
        else:
            fams = ["FastEthernet", "GigabitEthernet", "Ethernet"]
        for fam in fams:
            for p in d["ports"]:
                if p["n"].startswith(fam) and "." not in p["n"] and not p["link"]:
                    return p["n"]
        return None

    def next_name(self, prefix: str) -> str:
        """Il primo nome libero con quel prefisso: PC1, PC2, …"""
        used = {d["name"] for d in self.devices}
        i = 1
        while f"{prefix}{i}" in used:
            i += 1
        return f"{prefix}{i}"

    def to_json(self) -> dict:
        """La forma pubblica della topologia (campo «topology» dello Stato)."""
        return {"devices": self.devices, "links": self.links}


# Riga finale di pt_cli: «Final prompt: R1#  (mode: enable)». Con la console chiusa il prompt è
# «Username:» o «Password:» e il modo «logout».
FINAL_RE = re.compile(r"Final prompt:\s*(.*?)\s*\(mode:\s*([\w-]+)\)")
# Segni che i comandi sono finiti in un prompt di login invece che in IOS.
LOCKED_RE = re.compile(r"Final prompt:\s*(Username:|Password:)|% Login invalid|% Bad secrets|% Access denied")


def console_prompt(out: str) -> tuple[str, str]:
    """(prompt, modo) dall'output di pt_cli; ("", "") se non c'è la riga finale."""
    m = FINAL_RE.search(out)
    return (m.group(1).strip(), m.group(2)) if m else ("", "")


class PTError(RuntimeError):
    """Packet Tracer non ha risposto o uno strumento MCP ha risposto con un errore. Il server lo traduce in 502."""


class PTLink:
    """La sessione MCP verso packet-tracer-mcp.

    Tutti i metodi che parlano con PT presuppongono che il chiamante abbia già preso self.lock.
    """

    def __init__(self) -> None:
        self.session: ClientSession | None = None
        self.stack: AsyncExitStack | None = None
        self.lock = asyncio.Lock()
        self.topo = Topo()
        self.snap_at = 0.0
        self.status = "avvio…"
        self.ok = False
        self.links_dirty = False

    async def start(self) -> None:
        """Lancia packet-tracer-mcp (variabile PT_MCP_CMD, default «uvx packet-tracer-mcp --stdio»), controlla il bridge e legge il tavolo."""
        self.stack = AsyncExitStack()
        cmd = os.environ.get("PT_MCP_CMD", "uvx packet-tracer-mcp --stdio").split()
        params = StdioServerParameters(command=cmd[0], args=cmd[1:], env=dict(os.environ))
        r, w = await self.stack.enter_async_context(stdio_client(params))
        self.session = await self.stack.enter_async_context(ClientSession(r, w))
        await self.session.initialize()
        try:
            st = await self.call("pt_bridge_status", {}, 30)
            self.ok = "CONNECTED" in st
            self.status = st.splitlines()[0] if st else "?"
            await self.refresh()
        except Exception as e:  # noqa: BLE001
            self.ok, self.status = False, f"errore: {e}"

    async def stop(self) -> None:
        """Chiude la sessione MCP e il processo figlio."""
        if self.stack:
            await self.stack.aclose()

    async def call(self, tool: str, args: dict | None = None, timeout: float = 120) -> str:
        """Chiama uno strumento MCP e restituisce il testo della risposta. PTError se fallisce o va oltre il timeout."""
        if self.session is None:
            raise PTError("MCP non avviato")
        try:
            res = await asyncio.wait_for(self.session.call_tool(tool, args or {}), timeout)
        except asyncio.TimeoutError:
            raise PTError(f"{tool}: Packet Tracer non ha risposto in {timeout:.0f} s")
        text = "\n".join(getattr(c, "text", "") for c in res.content)
        try:  # quasi tutti gli strumenti avvolgono il testo in {"result": "..."}
            obj = json.loads(text)
            if isinstance(obj, dict) and set(obj) == {"result"}:
                text = str(obj["result"])
        except Exception:
            pass
        if getattr(res, "isError", None) or getattr(res, "is_error", None):
            raise PTError(text)
        return text

    async def refresh(self) -> Topo:
        """Rilegge il tavolo con lo snapshot (circa 1 s), aggiorna self.topo e lo restituisce."""
        raw = await self.call("pt_send_raw", {"js_code": SNAPSHOT_JS, "wait_result": True}, 30)
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            self.ok, self.status = False, raw[:200]
            raise PTError(f"lettura canvas fallita: {raw[:200]}")
        data = json.loads(m.group(0))
        if isinstance(data, dict) and "result" in data and isinstance(data["result"], str):
            data = json.loads(data["result"])
        if "error" in data:
            raise PTError(f"lettura canvas: {data['error']}")
        self.topo = Topo.parse(data)
        self.snap_at = time.time()
        self.ok, self.status = True, "connesso"
        return self.topo

    async def settle(self) -> None:
        """Se links_dirty, fa avanzare il tempo di PT: STP, ARP e DHCP si assestano subito invece che in ~30 s."""
        if self.links_dirty:
            try:
                await self.call("pt_fast_forward", {}, 30)
            except Exception:
                pass
            self.links_dirty = False

    async def ping(self, src: str, ip: str, creds: dict | None = None) -> tuple[bool, str]:
        """Ping vero da un dispositivo, 4 pacchetti, un tentativo solo: (riuscito, output).

        Riuscito = almeno 2 risposte su 4: il primo pacchetto può morire sull'ARP, e un tentativo in più
        costerebbe ~24 s quando il ping fallisce davvero (ogni pacchetto perso aspetta il suo timeout).
        PC e server: «ping -n 4» dal prompt dei comandi. Router e switch: «ping IP repeat 4», che richiede la
        modalità privilegiata (con creds fa prima il login; se la console resta chiusa usa il ping semplice
        da utente, 5 pacchetti).
        """
        await self.settle()
        d = self.topo.dev(src)
        if d and d["kind"] in ("router", "switch"):
            if creds:
                await self.unlock(src, creds)
            out = await self.call("pt_cli", {"device": src, "commands": ["enable", f"ping {ip} repeat 4"],
                                             "timeout": 40}, 90)
            if "Success rate" not in out:  # enable chiede una password che non abbiamo: ping da utente
                out = await self.call("pt_cli", {"device": src, "commands": ["", f"ping {ip}"], "timeout": 40}, 90)
            m = re.search(r"Success rate is \d+ percent \((\d+)/(\d+)\)", out)
            return bool(m and int(m.group(1)) >= 2), out
        out = await self.call("pt_host_command", {"device": src, "command": f"ping -n 4 {ip}", "timeout": 40}, 90)
        m = re.search(r"Received = (\d+)", out)
        return bool(m and int(m.group(1)) >= 2), out

    async def cli(self, device: str, commands: list[str], timeout: float = 30) -> tuple[bool, str]:
        """Scrive righe IOS nella console di router o switch: (nessuna riga rifiutata, testo della console)."""
        out = await self.call("pt_cli", {"device": device, "commands": commands, "timeout": timeout},
                              timeout * len(commands) + 30)
        bad = re.search(r"\b(ERROR|UNKNOWN COMMAND|TIMEOUT)\b", out)
        return (not bad), out

    async def unlock(self, device: str, creds: dict) -> None:
        """Porta la console di un dispositivo protetto in modalità privilegiata (prompt «#»).

        creds: {"username"?, "secret"?, "enable_secret"?}. Gestisce il login locale (Username/Password,
        attivato dall'hardening con utenti) e la password di enable. PTError se le credenziali non bastano.
        Misurato su PT 9.0.1: da «Password:» una riga vuota riporta a «Username:».
        """
        prompt, mode = console_prompt(await self.call("pt_cli", {"device": device, "commands": [""]}, 60))
        if mode == "logout" or prompt.endswith(":"):
            if not creds.get("username") or not creds.get("secret"):
                raise PTError(f"la console di {device} chiede utente e password")
            out = await self.call("pt_cli", {"device": device,
                                             "commands": ["", creds["username"], creds["secret"]]}, 60)
            prompt, mode = console_prompt(out)
        if prompt.endswith(">"):
            cmds = ["enable", creds["enable_secret"]] if creds.get("enable_secret") else ["enable"]
            prompt, mode = console_prompt(await self.call("pt_cli", {"device": device, "commands": cmds}, 60))
        if not prompt.endswith("#"):
            raise PTError(f"login su {device} non riuscito (prompt «{prompt or '?'}»): credenziali sbagliate?")

    async def clear_canvas(self) -> None:
        """Cancella tutti i dispositivi dal tavolo di Packet Tracer."""
        await self.refresh()
        for d in list(self.topo.devices):
            await self.call("pt_delete_device", {"device_name": d["name"]}, 30)
        await self.refresh()

#python proxy_master.py version 2.1
"""
─────────────────────────────────────────────────────────────
 Proxy_Master 
 Developer NgaTon 
 If you think this is Ai, go fuck yourself.
 Telegram @NgaT0N
─────────────────────────────────────────────────────────────
"""
import base64
import concurrent.futures
import csv
import os
import platform
import re
import signal
import socket
import ssl
import sys
import threading
import time
import urllib.request
from urllib.parse import urlsplit

# ─────────────────────────────────────────────────────────────
#  CONSTANTS (FIXED)
# ─────────────────────────────────────────────────────────────
VERSION       = "2.1"
DEV           = "NgaTon"
UA            = f"NgaTon-ProxyMaster/{VERSION}"

MAX_MS        = 220         
TIMEOUT       = 3.0         
DEFAULT_WORK  = 100         

TARGET_PRIMARY   = ("example.com",    443)
TARGET_SECONDARY = ("www.google.com", 443)

SOURCES = [
    ("TheSpeedX HTTP",   "http",   "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"),
    ("TheSpeedX SOCKS4", "socks4", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt"),
    ("TheSpeedX SOCKS5", "socks5", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"),
    ("monosans HTTP",    "http",   "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"),
    ("monosans HTTPS",   "https",  "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt"),
    ("monosans SOCKS4",  "socks4", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt"),
    ("monosans SOCKS5",  "socks5", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"),
    ("proxifly all",     "auto",   "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"),
]


IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    try:
        import ctypes
        _k = ctypes.windll.kernel32
        _k.SetConsoleMode(_k.GetStdHandle(-11), 7)
    except Exception:
        os.system("")

# ─────────────────────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────────────────────
R   = "\033[0m"
B   = "\033[1m"
DIM = "\033[2m"
G   = "\033[1;92m"
C   = "\033[1;96m"
Y   = "\033[1;93m"
RD  = "\033[1;91m"
W   = "\033[1;97m"
M   = "\033[1;95m"
BL  = "\033[1;94m"
GRY = "\033[90m"

# Long-name aliases (safety)
WHITE, GREEN, CYAN, YELLOW, RED, RESET, MAGENTA, BLUE = W, G, C, Y, RD, R, M, BL
ANSI_RE = re.compile(r"\033\[[0-9;]*[A-Za-z]")

# ─────────────────────────────────────────────────────────────
#  GLOBAL STATE
# ─────────────────────────────────────────────────────────────
STATE = {
    "working":     [],
    "verified":    [],
    "all_results": [],
    "lock":        threading.Lock(),
    "stop":        threading.Event(),
    "user_stop":   False,
    "saved":       False,
    "script_dir":  os.path.dirname(os.path.abspath(__file__)),
    "abort_count": 0,
}

# ─────────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────────
def banner():
    print(f"""{G}
   ███╗   ██╗ ██████╗  █████╗     ████████╗ ██████╗ ███╗   ██╗
   ████╗  ██║██╔════╝ ██╔══██╗    ╚══██╔══╝██╔═══██╗████╗  ██║
   ██╔██╗ ██║██║  ███╗███████║       ██║   ██║   ██║╚██╗ ██║
   ██║╚██╗██║██║   ██║██╔══██║       ██║   ██║   ██║ ██║╚██╗██║
   ██║ ╚████║╚██████╔╝██║  ██║       ██║   ╚██████╔╝ ██║ ╚████║
   ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═╝  ╚═══╝{R}
{C}  ══════════════════════════════════════════════════════════════
{W}   PROXY MASTER {DIM}v{VERSION}{W}   ·   Developer {M}{DEV}{W}
{C}  ══════════════════════════════════════════════════════════════{R}
""")

def section(num, title):
    pad = "─" * max(2, 50 - len(title))
    print(f"\n{C}  ┌─[{W} {num}. {title} {C}]{pad}{R}")

def ask_choice(prompt, valid, default=None):
    """Loop until a valid choice is entered."""
    while True:
        try:
            v = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise
        if not v and default is not None:
            return default
        if v in valid:
            return v
        print(f"{RD}  ✘ Invalid choice. Please try again.{R}")

def ask_int(prompt, lo, hi, default=None):
    """Loop until a valid integer within [lo, hi] is entered."""
    while True:
        try:
            v = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise
        if not v and default is not None:
            return default
        try:
            n = int(v)
            if lo <= n <= hi:
                return n
            print(f"{RD}  ✘ Enter a number between {lo} and {hi}.{R}")
        except ValueError:
            print(f"{RD}  ✘ Invalid number. Try again.{R}")

def vis_len(s):
    return len(ANSI_RE.sub("", s))

def pad_ansi(s, w):
    vl = vis_len(s)
    if vl > w:
        s = ANSI_RE.sub("", s)[:w]
        vl = len(s)
    return s + " " * (w - vl)

def human_time(sec):
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m"

# ─────────────────────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────────────────────
def parse_entry(line, default_protocol=""):
    line = line.strip().lstrip("\ufeff")
    if not line or line.startswith("#"):
        return None

    if "://" in line:
        try:
            p = urlsplit(line)
            scheme = p.scheme.lower()
            if scheme not in ("http", "https", "socks4", "socks4a", "socks5", "socks5h"):
                return None
            if not p.hostname or p.port is None:
                return None
            return {
                "raw": line, "host": p.hostname, "port": int(p.port),
                "user": p.username, "password": p.password, "hint": scheme,
            }
        except (ValueError, TypeError):
            return None

    if "@" in line:
        try:
            auth, endpoint = line.rsplit("@", 1)
            if ":" not in auth or ":" not in endpoint:
                return None
            user, password = auth.split(":", 1)
            host, port = endpoint.rsplit(":", 1)
            port = int(port)
            if not host or not 1 <= port <= 65535:
                return None
            return {
                "raw": line, "host": host.strip("[]"), "port": port,
                "user": user, "password": password, "hint": default_protocol,
            }
        except ValueError:
            return None

    parts = line.split(":")
    try:
        if len(parts) == 2:
            host, port = parts
            user = password = None
        elif len(parts) == 4:
            host, port, user, password = parts
        else:
            return None
        port = int(port)
        if not host or not 1 <= port <= 65535:
            return None
        return {
            "raw": line, "host": host.strip("[]"), "port": port,
            "user": user, "password": password, "hint": default_protocol,
        }
    except ValueError:
        return None

# ─────────────────────────────────────────────────────────────
#  SOCKET HELPERS
# ─────────────────────────────────────────────────────────────
def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        c = sock.recv(n - len(buf))
        if not c:
            raise OSError("Connection closed")
        buf += c
    return buf

def read_headers(sock, limit=16384):
    data = b""
    while b"\r\n\r\n" not in data and len(data) < limit:
        c = sock.recv(min(2048, limit - len(data)))
        if not c:
            break
        data += c
    if b"\r\n\r\n" not in data:
        raise OSError("Invalid HTTP headers")
    return data

def open_sock(proxy, timeout):
    s = socket.create_connection((proxy["host"], proxy["port"]), timeout=timeout)
    s.settimeout(timeout)
    return s

def auth_hdr(proxy):
    if proxy.get("user") is None:
        return ""
    raw = (proxy["user"] + ":" + (proxy.get("password") or "")).encode()
    return "Proxy-Authorization: Basic " + base64.b64encode(raw).decode() + "\r\n"


def http_connect(proxy, timeout, tls_proxy, host, port):
    s = open_sock(proxy, timeout)
    try:
        if tls_proxy:
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=proxy["host"])
        req = (
            f"CONNECT {host}:{port} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"{auth_hdr(proxy)}"
            f"User-Agent: {UA}\r\n"
            "Proxy-Connection: Keep-Alive\r\n\r\n"
        )
        s.sendall(req.encode("ascii"))
        first = read_headers(s).split(b"\r\n", 1)[0].decode("latin1", "replace")
        m = re.search(r"\s(\d{3})(?:\s|$)", first)
        if not m:
            raise OSError("Bad HTTP proxy response")
        code = int(m.group(1))
        if code != 200:
            if code == 407:
                raise OSError("Auth required (407)")
            raise OSError(f"CONNECT HTTP {code}")
        return s
    except Exception:
        s.close()
        raise

def socks5_connect(proxy, timeout, host, port):
    s = open_sock(proxy, timeout)
    try:
        user = proxy.get("user")
        if user is None:
            s.sendall(b"\x05\x01\x00")
            if recv_exact(s, 2) != b"\x05\x00":
                raise OSError("SOCKS5 no-auth failed")
        else:
            s.sendall(b"\x05\x02\x00\x02")
            rep = recv_exact(s, 2)
            if rep[0] != 5 or rep[1] == 255:
                raise OSError("SOCKS5 auth failed")
            if rep[1] == 2:
                u = user.encode()
                p = (proxy.get("password") or "").encode()
                if len(u) > 255 or len(p) > 255:
                    raise OSError("Credentials too long")
                s.sendall(b"\x01" + bytes([len(u)]) + u + bytes([len(p)]) + p)
                if recv_exact(s, 2)[1] != 0:
                    raise OSError("SOCKS5 creds rejected")
            elif rep[1] != 0:
                raise OSError("SOCKS5 auth unsupported")
        h = host.encode("idna")
        s.sendall(b"\x05\x01\x00\x03" + bytes([len(h)]) + h + port.to_bytes(2, "big"))
        head = recv_exact(s, 4)
        if head[0] != 5 or head[1] != 0:
            raise OSError(f"SOCKS5 code {head[1]}")
        if head[3] == 1:
            recv_exact(s, 6)
        elif head[3] == 4:
            recv_exact(s, 18)
        elif head[3] == 3:
            n = recv_exact(s, 1)[0]
            recv_exact(s, n + 2)
        else:
            raise OSError("Malformed SOCKS5")
        return s
    except Exception:
        s.close()
        raise

def socks4_connect(proxy, timeout, host, port):
    s = open_sock(proxy, timeout)
    try:
        user = (proxy.get("user") or "").encode("utf-8")
        h = host.encode("ascii") + b"\x00"
        s.sendall(b"\x04\x01" + port.to_bytes(2, "big") +
                  b"\x00\x00\x00\x01" + user + b"\x00" + h)
        rep = recv_exact(s, 8)
        if rep[1] != 0x5A:
            raise OSError(f"SOCKS4 code {rep[1]}")
        return s
    except Exception:
        s.close()
        raise

def make_tunnel(proxy, proto, timeout, host, port):
    if proto == "http":
        return http_connect(proxy, timeout, False, host, port)
    if proto == "https":
        return http_connect(proxy, timeout, True, host, port)
    if proto in ("socks5", "socks5h"):
        return socks5_connect(proxy, timeout, host, port)
    if proto in ("socks4", "socks4a"):
        return socks4_connect(proxy, timeout, host, port)
    raise OSError("Unsupported protocol")

# ─────────────────────────────────────────────────────────────
#  VERIFICATION
# ─────────────────────────────────────────────────────────────
def verify_tls(sock, host, timeout):
    sock.settimeout(timeout)
    ctx = ssl.create_default_context()
    tls = ctx.wrap_socket(sock, server_hostname=host)
    try:
        if not tls.getpeercert():
            raise OSError("No TLS cert")
        return tls
    except Exception:
        tls.close()
        raise

def _attempt(proxy, proto, timeout, host, port):
    started = time.perf_counter()
    sock = None
    try:
        sock = make_tunnel(proxy, proto, timeout, host, port)
        tls = verify_tls(sock, host, timeout)
        try:
            tls.close()
        except Exception:
            pass
        return True, (time.perf_counter() - started) * 1000
    except Exception:
        if sock:
            try:
                sock.close()
            except Exception:
                pass
        return False, (time.perf_counter() - started) * 1000

def check_proxy(proxy, protocol, timeout, max_ms, host, port):
    if protocol == "auto":
        hint = proxy.get("hint", "")
        if hint and hint != "auto":
            order = [hint] + [p for p in ("http", "https", "socks5", "socks4")
                              if p != hint]
        else:
            order = ["http", "https", "socks5", "socks4"]
    else:
        order = [protocol]

    for p in order:
        ok, ms = _attempt(proxy, p, timeout, host, port)
        if ok:
            if ms > max_ms:
                return {
                    "raw": proxy["raw"], "host": proxy["host"], "port": proxy["port"],
                    "user": proxy.get("user"), "password": proxy.get("password"),
                    "status": "SLOW", "protocol": p.upper(), "ms": ms,
                    "error": f">{max_ms}ms",
                }
            return {
                "raw": proxy["raw"], "host": proxy["host"], "port": proxy["port"],
                "user": proxy.get("user"), "password": proxy.get("password"),
                "status": "WORKING", "protocol": p.upper(), "ms": ms, "error": "",
            }

    return {
        "raw": proxy["raw"], "host": proxy["host"], "port": proxy["port"],
        "user": proxy.get("user"), "password": proxy.get("password"),
        "status": "DEAD", "protocol": "-", "ms": None, "error": "",
    }

# ─────────────────────────────────────────────────────────────
#  LIVE BOX UI
# ─────────────────────────────────────────────────────────────
BOX_W = 62          

class LiveBox:
    """A fixed-size box that redraws in place."""
    def __init__(self, title="NgaTon Proxy Master", max_rows=5):
        self.title = title
        self.max_rows = max_rows
        self.recent = []
        self.rendered = 0
        self.hidden_cursor = False

    def hide_cursor(self):
        if not self.hidden_cursor:
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
            self.hidden_cursor = True

    def show_cursor(self):
        if self.hidden_cursor:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
            self.hidden_cursor = False

    def push(self, result):
        self.recent.append(result)
        if len(self.recent) > self.max_rows:
            self.recent.pop(0)

    def _row(self, text):
        return "│ " + pad_ansi(text, BOX_W - 2) + " │"

    def _hline(self, ch="─"):
        return ch + ch * BOX_W + ch

    def draw(self, s):
        inner = BOX_W - 2
        lines = []
        lines.append(self._hline("┌"))
        lines.append(self._row(f"{G}{self.title}{R}"))
        lines.append(self._hline("├"))

        # progress
        pct = s["done"] / max(s["total"], 1)
        bw = inner - 18
        filled = int(bw * pct)
        bar = "█" * filled + "░" * (bw - filled)
        lines.append(self._row(f"{W}Progress{R} [{C}{bar}{R}] {W}{pct*100:5.1f}%{R}"))

       
        lines.append(self._row(
            f"{W}Checked {C}{s['done']}{W}/{s['total']}{R}   "
            f"{W}Working {G}{s['ok']}{W}/{s['target']}{R}   "
            f"{W}Dead {RD}{s['dead']}{R}"
        ))

        
        best = f"{s['best']:.0f}ms" if s.get("best") is not None else "-"
        lines.append(self._row(
            f"{W}Speed {C}{s['speed']:.0f}/s{R}   "
            f"{W}ETA {C}{s['eta']}{R}   "
            f"{W}Best {G}{best}{R}"
        ))
        lines.append(self._hline("├"))

        # recent results
        for i in range(self.max_rows):
            if i < len(self.recent):
                lines.append(self._row(self._fmt(self.recent[i])))
            else:
                lines.append(self._row(""))
        lines.append(self._hline("└"))

        out = []
        if self.rendered:
            out.append(f"\033[{self.rendered}A")
        for ln in lines:
            out.append("\033[K" + ln + "\n")
        sys.stdout.write("".join(out))
        sys.stdout.flush()
        self.rendered = len(lines)

    def _fmt(self, r):
        hp = f'{r["host"]}:{r["port"]}'
        if len(hp) > 22:
            hp = hp[:21] + "…"
        if r["status"] == "WORKING":
            icon = f"{G}✔{R}"
            color = G
        elif r["status"] == "SLOW":
            icon = f"{Y}●{R}"
            color = Y
        else:
            icon = f"{RD}✘{R}"
            color = RD
        lat = f'{r["ms"]:.0f}ms' if r["ms"] is not None else "-"
        proto = r["protocol"] if r["protocol"] != "-" else "-"
        return f'{icon} {W}{hp:<22}{R} {C}{proto:<6}{R} {Y}{lat:>7}{R} {color}{r["status"]}{R}'

    def finalize(self):
        """Print the box one last time and move on."""
        self.rendered = 0
        self.show_cursor()
        print()

# ─────────────────────────────────────────────────────────────
#  FETCHER
# ─────────────────────────────────────────────────────────────
def fetch_source(src, timeout):
    name, proto, url = src
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=max(timeout, 6.0)) as r:
            body = r.read(12 * 1024 * 1024).decode("utf-8", "replace")
        entries = []
        for line in body.splitlines():
            it = parse_entry(line, proto)
            if it:
                entries.append(it)
        return name, entries, None
    except Exception as e:
        return name, [], str(e)[:120]

def fetch_all(timeout):
    print(f"\n{W}[*] Fetching public proxy lists...{R}")
    entries, seen = [], set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(SOURCES), 8)) as pool:
        futs = [pool.submit(fetch_source, s, timeout) for s in SOURCES]
        for fut in concurrent.futures.as_completed(futs):
            name, items, err = fut.result()
            if items:
                print(f"{G}  [+] {name:<22} {len(items):>6} entries{R}")
                for it in items:
                    key = (it["host"], it["port"], it.get("user"), it.get("password"))
                    if key not in seen:
                        seen.add(key)
                        entries.append(it)
            else:
                print(f"{Y}  [!] {name:<22} {err or 'empty'}{R}")
    return entries

# ─────────────────────────────────────────────────────────────
#  SAVE / SIGNAL
# ─────────────────────────────────────────────────────────────
def _fmt_out(r):
    raw = r["raw"]
    if "://" in raw:
        return raw
    scheme = (r.get("protocol") or "http").lower()
    if scheme in ("-", "", "auto"):
        scheme = "http"
    u, p = r.get("user"), r.get("password")
    auth = f"{u}:{p}@" if (u and p) else (f"{u}@" if u else "")
    return f"{scheme}://{auth}{r['host']}:{r['port']}"

def save_all(prefix="proxy"):
    with STATE["lock"]:
        if STATE["saved"]:
            return STATE.get("_paths", [])
        STATE["saved"] = True
        working  = list(STATE["working"])
        verified = list(STATE["verified"])
        allres   = list(STATE["all_results"])

    finals = verified if verified else working
    finals = sorted(finals, key=lambda r: (r["ms"] if r["ms"] is not None else 1e9))

    d = STATE["script_dir"]
    p_good = os.path.join(d, f"{prefix}.txt")
    p_dead = os.path.join(d, f"{prefix}_dead.txt")
    p_all  = os.path.join(d, f"{prefix}_all.txt")
    p_rep  = os.path.join(d, f"{prefix}_report.csv")

    try:
        with open(p_good, "w", encoding="utf-8") as f:
            for r in finals:
                f.write(_fmt_out(r) + "\n")
    except OSError as e:
        print(f"{RD}[!] write {p_good}: {e}{R}")

    try:
        with open(p_dead, "w", encoding="utf-8") as f:
            for r in allres:
                if r["status"] != "WORKING":
                    f.write(r["raw"] + "\n")
    except OSError:
        pass

    try:
        with open(p_all, "w", encoding="utf-8") as f:
            for r in allres:
                f.write(r["raw"] + "\n")
    except OSError:
        pass

    try:
        with open(p_rep, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["proxy", "host", "port", "status", "type", "latency_ms"])
            for r in allres:
                w.writerow([
                    r["raw"], r["host"], r["port"], r["status"], r["protocol"],
                    f'{r["ms"]:.1f}' if r["ms"] is not None else "",
                ])
    except OSError:
        pass

    paths = [p_good, p_dead, p_all, p_rep]
    STATE["_paths"] = paths
    return paths

def install_signals():
    def handler(signum, frame):
        STATE["abort_count"] += 1
        if STATE["abort_count"] >= 2:
            try:
                save_all()
            except Exception:
                pass
            sys.stdout.write("\033[?25h\n")
            print(f"\n{RD}[!] Force exit.{R}")
            os._exit(130)
        STATE["stop"].set()
        STATE["user_stop"] = True
    try:
        signal.signal(signal.SIGINT,  handler)
        signal.signal(signal.SIGTERM, handler)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────
#  INTERACTIVE SETUP 
# ─────────────────────────────────────────────────────────────
def interactive_setup():
    banner()

    section(1, "PROTOCOL")
    print(f"  {W}[1]{R} AUTO  {DIM}(recommended — tries all){R}")
    print(f"  {W}[2]{R} HTTP")
    print(f"  {W}[3]{R} HTTPS  {DIM}(TLS to proxy){R}")
    print(f"  {W}[4]{R} SOCKS4")
    print(f"  {W}[5]{R} SOCKS5")
    p = ask_choice(f"{C}  ➤ Choose [1-5] (default 1): {W}", {"1","2","3","4","5"}, "1")
    protocol = {"1": "auto", "2": "http", "3": "https",
                "4": "socks4", "5": "socks5"}[p]

    section(2, "TARGET COUNT")
    target = ask_int(f"{C}  ➤ How many WORKING proxies? (1-10000, default 30): {W}",
                     1, 10000, 30)

    section(3, "WORKERS")
    print(f"  {DIM}Higher = faster but may trigger rate limits.{R}")
    workers = ask_int(f"{C}  ➤ Concurrent workers (1-500, default {DEFAULT_WORK}): {W}",
                      1, 500, DEFAULT_WORK)

    # Fixed settings display
    print(f"\n{C}  ╔{'═' * 56}╗{R}")
    print(f"{C}  ║{W}  CONFIGURATION{' ' * 41}{C}║{R}")
    print(f"{C}  ╠{'═' * 56}╣{R}")
    rows = [
        ("Protocol",  protocol.upper()),
        ("Target",    f"{target} working proxies"),
        ("Workers",   str(workers)),
        ("Max ms",    f"{MAX_MS} ms  {DIM}(fixed){R}"),
        ("Timeout",   f"{TIMEOUT:.1f}s  {DIM}(fixed){R}"),
    ]
    for k, v in rows:
        pad = 56 - len(k) - vis_len(str(v)) - 4
        print(f"{C}  ║{W}  {k:<11}{Y}{v}{' ' * pad}{C}║{R}")
    print(f"{C}  ╚{'═' * 56}╝{R}")

    if ask_choice(f"\n{C}  ➤ Start scan? [Y/n]: {W}",
                  {"y", "Y", "yes", "YES", "n", "N", "no", "NO", ""}, "y").lower() \
            not in ("y", "yes", ""):
        print(f"{Y}  Cancelled.{R}")
        return None

    return {"protocol": protocol, "target": target, "workers": workers}

# ─────────────────────────────────────────────────────────────
#  SCAN (with live box)
# ─────────────────────────────────────────────────────────────
def scan(candidates, cfg):
    total    = len(candidates)
    target   = cfg["target"]
    workers  = cfg["workers"]
    protocol = cfg["protocol"]

    box = LiveBox(f"NgaTon Proxy Master v{VERSION} — SCANNING", max_rows=5)
    box.hide_cursor()

    counters = {"done": 0, "ok": 0, "dead": 0, "slow": 0, "best": None}
    start = time.time()

    def refresh():
        elapsed = time.time() - start
        speed = counters["done"] / max(elapsed, 0.1)
        remaining = total - counters["done"]
        eta = remaining / max(speed, 0.01)
        box.draw({
            "done":   counters["done"],
            "total":  total,
            "ok":     counters["ok"],
            "dead":   counters["dead"],
            "target": target,
            "speed":  speed,
            "eta":    human_time(eta) if counters["done"] < total else "done",
            "best":   counters["best"],
        })

    refresh()

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
    futures = {pool.submit(check_proxy, p, protocol, TIMEOUT, MAX_MS,
                           TARGET_PRIMARY[0], TARGET_PRIMARY[1]): p
               for p in candidates}

    try:
        for fut in concurrent.futures.as_completed(futures):
            if STATE["stop"].is_set():
                break
            try:
                r = fut.result()
            except Exception:
                p = futures[fut]
                r = {"raw": p["raw"], "host": p["host"], "port": p["port"],
                     "user": p.get("user"), "password": p.get("password"),
                     "status": "ERROR", "protocol": "-", "ms": None, "error": ""}

            counters["done"] += 1
            with STATE["lock"]:
                STATE["all_results"].append(r)
                if r["status"] == "WORKING":
                    STATE["working"].append(r)
                    counters["ok"] += 1
                    if counters["best"] is None or (r["ms"] or 1e9) < counters["best"]:
                        counters["best"] = r["ms"]
                elif r["status"] == "SLOW":
                    counters["slow"] += 1
                else:
                    counters["dead"] += 1

            box.push(r)
            refresh()

            if counters["ok"] >= target:
                STATE["stop"].set()
                break
    finally:
        for f in futures:
            f.cancel()
        try:
            pool.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            pool.shutdown(wait=False)

    box.finalize()
    return counters["ok"]

# ─────────────────────────────────────────────────────────────
#  RE-VERIFY (with live box)
# ─────────────────────────────────────────────────────────────
def reverify(cfg):
    with STATE["lock"]:
        working = list(STATE["working"])
    if not working:
        return []

    protocol = cfg["protocol"]
    workers  = min(len(working), cfg["workers"])

    box = LiveBox(f"NgaTon Proxy Master v{VERSION} — VERIFYING", max_rows=5)
    box.hide_cursor()

    verified = []
    counters = {"done": 0, "ok": 0, "dead": 0, "slow": 0, "best": None}
    total = len(working)
    start = time.time()

    def refresh():
        elapsed = time.time() - start
        speed = counters["done"] / max(elapsed, 0.1)
        eta = (total - counters["done"]) / max(speed, 0.01)
        box.draw({
            "done":   counters["done"],
            "total":  total,
            "ok":     counters["ok"],
            "dead":   counters["dead"],
            "target": total,
            "speed":  speed,
            "eta":    human_time(eta) if counters["done"] < total else "done",
            "best":   counters["best"],
        })

    refresh()

    def _reverify_one(r):
        proxy = {"raw": r["raw"], "host": r["host"], "port": r["port"],
                 "user": r.get("user"), "password": r.get("password"),
                 "hint": (r["protocol"].lower() if r["protocol"] not in ("-", "") else "")}
        proto = r["protocol"].lower() if r["protocol"] not in ("-", "") else "auto"
        ok1, ms1 = _attempt(proxy, proto, TIMEOUT,
                            TARGET_PRIMARY[0], TARGET_PRIMARY[1])
        if not ok1:
            return None, ms1
        ok2, _ = _attempt(proxy, proto, TIMEOUT,
                          TARGET_SECONDARY[0], TARGET_SECONDARY[1])
        if not ok2:
            return None, ms1
        out = dict(r); out["ms"] = ms1
        return out, ms1

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(_reverify_one, r): r for r in working}
        for fut in concurrent.futures.as_completed(futs):
            if STATE["stop"].is_set() and STATE["user_stop"]:
                break
            counters["done"] += 1
            orig = futs[fut]
            try:
                res, ms = fut.result()
            except Exception:
                res, ms = None, None

            if res is not None:
                verified.append(res)
                counters["ok"] += 1
                if counters["best"] is None or (ms or 1e9) < counters["best"]:
                    counters["best"] = ms
                box.push(res)
            else:
                counters["dead"] += 1
                fake = dict(orig); fake["status"] = "DROPPED"; fake["protocol"] = "-"
                fake["ms"] = ms
                box.push(fake)

            refresh()

    box.finalize()
    return verified

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
def run():
    STATE["script_dir"] = os.path.dirname(os.path.abspath(__file__))

    try:
        cfg = interactive_setup()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Y}[!] Cancelled.{R}")
        return 130
    if not cfg:
        return 0

   
    candidates = fetch_all(TIMEOUT)
    if not candidates:
        print(f"{RD}[!] No candidates loaded. Check internet.{R}")
        return 2
    print(f"{G}[+] Unique candidates: {len(candidates)}{R}")

    install_signals()
    t0 = time.time()

    try:
        scan(candidates, cfg)

        if not STATE["user_stop"]:
            verified = reverify(cfg)
            with STATE["lock"]:
                STATE["verified"] = verified
                STATE["working"]  = verified
        else:
            print(f"\n{Y}[!] Stopped by user. Skipping re-verify.{R}")

        paths = save_all("proxy")

        with STATE["lock"]:
            wn = len(STATE["verified"] or STATE["working"])
            tn = len(STATE["all_results"])

        elapsed = time.time() - t0

        print(f"\n{C}  ╔{'═' * 56}╗{R}")
        print(f"{C}  ║{W}  SCAN COMPLETE{' ' * 41}{C}║{R}")
        print(f"{C}  ╠{'═' * 56}╣{R}")
        for k, v in [
            ("Elapsed",  human_time(elapsed)),
            ("Checked",  str(tn)),
            ("Verified", f"{wn} proxies"),
            ("Requested", str(cfg["target"])),
        ]:
            pad = 56 - len(k) - vis_len(str(v)) - 4
            print(f"{C}  ║{W}  {k:<11}{G}{v}{' ' * pad}{C}║{R}")
        print(f"{C}  ╚{'═' * 56}╝{R}")

        print(f"\n{W}  Output files:{R}")
        for p in paths:
            if os.path.isfile(p):
                sz = os.path.getsize(p)
                szs = f"{sz} B" if sz < 1024 else f"{sz/1024:.1f} KB"
                print(f"    {G}▸ {p}{DIM}  ({szs}){R}")

        print(f"\n{Y}  [!] Public proxies are untrusted. Do not send sensitive data.{R}\n")
        return 130 if STATE["user_stop"] else 0

    except KeyboardInterrupt:
        print(f"\n{Y}[!] Interrupted. Saving partial results...{R}")
        paths = save_all("proxy")
        with STATE["lock"]:
            wn = len(STATE["verified"] or STATE["working"])
            tn = len(STATE["all_results"])
        print(f"{G}[+] Saved {wn} working / {tn} checked.{R}")
        for p in paths:
            print(f"    {C}{p}{R}")
        return 130


def main():
    try:
        return run()
    except KeyboardInterrupt:
        try:
            save_all("proxy")
        except Exception:
            pass
        print(f"\n{Y}[!] Stopped. Partial results saved.{R}")
        return 130


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        try:
            save_all("proxy")
        except Exception:
            pass
        os._exit(130)
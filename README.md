# ngaton-proxy-master
<div align="center">

```
   ███╗   ██╗ ██████╗  █████╗     ████████╗ ██████╗ ███╗   ██╗
   ████╗  ██║██╔════╝ ██╔══██╗    ╚══██╔══╝██╔═══██╗████╗  ██║
   ██╔██╗ ██║██║  ███╗███████║       ██║   ██║   ██║╚██╗ ██║
   ██║╚██╗██║██║   ██║██╔══██║       ██║   ██║   ██║ ██║╚██╗██║
   ██║ ╚████║╚██████╔╝██║  ██║       ██║   ╚██████╔╝ ██║ ╚████║
   ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═╝  ╚═══╝
```

# NgaTon Proxy Master

**Ultimate cross-platform proxy hunter & checker.**  
Fetch, verify, and filter proxies in real-time with a clean live-box UI.

![Version](https://img.shields.io/badge/version-2.1-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-yellow)
![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux%20%7C%20Windows%20%7C%20macOS-success)
![License](https://img.shields.io/badge/license-MIT-green)

Developer : **NgaTon**  
Telegram  : [@NgaTON_0](https://t.me/NgaTON_0)  
TikTok    : [@ngat0n](https://tiktok.com/@ngat0n)

</div>

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
   - [Termux (Android)](#1-termux-android)
   - [Linux](#2-linux)
   - [macOS](#3-macos)
   - [Windows](#4-windows)
5. [Usage](#usage)
6. [Recommended Settings per OS](#recommended-settings-per-os)
7. [Customizing the Tool](#customizing-the-tool)
8. [Output Files](#output-files)
9. [How It Works](#how-it-works)
10. [Troubleshooting](#troubleshooting)
11. [Safety Notice](#safety-notice)
12. [Contact](#contact)

---

## Overview

**NgaTon Proxy Master** is a single-file Python 3 tool that:

- Fetches public proxy lists from multiple sources
- Tests each proxy against **two real TLS targets**
- Detects the working protocol (HTTP / HTTPS / SOCKS4 / SOCKS5)
- Filters by maximum latency (default **150 ms**)
- Shows a **clean live box UI** — no terminal spam
- Auto-saves results, even if you press **Ctrl+C**

Built with **Python 3 standard library only** — no `pip install` needed.

---

## Features

| Feature | Description |
|--------|-------------|
| ✅ Zero dependencies | Python 3 standard library only |
| ✅ Cross-platform | Termux, Linux, Windows, macOS |
| ✅ Protocol auto-detect | HTTP, HTTPS, SOCKS4, SOCKS5 |
| ✅ Two-stage verification | example.com + google.com |
| ✅ Max latency filter | Default 150 ms (editable) |
| ✅ Target count | Stop automatically when goal is met |
| ✅ Live box UI | Clean progress, no scroll spam |
| ✅ Auto-save on Ctrl+C | Partial results never lost |
| ✅ Multi-source fetching | 8 public list endpoints |
| ✅ Paid proxy support | `user:pass@host:port`, `host:port:user:pass`, URL formats |

---

## Requirements

- **Python 3.7+**
- An internet connection
- No `pip install` needed — standard library only

---

## Installation

### 1. Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install python -y
pkg install git -y
```

Download the tool:
```bash
git clone https://github.com/NgaTon007/ngaton-proxy-master.git
cd ngaton-proxy-master
```

Run:
```bash
python proxy_master.py
```

**Optional — keep scan alive with screen off:**
```bash
pkg install termux-api -y
termux-wake-lock
python proxy_master.py
```

---

### 2. Linux

**Debian / Ubuntu / Kali:**
```bash
sudo apt update
sudo apt install python3 -y
```

**Fedora / RHEL:**
```bash
sudo dnf install python3 -y
```

**Arch:**
```bash
sudo pacman -S python --noconfirm
```

Run:
```bash
git clone https://github.com/NgaTon007/ngaton-proxy-master.git
cd ngaton-proxy-master
python3 proxy_master.py
```

---

### 3. macOS

Install Python via Homebrew (recommended):
```bash
brew install python3
```

Or download from python.org.

Run:
```bash
git clone https://github.com/NgaTon007/ngaton-proxy-master.git
cd ngaton-proxy-master
python3 proxy_master.py
```

> **Note (macOS):** If you see a firewall prompt on first run, click **Allow**.

---

### 4. Windows

**Option A — Command Prompt / PowerShell**

1. Install Python from the Microsoft Store, or from python.org  
   *(check "Add Python to PATH" during install)*
2. Open **PowerShell** or **CMD**:

```powershell
git clone https://github.com/NgaTon007/ngaton-proxy-master.git
cd ngaton-proxy-master
python proxy_master.py
```

**Option B — Windows Terminal (recommended for best UI colors)**

- Install from Microsoft Store: **Windows Terminal**
- Right-click → Run as Administrator (only if needed)
- Use the same commands as above

> **Note:** ANSI colors work natively on Windows 10+ (build 1511 or later).

---

## Usage

Once you run the tool, you will see prompts:

```
1. PROTOCOL        → 1=AUTO  2=HTTP  3=HTTPS  4=SOCKS4  5=SOCKS5
2. TARGET COUNT    → how many WORKING proxies you want (1–10000)
3. WORKERS         → concurrency (1–500)
4. CONFIRM         → Y/n
```

Then the live box appears:

```
┌──────────────────────────────────────────────────────────────┐
│ NgaTon Proxy Master v4.1 — SCANNING                          │
├──────────────────────────────────────────────────────────────┤
│ Progress [████████████░░░░░░░░░░░░░░░░░░░░░░░░]  35.2%       │
│ Checked 352/1000   Working 12/30   Dead 340                  │
│ Speed 87/s   ETA 7m 20s   Best 89ms                          │
├──────────────────────────────────────────────────────────────┤
│ ✔ 45.32.11.9:8080       HTTP     89ms   WORKING              │
│ ✔ 1.2.3.4:8080          SOCKS5  132ms   WORKING              │
│ ✘ 12.34.56.78:1080      -          -    DEAD                 │
│ ✘ 98.76.54.32:3128      -          -    DEAD                 │
└──────────────────────────────────────────────────────────────┘
```

**Controls:**

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop gracefully → auto-save partial results |
| `Ctrl+C` twice | Force exit → still saves |

---

## Recommended Settings per OS

Different devices handle concurrency differently. Use these as a starting point.

| OS / Device | Workers | Notes |
|-------------|---------|-------|
| **Termux (Android, low-end)** | `40` – `60` | Save battery; avoid overheating |
| **Termux (Android, high-end)** | `80` – `120` | Modern phones handle this well |
| **Linux (Desktop/Server)** | `150` – `300` | Depending on CPU / network |
| **macOS** | `100` – `200` | macOS has per-process socket limits |
| **Windows** | `80` – `150` | Windows networking stack is slower for many sockets |
| **VPS (any OS)** | `200` – `500` | Best performance |

**Rules of thumb:**
- Start low (`50`), watch the **Speed** in the box → if speed plateaus, workers are enough.
- If you see many **DEAD** results at once, your ISP may throttle → lower workers.
- On mobile data, use `40–60` — higher causes drops.

---

## Customizing the Tool

Open `proxy_master.py` in any text editor and change these constants at the top of the file:

### ⏱ Change Timeout (default 2.0s)

```python
TIMEOUT = 2.0
```
- Lower (e.g. `1.5`) → faster scans, but may miss slower proxies
- Higher (e.g. `5.0`) → catches more working proxies, but scan takes longer

### 📉 Change Max Latency (default 150 ms)

```python
MAX_MS = 150
```
- Lower (e.g. `80`) → only very fast proxies
- Higher (e.g. `500`) → more results, but slower proxies

### 🧵 Change Default Workers (default 100)

```python
DEFAULT_WORK = 100
```
- This is only the **suggested default**; you can still change it at the prompt.

### 🌐 Add or Remove Sources

Edit the `SOURCES` list:

```python
SOURCES = [
    ("TheSpeedX HTTP",   "http",   "https://raw.githubusercontent.com/..."),
    # add your own here
]
```

Format: `(display_name, default_protocol, url)`

### 🎯 Change Verification Targets

```python
TARGET_PRIMARY   = ("example.com",    443)
TARGET_SECONDARY = ("www.google.com", 443)
```

> ⚠️ Only use sites you're allowed to test against.

### 🎨 Change Box Width

```python
BOX_W = 62   # inner content width
```

---

## Output Files

After every scan, four files are saved next to the script:

| File | Content |
|------|---------|
| **`proxy.txt`** | ✅ Verified working proxies (with scheme) |
| **`proxy_dead.txt`** | ❌ Dead / slow proxies |
| **`proxy_all.txt`** | 📋 Everything that was scanned |
| **`proxy_report.csv`** | 📊 Full CSV report (status, type, latency) |

**`proxy.txt` format:**
```
http://1.2.3.4:8080
socks5://user:pass@5.6.7.8:1080
https://9.10.11.12:8443
```

Proxies are sorted by latency (fastest first).

---

## How It Works

For each proxy:

1. **Connect** to the proxy on the given host:port
2. **Negotiate** the protocol (HTTP CONNECT / SOCKS5 handshake / SOCKS4)
3. **Tunnel** to `example.com:443`
4. **TLS handshake** through the tunnel (end-to-end)
5. **Verify** the certificate is real

Proxies that pass step 1–5 are marked **WORKING**.  
Then every working proxy is **re-verified** against a *second* target (`google.com:443`).  
Only proxies that pass **both** targets go into `proxy.txt`.

This eliminates false positives — you get real, working proxies.

---

## Troubleshooting

**`NameError: name 'WHITE' is not defined`**  
→ Make sure you're using **v4.1** or later. Older versions had a missing alias.  
Fixed by adding compatibility aliases:
```python
WHITE, GREEN, CYAN, YELLOW, RED = W, G, C, Y, RD
```

**`ModuleNotFoundError`**  
→ The tool uses only standard library. You're probably running Python 2.  
Use `python3` instead of `python`.

**No proxies found**  
→ Increase `MAX_MS` to `500` and try again.  
→ Increase `TIMEOUT` to `4.0`.  
→ Public lists may be stale at certain times of day.

**Colors don't work on Windows**  
→ Use **Windows Terminal** or **PowerShell** (not old `cmd.exe`).  
→ Windows 10 build 1511+ required.

**Scan is slow**  
→ Increase workers.  
→ Lower timeout.

**Terminal still shows old output above the box**  
→ Resize your terminal to at least **80 columns × 25 rows**.  
→ Use a terminal that supports ANSI cursor movement (all modern ones do).

---

## Safety Notice

> ⚠️ **Important**
>
> - This tool is for **educational and testing purposes only**.
> - **Public proxies are untrusted** — never send passwords, OTPs, banking data, or personal info through them.
> - Only test proxies you **own** or have **written authorization** to test.
> - "Working" means the proxy passed a specific test **at a specific moment**. It may stop working at any time.
> - The developer is **not responsible** for misuse of this tool.

---

## Contact

<div align="center">

**Developer : NgaTon**

Telegram  : [@NgaTON_0](https://t.me/NgaTON_0)  
TikTok    : [@ngat0n](https://tiktok.com/@ngat0n)

⭐ If you find this tool useful, give the repo a star!

</div>

---

## License

MIT License — free to use, modify, and distribute.  
See `LICENSE` file for details.

---

<div align="center">
Made with 🖤 by <b>NgaTon</b>
</div>

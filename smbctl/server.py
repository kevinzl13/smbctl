#!/usr/bin/env python3

import argparse
import subprocess
import os
import socket
import signal
import sys
import json
import time
import shutil

STATE_FILE = os.path.expanduser("~/.smbctl_server.json")


# =========================
# STATE
# =========================
def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


# =========================
# NETWORK
# =========================
def get_ips():
    hostname = socket.gethostname()
    ips = set()

    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ":" not in ip:
                ips.add(ip)
    except:
        pass

    ips.add("127.0.0.1")
    return sorted(ips)


# =========================
# START SERVER (BACKGROUND)
# =========================
def start_server(args):
    if os.name == "nt":
        print("[!] SMB server mode is Linux only")
        sys.exit(1)

    directory = os.path.abspath(args.directory or os.getcwd())
    share = args.share

    if shutil.which("impacket-smbserver") is None:
        print("[!] impacket-smbserver not found in PATH")
        sys.exit(1)

    if not os.path.isdir(directory):
        print("[!] Directory does not exist")
        sys.exit(1)

    state = load_state()

    if state:
        pid = state.get("pid")

        try:
            os.kill(pid, 0)

            print(
                f"[!] SMB server already running "
                f"(PID {pid})"
            )

            return

        except OSError:
            save_state({})

    cmd = [
        "impacket-smbserver",
        share,
        directory,
        "-smb2support"
    ]

    if args.user and args.password:
        cmd += ["-username", args.user, "-password", args.password]

    print("\n[+] SMB SERVER STARTING (LINUX DAEMON MODE)")
    print("[+] Share     :", share)
    print("[+] Directory :", directory)
    if args.user and args.password:
        print("[+] Auth      : enabled")
        print("[+] User      :", args.user)
    else:
        print("[+] Auth      : guest")
    print("\n[+] Access URLs:")
    for ip in get_ips():
        print(f"    smb://{ip}/{share}")

    # BACKGROUND PROCESS (NO BLOCK)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

    time.sleep(1)

    if process.poll() is not None:
        print("[!] SMB server failed to start")
        sys.exit(1)

    state = {
        "pid": process.pid,
        "share": share,
        "dir": directory,
        "time": time.time(),
        "auth": bool(args.user and args.password),
        "user": args.user
    }

    save_state(state)

    print(f"\n[+] Server running in background (PID {process.pid})")
    print("[+] You can now use this terminal normally\n")


# =========================
# STOP SERVER
# =========================
def stop_server():
    state = load_state()

    if not state:
        print("[-] No SMB server running")
        return

    pid = state.get("pid")

    print(f"[+] Stopping server (PID {pid})...")

    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)

        # verify kill
        os.kill(pid, 0)

    except ProcessLookupError:
        print("[+] Process already stopped")

    except:
        try:
            os.kill(pid, signal.SIGKILL)
        except:
            pass

    save_state({})
    print("[+] Server stopped")


# =========================
# STATUS
# =========================
def status_server():
    state = load_state()

    if not state:
        print("[-] No SMB server running")
        return

    pid = state.get("pid")

    try:
        os.kill(pid, 0)
        alive = True
    except:
        alive = False

    if not alive:
        save_state({})

    uptime = int(time.time() - state.get("time", time.time()))

    print("\n=== SMB SERVER STATUS ===")
    print(f"PID      : {pid}")
    print(f"Auth     : {state.get('auth')}")
    print(f"User     : {state.get('user')}")
    print(f"Share    : {state.get('share')}")
    print(f"Dir      : {state.get('dir')}")
    print(f"Alive    : {'YES' if alive else 'NO'}")
    print(f"Uptime   : {uptime}s")


# =========================
# INFO
# =========================
def info_server():
    state = load_state()

    if not state:
        print("[-] No server running")
        return

    print("\n=== ACCESS INFO ===\n")

    for ip in get_ips():

        print(f"SMB URL:")
        print(f"  smb://{ip}/{state['share']}")

        print("\nClient:")
        print(
            f"  smbctl connect "
            f"-i {ip} "
            f"-s {state['share']}"
        )

        print()

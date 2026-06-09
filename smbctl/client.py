#!/usr/bin/env python3

import argparse
import subprocess
import platform
import os
import json
import shutil

STATE_FILE = os.path.expanduser("~/.smbctl_sessions.json")


# =========================
# STORAGE
# =========================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# =========================
# CONNECTION RESOLUTION
# =========================
def get_connection(state, server):
    for k, v in state.items():
        if k.startswith(server + ":"):
            return k, v
    return None, None


# =========================
# WINDOWS CONNECT (UNC ONLY)
# =========================
def win_connect(user, password, ip, share, drive="Z"):
    unc = f"\\\\{ip}\\{share}"
    drive_letter = f"{drive}:"

    cmd = [
        "net",
        "use",
        drive_letter,
        unc
    ]

    if user and password:
        cmd += [password, f"/user:{user}"]
    else:
        cmd += ["/user:guest"]

    cmd += ["/persistent:no"]

    subprocess.run(cmd, check=True)

    return drive_letter


def win_disconnect(drive):
    subprocess.run(
        ["net", "use", drive, "/delete", "/y"],
        check=False
    )


# =========================
# LINUX CONNECT
# =========================
def lin_connect(user, password, ip, share, mount):
    unc = f"//{ip}/{share}"

    os.makedirs(mount, exist_ok=True)

    opts = []

    if user and password:
        opts += [f"username={user}", f"password={password}"]
    else:
        opts.append("guest")

    opts.append("vers=2.0")

    cmd = ["mount", "-t", "cifs", unc, mount, "-o", ",".join(opts)]

    subprocess.run(cmd, check=True)
    return mount


def lin_disconnect(mount):
    subprocess.run(
        ["umount", mount],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )

    try:
        if os.path.isdir(mount):
            os.rmdir(mount)
    except:
        pass


# =========================
# DISCONNECT
# =========================
def _disconnect(system, entry):
    if system == "windows":
        win_disconnect(entry["target"])
    else:
        lin_disconnect(entry["target"])


def cmd_disconnect(args):
    state = load_state()
    system = platform.system().lower()

    if args.ip:
        key, entry = get_connection(state, args.ip)

        if not entry:
            print("[!] No connection found")
            return

        _disconnect(system, entry)
        state.pop(key, None)

    else:
        for k, entry in list(state.items()):
            _disconnect(system, entry)
            state.pop(k, None)

    save_state(state)
    print("[+] Disconnected")


# =========================
# CONNECT
# =========================
def cmd_connect(args):
    state = load_state()
    system = platform.system().lower()

    key = f"{args.ip}:{args.share}"

    if system == "windows":
        target = win_connect(
            args.user,
            args.password,
            args.ip,
            args.share,
            args.drive
        )

    elif system == "linux":
        target = lin_connect(
            args.user,
            args.password,
            args.ip,
            args.share,
            args.mount
        )
    else:
        print("[!] Unsupported system")
        return

    state[key] = {
        "type": system,
        "target": target,
        "share": args.share,
        "drive": args.drive if system == "windows" else None,
        "mount": args.mount if system == "linux" else None,
        "auth": bool(args.user and args.password)
    }

    save_state(state)

    print("[+] Connected:", key)
    print("[+] Target:", target)


# =========================
# LIST
# =========================
def cmd_list(args):
    state = load_state()

    if not state:
        print("[-] No active connections")
        return

    print("\n================ SMB CONNECTIONS ================\n")

    for k, v in state.items():
        server = k.split(":")[0]
        share = k.split(":")[1]

        print(f"SERVER  : {server}")
        print(f"SHARE   : {share}")
        print(f"CLIENT  : {v.get('type')}")
        if v.get("type") == "windows":
            print(f"DRIVE   : {v.get('target')}")
        else:
            print(f"MOUNT   : {v.get('target')}")
        print(f"AUTH    : {v.get('auth')}")
        print("-" * 50)


# =========================
# STATUS
# =========================
def cmd_status(args):
    state = load_state()

    print("\n=== STATUS ===")
    print(f"Active connections: {len(state)}")
    print("State file:", STATE_FILE)


# =========================
# CLEAN PATH (FIX DUPLICATION)
# =========================
def clean_remote_path(path, share):
    path = path.lstrip("/")

    # evita smbFolder/smbFolder duplication
    if path.startswith(share + "/"):
        return path[len(share) + 1:]

    return path


# =========================
# COPY (FIXED FINAL)
# =========================
def cmd_copy(args):
    state = load_state()
    system = platform.system().lower()

    src = args.src
    dst = args.dst

    # =========================
    # SMB -> LOCAL
    # =========================
    if ":" in src:

        server, remote_file = src.split(":", 1)
        remote_file = remote_file.lstrip("/")

        key, entry = get_connection(state, server)

        if not entry:
            print("[!] No active connection for server:", server)
            return

        share = entry["share"]
        remote_file = clean_remote_path(remote_file, share)

        base = entry["target"]

        if system == "windows":
            full_remote = base + "\\" + remote_file.replace("/", "\\")
        else:
            full_remote = os.path.join(base, remote_file)

        if not os.path.exists(full_remote):
            print("[!] File not found in SMB:")
            print(full_remote)
            return

        local_dst = dst if dst else "."

        if os.path.isdir(local_dst):
            local_dst = os.path.join(local_dst, os.path.basename(remote_file))

        shutil.copy2(full_remote, local_dst)

        print(f"[+] Copied SMB -> {local_dst}")

    # =========================
    # LOCAL -> SMB
    # =========================
    else:

        server, remote_path = dst.split(":", 1)
        remote_path = remote_path.lstrip("/")

        key, entry = get_connection(state, server)

        if not entry:
            print("[!] No active connection for server:", server)
            return

        base = entry["target"]

        if system == "windows":
            full_remote = base + "\\" + remote_path.replace("/", "\\")
        else:
            full_remote = os.path.join(base, remote_path)

        shutil.copy2(src, full_remote)

        print(f"[+] Copied LOCAL -> SMB: {full_remote}")

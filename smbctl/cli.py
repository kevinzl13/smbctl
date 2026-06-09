#!/usr/bin/env python3

import argparse

from .client import (
    cmd_connect,
    cmd_disconnect,
    cmd_list,
    cmd_status,
    cmd_copy,
)

from .server import (
    start_server,
    stop_server,
    status_server,
    info_server,
)


def main():
    parser = argparse.ArgumentParser(
        prog="smbctl",
        description="SMB Client + Server Toolkit"
    )

    root = parser.add_subparsers(
        dest="section",
        required=True
    )

    # ==================================================
    # CLIENT
    # ==================================================
    connect = root.add_parser(
        "connect",
        help="Connect to SMB share"
    )

    connect.add_argument(
        "-i",
        "--ip",
        required=True,
        help="Server IP"
    )

    connect.add_argument(
        "-s",
        "--share",
        default="smbFolder",
        help="SMB share name"
    )

    connect.add_argument(
        "-u",
        "--user",
        help="Username"
    )

    connect.add_argument(
        "-p",
        "--password",
        help="Password"
    )

    # Windows
    connect.add_argument(
        "--drive",
        default="Z",
        help="Drive letter on Windows (default: Z)"
    )

    # Linux
    connect.add_argument(
        "-m",
        "--mount",
        default="/mnt/smb",
        help="Mount point on Linux"
    )

    disconnect = root.add_parser(
        "disconnect",
        help="Disconnect SMB share"
    )

    disconnect.add_argument(
        "-i",
        "--ip"
    )

    root.add_parser(
        "list",
        help="List SMB connections"
    )

    root.add_parser(
        "status",
        help="Client status"
    )

    copy_cmd = root.add_parser(
        "copy",
        help="Copy files between local and SMB",
        description="""
            Examples
            
            LOCAL -> SMB
              smbctl copy file.txt 192.168.1.10:/smbFolder/file.txt
            
              smbctl copy backup.zip 192.168.1.10:/smbFolder/backups/backup.zip
            
            SMB -> LOCAL
              smbctl copy 192.168.1.10:/smbFolder/file.txt .
            
              smbctl copy 192.168.1.10:/smbFolder/file.txt ./downloads/
            
              smbctl copy 192.168.1.10:/smbFolder/docs/report.pdf report.pdf
            """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    copy_cmd.add_argument(
        "src",
        help="Source path (local file or SMB path)"
    )

    copy_cmd.add_argument(
        "dst",
        help="Destination path (local file/folder or SMB path)"
    )

    # ==================================================
    # SERVER
    # ==================================================

    server = root.add_parser(
        "server",
        help="SMB server management"
    )

    server_sub = server.add_subparsers(
        dest="server_cmd",
        required=True
    )

    start = server_sub.add_parser(
        "start",
        help="Start SMB server"
    )

    start.add_argument(
        "-d",
        "--directory",
        default="."
    )

    start.add_argument(
        "-s",
        "--share",
        default="smbFolder"
    )

    start.add_argument(
        "-u",
        "--user"
    )

    start.add_argument(
        "-p",
        "--password"
    )

    server_sub.add_parser(
        "stop",
        help="Stop SMB server"
    )

    server_sub.add_parser(
        "status",
        help="Server status"
    )

    server_sub.add_parser(
        "info",
        help="Server connection info"
    )

    args = parser.parse_args()

    # ==================================================
    # ROUTER
    # ==================================================

    if args.section == "connect":
        cmd_connect(args)

    elif args.section == "disconnect":
        cmd_disconnect(args)

    elif args.section == "list":
        cmd_list(args)

    elif args.section == "status":
        cmd_status(args)

    elif args.section == "copy":
        cmd_copy(args)

    elif args.section == "server":

        if args.server_cmd == "start":
            start_server(args)

        elif args.server_cmd == "stop":
            stop_server()

        elif args.server_cmd == "status":
            status_server()

        elif args.server_cmd == "info":
            info_server()

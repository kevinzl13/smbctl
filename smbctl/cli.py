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
        help="Connect to SMB share",
        description="""
            Connect to an SMB file share.
            Examples:
            
              Windows
                smbctl connect -i 192.168.1.10
            
                smbctl connect -i 192.168.1.10 --mount Z
            
              Linux
                smbctl connect -i 192.168.1.10
            
                smbctl connect -i 192.168.1.10 --mount /mnt/share
            
              Authenticated share
                smbctl connect -i 192.168.1.10 -u kevin -p secret
            """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    connect.add_argument(
        "-i",
        "--ip",
        required=True,
        help="IP address of the SMB server"
    )

    connect.add_argument(
        "-s",
        "--share",
        default="smbFolder",
        help="Name of the shared SMB folder (default: smbFolder)"
    )

    connect.add_argument(
        "-u",
        "--user",
        help="Username used for SMB authentication"
    )

    connect.add_argument(
        "-p",
        "--password",
        help="Password used for SMB authentication"
    )

    connect.add_argument(
        "-m",
        "--mount",
        help=""" Mount target.
            - Windows: 
                Drive letter to use. default: Z:
                Examples:
                    Z:
                    X:
            - Linux: 
                Directory where the share will appear. default: /mnt/smbFolder
                Examples:
                    /mnt/smbFolder
                    /mnt/share
            """
    )

    disconnect = root.add_parser(
        "disconnect",
        help="Disconnect one or all SMB connections",
        description="""
        Examples:
          - Disconnect one server
              smbctl disconnect -i 192.168.1.10
          - Disconnect everything
              smbctl disconnect
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    disconnect.add_argument(
        "-i",
        "--ip",
        help="Server IP to disconnect. If omitted, all connections are removed."
    )

    root.add_parser(
        "list",
        help="Show all active SMB connections",
        description="Display currently mounted SMB shares."
    )

    root.add_parser(
        "status",
        help="Show client status",
        description="Display SMB client information and saved sessions."
    )

    copy_cmd = root.add_parser(
        "copy",
        help="Copy files between local and SMB",
        description="""
            Examples
            - LOCAL -> SMB
                smbctl copy file.txt 192.168.1.10:/smbFolder/file.txt
                smbctl copy backup.zip 192.168.1.10:/smbFolder/backups/backup.zip
            - SMB -> LOCAL
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
        help="Start an SMB file server",
        description="""
            Share a local directory over SMB.
            Examples:
              - Share current directory
                  smbctl server start
              - Share another directory
                  smbctl server start -d ~/Downloads
              - Share with authentication
                  smbctl server start -u kevin -p secret
              - Custom share name
                  smbctl server start -s files
            """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    server_sub = server.add_subparsers(
        dest="server_cmd",
        required=True
    )

    start = server_sub.add_parser(
        "start",
        help="Start an SMB file server",
        description="""
            Share a local directory over SMB.
            Examples:
              - Share current directory
                  smbctl server start
              - Share another directory
                  smbctl server start -d ~/Downloads
              - Share with authentication
                  smbctl server start -u kevin -p secret
              - Custom share name
                  smbctl server start -s files
            """,
        formatter_class=argparse.RawTextHelpFormatter

    )

    start.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Local directory to share over the network"
    )

    start.add_argument(
        "-s",
        "--share",
        default="smbFolder",
        help="Network share name visible to clients"
    )

    start.add_argument(
        "-u",
        "--user",
        help="Require username authentication"
    )

    start.add_argument(
        "-p",
        "--password",
        help="Require password authentication"
    )

    server_sub.add_parser(
        "stop",
        help="Stop the running SMB server",
        description="""
            Stop the SMB server started with:
              smbctl server start
            This terminates the background server process.
            """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    server_sub.add_parser(
        "status",
        help="Show SMB server status",
        description="""
            Display information about the running SMB server.
            Shows:
              - Process ID (PID)
              - Shared directory
              - Share name
              - Uptime
              - Running state
            """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    server_sub.add_parser(
        "info",
        help="Show connection information",
        description="""
            Display SMB URLs clients can use to connect.
            Example output:
              smb://192.168.1.10/smbFolder
              smb://10.0.0.5/smbFolder
            """,
        formatter_class=argparse.RawTextHelpFormatter
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

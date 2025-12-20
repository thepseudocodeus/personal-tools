#!/usr/bin/env python3
"""Arch Linux Logseq / Omarchy Update Helper
-----------------------------------------
Updated to use arch specific approach
"""

import os
import subprocess
from pathlib import Path

import psutil

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
except ImportError:

    class Fore:
        RED = GREEN = YELLOW = CYAN = RESET = ""

    class Style:
        BRIGHT = NORMAL = RESET_ALL = ""


LOGSEQ_WORKSPACE = Path.home() / "Documents/Logseq"
CACHE_PATH = Path.home() / ".config/Logseq/Cache" # [] TODO: confirm this is correct path


def say(message, color=Fore.CYAN, level="INFO"):
    prefix = f"[{level}]".ljust(7)
    print(f"{Style.BRIGHT}{color}{prefix}{Style.RESET_ALL} {message}")


def divider(label=""):
    print("\n" + "-" * 60)
    if label:
        print(f"{Style.BRIGHT}{label}")
        print("-" * 60)


def check_logseq_processes():
    divider("LOGSEQ PROCESS CHECK")
    found = False
    for proc in psutil.process_iter(["pid", "name"]):
        if "logseq" in proc.info["name"].lower():
            say(f"Found running Logseq process (PID {proc.info['pid']})", Fore.YELLOW)
            found = True
    if not found:
        say("No Logseq processes running.", Fore.GREEN)
    return found


def kill_logseq_processes():
    for proc in psutil.process_iter(["pid", "name"]):
        if "logseq" in proc.info["name"].lower():
            try:
                proc.kill()
                say(f"Killed Logseq process PID {proc.info['pid']}", Fore.YELLOW)
            except Exception as e:
                say(f"Failed to kill PID {proc.info['pid']}: {e}", Fore.RED, "ERROR")


def check_workspace():
    divider("WORKSPACE CHECK")
    if not LOGSEQ_WORKSPACE.exists():
        say(f"Workspace path not found: {LOGSEQ_WORKSPACE}", Fore.RED, "ERROR")
        say("Creating workspace folder...", Fore.YELLOW)
        LOGSEQ_WORKSPACE.mkdir(parents=True, exist_ok=True)
        say(f"Workspace created at {LOGSEQ_WORKSPACE}", Fore.GREEN)
    else:
        say(f"Workspace exists at {LOGSEQ_WORKSPACE}", Fore.GREEN)

    if os.access(LOGSEQ_WORKSPACE, os.W_OK):
        say("Workspace is writable.", Fore.GREEN)
    else:
        say("Workspace is NOT writable! Adjusting permissions...", Fore.YELLOW)
        os.chmod(LOGSEQ_WORKSPACE, 0o755)


def clear_cache():
    divider("CACHE CLEANUP")
    if CACHE_PATH.exists():
        try:
            import shutil

            shutil.rmtree(CACHE_PATH)
            say(f"Cache cleared at {CACHE_PATH}", Fore.GREEN)
        except Exception as e:
            say(f"Failed to clear cache: {e}", Fore.RED, "ERROR")
    else:
        say("No cache directory found.", Fore.GREEN)


def check_file_locks():
    divider("FILE LOCKS")
    try:
        locks = []
        for f in LOGSEQ_WORKSPACE.rglob("*"):
            if f.suffix in [".lock", ".tmp"]:
                locks.append(f)
        if locks:
            say(f"Found {len(locks)} lock/tmp files:", Fore.YELLOW)
            for f in locks[:5]:
                say(f" → {f}", Fore.YELLOW)
            if len(locks) > 5:
                say("...more files omitted", Fore.YELLOW)
        else:
            say("No lock or temporary files found.", Fore.GREEN)
    except Exception as e:
        say(f"Error scanning files: {e}", Fore.RED, "ERROR")


def reinstall_logseq():
    divider("LOGSEQ REINSTALL (OPTIONAL)")
    say("Checking if logseq binary is present...", Fore.CYAN)
    result = subprocess.run(
        ["which", "logseq"], check=False, capture_output=True, text=True
    )
    if not result.stdout.strip():
        say("Logseq not found. Installing from AUR...", Fore.YELLOW)
        try:
            subprocess.run(["yay", "-S", "logseq-bin"], check=True)
            say("Logseq installed successfully.", Fore.GREEN)
        except Exception as e:
            say(f"Failed to install Logseq: {e}", Fore.RED, "ERROR")
    else:
        say(f"Logseq binary found at {result.stdout.strip()}", Fore.GREEN)


def main():
    divider("OMARCHY / ARCH LOGSEQ UPDATE HELPER")
    say("Starting diagnostic and prep pipeline...", Fore.CYAN)

    if check_logseq_processes():
        kill_logseq_processes()

    check_workspace()
    clear_cache()
    check_file_locks()

    divider("PIPELINE COMPLETE")
    say("Logseq workspace is ready for update or launch.", Fore.CYAN)


if __name__ == "__main__":
    main()

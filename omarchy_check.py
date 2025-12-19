#!/usr/bin/env python3
"""Omarchy Diagnostic Pipeline
--------------------------
Problem:
Omarchy update stops. The issues seems related to Logseq. Logseq also loads slowly on startup. This may be relevant to solving the problem.
"""

import os
import platform
import shutil
from pathlib import Path

import psutil

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
except ImportError:
    # [] TODO: Found in documentation. Confirm it works
    class Fore:
        RED = GREEN = YELLOW = CYAN = RESET = ""

    class Style:
        BRIGHT = NORMAL = RESET_ALL = ""


# Global variables
OMARCHY_PATH = Path.home() / "Omarchy"
CHECK_LOGSEQ = True
COLOR_OUTPUT = True


def say(message, color=Fore.CYAN, level="INFO"):
    """Prints readable, color-coded output with consistent structure."""
    prefix = f"[{level}]".ljust(7)
    if not COLOR_OUTPUT:
        color = ""
    print(f"{Style.BRIGHT}{color}{prefix}{Style.RESET_ALL} {message}")


def divider(label=""):
    """Prints a section divider."""
    print("\n" + "-" * 60)
    if label:
        print(f"{Style.BRIGHT}{label}")
        print("-" * 60)


def check_system_info():
    """Displays system information."""
    divider("SYSTEM INFORMATION")
    say(f"Operating System: {platform.system()} {platform.release()}")
    say(f"Python Version: {platform.python_version()}")
    say(f"CPU Cores: {psutil.cpu_count(logical=True)}")
    mem = psutil.virtual_memory()
    say(
        f"Memory: {round(mem.total / (1024**3), 2)} GB total, {round(mem.available / (1024**3), 2)} GB free",
    )


def check_disk_space():
    """Check disk space."""
    divider("DISK SPACE")
    total, used, free = shutil.disk_usage("/")
    say(
        f"Total: {total // (2**30)} GB | Used: {used // (2**30)} GB | Free: {free // (2**30)} GB",
    )
    if free / total < 0.1:
        say("Warning: Less than 10% disk space available!", Fore.YELLOW, "WARN")


def check_logseq_processes():
    if not CHECK_LOGSEQ:
        return
    divider("LOGSEQ PROCESSES")
    found = False
    for proc in psutil.process_iter(["pid", "name"]):
        if "logseq" in proc.info["name"].lower():
            say(
                f"Logseq process detected (PID {proc.info['pid']})",
                Fore.YELLOW,
                "INFO",
            )
            found = True
    if not found:
        say("No Logseq process currently running.", Fore.GREEN)


def check_folder_integrity(path: Path):
    divider("OMARCHY / WORKSPACE CHECK")
    if not path.exists():
        say(f"Path not found: {path}", Fore.RED, "ERROR")
        return
    say(f"Scanning folder: {path}")

    tmp_files = list(path.rglob("*.tmp"))
    lock_files = list(path.rglob("*.lock"))
    if tmp_files or lock_files:
        say(
            f"Found {len(tmp_files)} temporary files and {len(lock_files)} lock files.",
            Fore.YELLOW,
            "WARN",
        )
        for f in tmp_files[:3] + lock_files[:3]:
            say(f" → {f}", Fore.YELLOW)
        if len(tmp_files) + len(lock_files) > 6:
            say("...more files omitted for brevity...", Fore.YELLOW)
    else:
        say("No lock or temporary files detected.", Fore.GREEN)

    if os.access(path, os.W_OK):
        say("Folder is writable.", Fore.GREEN)
    else:
        say("Permission denied. Folder is not writable!", Fore.RED, "ERROR")


def check_resource_usage():
    divider("RESOURCE UTILIZATION SNAPSHOT")
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    say(f"CPU Load: {cpu}% | Memory Usage: {mem}%")
    if cpu > 85 or mem > 85:
        say(
            "CPU and memory usage impact LogSeq performance.",
            Fore.YELLOW,
            "WARN",
        )


def main():
    divider("OMARCHY / ARCH SYSTEM DIAGNOSTIC")
    say("Running diagnostics..", Fore.CYAN)

    try:
        check_system_info()
        check_disk_space()
        check_logseq_processes()
        check_folder_integrity(OMARCHY_PATH)
        check_resource_usage()

        divider("SUMMARY")
        say("All checks complete. Review any WARN or ERROR messages above.", Fore.CYAN)
        say(
            "Determine if Logseq is blocking updates.",
            Fore.CYAN,
        )
    except Exception as e:
        say(f"Critical error: {e}", Fore.RED, "ERROR")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Version: 12-04-2025-v0.0.2

"""Bootstrap App

This module applies the setup steps found useful from personal experience for new projects.

Current environment boostrap:
1. Initiate UV: uv init
2. Initiate Task: task --init
3. Add typical python packages from the requirements-dev.txt file

Author: A.J. Igherighe
Inspired by typer documentation, Google style guide, github, and other examples.
"""

# [ ] TODO: refine imports based on what is consistently used
import shlex

# from pprint import pprint
# from typing import Optional
import subprocess
import sys
import traceback
from enum import Enum
from pathlib import Path

import typer
from loguru import logger

app_version = "0.0.4"

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)


# [ ] TODO: add functionality to output log information to file
class OutputFormat(str, Enum):
    """Available output formats"""

    yaml = "yaml"
    json = "json"
    xml = "xml"
    text = "text"


class BootstrapException(Exception):
    """Generic exception for Bootstrap operations"""

    def __init__(self, message: str, rc: int = 1):
        super().__init__(message)
        self.rc = rc


class Bootstrap:
    """Bootstrap handles setting up this environment."""

    version = app_version
    name = "Bootstrap Environment"

    def __init__(self, path: Path):
        self.path = path
        logger.debug(f"Bootstrap initialized with path: {path}")

    def hello(self):
        """Simple Hello World"""
        message = f"Hello World: {self.path}"
        logger.info(message)
        print(message)

    def world(self):
        """Print three times World"""
        message = "Hello World World World"
        logger.info("Executing world method")
        print(message)

    # [ ] TODO: adjust timeout timing based on updated results
    def run_command(
        self,
        command: str,
        timeout: int = 60,
        check: bool = True,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        """Execute a shell command with proper error handling.

        Args:
            command: Command string to execute
            timeout: Timeout in seconds (default: 60)
            check: Raise exception on non-zero exit (default: True)
            capture_output: Capture stdout/stderr (default: True)

        Returns:
            CompletedProcess instance

        Raises:
            BootstrapException: If command fails or times out

        """
        command_list = shlex.split(command)
        logger.info(f"Executing command: {command}")

        try:
            result = subprocess.run(
                command_list,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=check,
            )

            if result.stdout:
                logger.debug(f"Command stdout: {result.stdout.strip()}")
            if result.stderr:
                logger.warning(f"Command stderr: {result.stderr.strip()}")

            logger.success(f"Command completed successfully: {command}")
            return result

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout}s: {command}"
            logger.error(error_msg)
            raise BootstrapException(error_msg, rc=124) from e

        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}: {command}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr.strip()}"
            logger.error(error_msg)
            raise BootstrapException(error_msg, rc=e.returncode) from e

        except FileNotFoundError as e:
            error_msg = f"Command not found: {command_list[0]}"
            logger.error(error_msg)
            raise BootstrapException(
                f"{error_msg}. Please ensure it's installed and in your PATH.",
                rc=127,
            ) from e

    def install_reqs(self, requirements_file: str = "requirements-dev.txt"):
        """Install packages from a requirements file using uv.

        Args:
            requirements_file: Path to requirements file

        Raises:
            BootstrapException: If installation fails

        """
        req_path = Path(requirements_file)

        if not req_path.exists():
            raise BootstrapException(
                f"Requirements file not found: {requirements_file}",
                rc=2,
            )

        logger.info(f"Installing packages from: {requirements_file}")
        command = f"uv add -r {requirements_file}"

        # Use longer timeout for package installation (5 minutes)
        self.run_command(command, timeout=300)

        logger.success("All packages installed successfully")

    def fail(self):
        """Return an application exception"""
        logger.error("Failure method called - raising exception")
        raise BootstrapException("This failure does not create python tracebacks")


cli_app = typer.Typer(
    help="Bootstrap the environment.",
    invoke_without_command=True,
    no_args_is_help=True,
    add_completion=False,  # [] TODO: consider removing this if not used often
)


def configure_logger(verbose: int):
    """Configure loguru logger based on verbosity level.

    Args:
        verbose: Verbosity level (0-3)
            0: WARNING
            1: INFO
            2: DEBUG
            3: TRACE

    """
    logger.remove()

    level_map = {
        0: "WARNING",
        1: "INFO",
        2: "DEBUG",
        3: "TRACE",
    }

    level = level_map.get(verbose, "TRACE")

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    logger.debug(f"Logger configured with level: {level}")


@cli_app.callback()
def main(
    ctx: typer.Context,
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        min=0,
        max=3,
        help="Increase verbosity (0=WARNING, 1=INFO, 2=DEBUG, 3=TRACE)",
    ),
    working_dir: Path = typer.Option(
        Path(),
        "-c",
        "--config",
        help="Working directory for bootstrap operations",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Display version and exit",
    ),
):
    """Bootstrap environment setup tool.

    Use this tool to initialize and configure development environments
    with common tools and dependencies.
    """
    configure_logger(verbose)

    logger.info(f"Bootstrap CLI v{app_version} starting")
    logger.debug(f"Working directory: {working_dir}")
    logger.debug(f"Verbosity level: {verbose}")

    if version:
        typer.echo(f"Bootstrap CLI version {app_version}")
        raise typer.Exit(0)

    ctx.obj = {
        "bootstrap": Bootstrap(working_dir),
    }


@cli_app.command("help")
def cli_help(ctx: typer.Context):
    """Display detailed help message"""
    logger.debug("Help command invoked")
    root_ctx = ctx.find_root()
    typer.echo(root_ctx.get_help())


@cli_app.command("logging")
def cli_logging():
    """Test logging at all levels"""
    logger.trace("SHOW TRACE - Most detailed debugging")
    logger.debug("SHOW DEBUG - Debug information")
    logger.info("SHOW INFO - General information")
    logger.success("SHOW SUCCESS - Operation succeeded")
    logger.warning("SHOW WARNING - Warning message")
    logger.error("SHOW ERROR - Error occurred")
    logger.critical("SHOW CRITICAL - Critical failure")


@cli_app.command("install-reqs")
def cli_install_reqs(
    ctx: typer.Context,
    requirements_file: str = typer.Option(
        "requirements-dev.txt",
        "--file",
        "-f",
        help="Requirements file to install",
    ),
    timeout: int = typer.Option(
        300,
        "--timeout",
        "-t",
        help="Timeout in seconds for installation",
        min=10,
        max=3600,
    ),
):
    """Install development requirements using uv.

    This command reads a requirements file and installs all listed
    packages using the uv package manager.
    """
    bootstrap = ctx.obj["bootstrap"]

    logger.info(f"Installing requirements from: {requirements_file}")

    try:
        bootstrap.install_reqs(requirements_file)
        typer.secho("✓ Requirements installed successfully!", fg=typer.colors.GREEN)

    except BootstrapException as e:
        logger.error(f"Installation failed: {e}")
        typer.secho(f"✗ {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=e.rc)


@cli_app.command("init")
def cli_init(
    ctx: typer.Context,
    skip_uv: bool = typer.Option(False, "--skip-uv", help="Skip UV initialization"),
    skip_task: bool = typer.Option(
        False,
        "--skip-task",
        help="Skip Task initialization",
    ),
):
    """Initialize a new project with UV and Task.

    This sets up a new Python project with:
    - UV for dependency management
    - Task for task automation
    """
    bootstrap = ctx.obj["bootstrap"]

    typer.echo("Initializing project...")

    try:
        if not skip_uv:
            typer.echo("• Initializing UV...")
            bootstrap.run_command("uv init", timeout=30)

        if not skip_task:
            typer.echo("• Initializing Task...")
            bootstrap.run_command("task --init", timeout=30)

        typer.secho("✓ Project initialized successfully!", fg=typer.colors.GREEN)

    except BootstrapException as e:
        typer.secho(f"✗ Initialization failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=e.rc)


@cli_app.command("demo")
def cli_demo(ctx: typer.Context):
    """Run a demo of bootstrap functionality"""
    bootstrap = ctx.obj["bootstrap"]

    typer.echo("Running Bootstrap Demo...")
    typer.echo("-" * 50)

    bootstrap.hello()
    bootstrap.world()

    typer.secho("✓ Demo completed!", fg=typer.colors.GREEN)


# [] TODO: remove later if this is no longer needed
cli_src = typer.Typer(help="Manage project sources")
cli_app.add_typer(cli_src, name="source")


@cli_src.callback()
def src_callback():
    """Source management commands."""
    logger.debug("Source group command invoked")


@cli_src.command("ls")
def src_ls():
    """List all configured sources"""
    logger.info("Listing sources")
    typer.echo("Sources:")
    typer.echo("  • source1")
    typer.echo("  • source2")


@cli_src.command("install")
def src_install(
    source_name: str = typer.Argument(..., help="Name of source to install"),
):
    """Install a specific source"""
    logger.info(f"Installing source: {source_name}")
    typer.echo(f"Installing source: {source_name}")


@cli_src.command("update")
def src_update():
    """Update all sources"""
    logger.info("Updating sources")
    typer.echo("Updating all sources...")


def clean_terminate(err: Exception):
    """Terminate gracefully based on exception type.

    Args:
        err: Exception that caused termination

    """
    # Define user-facing errors (expected errors)
    user_errors = (
        PermissionError,
        FileExistsError,
        FileNotFoundError,
        InterruptedError,
        IsADirectoryError,
        NotADirectoryError,
        BootstrapException,
    )

    if isinstance(err, subprocess.TimeoutExpired):
        logger.error(f"Command timed out: {err.cmd}")
        logger.critical("Operation exceeded maximum allowed time")
        sys.exit(
            124,
        )  # [ ] TODO: This code came from a google search. Confirm it's accuracy.

    # Handle expected user errors
    if isinstance(err, user_errors):
        rc = int(getattr(err, "rc", getattr(err, "errno", 1)))
        advice = getattr(err, "advice", None)

        if advice:
            logger.warning(advice)

        logger.error(str(err))
        err_name = err.__class__.__name__
        logger.critical(f"Bootstrap exited with error {err_name} (exit code: {rc})")
        sys.exit(rc)

    # These are unexpected errors that represent opportunities to improve this script.
    rc = 255
    logger.error("Unexpected error occurred:")
    logger.error(traceback.format_exc())
    logger.critical(f"Uncaught error: {err.__class__.__name__}")
    logger.critical("This is likely a bug. Please report it with the traceback above.")
    sys.exit(rc)


def cli_run():
    """Main entry point for CLI application"""
    try:
        cli_app()
    except typer.Exit as e:
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        typer.echo("\nOperation cancelled.", err=True)
        sys.exit(130)
    except Exception as err:
        clean_terminate(err)


if __name__ == "__main__":
    cli_run()

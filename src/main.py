"""
Simple Sim Sports: Pro Wrestling
Entry point for the CLI application.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.cli.cli_app import CLIApp


def main():
    """Launch the CLI application."""
    app = CLIApp()
    app.run()


if __name__ == "__main__":
    main()
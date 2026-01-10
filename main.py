"""Main entry point for image-tools project."""

from menu import ToolMenu


def main():
    """Launch the interactive menu system."""
    menu = ToolMenu()
    menu.run()


if __name__ == "__main__":
    main()

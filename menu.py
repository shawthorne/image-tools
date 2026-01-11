#!/usr/bin/env python3
"""
## ***********************************************************************
## menu.py
## Console menu interface for Image Tools utilities
## Provides an interactive CLI with options to convert HTML to images and more
## Required: Standard Library, tools.html_to_images
## Copyright (c) 2025, Stephen Hawthorne
## Created Date: 2025-01-13
## Last Modified: 2025-01-13
## ***********************************************************************
"""

import sys
from pathlib import Path
from typing import Callable, Dict, Optional

# Import tools
from tools.html_to_images import convert_html_to_images


class ToolMenu:
    """Interactive menu for selecting and running tools."""
    
    def __init__(self):
        """Initialize the menu system."""
        self.tools: Dict[int, Dict[str, any]] = {
            1: {
                "name": "HTML Presentation to Images",
                "description": "Convert HTML presentations into multiple PNG images",
                "function": self._run_html_converter
            }
        }
    
    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("  IMAGE TOOLS - Main Menu")
        print("=" * 60)
        print()
        
        for num, tool_info in sorted(self.tools.items()):
            print(f"  {num}. {tool_info['name']}")
            print(f"     {tool_info['description']}")
            print()
        
        print("  0. Exit")
        print()
    
    def _run_html_converter(self) -> None:
        """Run the HTML to images converter tool."""
        print("\n" + "-" * 60)
        print("HTML Presentation to Images Converter")
        print("-" * 60)
        print()
        
        # Get input file
        print("Enter the path to your HTML file:")
        print("  (You can use a relative path from the 'source' folder)")
        html_file = input("HTML file: ").strip()
        
        if not html_file:
            print("No file specified. Returning to menu.")
            return
        
        # Optional output directory
        print("\nEnter output directory (press Enter for default 'output/'):")
        output_dir = input("Output directory: ").strip() or None
        
        try:
            print("\nProcessing...")
            output_files = convert_html_to_images(html_file, output_dir)
            print("\n✓ Conversion complete!")
        except FileNotFoundError as e:
            print(f"\n✗ Error: {e}")
        except Exception as e:
            print(f"\n✗ An error occurred: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self) -> None:
        """Run the interactive menu loop."""
        while True:
            self.display_menu()
            
            try:
                choice = input("Select an option: ").strip()
                
                if choice == "0":
                    print("\nGoodbye!")
                    break
                
                choice_num = int(choice)
                
                if choice_num in self.tools:
                    tool_info = self.tools[choice_num]
                    print(f"\nRunning: {tool_info['name']}")
                    tool_info["function"]()
                    
                    # Ask if user wants to continue
                    print("\n" + "-" * 60)
                    continue_choice = input("Return to menu? (Y/n): ").strip().lower()
                    if continue_choice == 'n':
                        break
                else:
                    print(f"\nInvalid option: {choice}. Please try again.")
            
            except ValueError:
                print("\nInvalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point for the menu system."""
    menu = ToolMenu()
    menu.run()


if __name__ == "__main__":
    main()

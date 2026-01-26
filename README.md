# Image Tools

A Python toolkit for image processing and conversion, featuring an interactive menu system for easy access to image manipulation tools.

## Overview

Image Tools provides a command-line interface for converting and processing images. The project currently includes a powerful HTML presentation to images converter that can split HTML documents into multiple PNG images.

## Features

### HTML Presentation to Images Converter

Converts HTML presentations (like slideshows or multi-section documents) into multiple PNG images. The tool:

- **Auto-detects break points**: Intelligently identifies sections in your HTML (e.g., slides, sections, divs) that should be split into separate images. Automatically detects common slide patterns (elements with class "slide", "section", "page", etc.) and finds all matching elements
- **Interactive selection**: Prompts you to choose which elements to use as break points if multiple options are detected
- **Full document rendering**: If no break points are found, renders the entire document as a single image
- **Standardized output**: Automatically resizes all generated images to match the largest dimensions, ensuring consistent sizing
- **High-quality rendering**: Uses Playwright with Chromium to render HTML with full CSS support, fonts, and images
- **Flexible paths**: Accepts relative paths from the `files/source/` folder or absolute paths

## Installation

This project uses `uv` for dependency management. Make sure you have Python 3.13+ installed.

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Install Playwright browsers (required for HTML rendering):
   ```bash
   uv run playwright install chromium
   ```

## Usage

Run the interactive menu system:

```bash
python menu.py
```

Or run the HTML converter directly:

```bash
python tools/html_to_images.py <html_file> [output_dir]
```

### Using the Menu

1. Launch the menu: `python menu.py`
2. Select option `1` for "HTML Presentation to Images"
3. Enter the path to your HTML file (relative to `files/source/` folder or absolute path)
4. Optionally specify an output directory (defaults to `files/output/`)
5. The tool will process your HTML and generate PNG images

### Example

```bash
$ python menu.py

============================================================
  IMAGE TOOLS - Main Menu
============================================================

  1. HTML Presentation to Images
     Convert HTML presentations into multiple PNG images

  0. Exit

Select an option: 1

------------------------------------------------------------
HTML Presentation to Images Converter
------------------------------------------------------------

Enter the path to your HTML file:
  (You can use a relative path from the 'files/source' folder)
HTML file: software-roles-infographic.html

Enter output directory (press Enter for default 'files/output/'):
Output directory: 

Processing...
✓ Conversion complete!
```

## Project Structure

```
image-tools/
├── menu.py              # Interactive menu system
├── tools/
│   └── html_to_images.py  # HTML to images converter
├── utils/
│   ├── file_utils.py      # File path validation and output management
│   ├── html_parser.py     # HTML parsing and break point detection
│   └── image_utils.py     # Image processing utilities
├── files/
│   ├── source/            # Input HTML files
│   └── output/            # Generated image files
└── pyproject.toml         # Project configuration
```

## Dependencies

- **playwright** (>=1.40.0): Browser automation for HTML rendering
- **beautifulsoup4** (>=4.12.0): HTML parsing and manipulation
- **pillow** (>=10.0.0): Image processing and manipulation

## Requirements

- Python 3.13 or higher
- Chromium browser (installed via Playwright)

## License

This project is provided as-is for personal or commercial use.

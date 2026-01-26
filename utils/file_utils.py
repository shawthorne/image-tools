#!/usr/bin/env python3
"""
## ***********************************************************************
## file_utils.py
## File path handling and output directory management utilities
## Provides functions for validating file paths and managing output directories
## Required: Standard Library (no external dependencies)
## Copyright (c) 2025, Stephen Hawthorne
## Created Date: 2025-01-13
## Last Modified: 2025-01-13
## ***********************************************************************
"""

import os
from pathlib import Path
from typing import Optional


def ensure_output_dir(output_dir: Optional[str] = None) -> Path:
    """
    Ensure the output directory exists, creating it if necessary.
    
    Args:
        output_dir: Optional custom output directory path.
                   If None, uses 'files/output' in project root.
    
    Returns:
        Path object for the output directory.
    """
    if output_dir is None:
        # Get project root (assuming this file is in utils/)
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "files" / "output"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_source_dir() -> Path:
    """
    Get the source directory path.
    
    Returns:
        Path object for the source directory.
    """
    project_root = Path(__file__).parent.parent
    return project_root / "files" / "source"


def validate_file_path(file_path: str) -> Path:
    """
    Validate and return a Path object for the given file path.
    Checks if file exists and raises error if not.
    
    Args:
        file_path: Path to the file (can be relative or absolute).
    
    Returns:
        Path object for the validated file.
    
    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    path = Path(file_path)
    
    # If relative path, check in source directory first
    if not path.is_absolute():
        source_dir = get_source_dir()
        potential_path = source_dir / path
        if potential_path.exists():
            return potential_path
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return path


def generate_output_filename(base_name: str, index: int, extension: str = "png") -> str:
    """
    Generate a numbered output filename.
    
    Args:
        base_name: Base name for the file (without extension).
        index: Index number (will be zero-padded to 2 digits).
        extension: File extension (default: "png").
    
    Returns:
        Formatted filename (e.g., "presentation_01.png").
    """
    return f"{base_name}_{index:02d}.{extension}"

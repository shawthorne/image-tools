"""Image processing helper utilities."""

from pathlib import Path
from PIL import Image
from typing import Optional, Tuple


def validate_image(image_path: Path) -> bool:
    """
    Validate that an image file exists and is readable.
    
    Args:
        image_path: Path to the image file.
    
    Returns:
        True if image is valid, False otherwise.
    """
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def get_image_dimensions(image_path: Path) -> Optional[Tuple[int, int]]:
    """
    Get the dimensions of an image.
    
    Args:
        image_path: Path to the image file.
    
    Returns:
        Tuple of (width, height) or None if image cannot be read.
    """
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return None


def resize_image_if_needed(
    image_path: Path,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    output_path: Optional[Path] = None
) -> Path:
    """
    Resize an image if it exceeds maximum dimensions.
    
    Args:
        image_path: Path to the source image.
        max_width: Maximum width in pixels (None for no limit).
        max_height: Maximum height in pixels (None for no limit).
        output_path: Optional output path (defaults to overwriting source).
    
    Returns:
        Path to the (possibly resized) image.
    """
    if max_width is None and max_height is None:
        return image_path
    
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Check if resize is needed
            needs_resize = False
            if max_width and width > max_width:
                needs_resize = True
                ratio = max_width / width
                width = max_width
                height = int(height * ratio)
            
            if max_height and height > max_height:
                needs_resize = True
                ratio = max_height / height
                height = max_height
                width = int(width * ratio)
            
            if needs_resize:
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                output = output_path or image_path
                resized.save(output, format='PNG')
                return output
        
        return image_path
    except Exception as e:
        print(f"Warning: Could not resize image {image_path}: {e}")
        return image_path


def resize_image_to_size(
    image_path: Path,
    target_width: int,
    target_height: int,
    output_path: Optional[Path] = None,
    background_color: Tuple[int, int, int] = (10, 15, 26)  # Default dark background
) -> Path:
    """
    Resize an image to exact dimensions, padding if necessary.
    
    Args:
        image_path: Path to the source image.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        output_path: Optional output path (defaults to overwriting source).
        background_color: RGB color for padding (default: dark blue-gray).
    
    Returns:
        Path to the resized image.
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if img.mode != 'RGB':
                # Create a white background for transparency
                rgb_img = Image.new('RGB', img.size, background_color)
                if img.mode == 'RGBA':
                    rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Calculate scaling to fit within target dimensions while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min(target_width / img_width, target_height / img_height)
            
            # Calculate new dimensions
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create new image with target size and background color
            final_img = Image.new('RGB', (target_width, target_height), background_color)
            
            # Calculate position to center the image
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            
            # Paste resized image onto background
            final_img.paste(resized, (x_offset, y_offset))
            
            # Save
            output = output_path or image_path
            final_img.save(output, format='PNG')
            return output
    except Exception as e:
        print(f"Warning: Could not resize image {image_path} to {target_width}x{target_height}: {e}")
        return image_path

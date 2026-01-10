"""HTML presentation to images converter tool."""

import asyncio
import re
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from utils.file_utils import ensure_output_dir, validate_file_path, generate_output_filename
from utils.html_parser import HTMLBreakDetector, parse_html_file
from utils.image_utils import get_image_dimensions, resize_image_to_size


class HTMLToImagesConverter:
    """Converts HTML presentations into multiple PNG images."""
    
    def __init__(self, viewport_width: int = 1920, viewport_height: int = 1080):
        """
        Initialize the converter.
        
        Args:
            viewport_width: Browser viewport width in pixels.
            viewport_height: Browser viewport height in pixels.
        """
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.browser: Optional[Browser] = None
    
    async def _initialize_browser(self) -> None:
        """Initialize the Playwright browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
    
    async def _close_browser(self) -> None:
        """Close the Playwright browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def _render_full_document(
        self,
        page: Page,
        html_content: str,
        output_path: Path
    ) -> None:
        """
        Render the entire HTML document as a single image with proper sizing.
        
        Args:
            page: Playwright page object.
            html_content: Full HTML content.
            output_path: Path to save the image.
        """
        # Use a larger viewport for better readability when rendering full document
        await page.set_viewport_size({"width": 2560, "height": 1440})
        
        # Load the HTML content
        await page.set_content(html_content, wait_until="networkidle")
        
        # Wait for fonts and images to load
        await page.wait_for_timeout(1000)
        
        # Use JavaScript to remove height restrictions and ensure all content is visible
        await page.evaluate("""
            () => {
                // Remove height restrictions on all elements
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    if (el.style.maxHeight) {
                        el.style.maxHeight = 'none';
                    }
                    if (el.style.overflow === 'hidden' || el.style.overflow === 'auto') {
                        el.style.overflow = 'visible';
                    }
                });
                // Ensure body and html don't restrict height
                document.body.style.overflow = 'visible';
                document.documentElement.style.overflow = 'visible';
            }
        """)
        
        # Wait a bit more for any CSS animations/transitions
        await page.wait_for_timeout(500)
        
        # Take full page screenshot to capture all content
        await page.screenshot(path=str(output_path), full_page=True)
    
    async def _render_section(
        self,
        page: Page,
        html_content: str,
        section_element,
        output_path: Path
    ) -> None:
        """
        Render a single section as an image.
        
        Args:
            page: Playwright page object.
            html_content: Full HTML content.
            section_element: BeautifulSoup element for the section.
            output_path: Path to save the image.
        """
        # Create a standalone HTML document for this section
        section_html = self._create_section_html(html_content, section_element)
        
        # Load the HTML content
        await page.set_content(section_html, wait_until="networkidle")
        
        # Wait for fonts and images to load
        await page.wait_for_timeout(1000)
        
        # Use JavaScript to ensure slides are visible and remove height restrictions
        await page.evaluate("""
            () => {
                // Force all slides to be visible
                const slides = document.querySelectorAll('.slide');
                slides.forEach(slide => {
                    slide.style.display = 'block';
                    slide.classList.add('active');
                    // Remove max-height restrictions to show all content
                    slide.style.maxHeight = 'none';
                    slide.style.overflow = 'visible';
                });
                // Also ensure body and container don't restrict height
                const body = document.body;
                if (body) {
                    body.style.overflow = 'visible';
                }
                const container = document.querySelector('.slide-container');
                if (container) {
                    container.style.overflow = 'visible';
                }
            }
        """)
        
        # Wait a bit more for any CSS animations/transitions
        await page.wait_for_timeout(500)
        
        # Always use full page screenshot to capture all content
        await page.screenshot(path=str(output_path), full_page=True)
    
    def _create_section_html(self, full_html: str, section_element) -> str:
        """
        Create a standalone HTML document for a section.
        
        Args:
            full_html: The full HTML content.
            section_element: BeautifulSoup element for the section.
        
        Returns:
            Complete HTML document string for the section.
        """
        # Convert section element to string first (to avoid BeautifulSoup instance issues)
        section_html = str(section_element)
        
        # Modify section HTML to ensure slide is visible
        # Use regex replacement to handle multiple classes properly
        # Handle class="slide ..." or class='slide ...'
        section_html = re.sub(
            r'class="(slide[^"]*)"',
            lambda m: f'class="{m.group(1)} active"' if 'active' not in m.group(1) else f'class="{m.group(1)}"',
            section_html
        )
        section_html = re.sub(
            r"class='(slide[^']*)'",
            lambda m: f"class='{m.group(1)} active'" if 'active' not in m.group(1) else f"class='{m.group(1)}'",
            section_html
        )
        
        # Parse the full HTML to get head content (styles, scripts, etc.)
        soup = BeautifulSoup(full_html, "html.parser")
        
        # Find or create head and body
        head = soup.find("head")
        if not head:
            head = soup.new_tag("head")
            soup.insert(0, head)
        
        body = soup.find("body")
        if not body:
            body = soup.new_tag("body")
            soup.append(body)
        
        # Replace body content with just the section
        body.clear()
        
        # Create wrapper div to maintain structure and parse into main soup
        wrapper_html = f'<div class="slide-container">{section_html}</div>'
        wrapper_parsed = BeautifulSoup(wrapper_html, "html.parser")
        # Extract the wrapper div and append to body
        wrapper_div = wrapper_parsed.find("div")
        if wrapper_div:
            # Convert to string and re-parse into main soup to avoid instance issues
            body.append(BeautifulSoup(str(wrapper_div), "html.parser"))
        else:
            body.append(BeautifulSoup(section_html, "html.parser"))
        
        # Add CSS override to ensure slide is visible (important for slides with display:none)
        style_tag = soup.new_tag("style")
        style_tag.string = """
            .slide {
                display: block !important;
            }
            .slide.active {
                display: block !important;
            }
        """
        head.append(style_tag)
        
        # Ensure we have a proper HTML structure
        if not soup.find("html"):
            html_tag = soup.new_tag("html")
            html_tag.insert(0, head)
            html_tag.append(body)
            soup = BeautifulSoup(f"<!DOCTYPE html>\n{html_tag}", "html.parser")
        
        return str(soup)
    
    async def convert(
        self,
        html_file_path: str,
        output_dir: Optional[str] = None,
        selectors: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Convert HTML presentation to images.
        
        Args:
            html_file_path: Path to the HTML file.
            output_dir: Optional output directory (defaults to project output/).
            selectors: Optional list of CSS selectors for break points.
                      If None, will auto-detect and prompt user.
        
        Returns:
            List of paths to generated image files.
        """
        # Validate input file
        file_path = validate_file_path(html_file_path)
        
        # Ensure output directory exists
        output_path = ensure_output_dir(output_dir)
        
        # Parse HTML
        html_content = parse_html_file(file_path)
        detector = HTMLBreakDetector(html_content)
        
        # Determine break points
        if selectors is None:
            auto_detected = detector.auto_detect_breaks()
            selectors = detector.prompt_user_for_breaks(auto_detected)
        
        # Get base name for output files
        base_name = file_path.stem
        
        # Initialize browser
        await self._initialize_browser()
        
        try:
            # Create a new page
            page = await self.browser.new_page(
                viewport={"width": self.viewport_width, "height": self.viewport_height}
            )
            
            output_files = []
            
            if not selectors:
                # Single image - render entire document
                print("No break points detected. Rendering entire document as single image...")
                output_file = output_path / generate_output_filename(base_name, 1)
                await self._render_full_document(page, html_content, output_file)
                output_files.append(output_file)
            else:
                # Multiple images - one per section
                elements = detector.get_elements_by_selectors(selectors)
                
                if not elements:
                    print(f"Warning: No elements found with selectors: {selectors}")
                    print("Rendering entire document as single image...")
                    output_file = output_path / generate_output_filename(base_name, 1)
                    await self._render_full_document(page, html_content, output_file)
                    output_files.append(output_file)
                else:
                    print(f"Rendering {len(elements)} section(s)...")
                    for i, element in enumerate(elements, 1):
                        print(f"  Processing section {i}/{len(elements)}...")
                        output_file = output_path / generate_output_filename(base_name, i)
                        await self._render_section(page, html_content, element, output_file)
                        output_files.append(output_file)
            
            await page.close()
            
            # Standardize all images to the same size
            if len(output_files) > 1:
                print("\nStandardizing image sizes...")
                # Find maximum dimensions across all images
                max_width = 0
                max_height = 0
                for output_file in output_files:
                    dims = get_image_dimensions(output_file)
                    if dims:
                        max_width = max(max_width, dims[0])
                        max_height = max(max_height, dims[1])
                
                if max_width > 0 and max_height > 0:
                    print(f"  Resizing all images to {max_width}x{max_height}...")
                    for output_file in output_files:
                        resize_image_to_size(output_file, max_width, max_height)
            
            print(f"\n✓ Successfully created {len(output_files)} image(s)")
            print(f"  Output directory: {output_path}")
            for output_file in output_files:
                dims = get_image_dimensions(output_file)
                if dims:
                    print(f"  - {output_file.name} ({dims[0]}x{dims[1]})")
                else:
                    print(f"  - {output_file.name}")
            
            return output_files
            
        finally:
            await self._close_browser()


def convert_html_to_images(
    html_file_path: str,
    output_dir: Optional[str] = None,
    selectors: Optional[List[str]] = None
) -> List[Path]:
    """
    Convenience function to convert HTML to images (synchronous wrapper).
    
    Args:
        html_file_path: Path to the HTML file.
        output_dir: Optional output directory.
        selectors: Optional list of CSS selectors for break points.
    
    Returns:
        List of paths to generated image files.
    """
    converter = HTMLToImagesConverter()
    return asyncio.run(converter.convert(html_file_path, output_dir, selectors))


if __name__ == "__main__":
    # Allow running as standalone script
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python html_to_images.py <html_file> [output_dir]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_html_to_images(html_file, output)

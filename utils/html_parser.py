"""HTML parsing and break detection logic for presentations."""

from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Optional, Dict, Any


class HTMLBreakDetector:
    """Detects logical breaks in HTML presentations."""
    
    # Common class names that indicate slides/sections
    COMMON_SLIDE_CLASSES = ["slide", "section", "page", "step", "slide-page"]
    
    # Common data attributes
    COMMON_DATA_ATTRS = ["data-slide", "data-page", "data-section"]
    
    def __init__(self, html_content: str):
        """
        Initialize the break detector with HTML content.
        
        Args:
            html_content: The HTML content as a string.
        """
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.html_content = html_content
    
    def auto_detect_breaks(self) -> List[Dict[str, Any]]:
        """
        Automatically detect potential break points in the HTML.
        
        Returns:
            List of dictionaries containing break information:
            {
                'element': BeautifulSoup element,
                'selector': CSS selector string,
                'confidence': 'high' | 'medium' | 'low',
                'reason': Description of why this was detected
            }
        """
        breaks = []
        
        # Check for common slide class names
        for class_name in self.COMMON_SLIDE_CLASSES:
            elements = self.soup.find_all(class_=class_name)
            for elem in elements:
                breaks.append({
                    'element': elem,
                    'selector': self._get_selector(elem),
                    'confidence': 'high',
                    'reason': f"Found element with class '{class_name}'"
                })
        
        # Check for data attributes
        for attr in self.COMMON_DATA_ATTRS:
            elements = self.soup.find_all(attrs={attr: True})
            for elem in elements:
                breaks.append({
                    'element': elem,
                    'selector': self._get_selector(elem),
                    'confidence': 'high',
                    'reason': f"Found element with attribute '{attr}'"
                })
        
        # Check for semantic HTML elements
        semantic_tags = ['section', 'article']
        for tag in semantic_tags:
            elements = self.soup.find_all(tag)
            for elem in elements:
                # Only add if not already found by class/data-attr
                selector = self._get_selector(elem)
                if not any(b['selector'] == selector for b in breaks):
                    breaks.append({
                        'element': elem,
                        'selector': selector,
                        'confidence': 'medium',
                        'reason': f"Found semantic <{tag}> element"
                    })
        
        # Remove duplicates based on selector
        seen_selectors = set()
        unique_breaks = []
        for break_info in breaks:
            selector = break_info['selector']
            if selector not in seen_selectors:
                seen_selectors.add(selector)
                unique_breaks.append(break_info)
        
        return unique_breaks
    
    def _get_selector(self, element) -> str:
        """
        Generate a CSS selector for an element.
        
        Args:
            element: BeautifulSoup element.
        
        Returns:
            CSS selector string.
        """
        # Try to build a unique selector
        if element.get('id'):
            return f"#{element['id']}"
        
        if element.get('class'):
            classes = ' '.join(element['class'])
            return f".{classes.replace(' ', '.')}"
        
        # Fallback to tag name with parent context
        parent = element.parent
        if parent and parent.name:
            return f"{parent.name} > {element.name}"
        
        return element.name
    
    def get_element_text_preview(self, element, max_length: int = 100) -> str:
        """
        Get a text preview of an element for display to user.
        
        Args:
            element: BeautifulSoup element.
            max_length: Maximum length of preview text.
        
        Returns:
            Preview text string.
        """
        text = element.get_text(strip=True)
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def display_detected_breaks(self, breaks: List[Dict[str, Any]]) -> None:
        """
        Display detected breaks to the user in a readable format.
        
        Args:
            breaks: List of break dictionaries from auto_detect_breaks().
        """
        if not breaks:
            print("\nNo automatic break points detected.")
            return
        
        print(f"\nDetected {len(breaks)} potential break point(s):")
        print("-" * 60)
        for i, break_info in enumerate(breaks, 1):
            preview = self.get_element_text_preview(break_info['element'])
            print(f"{i}. [{break_info['confidence'].upper()}] {break_info['reason']}")
            print(f"   Selector: {break_info['selector']}")
            print(f"   Preview: {preview}")
            print()
    
    def prompt_user_for_breaks(self, auto_detected: List[Dict[str, Any]]) -> List[str]:
        """
        Prompt user to confirm or customize break points.
        
        Args:
            auto_detected: List of automatically detected breaks.
        
        Returns:
            List of CSS selectors to use for breaks.
        """
        if not auto_detected:
            print("\nNo automatic break points were detected.")
            print("Please provide a CSS selector to identify slides/sections.")
            print("Examples: '.slide', '#slides > div', 'section'")
            selector = input("Enter CSS selector: ").strip()
            if selector:
                return [selector]
            return []
        
        self.display_detected_breaks(auto_detected)
        
        print("Options:")
        print("  [Enter] - Use all detected breaks")
        print("  [1-N]   - Use specific break numbers (comma-separated)")
        print("  [c]     - Enter custom CSS selector")
        print("  [n]     - No breaks (single image)")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == '':
            # Use all detected breaks
            return [b['selector'] for b in auto_detected]
        elif choice == 'n':
            return []
        elif choice == 'c':
            selector = input("Enter custom CSS selector: ").strip()
            return [selector] if selector else []
        else:
            # Parse number selection
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = [auto_detected[i]['selector'] for i in indices if 0 <= i < len(auto_detected)]
                return selected
            except (ValueError, IndexError):
                print("Invalid selection. Using all detected breaks.")
                return [b['selector'] for b in auto_detected]
    
    def get_elements_by_selectors(self, selectors: List[str]) -> List:
        """
        Get all elements matching the given selectors.
        
        Args:
            selectors: List of CSS selector strings.
        
        Returns:
            List of BeautifulSoup elements.
        """
        elements = []
        for selector in selectors:
            try:
                # BeautifulSoup's select() method for CSS selectors
                found = self.soup.select(selector)
                elements.extend(found)
            except Exception as e:
                print(f"Warning: Could not parse selector '{selector}': {e}")
        
        return elements
    
    def extract_section_html(self, element) -> str:
        """
        Extract the HTML content of a section element.
        
        Args:
            element: BeautifulSoup element.
        
        Returns:
            HTML string for the element and its contents.
        """
        return str(element)


def parse_html_file(file_path: Path) -> str:
    """
    Read and parse an HTML file.
    
    Args:
        file_path: Path to the HTML file.
    
    Returns:
        HTML content as string.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

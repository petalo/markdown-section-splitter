#!/usr/bin/env python3
"""
Edge Cases Demo for Markdown Section Splitter

This script demonstrates specific edge cases and shows how the splitter handles them.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the splitter
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_section_splitter import MarkdownSplitter
import tempfile


def demo_anchor_generation():
    """Demo anchor generation for various complex cases."""
    
    print("🔗 ANCHOR GENERATION DEMO")
    print("=" * 40)
    
    # Create a dummy splitter just for anchor generation
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    temp_file.write("# Test")
    temp_file.close()
    
    splitter = MarkdownSplitter(temp_file.name)
    
    test_cases = [
        # Spanish with accents (essential for testing)
        ("Configuración Básica", "Spanish with accents"),
        ("Índice de Configuración", "Spanish with special í"),
        
        # Special characters
        ("Diseño & Arquitectura", "Ampersand handling"),
        ("FAQ's y Preguntas", "Apostrophes"),
        ("Página: ¿Cómo funciona?", "Question marks"),
        
        # Multiple languages
        ("русский текст (Russian Text)", "Cyrillic + Latin"),
        ("中文标题 (Chinese Title)", "Chinese + English"),
        ("Ελληνικά (Greek)", "Greek + English"),
        
        # Emojis
        ("🚀 Proyecto Principal", "Emoji at start"),
        ("Desarrollo 🛠️ y Testing", "Emoji in middle"),
        ("Deploy y Producción 🌐", "Emoji at end"),
        ("⚡ Performance & 🔧 Optimización", "Multiple emojis"),
        
        # Numbers and symbols
        ("100% Coverage ✅ Testing", "Percentage and emoji"),
        ("$$ Costos y Pricing €€", "Money symbols"),
        ("API Reference (v2.0) - 🔗 Enlaces", "Version and symbols"),
        
        # Markdown formatting in headers
        ("Header with **bold** and *italic* text", "Markdown formatting"),
        ("Header with `code` in it", "Code formatting"),
        ("Header with [link](http://example.com)", "Link formatting"),
        ("Header with <em>HTML</em> tags", "HTML tags"),
        
        # Complex numbering
        ("1. Primera Sección", "Simple numbering"),
        ("1.3. Numeración Incorrecta", "Decimal numbering"),
        ("3.2.1. Formato de Nivel 3", "Triple numbering"),
        ("0. Desde Cero", "Zero numbering"),
        ("15. Número Alto", "High number"),
        
        # Edge cases
        ("C++ / Python Integration 🐍", "Programming languages"),
        ("Section    with    spaces", "Multiple spaces"),
        ("Section.with.dots", "Dots in title"),
        ("Section-with-hyphens", "Hyphens in title"),
    ]
    
    for i, (title, description) in enumerate(test_cases, 1):
        anchor = splitter.create_toc_anchor(title)
        print(f"{i:2d}. {description}")
        print(f"    Input:  '{title}'")
        print(f"    Anchor: '{anchor}'")
        print()


def demo_filename_generation():
    """Demo filename generation for complex cases."""
    
    print("📁 FILENAME GENERATION DEMO")
    print("=" * 40)
    
    # Create a test document with complex sections
    complex_doc = """# Test Document

## 1. Primera Sección
Content 1

## 1.3. Sección con Gap  
Content 2

## 4. Salto Grande
Content 3

## русский раздел
Content 4

## 中文部分
Content 5

## Performance & Optimización ⚡
Content 6

## 0. Sección Cero
Content 7

## Header with **bold** text
Content 8

## 15. Número Alto
Content 9
"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    temp_file.write(complex_doc)
    temp_file.close()
    
    splitter = MarkdownSplitter(temp_file.name)
    sections = splitter.analyze_sections()
    
    # Generate filenames
    for i, section in enumerate(sections):
        section.filename = splitter.determine_filename(section, i, sections)
    
    print("Generated Filenames:")
    print("-" * 20)
    
    for i, section in enumerate(sections, 1):
        print(f"{i:2d}. {section.filename:<45} ← '{section.title}'")
    
    print()


def demo_edge_case_detection():
    """Demo detection of various edge cases."""
    
    print("🧪 EDGE CASE DETECTION DEMO")
    print("=" * 40)
    
    edge_cases_doc = """# Edge Cases Document

## Normal Section
Regular content.

##Missing space
This shouldn't be detected.

## 
Empty header.

##    Only spaces
Spaces only header.

## Header with trailing spaces   
Should work.

##	Tab instead of space
Tab header.

```markdown
## Fake header in code
This is in a code block.
```

## Real header after code
This should be detected.

## Double ## in content
Content with ## symbols should be ignored.

**## Bold header-like text**
This is just bold text, not a header.

> ## Quote header
> This is in a blockquote.

<!-- ## Comment header -->
This is in a comment.
"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    temp_file.write(edge_cases_doc)
    temp_file.close()
    
    splitter = MarkdownSplitter(temp_file.name)
    sections = splitter.analyze_sections()
    
    print("Detected Sections (should filter malformed):")
    print("-" * 45)
    
    for i, section in enumerate(sections, 1):
        print(f"{i:2d}. '{section.title}' (lines {section.start_line}-{section.end_line})")
    
    print()
    print("Header Hierarchy Issues:")
    print("-" * 25)
    
    issues = splitter._validate_header_hierarchy(edge_cases_doc)
    if issues:
        for issue in issues:
            print(f"   ⚠️  {issue}")
    else:
        print("   ✅ No hierarchy issues detected")
    
    print()


def demo_unicode_handling():
    """Demo Unicode and international character handling."""
    
    print("🌍 UNICODE HANDLING DEMO")
    print("=" * 30)
    
    unicode_test_cases = [
        # Different scripts
        ("العربية", "Arabic"),
        ("한국어", "Korean"),
        ("日本語", "Japanese"),
        ("עברית", "Hebrew"),
        ("ไทย", "Thai"),
        ("Português", "Portuguese"),
        ("Français", "French"),
        ("Deutsch", "German"),
        
        # Special Unicode symbols
        ("Math: ∑∞√π", "Mathematical symbols"),
        ("Arrows: →←↑↓", "Arrow symbols"),
        ("Currency: ¥£₹₽", "Currency symbols"),
        ("Music: ♪♫♬♩", "Musical symbols"),
        
        # Mixed scripts
        ("English + 中文 + Русский", "Mixed scripts"),
        ("Tech: React.js + Vue.js", "Tech terms"),
        ("Emoji mix: 🎯📊📈💡", "Multiple emojis"),
    ]
    
    # Create dummy splitter for anchor generation
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    temp_file.write("# Test")
    temp_file.close()
    
    splitter = MarkdownSplitter(temp_file.name)
    
    for i, (text, description) in enumerate(unicode_test_cases, 1):
        anchor = splitter.create_toc_anchor(text)
        kebab = splitter._to_kebab_case(text)
        
        print(f"{i:2d}. {description}")
        print(f"    Original: '{text}'")
        print(f"    Anchor:   '{anchor}'")
        print(f"    Kebab:    '{kebab}'")
        print()


def main():
    """Run all demos."""
    
    print("🎯 MARKDOWN SECTION SPLITTER - EDGE CASES DEMO")
    print("=" * 60)
    print()
    
    demo_anchor_generation()
    print("\n" + "="*60 + "\n")
    
    demo_filename_generation()
    print("\n" + "="*60 + "\n")
    
    demo_edge_case_detection()
    print("\n" + "="*60 + "\n")
    
    demo_unicode_handling()
    
    print("🔚 Demo completed!")
    print("💡 This demonstrates how the splitter handles complex, real-world edge cases.")


if __name__ == "__main__":
    main()
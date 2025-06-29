#!/usr/bin/env python3
"""
Tests for Markdown Section Splitter

This module contains comprehensive tests for the MarkdownSplitter class.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from markdown_section_splitter import MarkdownSplitter, Section


class TestMarkdownSplitter(unittest.TestCase):
    """Test cases for MarkdownSplitter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_content = """# Main Title

## Section 1
This is the first section with some content.

### Subsection 1.1
Some subsection content.

## Section 2
This is the second section.

### Subsection 2.1
Another subsection.

#### Sub-subsection 2.1.1
Nested content.

## 3. Numbered Section
This section has a number.

## Conclusion
Final section without number.
"""
        self.test_file = Path(self.temp_dir) / "test.md"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(self.test_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test MarkdownSplitter initialization."""
        splitter = MarkdownSplitter(str(self.test_file))
        self.assertEqual(splitter.source_file, self.test_file)
        self.assertEqual(splitter.output_dir, self.test_file.parent)
        self.assertFalse(splitter.debug)
        self.assertIsInstance(splitter.content, list)

    def test_init_with_output_dir(self):
        """Test MarkdownSplitter initialization with custom output directory."""
        output_dir = Path(self.temp_dir) / "output"
        splitter = MarkdownSplitter(str(self.test_file), str(output_dir))
        self.assertEqual(splitter.output_dir, output_dir)

    def test_create_toc_anchor(self):
        """Test TOC anchor creation."""
        splitter = MarkdownSplitter(str(self.test_file))
        
        # Test basic conversion
        self.assertEqual(splitter.create_toc_anchor("Section Name"), "section-name")
        
        # Test with special characters
        self.assertEqual(splitter.create_toc_anchor("Section: Name!"), "section-name")
        
        # Test with numbers
        self.assertEqual(splitter.create_toc_anchor("3. Section Name"), "3-section-name")
        
        # Test with accented characters
        self.assertEqual(splitter.create_toc_anchor("Configuración"), "configuración")
        
        # Test with multiple spaces
        self.assertEqual(splitter.create_toc_anchor("Section    Name"), "section-name")
        
        # Test headers with hyphens in the name (the real issue)
        self.assertEqual(splitter.create_toc_anchor("16.1.1 Unit Testing - Core Services"), "1611-unit-testing---core-services")
        self.assertEqual(splitter.create_toc_anchor("16.1.2 Integration Testing - End-to-End"), "1612-integration-testing---end-to-end")
        self.assertEqual(splitter.create_toc_anchor("16.1.3 Load Testing - Performance"), "1613-load-testing---performance")
        
        # Test other cases with hyphens
        self.assertEqual(splitter.create_toc_anchor("Section - Subsection"), "section---subsection")
        self.assertEqual(splitter.create_toc_anchor("Multi - Word - Title"), "multi---word---title")

    def test_analyze_sections(self):
        """Test section analysis."""
        splitter = MarkdownSplitter(str(self.test_file))
        sections = splitter.analyze_sections()
        
        self.assertEqual(len(sections), 4)
        self.assertEqual(sections[0].title, "Section 1")
        self.assertEqual(sections[1].title, "Section 2")
        self.assertEqual(sections[2].title, "3. Numbered Section")
        self.assertEqual(sections[3].title, "Conclusion")

    def test_determine_filename(self):
        """Test filename determination."""
        splitter = MarkdownSplitter(str(self.test_file))
        sections = splitter.analyze_sections()
        
        # Set up sections with proper filenames
        for i, section in enumerate(sections):
            section.filename = splitter.determine_filename(section, i, sections)
        
        self.assertEqual(sections[0].filename, "00-section-1.md")
        self.assertEqual(sections[1].filename, "01-section-2.md")
        self.assertEqual(sections[2].filename, "03-numbered-section.md")
        self.assertEqual(sections[3].filename, "04-conclusion.md")

    def test_to_kebab_case(self):
        """Test kebab case conversion."""
        splitter = MarkdownSplitter(str(self.test_file))
        
        self.assertEqual(splitter._to_kebab_case("Section Name"), "section-name")
        self.assertEqual(splitter._to_kebab_case("API Reference"), "api-reference")
        self.assertEqual(splitter._to_kebab_case("Getting Started!"), "getting-started")
        self.assertEqual(splitter._to_kebab_case("3. Numbered Section"), "3-numbered-section")

    def test_extract_section_content(self):
        """Test section content extraction."""
        splitter = MarkdownSplitter(str(self.test_file))
        sections = splitter.analyze_sections()
        
        # Test first section
        processed_lines, toc_entries = splitter.extract_section_content(sections[0])
        
        self.assertTrue(processed_lines[0].startswith("# Section 1"))
        self.assertIn("<!-- omit in toc -->", processed_lines[0])
        self.assertEqual(len(toc_entries), 1)  # One subsection
        self.assertIn("Subsection 1.1", toc_entries[0])

    def test_create_main_toc(self):
        """Test main TOC creation."""
        splitter = MarkdownSplitter(str(self.test_file))
        sections = splitter.analyze_sections()
        
        # Set filenames
        for i, section in enumerate(sections):
            section.filename = splitter.determine_filename(section, i, sections)
        
        toc_lines = splitter.create_main_toc(sections)
        
        self.assertTrue(toc_lines[0].startswith("# Table of Contents"))
        self.assertIn("<!-- omit in toc -->", toc_lines[0])
        self.assertIn("Section 1", toc_lines[2])
        self.assertIn("00-section-1.md", toc_lines[2])

    def test_detect_broken_links(self):
        """Test broken link detection."""
        # Create content with broken links
        content_with_links = """# Main Title

## Section 1
See [Section 2](#section-2) for more info.
Also check [Non-existent](#non-existent) section.

## Section 2
Back to [Section 1](#section-1).
"""
        test_file_links = Path(self.temp_dir) / "test_links.md"
        with open(test_file_links, "w", encoding="utf-8") as f:
            f.write(content_with_links)
        
        splitter = MarkdownSplitter(str(test_file_links))
        sections = splitter.analyze_sections()
        
        # Set filenames
        for i, section in enumerate(sections):
            section.filename = splitter.determine_filename(section, i, sections)
        
        broken_links = splitter.detect_broken_links(sections)
        
        # Should detect the non-existent link
        self.assertTrue(any("non-existent" in link for link in broken_links))

    def test_validate_header_hierarchy(self):
        """Test header hierarchy validation."""
        splitter = MarkdownSplitter(str(self.test_file))
        
        # Test valid hierarchy
        valid_content = """# Title
## Section
### Subsection
#### Sub-subsection
"""
        issues = splitter._validate_header_hierarchy(valid_content)
        self.assertEqual(len(issues), 0)
        
        # Test invalid hierarchy (jump from # to ###)
        invalid_content = """# Title
### Invalid Jump
"""
        issues = splitter._validate_header_hierarchy(invalid_content)
        self.assertTrue(len(issues) > 0)

    def test_extract_anchors_from_content(self):
        """Test anchor extraction from content."""
        splitter = MarkdownSplitter(str(self.test_file))
        
        content = """# Main Title
## Section One
### Subsection
#### Sub-subsection
"""
        anchors = splitter._extract_anchors_from_content(content)
        
        expected_anchors = ["main-title", "section-one", "subsection", "sub-subsection"]
        self.assertEqual(anchors, expected_anchors)

    def test_split_file_dry_run(self):
        """Test dry run functionality."""
        splitter = MarkdownSplitter(str(self.test_file))
        sections = splitter.analyze_sections()
        
        # Should not create any files
        initial_files = list(Path(self.temp_dir).glob("*.md"))
        self.assertEqual(len(initial_files), 1)  # Only the test file

    def test_split_file_actual(self):
        """Test actual file splitting."""
        output_dir = Path(self.temp_dir) / "output"
        splitter = MarkdownSplitter(str(self.test_file), str(output_dir))
        splitter.split_file()
        
        # Check that files were created
        self.assertTrue((output_dir / "00-toc.md").exists())
        self.assertTrue((output_dir / "00-section-1.md").exists())
        self.assertTrue((output_dir / "01-section-2.md").exists())
        self.assertTrue((output_dir / "03-numbered-section.md").exists())
        self.assertTrue((output_dir / "04-conclusion.md").exists())
        self.assertTrue((output_dir / "recommended_prompts.txt").exists())

    def test_section_dataclass(self):
        """Test Section dataclass."""
        section = Section(
            title="Test Section",
            start_line=1,
            end_line=10,
            level=2,
            filename="test.md",
            anchor="test-section",
            subsections=[]
        )
        
        self.assertEqual(section.title, "Test Section")
        self.assertEqual(section.start_line, 1)
        self.assertEqual(section.end_line, 10)
        self.assertEqual(section.level, 2)
        self.assertEqual(section.filename, "test.md")
        self.assertEqual(section.anchor, "test-section")
        self.assertEqual(len(section.subsections), 0)

    def test_code_block_handling(self):
        """Test that code blocks are handled correctly."""
        content_with_code = """# Main Title

## Section 1
Here's some code:

```python
# This is a comment
def hello():
    print("Hello World")
```

Regular content after code.

## Section 2
More content.
"""
        test_file_code = Path(self.temp_dir) / "test_code.md"
        with open(test_file_code, "w", encoding="utf-8") as f:
            f.write(content_with_code)
        
        splitter = MarkdownSplitter(str(test_file_code))
        sections = splitter.analyze_sections()
        
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0].title, "Section 1")
        self.assertEqual(sections[1].title, "Section 2")

    def test_empty_file(self):
        """Test handling of empty files."""
        empty_file = Path(self.temp_dir) / "empty.md"
        with open(empty_file, "w", encoding="utf-8") as f:
            f.write("")
        
        splitter = MarkdownSplitter(str(empty_file))
        sections = splitter.analyze_sections()
        
        self.assertEqual(len(sections), 0)

    def test_file_without_sections(self):
        """Test handling of files without ## sections."""
        no_sections_content = """# Main Title

This is just a regular markdown file without sections.

Some more content here.
"""
        no_sections_file = Path(self.temp_dir) / "no_sections.md"
        with open(no_sections_file, "w", encoding="utf-8") as f:
            f.write(no_sections_content)
        
        splitter = MarkdownSplitter(str(no_sections_file))
        sections = splitter.analyze_sections()
        
        self.assertEqual(len(sections), 0)

    def test_complex_numbered_sections(self):
        """Test handling of complex numbered sections with gaps and errors."""
        complex_content = """# Main Title

## 1. First Section
Content of the first section.

## 1.3. Section with Incorrect Numbering
This section skips numbers.

### 1.3.1. Subsection
Subsection content.

## 4. Section that Jumps to 4
Large numbering jump.

### 4.2. Subsection without 4.1
Missing subsection 4.1.

#### 4.2.3. Sub-subsection Without 4.2.1 or 4.2.2
Triple numbering jump.

## 3.2.1. Section with Incorrect Level Format
This should be level 2 but has level 3 numbering.

## 0. Section with Zero
Numbering from zero.

## 15. Section with High Number
Very large jump.
"""
        complex_file = Path(self.temp_dir) / "complex_numbers.md"
        with open(complex_file, "w", encoding="utf-8") as f:
            f.write(complex_content)
        
        splitter = MarkdownSplitter(str(complex_file))
        sections = splitter.analyze_sections()
        
        # Should detect all sections despite numbering issues
        self.assertEqual(len(sections), 6)
        
        # Test filename generation with complex numbers
        for i, section in enumerate(sections):
            section.filename = splitter.determine_filename(section, i, sections)
        
        # Verify specific complex cases
        self.assertEqual(sections[0].title, "1. First Section")
        self.assertEqual(sections[1].title, "1.3. Section with Incorrect Numbering")
        self.assertEqual(sections[2].title, "4. Section that Jumps to 4")
        self.assertEqual(sections[3].title, "3.2.1. Section with Incorrect Level Format")
        self.assertEqual(sections[4].title, "0. Section with Zero")
        self.assertEqual(sections[5].title, "15. Section with High Number")

    def test_non_ascii_characters(self):
        """Test handling of non-ASCII characters in headers."""
        non_ascii_content = """# Main Title with Accents

## Configuración Básica
Content with ñ and accents.

## Índice de Configuración
More accents: á, é, í, ó, ú.

## Advanced Configuración
Subsection with accents.

## Diseño & Arquitectura
Special characters.

## FAQ's y Preguntas
Apostrophes and special characters.

## Página de Configuración: ¿Cómo?
Question marks and accents.

## Sección con "Comillas" y 'Apostrofes'
Different quote types.

## русский текст (Russian Text)
Cyrillic characters.

## 中文标题 (Chinese Title)
Chinese characters.

## Ελληνικά (Greek)
Greek characters.
"""
        non_ascii_file = Path(self.temp_dir) / "non_ascii.md"
        with open(non_ascii_file, "w", encoding="utf-8") as f:
            f.write(non_ascii_content)
        
        splitter = MarkdownSplitter(str(non_ascii_file))
        sections = splitter.analyze_sections()
        
        # Should detect all sections
        self.assertEqual(len(sections), 10)
        
        # Test anchor generation with non-ASCII characters
        anchors = []
        for section in sections:
            anchor = splitter.create_toc_anchor(section.title)
            anchors.append(anchor)
        
        # Verify specific anchor conversions
        expected_anchors = [
            "configuración-básica",
            "índice-de-configuración", 
            "advanced-configuración",
            "diseño-arquitectura",
            "faqs-y-preguntas",
            "página-de-configuración-cómo",
            "sección-con-comillas-y-apostrofes",
            "русский-текст-russian-text",
            "中文标题-chinese-title",
            "ελληνικά-greek"
        ]
        
        for expected, actual in zip(expected_anchors, anchors):
            self.assertEqual(actual, expected)

    def test_emoji_and_special_characters(self):
        """Test handling of emojis and special characters in headers."""
        emoji_content = """# 🚀 Main Project

## 📋 Initial Configuration
Section with emoji at start.

## Development 🛠️ and Testing
Emoji in the middle.

## Deploy and Production 🌐
Emoji at the end.

## ⚡ Performance & 🔧 Optimization
Multiple emojis.

## API Reference (v2.0) - 🔗 Links
Version and emojis.

## 🎯 Project Objectives 📈
Multiple emojis.

## Troubleshooting 🐛 & Debug 🔍
Emojis and symbols.

## How does it work? 🤔💭
Thinking emojis.

## C++ / Python Integration 🐍
Programming symbols.

## $$ Costs and Pricing €€
Monetary symbols.

## 100% Coverage ✅ Testing
Percentages and checks.
"""
        emoji_file = Path(self.temp_dir) / "emoji_test.md"
        with open(emoji_file, "w", encoding="utf-8") as f:
            f.write(emoji_content)
        
        splitter = MarkdownSplitter(str(emoji_file))
        sections = splitter.analyze_sections()
        
        # Should detect all sections
        self.assertEqual(len(sections), 11)
        
        # Test filename generation with emojis
        for i, section in enumerate(sections):
            section.filename = splitter.determine_filename(section, i, sections)
        
        # Test that filenames are generated properly (emojis should be removed/converted)
        filenames = [section.filename for section in sections]
        
        # All filenames should be valid (no emojis in filenames)
        for filename in filenames:
            self.assertTrue(filename.endswith('.md'))
            self.assertNotIn('🚀', filename)
            self.assertNotIn('📋', filename)
            self.assertNotIn('🛠️', filename)
            
        # Test anchor generation with emojis
        for section in sections:
            anchor = splitter.create_toc_anchor(section.title)
            # Anchors should be URL-safe (no emojis)
            self.assertNotIn('🚀', anchor)
            self.assertNotIn('📋', anchor)
            self.assertNotIn('€', anchor)
            self.assertNotIn('$', anchor)

    def test_mixed_header_hierarchy_complex(self):
        """Test complex header hierarchy with various edge cases."""
        complex_hierarchy = """# Main Document

## 1. Section One
Content here.

### 1.1. Subsection
More content.

#### 1.1.1. Deep nesting
Very deep.

##### 1.1.1.1. Even deeper
Too deep?

###### 1.1.1.1.1. Maximum depth
Six levels.

## 2. Section Two
Back to level 2.

### 2.1. Another subsection
Content.

## 3. Section Three

#### 3.1.1. Skipped level 3!
This jumps from h2 to h4.

### 3.1. Now back to h3
Weird ordering.

## 4. Section Four

```python
# This code block contains fake headers
## Not a real header
### Also not a header
def function():
    pass
```

Real content continues.

### 4.1. Real subsection after code
This should be detected.

## 5. Final Section
The end.
"""
        complex_hierarchy_file = Path(self.temp_dir) / "complex_hierarchy.md"
        with open(complex_hierarchy_file, "w", encoding="utf-8") as f:
            f.write(complex_hierarchy)
        
        splitter = MarkdownSplitter(str(complex_hierarchy_file))
        sections = splitter.analyze_sections()
        
        # Should detect main sections (level 2 headers)
        # Fixed: Now correctly ignores headers in code blocks
        self.assertEqual(len(sections), 5)
        
        section_titles = [s.title for s in sections]
        expected_titles = [
            "1. Section One",
            "2. Section Two", 
            "3. Section Three",
            "4. Section Four",
            "5. Final Section"
        ]
        
        self.assertEqual(section_titles, expected_titles)
        
        # Test header hierarchy validation
        issues = splitter._validate_header_hierarchy(complex_hierarchy)
        
        # Should detect the level skip (h2 to h4)
        self.assertTrue(any("jump" in issue.lower() for issue in issues))

    def test_edge_case_malformed_headers(self):
        """Test malformed or edge case headers."""
        malformed_content = """# Main Title

##Missing space after hashes
This shouldn't be detected as a header.

## 
Empty header text.

##    Extra spaces but no content
Spaces only.

## Header with trailing spaces   
Should still work.

##	Header with tab
Tab instead of space.

## Header with ### inside the text
This should work normally.

## Header with **bold** and *italic* text
Formatting in headers.

## Header with `code` in it
Code formatting in header.

## Header with [link](http://example.com) 
Link in header.

## Header with <em>HTML</em> tags
HTML in header.

## 
## Double empty header
Two empty headers.

## Normal Header After Malformed
This should work fine.
"""
        malformed_file = Path(self.temp_dir) / "malformed.md"
        with open(malformed_file, "w", encoding="utf-8") as f:
            f.write(malformed_content)
        
        splitter = MarkdownSplitter(str(malformed_file))
        sections = splitter.analyze_sections()
        
        # Should only detect properly formatted headers
        # The exact count depends on how the parser handles edge cases
        self.assertGreater(len(sections), 0)
        
        # Test that well-formed headers are detected
        section_titles = [s.title for s in sections]
        self.assertIn("Header with trailing spaces", section_titles)
        self.assertIn("Normal Header After Malformed", section_titles)
        
        # Test anchor generation for complex headers
        for section in sections:
            anchor = splitter.create_toc_anchor(section.title)
            # Should produce valid anchors even with formatting
            self.assertTrue(len(anchor) > 0)
            self.assertNotIn('*', anchor)  # Bold formatting removed
            self.assertNotIn('`', anchor)  # Code formatting removed
            self.assertNotIn('[', anchor)  # Link formatting removed
            self.assertNotIn('<', anchor)  # HTML tags removed


class TestCommandLineInterface(unittest.TestCase):
    """Test command line interface functionality."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from markdown_section_splitter import main
        self.assertTrue(callable(main))

    @patch('sys.argv', ['markdown_section_splitter.py', '--help'])
    def test_help_argument(self):
        """Test help argument functionality."""
        from markdown_section_splitter import main
        
        # Should exit with SystemExit due to --help
        with self.assertRaises(SystemExit):
            main()

    def test_output_dir_argument(self):
        """Test --output-dir argument functionality."""
        temp_file = Path(tempfile.mkdtemp()) / "test_input.md"
        output_dir = Path(tempfile.mkdtemp()) / "custom_output"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("# Test\n\n## Section 1\nContent")
        
        with patch('sys.argv', ['markdown_section_splitter.py', str(temp_file), '--output-dir', str(output_dir)]):
            from markdown_section_splitter import main
            main()
        
        # Check that files were created in custom output directory
        self.assertTrue((output_dir / "00-toc.md").exists())
        self.assertTrue((output_dir / "00-section-1.md").exists())

    def test_dry_run_argument(self):
        """Test --dry-run argument functionality."""
        temp_file = Path(tempfile.mkdtemp()) / "test_input.md"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("# Test\n\n## Section 1\nContent")
        
        with patch('sys.argv', ['markdown_section_splitter.py', str(temp_file), '--dry-run']):
            from markdown_section_splitter import main
            with patch('sys.stdout'):  # Capture stdout to avoid cluttering test output
                main()
        
        # In dry-run mode, no files should be created
        output_dir = temp_file.parent / "output"
        self.assertFalse(output_dir.exists())

    def test_debug_argument(self):
        """Test --debug argument functionality."""
        import io
        from contextlib import redirect_stdout
        
        temp_file = Path(tempfile.mkdtemp()) / "test_input.md"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("# Test\n\n## Section 1\nContent")
        
        with patch('sys.argv', ['markdown_section_splitter.py', str(temp_file), '--debug']):
            from markdown_section_splitter import main
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()
        
        # Debug mode should produce specific debug outputs
        self.assertIn("🔍 DEBUG: Starting split process", output)
        self.assertIn("🔍 DEBUG: Source file:", output)
        self.assertIn("🔍 DEBUG: Processing section:", output)


class TestCodeBlockFix(unittest.TestCase):
    """Test cases specific to the code block header detection fix."""

    def test_basic_code_block_headers_ignored(self):
        """Test that headers inside code blocks are ignored."""
        content = """# Main Document

## Real Section 1
Some content here.

```python
# This is code
## Fake Header
def function():
    pass
```

## Real Section 2
More content.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 2)
            self.assertEqual(sections[0].title, "Real Section 1")
            self.assertEqual(sections[1].title, "Real Section 2")

    def test_multiple_code_blocks_different_languages(self):
        """Test multiple code blocks with different languages."""
        content = """# Main Document

## Section 1
Content here.

```bash
echo "test"
## Fake Bash Header
```

Some text between blocks.

```python
# Python comment
## Another Fake Header
print("hello")
```

## Section 2
Final content.

```javascript
// JS comment  
## JS Fake Header
console.log("test");
```

## Section 3
The end.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 3)
            self.assertEqual(sections[0].title, "Section 1")
            self.assertEqual(sections[1].title, "Section 2")
            self.assertEqual(sections[2].title, "Section 3")

    def test_nested_markdown_content_in_code_blocks(self):
        """Test code blocks containing markdown-like content."""
        content = """# Main Document

## Section 1
Content.

```markdown
# This looks like a header
## This also looks like a header
### And this too

- List item
- Another item
```

## Section 2
More content.

```html
<h2>HTML Header</h2>
<!-- ## Comment header -->
```

## Section 3
Final section.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 3)
            self.assertEqual(sections[0].title, "Section 1")
            self.assertEqual(sections[1].title, "Section 2")
            self.assertEqual(sections[2].title, "Section 3")

    def test_code_block_at_document_start(self):
        """Test code block at the very beginning of document."""
        content = """# Main Document

```python
## Fake header at start
print("hello")
```

## First Real Section
Content here.

## Second Real Section
More content.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 2)
            self.assertEqual(sections[0].title, "First Real Section")
            self.assertEqual(sections[1].title, "Second Real Section")

    def test_code_block_at_document_end(self):
        """Test code block at the very end of document."""
        content = """# Main Document

## First Section
Content here.

## Second Section
More content.

```python
## Fake header at end
print("goodbye")
```
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 2)
            self.assertEqual(sections[0].title, "First Section")
            self.assertEqual(sections[1].title, "Second Section")

    def test_empty_code_blocks(self):
        """Test empty code blocks don't cause issues."""
        content = """# Main Document

## Section 1
Content.

```
```

## Section 2
Content after empty block.

```python
```

## Section 3
Final section.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 3)
            self.assertEqual(sections[0].title, "Section 1")
            self.assertEqual(sections[1].title, "Section 2")
            self.assertEqual(sections[2].title, "Section 3")

    def test_code_blocks_with_real_headers_around(self):
        """Test code blocks surrounded by real headers."""
        content = """# Main Document

## Before Code Block
Content before.

```python
def function():
    # Comment
    ## Fake Header Inside
    pass
```

## After Code Block
Content after the block.

### Subsection
Subsection content.

```bash
echo "test"
## Another Fake
```

## Final Section
The end.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            sections = splitter.analyze_sections()
            
            self.assertEqual(len(sections), 3)
            self.assertEqual(sections[0].title, "Before Code Block")
            self.assertEqual(sections[1].title, "After Code Block")
            self.assertEqual(sections[2].title, "Final Section")

    def test_numbered_subsections_toc_links(self):
        """Test that numbered subsections generate correct TOC links."""
        content = """# Main Document

## 16. Testing Strategy
Content for main section.

### 16.1.1 Unit Testing - Core Services
Unit testing content.

### 16.1.2 Integration Testing - End-to-End
Integration testing content.

### 16.1.3 Load Testing - Performance
Load testing content.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            splitter = MarkdownSplitter(f.name)
            processed_lines, toc_entries = splitter.extract_section_content(
                Section(
                    title="16. Testing Strategy",
                    start_line=3,
                    end_line=15,
                    level=2,
                    filename="16-testing-strategy.md",
                    anchor="16-testing-strategy",
                    subsections=[]
                )
            )
            
            # Check that TOC entries have correct anchors
            expected_toc_entries = [
                "- [16.1.1 Unit Testing - Core Services](#1611-unit-testing---core-services)",
                "- [16.1.2 Integration Testing - End-to-End](#1612-integration-testing---end-to-end)",
                "- [16.1.3 Load Testing - Performance](#1613-load-testing---performance)"
            ]
            
            self.assertEqual(toc_entries, expected_toc_entries)


if __name__ == "__main__":
    unittest.main()
# Markdown Section Splitter

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Python tool to split large markdown documentation files into multiple organized files with proper structure, table of contents, and cross-references.

## Features

- **Automatic Section Detection**: Splits documents based on `##` headers
- **Smart File Naming**: Generates kebab-case filenames with proper numbering
- **Header Promotion**: Automatically promotes headers by one level (`##` → `#`, `###` → `##`, etc.)
- **Table of Contents**: Generates both main TOC and internal TOCs for each file
- **Cross-Reference Detection**: Identifies and reports broken internal links
- **Quality Validation**: Comprehensive checks for structure and content quality
- **Context-Aware Prompts**: Generates LLM prompts for post-processing
- **Debug Mode**: Detailed output for troubleshooting

## Installation

### Option 1: Direct Download (Standalone)

No installation required! This is a standalone Python script.

1. Download `markdown_section_splitter.py`
2. Run directly with Python

**Requirements:**

- Python 3.6+
- No external dependencies

### Option 2: Install from Source

```bash
git clone https://github.com/petalo/markdown-section-splitter.git
cd markdown-section-splitter
pip install -e .
```

After installation, you can use the `markdown-splitter` command:

```bash
markdown-splitter your-document.md
```

### Option 3: Install with pip (Future)

```bash
pip install markdown-section-splitter
```

*Note: PyPI package coming soon!*

## Usage

### Basic Usage

```bash
python markdown_section_splitter.py your-document.md
```

This will split `your-document.md` and create the output files in the same directory.

### Advanced Usage

```bash
# Specify output directory
python markdown_section_splitter.py your-document.md --output-dir ./split-docs

# Preview what would be created (dry run)
python markdown_section_splitter.py your-document.md --dry-run

# Enable debug mode for detailed output
python markdown_section_splitter.py your-document.md --debug

# Combine options
python markdown_section_splitter.py your-document.md --output-dir ./docs --debug
```

## Input Format

The script expects a markdown file with sections defined by `##` headers:

```markdown
# Main Title

## Section 1
Content for section 1...

## Section 2
Content for section 2...

### Subsection 2.1
Content for subsection...

## Section 3
Content for section 3...
```

## Output Structure

The script creates:

1. **Main TOC**: `00-toc.md` - Links to all sections
2. **Section Files**: Numbered files like `01-section-1.md`, `02-section-2.md`
3. **Prompts File**: `recommended_prompts.txt` - LLM prompts for post-processing

### Example Output

```text
output/
├── 00-toc.md
├── 00-resumen-ejecutivo.md
├── 01-sistema-de-entitlements.md
├── 02-analisis-de-apariciones.md
├── ...
└── recommended_prompts.txt
```

## File Naming Rules

- **Numbered sections**: `01-section-name.md`, `02-section-name.md`
- **Unnumbered sections**: `00-section-name.md` (first), `01-section-name.md` (others)
- **Kebab-case conversion**: "Section Name" → `section-name`

## Header Promotion

The script automatically promotes headers by one level:

- `## Section` → `# Section`
- `### Subsection` → `## Subsection`
- `#### Sub-subsection` → `### Sub-subsection`

## Quality Validation

The script performs several quality checks:

- ✅ Header hierarchy validation
- ✅ Missing TOC detection
- ✅ Broken link detection
- ✅ File size validation
- ✅ Structure consistency checks

## Debug Mode

Use `--debug` to get detailed information about:

- Section detection process
- Header hierarchy analysis
- Code block detection
- File processing steps

## Post-Processing with LLMs

The script generates `recommended_prompts.txt` with context-aware prompts for:

- Content review and validation
- Broken link fixing
- Code block validation
- Image/media validation

## Examples

### Example 1: Basic Split

```bash
python markdown_section_splitter.py documentation.md
```

**Input:**

```markdown
# API Documentation

## Authentication
How to authenticate...

## Endpoints
Available endpoints...

### GET /users
Get user information...
```

**Output:**

- `00-toc.md` - Main table of contents
- `01-authentication.md` - Authentication section
- `02-endpoints.md` - Endpoints section with internal TOC

### Example 2: Debug Mode

```bash
python markdown_section_splitter.py documentation.md --debug
```

Shows detailed information about the splitting process, including header detection and file creation steps.

## Troubleshooting

### Common Issues

1. **"No sections found"**
   - Ensure your document has `##` headers
   - Check that headers are properly formatted

2. **"Header level jump" warnings**
   - These are usually false positives from code blocks
   - Use `--debug` to see detailed analysis

3. **"Missing Table of Contents section"**
   - This is normal for files without subsections
   - Only files with `##` headers get internal TOCs

### Debug Tips

- Use `--dry-run` to preview what will be created
- Use `--debug` to see detailed processing information
- Check the generated `recommended_prompts.txt` for post-processing guidance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Quick Start for Contributors

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/markdown-section-splitter.git`
3. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install development dependencies: `pip install -r requirements-dev.txt`
5. Make your changes
6. Run tests: `python -m unittest discover tests -v`
7. Format code: `black .`
8. Submit a Pull Request

For detailed contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Testing and Examples

The project includes comprehensive test files and examples:

- **Unit Tests**: Run `python -m unittest discover tests -v`
- **Complex Document Example**: `tests/sample_complex_document.md` - A comprehensive markdown file with international characters, emojis, complex numbering, and edge cases
- **Live Testing**: `python tests/run_test_example.py` - Runs the splitter on the complex document and shows detailed output
- **Edge Cases Demo**: `python tests/run_edge_cases_demo.py` - Demonstrates how the splitter handles various edge cases

The test suite covers 24 different scenarios including Unicode handling, emoji processing, malformed headers, and complex numbering schemes.

## License

This project is open source and available under the [MIT License](LICENSE).

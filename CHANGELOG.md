# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1] - 2025-06-29

### Fixed

- Fixed anchor generation for headers with hyphens (e.g., "Unit Testing - Core Services")
- TOC links now preserve multiple hyphens to match GitHub's behavior
- Improved test coverage for numbered subsections with hyphenated names

## [0.5.0] - 2025-06-29

### Added

- Initial release of Markdown Section Splitter
- Automatic section detection based on `##` headers
- Smart file naming with kebab-case conversion
- Header promotion (automatically promotes headers by one level)
- Table of Contents generation (both main TOC and internal TOCs)
- Cross-reference detection and broken link reporting
- Quality validation with comprehensive checks
- Context-aware prompt generation for LLM post-processing
- Debug mode for detailed output
- Dry run mode for previewing changes
- Comprehensive test suite
- Command-line interface with argparse
- Support for Python 3.6+

### Features

- **Automatic Section Detection**: Splits documents based on `##` headers
- **Smart File Naming**: Generates kebab-case filenames with proper numbering
- **Header Promotion**: Automatically promotes headers by one level
- **Table of Contents**: Generates both main TOC and internal TOCs for each file
- **Cross-Reference Detection**: Identifies and reports broken internal links
- **Quality Validation**: Comprehensive checks for structure and content quality
- **Context-Aware Prompts**: Generates LLM prompts for post-processing
- **Debug Mode**: Detailed output for troubleshooting
- **Dry Run Mode**: Preview changes without creating files

### Technical Details

- Zero external dependencies (uses only Python standard library)
- Comprehensive error handling and validation
- Well-documented code with type hints
- Extensive test coverage
- Modern Python packaging with pyproject.toml
- Cross-platform compatibility

### Documentation

- Comprehensive README with usage examples
- Inline code documentation
- Test examples demonstrating functionality
- Troubleshooting guide
- Contributing guidelines

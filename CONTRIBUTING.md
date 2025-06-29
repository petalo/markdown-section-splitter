# Contributing to Markdown Section Splitter

Thank you for considering contributing to Markdown Section Splitter! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a simple code of conduct: be respectful, constructive, and helpful in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.6 or higher
- Git

### Setup Instructions

1. Clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/markdown-section-splitter.git
   cd markdown-section-splitter
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

4. Run tests to ensure everything works:

   ```bash
   python -m unittest discover tests -v
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues in the existing code
- **Feature enhancements**: Add new functionality
- **Documentation improvements**: Improve README, code comments, or add examples
- **Test improvements**: Add or improve test coverage
- **Performance optimizations**: Make the code run faster or use less memory

### Before You Start

1. Check existing issues to see if your idea/bug is already being discussed
2. For major changes, consider opening an issue first to discuss the approach
3. Make sure you understand the project's goals and scope

## Testing

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run a specific test
python -m unittest tests.test_markdown_section_splitter.TestMarkdownSplitter.test_analyze_sections -v
```

### Writing Tests

- Add tests for any new functionality
- Ensure your tests cover edge cases
- Use descriptive test names
- Follow the existing test structure

### Test Coverage

The project aims for high test coverage. When adding new features:

1. Write tests for the happy path
2. Write tests for error conditions
3. Write tests for edge cases
4. Test with different input types

## Code Style

### Python Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write descriptive docstrings for classes and functions
- Keep functions focused and reasonably sized
- Use meaningful variable and function names

### Code Formatting

We recommend using `black` for code formatting:

```bash
black markdown_section_splitter.py test_markdown_section_splitter.py
```

### Linting

Use `flake8` for linting:

```bash
flake8 markdown_section_splitter.py test_markdown_section_splitter.py
```

### Type Checking

Use `mypy` for type checking:

```bash
mypy markdown_section_splitter.py
```

## Submitting Changes

### Pull Request Process

1. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes in logical, atomic commits

3. Write clear commit messages:

   ```text
   Add feature: support for custom TOC headers
   
   - Allow users to specify custom TOC header text
   - Update tests to cover new functionality
   - Update documentation with examples
   ```

4. Push your branch to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a pull request on GitHub

### Pull Request Requirements

- All tests must pass
- Code should follow the project's style guidelines
- Include tests for new functionality
- Update documentation if needed
- Provide a clear description of the changes

### Review Process

1. Maintainers will review your pull request
2. You may be asked to make changes
3. Once approved, your PR will be merged

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Clear steps to reproduce the issue
- Expected behavior vs. actual behavior
- Any error messages
- Sample input files (if applicable)

### Feature Requests

When requesting features:

- Describe the use case
- Explain why this feature would be beneficial
- Provide examples of how it would work
- Consider if it fits the project's scope

### Issue Templates

Use these templates when creating issues:

**Bug Report:**

```text
**Bug Description:**
Brief description of the bug.

**To Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**Environment:**
- Python version:
- OS:
- File details:

**Additional Context:**
Any other context about the problem.
```

**Feature Request:**

```text
**Feature Description:**
Brief description of the feature.

**Use Case:**
Why is this feature needed?

**Proposed Solution:**
How do you think this should work?

**Additional Context:**
Any other context or screenshots.
```

## Development Guidelines

### Architecture

- Keep the main `MarkdownSplitter` class focused on core functionality
- Use the `Section` dataclass for representing document sections
- Separate concerns: parsing, processing, and output generation
- Maintain backward compatibility when possible

### Error Handling

- Use appropriate exception types
- Provide helpful error messages
- Handle edge cases gracefully
- Don't suppress errors unless necessary

### Performance

- Consider performance impact of changes
- Use efficient algorithms and data structures
- Profile code when making performance claims
- Document any performance trade-offs

## Questions?

If you have questions about contributing:

1. Check the existing documentation
2. Look at existing issues and pull requests
3. Create a new issue with the "question" label
4. Contact the maintainers

Thank you for contributing to Markdown Section Splitter!

#!/bin/bash
# Quick PyPI upload commands for Markdown Section Splitter

set -e  # Exit on any error

echo "🚀 Starting PyPI upload process..."

# Check if build tools are installed
echo "📦 Checking build tools..."
python -m pip install --upgrade build twine

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "🔨 Building package..."
python -m build

# List built files
echo "📋 Built files:"
ls -la dist/

# Upload to TestPyPI first (safer)
echo "🧪 Uploading to TestPyPI..."
read -p "Press Enter to upload to TestPyPI (or Ctrl+C to cancel): "
python -m twine upload --repository testpypi dist/*

echo "✅ Uploaded to TestPyPI!"
echo "🔗 Check: https://test.pypi.org/project/markdown-section-splitter/"

# Test installation from TestPyPI
echo "🧪 Testing installation from TestPyPI..."
read -p "Press Enter to test install from TestPyPI (or Ctrl+C to skip): "
pip install --index-url https://test.pypi.org/simple/ --no-deps markdown-section-splitter

# Test the installation
echo "🧪 Testing CLI..."
markdown-splitter --help

echo "✅ TestPyPI installation works!"

# Upload to production PyPI
echo "🚀 Ready to upload to production PyPI..."
read -p "Press Enter to upload to production PyPI (or Ctrl+C to cancel): "
python -m twine upload dist/*

echo "🎉 Successfully uploaded to PyPI!"
echo "🔗 Check: https://pypi.org/project/markdown-section-splitter/"

# Test production installation
echo "🧪 Testing production installation..."
read -p "Press Enter to test production install (or Ctrl+C to skip): "
pip install --upgrade markdown-section-splitter

echo "✅ Production installation works!"
echo "🎉 Package is now available via: pip install markdown-section-splitter"
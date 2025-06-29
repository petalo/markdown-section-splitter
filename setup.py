#!/usr/bin/env python3
"""Setup script for Markdown Section Splitter."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="markdown-section-splitter",
    version="0.5.0",
    author="Diego Mariño",
    author_email="diegomarino@users.noreply.github.com",
    description="A tool to split large markdown files into organized sections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/petalo/markdown-section-splitter",
    py_modules=["markdown_section_splitter"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "markdown-splitter=markdown_section_splitter:main",
        ],
    },
    keywords="markdown documentation splitter toc",
    project_urls={
        "Bug Reports": "https://github.com/petalo/markdown-section-splitter/issues",
        "Source": "https://github.com/petalo/markdown-section-splitter",
    },
)

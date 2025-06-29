#!/usr/bin/env python3
"""
Markdown Section Splitter

A tool to split large markdown documentation files into multiple organized files
with proper structure, TOCs, and cross-references.

Usage:
    python markdown_section_splitter.py source_file [--output-dir output_dir] [--dry-run] [--debug]

Features:
    - Automatic TOC detection and generation
    - Intelligent section numbering based on ## headers
    - Header level promotion
    - Cross-file linking
    - Configurable output structure
    - Post-processing suggestions for broken links
    - Debug mode for detailed output
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Section:
    """Represents a section in the markdown file."""

    title: str
    start_line: int
    end_line: int
    level: int
    filename: str
    anchor: str
    subsections: List["Section"]


class MarkdownSplitter:
    """Main class for splitting markdown files."""

    def __init__(
        self, source_file: str, output_dir: Optional[str] = None, debug: bool = False
    ) -> None:
        """Initialize the splitter with source file and optional output directory.

        Args:
            source_file: Path to the source markdown file
            output_dir: Output directory (default: same as source file)
            debug: Enable debug mode for detailed output
        """
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir) if output_dir else self.source_file.parent
        self.debug = debug
        self.content = self._read_file()
        self.sections: List[Section] = []
        self.broken_links: List[str] = []

    def _read_file(self) -> List[str]:
        """Read the source markdown file.

        Returns:
            List of lines from the file
        """
        with open(self.source_file, "r", encoding="utf-8") as f:
            return f.readlines()

    def create_toc_anchor(self, text: str) -> str:
        """Create a proper anchor for TOC links following GitHub's exact standard.

        Args:
            text: The text to convert to an anchor

        Returns:
            URL-safe anchor string
        """
        # Follow GitHub's exact standard for anchor generation
        anchor = text.strip()

        # Convert to lowercase
        anchor = anchor.lower()

        # Remove markdown formatting characters (asterisks, backticks)
        anchor = re.sub(r"[`*]", "", anchor)

        # Remove dots explicitly (instead of replacing them with hyphens)
        anchor = re.sub(r"\.", "", anchor, flags=re.UNICODE)

        # Remove special characters except alphanumeric, spaces, hyphens, colons, and accented characters
        # GitHub preserves accented characters like á, é, í, ó, ú, ñ, etc.
        # Use a more precise pattern that matches GitHub's behavior exactly
        anchor = re.sub(r"[^\w\s\-:áéíóúüñ]", "", anchor, flags=re.UNICODE)

        # Replace spaces and colons with hyphens
        anchor = re.sub(r"[\s:]+", "-", anchor)

        # Remove leading/trailing hyphens
        anchor = anchor.strip("-")

        return anchor

    def detect_toc(self) -> Optional[List[str]]:
        """Detect if there's an existing TOC in the first lines using multiple strategies.

        Returns:
            List of TOC lines if found, None otherwise
        """
        # Strategy 1: Look for explicit TOC headers
        toc_lines = self._detect_toc_by_header()
        if toc_lines:
            return toc_lines

        # Strategy 2: Look for bullet points with markdown links (most common)
        toc_lines = self._detect_toc_by_bullet_links()
        if toc_lines:
            return toc_lines

        # Strategy 3: Look for consecutive bullet points (fallback)
        toc_lines = self._detect_toc_by_bullets_only()
        if toc_lines:
            return toc_lines

        return None

    def _detect_toc_by_header(self) -> Optional[List[str]]:
        """Detect TOC by looking for explicit TOC headers.

        Returns:
            List of TOC lines if found, None otherwise
        """
        toc_lines = []
        in_toc = False

        for line in self.content[:50]:
            line = line.strip()

            # Look for TOC headers
            if line.startswith(
                (
                    "## Table of Contents",
                    "# Table of Contents",
                    "## Contents",
                    "# Contents",
                )
            ):
                in_toc = True
                continue

            if in_toc:
                # End TOC when we hit another header
                if line.startswith(("## ", "# ")):
                    break
                # Collect TOC entries
                if line and line.startswith("- "):
                    toc_lines.append(line)

        return toc_lines if toc_lines else None

    def _detect_toc_by_bullet_links(self) -> Optional[List[str]]:
        """Detect TOC by looking for bullet points with markdown links.

        Returns:
            List of TOC lines if found, None otherwise
        """
        toc_lines = []
        header_count = 0
        max_headers_to_check = 4
        consecutive_toc_entries = 0

        for line in self.content[:100]:  # Check first 100 lines
            line = line.strip()

            # Count headers
            if line.startswith(("## ", "# ")):
                header_count += 1
                if header_count > max_headers_to_check:
                    break

            # Look for bullet points with markdown links: - [text](link)
            if re.match(r"^\s*[-*]\s+\[.*\]\(.*\)", line):
                toc_lines.append(line)
                consecutive_toc_entries += 1
            elif line.startswith(("## ", "# ")):
                # Reset if we hit a header
                consecutive_toc_entries = 0
                toc_lines = []  # Reset TOC lines
            elif line and not line.startswith(("## ", "# ")):
                consecutive_toc_entries = 0

        # Only return if we found a reasonable number of consecutive TOC entries
        return toc_lines if consecutive_toc_entries >= 3 else None

    def _detect_toc_by_bullets_only(self) -> Optional[List[str]]:
        """Detect TOC by looking for bullet point patterns that look like TOC (fallback).

        Returns:
            List of TOC lines if found, None otherwise
        """
        toc_lines = []
        consecutive_bullets = 0
        max_consecutive = 0

        for line in self.content[:100]:
            line = line.strip()

            # Look for bullet patterns that could be TOC (without links)
            if re.match(r"^\s*[-*]\s+[A-Za-z]", line):  # Bullet + capital letter
                consecutive_bullets += 1
                toc_lines.append(line)
            elif line.startswith(("## ", "# ")):
                # Reset if we hit a header
                if consecutive_bullets > max_consecutive:
                    max_consecutive = consecutive_bullets
                consecutive_bullets = 0
                toc_lines = []  # Reset TOC lines
            elif line and not line.startswith(("## ", "# ")):
                consecutive_bullets = 0

        # Only return if we found a reasonable pattern
        return toc_lines if max_consecutive >= 3 else None

    def analyze_sections(self) -> List[Section]:
        """Analyze file structure and extract sections based on ## headers.

        Returns:
            List of Section objects representing the document structure
        """
        sections = []
        current_section: Optional[Section] = None
        in_code_block = False

        for line_num, line in enumerate(self.content, 1):
            line = line.strip()

            # Check if we're entering or leaving a code block
            if line.startswith("```"):
                in_code_block = not in_code_block
                if self.debug:
                    print(
                        f"🔍 DEBUG: Code block {'started' if in_code_block else 'ended'} at line {line_num}"
                    )
                continue

            # Skip header detection if we're inside a code block
            if in_code_block:
                if self.debug and line.startswith("## "):
                    print(
                        f"🔍 DEBUG: Ignoring header in code block at line {line_num}: {line}"
                    )
                continue

            if line.startswith("## ") and not line.startswith("## Table of Contents"):
                # Found a main section
                title = line.replace("## ", "").strip()

                if current_section:
                    current_section.end_line = line_num - 1
                    sections.append(current_section)

                current_section = Section(
                    title=title,
                    start_line=line_num,
                    end_line=len(self.content),
                    level=2,
                    filename="",
                    anchor=self.create_toc_anchor(title),
                    subsections=[],
                )

        # Add the last section
        if current_section:
            sections.append(current_section)

        return sections

    def determine_filename(
        self, section: Section, index: int, all_sections: List[Section]
    ) -> str:
        """Determine filename based on numbering rules from the prompt.

        Args:
            section: The section to determine filename for
            index: Index of the section in the list
            all_sections: List of all sections for context

        Returns:
            Filename for the section
        """
        title = section.title

        # Extract number from title if it exists
        number_match = re.match(r"^(\d+)\.\s*(.+)$", title)

        if number_match:
            # Section has a number
            number = int(number_match.group(1))
            clean_title = number_match.group(2)
            filename = f"{number:02d}-{self._to_kebab_case(clean_title)}.md"
        else:
            # Section has no number - determine based on position
            if index == 0:
                # First section without number
                filename = f"00-{self._to_kebab_case(title)}.md"
            else:
                # Find the last numbered section before this one
                last_number = 0
                for prev_section in all_sections[:index]:
                    prev_match = re.match(r"^(\d+)\.\s*(.+)$", prev_section.title)
                    if prev_match:
                        last_number = int(prev_match.group(1))

                if last_number == 0:
                    # No previous numbered sections, use sequential
                    filename = f"{index:02d}-{self._to_kebab_case(title)}.md"
                else:
                    # Use the last number + 1
                    filename = f"{last_number + 1:02d}-{self._to_kebab_case(title)}.md"

        return filename

    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case.

        Args:
            text: Text to convert

        Returns:
            Kebab-case version of the text
        """
        # Remove special characters and convert to lowercase
        text = re.sub(r"[^\w\s-]", "", text.lower())
        # Replace spaces and multiple hyphens with single hyphens
        text = re.sub(r"[\s-]+", "-", text)
        return text.strip("-")

    def extract_section_content(self, section: Section) -> Tuple[List[str], List[str]]:
        """Extract and process section content.

        Args:
            section: Section to extract content from

        Returns:
            Tuple of (processed_lines, toc_entries)
        """
        section_lines = self.content[section.start_line - 1 : section.end_line]

        # First pass: collect all headers that exist in this section
        # Filter out empty lines at the beginning and end
        processed_lines = []
        toc_entries = []

        processed_lines.append(f"# {section.title} <!-- omit in toc -->")
        processed_lines.append("")

        # Collect headers that actually exist in this section
        # Track if we've started processing content
        # Skip the original section title line (## ...)
        content_started = False

        for line in section_lines:
            line = line.rstrip("\n")

            # Skip empty lines at the beginning
            if line.startswith("## ") and not content_started:
                content_started = True
                continue

            if line.startswith("### "):
                # Only add to TOC if this header actually exists in this section
                header_text = line.replace("### ", "")
                new_header = f"## {header_text}"
                processed_lines.append(new_header)
                # Add to TOC
                anchor = self.create_toc_anchor(header_text)
                toc_entries.append(f"- [{header_text}](#{anchor})")

            elif line.startswith("#### "):
                # Only add to TOC if this header actually exists in this section
                header_text = line.replace("#### ", "")
                new_header = f"### {header_text}"
                processed_lines.append(new_header)
                # Add to TOC with indent
                anchor = self.create_toc_anchor(header_text)
                toc_entries.append(f"  - [{header_text}](#{anchor})")

            elif line.startswith("##### "):
                # Only add to TOC if this header actually exists in this section
                header_text = line.replace("##### ", "")
                new_header = f"#### {header_text}"
                processed_lines.append(new_header)
                # Add to TOC with more indent
                anchor = self.create_toc_anchor(header_text)
                toc_entries.append(f"    - [{header_text}](#{anchor})")

            elif line.startswith("###### "):
                # Only add to TOC if this header actually exists in this section
                header_text = line.replace("###### ", "")
                new_header = f"##### {header_text}"
                processed_lines.append(new_header)

            else:
                processed_lines.append(line)

        # Clean up empty lines at the end
        # Remove trailing empty lines
        while processed_lines and processed_lines[-1].strip() == "":
            processed_lines.pop()

        # Add one final empty line
        processed_lines.append("")

        # Only return TOC entries if there are actually headers in this section
        return processed_lines, toc_entries

    def create_main_toc(self, sections: List[Section]) -> List[str]:
        """Create the main TOC file content.

        Args:
            sections: List of sections to include in TOC

        Returns:
            List of lines for the TOC file
        """
        toc_lines = []
        toc_lines.append("# Table of Contents <!-- omit in toc -->")
        toc_lines.append("")

        for section in sections:
            # Main section link
            toc_lines.append(f"- [{section.title}]({section.filename})")

            # Add subsection links if any
            for subsection in section.subsections:
                indent = "  " * (subsection.level - 2)
                toc_lines.append(
                    f"{indent}- [{subsection.title}]({section.filename}#{subsection.anchor})"
                )

        return toc_lines

    def detect_broken_links(self, sections: List[Section]) -> List[str]:
        """Detect potential broken links in the content.

        Args:
            sections: List of sections to check

        Returns:
            List of broken link descriptions
        """
        broken_links = []
        section_anchors = {section.anchor: section.filename for section in sections}

        for section in sections:
            section_content = "\n".join(
                self.content[section.start_line - 1 : section.end_line]
            )

            # Find all markdown links
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            matches = re.findall(link_pattern, section_content)

            for link_text, link_url in matches:
                if link_url.startswith("#"):
                    # Internal link
                    anchor = link_url[1:]  # Remove #
                    if anchor not in section_anchors:
                        broken_links.append(
                            f"Broken internal link '{link_text}' -> '{link_url}' in {section.filename}"
                        )
                elif link_url.startswith("./") or link_url.endswith(".md"):
                    # File link
                    broken_links.append(
                        f"File link '{link_text}' -> '{link_url}' may need updating in {section.filename}"
                    )

        return broken_links

    def _generate_prompts_file(self) -> None:
        """Generate context-aware prompts based on the actual split results."""
        prompts = []

        # Analyze the split to determine what kind of prompts are needed
        has_broken_links = len(self.broken_links) > 0
        has_code_blocks = any(
            "```" in "\n".join(self.content[section.start_line - 1 : section.end_line])
            for section in self.sections
        )
        has_images = any(
            "!" in "\n".join(self.content[section.start_line - 1 : section.end_line])
            for section in self.sections
        )
        has_numbered_sections = any(
            re.match(r"^\d+\.", section.title) for section in self.sections
        )

        prompts.append("# Recommended Prompts for Post-Processing")
        prompts.append("")
        prompts.append(
            "This file contains ready-to-use prompts for LLMs to help with post-processing"
        )
        prompts.append(
            "the split markdown files. Copy and paste these prompts into your preferred LLM."
        )
        prompts.append("")
        prompts.append("**Split Summary:**")
        prompts.append(f"- Total sections: {len(self.sections)}")
        prompts.append(f"- Broken links detected: {len(self.broken_links)}")
        prompts.append(f"- Contains code blocks: {has_code_blocks}")
        prompts.append(f"- Contains images: {has_images}")
        prompts.append(f"- Numbered sections: {has_numbered_sections}")
        prompts.append("")

        # Always include the basic content review prompt
        prompts.append("## Content Review and Structure Validation")
        prompts.append("")
        prompts.append("```")
        prompts.append(
            "You are a technical documentation expert. Review the structure and content of these markdown files"
        )
        prompts.append("that were created by splitting a large document.")
        prompts.append("")
        prompts.append("**Context:**")
        prompts.append("- Each file represents a section from the original document")
        prompts.append(
            "- Headers were promoted by one level (## became #, ### became ##, etc.)"
        )
        prompts.append(
            "- Each file should be self-contained and make sense as a standalone document"
        )
        prompts.append("- Internal TOCs were generated automatically")
        prompts.append("")
        prompts.append("**Files to review:**")
        for section in self.sections:
            prompts.append(f"- {section.filename}: {section.title}")
        prompts.append("")
        prompts.append("**Review criteria:**")
        prompts.append(
            "1. **Content completeness**: Each file should contain all necessary information"
        )
        prompts.append("2. **Logical flow**: Content should follow a logical sequence")
        prompts.append(
            "3. **Header hierarchy**: Headers should be properly nested and meaningful"
        )
        prompts.append(
            "4. **TOC accuracy**: Internal TOCs should match the actual content structure"
        )
        prompts.append(
            "5. **Cross-references**: Any remaining internal links should be valid"
        )

        if has_code_blocks:
            prompts.append(
                "6. **Code blocks**: Ensure code examples are complete and properly formatted"
            )
        if has_images:
            prompts.append(
                "7. **Images and diagrams**: Verify that image references are correct"
            )

        prompts.append("8. **Consistency**: Check for consistent formatting and style")
        prompts.append("")
        prompts.append("**Common issues to look for:**")
        prompts.append("- Incomplete sections that reference content in other files")
        if has_images:
            prompts.append("- Broken image or file references")
        prompts.append("- Inconsistent header numbering or naming")
        prompts.append("- Missing context that was in the original document")
        prompts.append("- Duplicate content across files")
        prompts.append("")
        prompts.append("**Output format:**")
        prompts.append("- Provide a summary of findings")
        prompts.append("- List specific issues found in each file")
        prompts.append("- Suggest improvements for structure and content")
        prompts.append(
            "- Recommend any files that should be merged or split differently"
        )
        prompts.append("```")
        prompts.append("")

        # Include broken links prompt only if there are broken links
        if has_broken_links:
            prompts.append("## Fix Broken Links")
            prompts.append("")
            prompts.append("```")
            prompts.append(
                "You are a technical documentation expert. A large markdown file has been split into multiple files."
            )
            prompts.append(
                "Your task is to identify and fix broken links between sections."
            )
            prompts.append("")
            prompts.append("**Context:**")
            prompts.append("- The original file was split based on ## headers")
            prompts.append("- Each section became its own file with promoted headers")
            prompts.append(
                "- Internal links (#anchor) may now point to non-existent anchors"
            )
            prompts.append(
                "- File references may need updating to point to correct files"
            )
            prompts.append("")
            prompts.append("**Files to review:**")
            for section in self.sections:
                prompts.append(f"- {section.filename}")
            prompts.append("")
            prompts.append("**Broken links detected:**")
            for link in self.broken_links:
                prompts.append(f"- {link}")
            prompts.append("")
            prompts.append("**Tasks:**")
            prompts.append("1. Scan each file for markdown links: `[text](url)`")
            prompts.append("2. Identify broken internal links (starting with #)")
            prompts.append(
                "3. Find the correct target file and anchor for each broken link"
            )
            prompts.append(
                "4. Update file references to point to the correct split files"
            )
            prompts.append("5. Verify that all cross-references work correctly")
            prompts.append("")
            prompts.append("**Common patterns to fix:**")
            prompts.append(
                "- `[Section Name](#section-anchor)` → `[Section Name](filename.md#section-anchor)`"
            )
            prompts.append(
                "- `[Previous Section](#previous)` → `[Previous Section](previous-file.md#previous)`"
            )
            prompts.append(
                "- `[Next Section](#next)` → `[Next Section](next-file.md#next)`"
            )
            prompts.append("```")
            prompts.append("")

        # Add specialized prompts based on content analysis
        if has_code_blocks:
            prompts.append("## Code Block Validation")
            prompts.append("")
            prompts.append("```")
            prompts.append(
                "You are a technical documentation expert. Review the code blocks in these markdown files"
            )
            prompts.append(
                "to ensure they are complete, properly formatted, and functional."
            )
            prompts.append("")
            prompts.append("**Files to review:**")
            for section in self.sections:
                prompts.append(f"- {section.filename}")
            prompts.append("")
            prompts.append("**Tasks:**")
            prompts.append("1. Check that all code blocks are properly closed with ```")
            prompts.append("2. Verify that code examples are complete and runnable")
            prompts.append("3. Ensure proper syntax highlighting is specified")
            prompts.append(
                "4. Check that code references (imports, functions) are valid"
            )
            prompts.append(
                "5. Verify that code examples match the surrounding documentation"
            )
            prompts.append("```")
            prompts.append("")

        if has_images:
            prompts.append("## Image and Media Validation")
            prompts.append("")
            prompts.append("```")
            prompts.append(
                "You are a technical documentation expert. Review the images and media references"
            )
            prompts.append(
                "in these markdown files to ensure they are properly linked and accessible."
            )
            prompts.append("")
            prompts.append("**Files to review:**")
            for section in self.sections:
                prompts.append(f"- {section.filename}")
            prompts.append("")
            prompts.append("**Tasks:**")
            prompts.append(
                "1. Check that all image references use proper markdown syntax: `![alt](path)`"
            )
            prompts.append(
                "2. Verify that image paths are correct relative to the file location"
            )
            prompts.append("3. Ensure alt text is descriptive and meaningful")
            prompts.append("4. Check that diagrams and charts are properly referenced")
            prompts.append(
                "5. Verify that any embedded media (videos, etc.) is accessible"
            )
            prompts.append("```")
            prompts.append("")

        # Write prompts to file
        prompts_file = self.output_dir / "recommended_prompts.txt"
        with open(prompts_file, "w", encoding="utf-8") as f:
            f.write("\n".join(prompts))

        print(f"Created: {prompts_file}")
        print(
            "💡 Tip: Use the context-aware prompts in 'recommended_prompts.txt' with your preferred LLM for post-processing"
        )

    def split_file(self) -> None:
        """Main method to split the file."""
        if self.debug:
            print("🔍 DEBUG: Starting split process")
            print(f"🔍 DEBUG: Source file: {self.source_file}")
            print(f"🔍 DEBUG: Output directory: {self.output_dir}")

        print(f"Splitting: {self.source_file}")
        print(f"Output directory: {self.output_dir}")

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Always use analyze_sections() - it works correctly
        print("📋 Analyzing file structure based on ## headers")
        self.sections = self.analyze_sections()

        if not self.sections:
            print("No sections found! Make sure the file has ## headers.")
            return

        print(f"Found {len(self.sections)} sections")

        # Determine filenames
        for i, section in enumerate(self.sections):
            section.filename = self.determine_filename(section, i, self.sections)
            print(f"  {section.filename}: {section.title}")

        # Create main TOC file
        toc_content = self.create_main_toc(self.sections)
        toc_file = self.output_dir / "00-toc.md"
        with open(toc_file, "w", encoding="utf-8") as f:
            f.write("\n".join(toc_content))
        print(f"Created: {toc_file}")

        # Process each section
        for section in self.sections:
            if self.debug:
                print(f"🔍 DEBUG: Processing section: {section.title}")
                print(f"🔍 DEBUG: Lines {section.start_line}-{section.end_line}")

            processed_lines, toc_entries = self.extract_section_content(section)

            # Insert TOC after title if there are TOC entries
            if toc_entries:
                final_lines = processed_lines[:2]  # Title and empty line
                final_lines.append("## Table of Contents <!-- omit in toc -->")
                final_lines.append("")  # Add blank line after TOC header
                final_lines.extend(toc_entries)
                # Add the rest of the content, but skip the first two lines (title and empty line)
                # and the last line (empty line) since we already added one
                if len(processed_lines) > 3:
                    final_lines.extend(processed_lines[2:-1])
            else:
                final_lines = processed_lines

            # Write the output
            output_file = self.output_dir / section.filename
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(final_lines))

            print(f"Created: {output_file}")

        # Detect broken links
        self.broken_links = self.detect_broken_links(self.sections)

        # Validate quality
        print("✅ Running quality validation...")
        quality_issues = self.validate_split_quality()
        if quality_issues:
            print("⚠️  Quality issues found:")
            for issue in quality_issues:
                print(f"  {issue}")
        else:
            print("✅ All quality checks passed!")

        # Generate context-aware prompts
        self._generate_prompts_file()

        print(f"\nAll {len(self.sections)} sections processed successfully!")

    def validate_split_quality(self) -> List[str]:
        """Run quality checks on the split result.

        Returns:
            List of quality issues found
        """
        issues = []

        # Check each generated file
        for section in self.sections:
            file_path = self.output_dir / section.filename

            if not file_path.exists():
                issues.append(f"❌ File {section.filename} was not created")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_issues = self._validate_file_quality(section, content)
                issues.extend(file_issues)

        # Check TOC file
        toc_issues = self._validate_toc_quality()
        issues.extend(toc_issues)

        # Check overall structure
        structure_issues = self._validate_structure_quality()
        issues.extend(structure_issues)

        return issues

    def _validate_file_quality(self, section: Section, content: str) -> List[str]:
        """Validate quality of a single file.

        Args:
            section: Section being validated
            content: File content to validate

        Returns:
            List of quality issues found
        """
        issues = []
        lines = content.split("\n")

        # Check for omit comment in title
        if not content.startswith(f"# {section.title} <!-- omit in toc -->"):
            issues.append(f"⚠️  {section.filename}: Missing omit comment in title")

        # Check for TOC section
        if "## Table of Contents" not in content:
            # Only warn if the file has subsections (## headers)
            has_subsections = any(
                line.startswith("## ") and not line.startswith("## Table of Contents")
                for line in lines
            )
            if has_subsections:
                issues.append(
                    f"⚠️  {section.filename}: Missing Table of Contents section"
                )
            # If no subsections, it's normal to not have a TOC

        # Check header hierarchy
        header_issues = self._validate_header_hierarchy(content)
        for issue in header_issues:
            issues.append(f"⚠️  {section.filename}: {issue}")

        # Check for broken internal links
        broken_links = self._find_broken_internal_links(content, section)
        for link in broken_links:
            issues.append(f"❌ {section.filename}: Broken internal link: {link}")

        # Check for empty sections
        if len(content.strip()) < 100:  # Arbitrary minimum
            issues.append(f"⚠️  {section.filename}: Content seems too short")

        return issues

    def _validate_header_hierarchy(self, content: str) -> List[str]:
        """Validate that headers follow proper hierarchy.

        Args:
            content: Content to validate

        Returns:
            List of header hierarchy issues
        """
        issues = []
        debug_info = []
        lines = content.split("\n")
        current_level = None
        in_code_block = False

        for line in lines:
            # Check if we're entering or leaving a code block
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if self.debug:
                    debug_info.append(
                        f"Code block {'started' if in_code_block else 'ended'}: {line.strip()}"
                    )
                continue

            # Skip lines inside code blocks
            if in_code_block:
                if self.debug:
                    debug_info.append(f"Code line (ignored): {line.strip()}")
                continue

            if re.match(r"^#{1,6}\s+", line):
                level = len(line) - len(line.lstrip("#"))

                if self.debug:
                    debug_info.append(f"Header: {line.strip()} (level {level})")

                if current_level is None:
                    current_level = level
                    if self.debug:
                        debug_info.append(
                            f"  → First header, setting current_level = {level}"
                        )
                else:
                    # Only report jumps if the previous level was a real header
                    if level > current_level + 1:
                        jump_info = f"Header level jump: {current_level} → {level}"
                        issues.append(jump_info)
                        if self.debug:
                            debug_info.append(f"  → WARNING: {jump_info}")
                    else:
                        if self.debug:
                            debug_info.append(
                                f"  → Valid jump: {current_level} → {level}"
                            )
                    current_level = level
            # If line doesn't start with #, keep current_level unchanged
            elif line.strip().startswith("**") and line.strip().endswith("**"):
                if self.debug:
                    debug_info.append(f"Bold text (ignored): {line.strip()}")

        # Only show debug info if there are issues and debug is enabled
        if issues and self.debug:
            print("🔍 Header hierarchy debug info:")
            for info in debug_info:
                print(f"    {info}")

        return issues

    def _find_broken_internal_links(self, content: str, _section: Section) -> List[str]:
        """Find broken internal links in content.

        Args:
            content: Content to check for broken links
            _section: Section being checked (unused but kept for interface consistency)

        Returns:
            List of broken link descriptions
        """
        broken_links = []

        # Extract all anchors from this file
        anchors = self._extract_anchors_from_content(content)

        # Find all internal links
        link_pattern = r"\[([^\]]+)\]\(#([^)]+)\)"
        matches = re.findall(link_pattern, content)

        for link_text, anchor in matches:
            if anchor not in anchors:
                broken_links.append(f"[{link_text}](#{anchor})")

        return broken_links

    def _extract_anchors_from_content(self, content: str) -> List[str]:
        """Extract all potential anchors from content.

        Args:
            content: Content to extract anchors from

        Returns:
            List of anchor strings
        """
        anchors = []

        # Find all headers and create anchors
        header_pattern = r"^(#{1,6})\s+(.+)$"
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            header_text = match.group(2)
            anchor = self.create_toc_anchor(header_text)
            anchors.append(anchor)

        return anchors

    def _validate_toc_quality(self) -> List[str]:
        """Validate the main TOC file.

        Returns:
            List of TOC quality issues
        """
        issues = []
        toc_file = self.output_dir / "00-toc.md"

        if not toc_file.exists():
            issues.append("❌ Main TOC file (00-toc.md) was not created")
            return issues

        with open(toc_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for omit comment
        if "<!-- omit in toc -->" not in content:
            issues.append("⚠️  Main TOC: Missing omit comment")

        # Check that all sections are linked
        for section in self.sections:
            if section.filename not in content:
                issues.append(f"❌ Main TOC: Missing link to {section.filename}")

        return issues

    def _validate_structure_quality(self) -> List[str]:
        """Validate overall structure quality.

        Returns:
            List of structure quality issues
        """
        issues = []

        # Check for consistent numbering
        numbered_sections = [s for s in self.sections if re.match(r"^\d+\.", s.title)]
        if numbered_sections:
            numbers = [
                int(re.match(r"^(\d+)\.", s.title).group(1)) for s in numbered_sections
            ]
            expected_numbers = list(range(1, len(numbers) + 1))
            if numbers != expected_numbers:
                issues.append(f"⚠️  Inconsistent section numbering: {numbers}")

        # Check for duplicate filenames
        filenames = [s.filename for s in self.sections]
        duplicates = [f for f in set(filenames) if filenames.count(f) > 1]
        if duplicates:
            issues.append(f"❌ Duplicate filenames: {duplicates}")

        # Check for reasonable file sizes
        for section in self.sections:
            file_path = self.output_dir / section.filename
            if file_path.exists():
                size = file_path.stat().st_size
                if size < 100:  # Very small files might be incomplete
                    issues.append(
                        f"⚠️  {section.filename}: Very small file ({size} bytes)"
                    )

        return issues


def main() -> None:
    """Main function to handle command line arguments and execute the splitter."""
    parser = argparse.ArgumentParser(
        description="Split large markdown files into sections"
    )
    parser.add_argument("source_file", help="Source markdown file to split")
    parser.add_argument(
        "--output-dir", help="Output directory (default: same as source file)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating files",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed output",
    )

    args = parser.parse_args()

    splitter = MarkdownSplitter(args.source_file, args.output_dir, args.debug)

    if args.dry_run:
        # Show what would be created
        sections = splitter.analyze_sections()
        print(f"Would create {len(sections)} files:")
        for i, section in enumerate(sections):
            filename = splitter.determine_filename(section, i, sections)
            print(f"  {filename}: {section.title}")
    else:
        splitter.split_file()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test Runner for Markdown Section Splitter

This script runs the markdown splitter on the sample complex document
and generates visible output for testing and demonstration purposes.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path so we can import the splitter
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_section_splitter import MarkdownSplitter


def run_splitter_test():
    """Run the splitter on the sample document and show results."""
    
    # Paths
    test_dir = Path(__file__).parent
    sample_file = test_dir / "sample_complex_document.md"
    output_dir = test_dir / "test_output"
    
    # Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    print("🚀 MARKDOWN SECTION SPLITTER - TEST RUN")
    print("=" * 50)
    print(f"📄 Input file: {sample_file}")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Initialize splitter
    splitter = MarkdownSplitter(str(sample_file), str(output_dir), debug=True)
    
    # Run the splitting
    print("🔄 Starting split process...")
    print("-" * 30)
    
    splitter.split_file()
    
    print()
    print("✅ SPLIT COMPLETE!")
    print("=" * 50)
    
    # Show generated files
    print("📂 Generated Files:")
    print("-" * 20)
    
    generated_files = sorted(output_dir.glob("*"))
    for i, file_path in enumerate(generated_files, 1):
        size = file_path.stat().st_size
        print(f"{i:2d}. {file_path.name:<35} ({size:,} bytes)")
    
    print()
    
    # Show sections analysis
    print("📋 Sections Analysis:")
    print("-" * 25)
    
    sections = splitter.sections
    for i, section in enumerate(sections, 1):
        print(f"{i:2d}. {section.filename:<35} → '{section.title}'")
    
    print()
    
    # Show broken links if any
    if splitter.broken_links:
        print("🔗 Broken Links Found:")
        print("-" * 23)
        for link in splitter.broken_links:
            print(f"   ⚠️  {link}")
        print()
    
    # Show quality issues
    print("🔍 Quality Validation:")
    print("-" * 22)
    
    quality_issues = splitter.validate_split_quality()
    if quality_issues:
        for issue in quality_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No quality issues found!")
    
    print()
    
    # Show file contents preview
    print("👁️  File Contents Preview:")
    print("-" * 27)
    
    # Show TOC
    toc_file = output_dir / "00-toc.md"
    if toc_file.exists():
        print(f"\n📑 {toc_file.name}:")
        print("   " + "─" * 40)
        with open(toc_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:15]  # First 15 lines
            for line in lines:
                print(f"   {line.rstrip()}")
            if len(f.readlines()) > 15:
                print(f"   ... ({len(lines)} more lines)")
    
    # Show first few section files
    section_files = sorted([f for f in generated_files if f.name.endswith('.md') and f.name != '00-toc.md'])[:3]
    
    for section_file in section_files:
        print(f"\n📄 {section_file.name}:")
        print("   " + "─" * 40)
        with open(section_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]  # First 10 lines
            for line in lines:
                print(f"   {line.rstrip()}")
            if len(f.readlines()) > 10:
                print(f"   ... (more content)")
    
    # Show anchor examples
    print(f"\n🔗 Anchor Generation Examples:")
    print("   " + "─" * 30)
    
    anchor_examples = [
        "Configuración Inicial 📋",
        "русский раздел (Sección en Ruso)", 
        "中文部分 (Sección China)",
        "Performance & Optimización ⚡🔧",
        "Header with **bold** and *italic* text",
        "$$ Costos y Pricing €€"
    ]
    
    for example in anchor_examples:
        anchor = splitter.create_toc_anchor(example)
        print(f"   '{example}' → '{anchor}'")
    
    print()
    print("🎯 TEST SUMMARY:")
    print("-" * 15)
    print(f"   • Total sections created: {len(sections)}")
    print(f"   • Total files generated: {len(generated_files)}")
    print(f"   • Broken links found: {len(splitter.broken_links)}")
    print(f"   • Quality issues: {len(quality_issues)}")
    
    # Test specific edge cases
    print()
    print("🧪 Edge Cases Detected:")
    print("-" * 23)
    
    edge_cases = []
    
    # Check for numbered sections with gaps
    numbered_sections = [s for s in sections if any(c.isdigit() for c in s.title.split('.')[0])]
    if numbered_sections:
        edge_cases.append(f"   📊 Numbered sections with gaps: {len(numbered_sections)}")
    
    # Check for non-ASCII characters
    non_ascii_sections = [s for s in sections if not s.title.isascii()]
    if non_ascii_sections:
        edge_cases.append(f"   🌍 Non-ASCII sections: {len(non_ascii_sections)}")
    
    # Check for emojis
    emoji_sections = [s for s in sections if any(ord(c) > 127 and ord(c) < 0x1F000 or ord(c) > 0x1F999 for c in s.title)]
    if emoji_sections:
        edge_cases.append(f"   😀 Sections with emojis: {len(emoji_sections)}")
    
    # Check for special characters
    special_char_sections = [s for s in sections if any(c in s.title for c in '&$€%*[]()<>')]
    if special_char_sections:
        edge_cases.append(f"   ⚡ Sections with special chars: {len(special_char_sections)}")
    
    if edge_cases:
        for case in edge_cases:
            print(case)
    else:
        print("   ✅ No specific edge cases detected")
    
    print()
    print("🔚 Test completed! Check the output directory for all generated files.")
    print(f"📁 Output location: {output_dir.absolute()}")
    

def show_file_tree():
    """Show the file tree of generated output."""
    output_dir = Path(__file__).parent / "test_output"
    
    if not output_dir.exists():
        print("❌ Output directory not found. Run the test first.")
        return
    
    print("\n🌳 Generated File Tree:")
    print("-" * 25)
    
    def print_tree(directory, prefix=""):
        items = sorted(directory.iterdir())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix)
    
    print_tree(output_dir)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--tree":
        show_file_tree()
    else:
        run_splitter_test()
        print("\n💡 Tip: Run 'python run_test_example.py --tree' to see just the file tree")
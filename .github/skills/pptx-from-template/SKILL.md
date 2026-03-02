---
name: pptx-from-template
description: "Creates a new PowerPoint (.pptx) presentation based on an existing template PPTX, reusing its slide layouts, styles, fonts, colors, and backgrounds. Use this skill when the user asks to generate slides, create a new presentation from an existing one, or produce a PPTX with consistent branding from a template."
argument-hint: "[template.pptx] [content description or plan]"
---

# Create PPTX from Template

This skill creates a new PowerPoint presentation that inherits all styles, slide layouts, backgrounds, fonts, and color schemes from an existing PPTX template. It uses the `python-pptx` package.

## When to use

- User asks to create a new PPTX based on an existing presentation's style
- User wants to generate slides with consistent branding from a template
- User asks to produce a presentation using a previous session's look and feel
- User has ASCII/markdown slide content and wants it turned into a styled PPTX

## Prerequisites

`python-pptx` is declared as an inline script dependency, so no manual install is needed when using `uv run`.

## Helper module

This skill includes a reusable Python module at `.github/skills/pptx-from-template/pptx_from_template.py`.

To inspect a template directly:
```bash
uv run .github/skills/pptx-from-template/pptx_from_template.py template.pptx
```

Available functions:

| Function | Purpose |
|---|---|
| `inspect_template(path)` | Returns a dict with dimensions, layouts, placeholders, and existing slides |
| `print_template_info(path)` | Prints a human-readable summary of the template |
| `create_pptx_from_template(template, output, slides)` | Creates a new PPTX from a template with a list of slide content dicts |
| `set_body_bullets(placeholder, lines)` | Sets placeholder text as bullet points |
| `add_code_block(slide, code, ...)` | Adds a monospace code block with dark background |
| `copy_slide_background(source, target)` | Copies background XML from one slide to another |

## How it works

The approach uses the template PPTX as the base file, which preserves:
- **Slide master & layouts**: All layouts (title, content, section header, blank, etc.) with their formatting
- **Theme**: Colors, fonts, effects
- **Slide backgrounds**: Solid fills, gradient fills, and background images
- **Placeholder styles**: Font sizes, positions, bullet styles

### Step 1: Inspect the template

Before generating slides, inspect the template to discover available slide layouts and their placeholders. Run this Python snippet to list them:

```python
from pptx import Presentation

template = Presentation("template.pptx")

print(f"Slide dimensions: {template.slide_width} x {template.slide_height} EMUs")
print(f"  ({template.slide_width / 914400:.1f}\" x {template.slide_height / 914400:.1f}\")\n")

for i, layout in enumerate(template.slide_layouts):
    print(f"Layout [{i}]: '{layout.name}'")
    for ph in layout.placeholders:
        print(f"  Placeholder idx={ph.placeholder_format.idx}, "
              f"name='{ph.name}', "
              f"type={ph.placeholder_format.type}, "
              f"size=({ph.left}, {ph.top}, {ph.width}, {ph.height})")
    print()
```

Also inspect existing slides to see which layouts are used and how content is structured:

```python
for i, slide in enumerate(template.slides):
    layout_name = slide.slide_layout.name
    print(f"Slide {i+1}: layout='{layout_name}'")
    for shape in slide.shapes:
        if shape.has_text_frame:
            text = shape.text_frame.text[:80]
            print(f"  Shape '{shape.name}': \"{text}\"")
        elif shape.shape_type == 13:  # Picture
            print(f"  Picture '{shape.name}': {shape.width}x{shape.height}")
    print()
```

### Step 2: Generate the new presentation

Use the template as the starting point. Delete existing slides (keeping the slide master/layouts), then add new slides using the discovered layouts.

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from lxml import etree
import copy

def create_pptx_from_template(template_path, output_path, slides_content):
    """Create a new PPTX from a template, preserving all styles.

    Args:
        template_path: Path to the template .pptx file
        output_path: Path for the output .pptx file
        slides_content: List of dicts, each with:
            - layout_index (int): Index of the slide layout to use
            - title (str, optional): Title text
            - body (str, optional): Body/content text
            - notes (str, optional): Speaker notes
    """
    prs = Presentation(template_path)

    # Delete all existing slides (keep layouts/masters)
    while len(prs.slides) > 0:
        rId = prs.slides._sldIdLst[0].get('r:id')
        prs.part.drop_rel(rId)
        prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])

    # Add new slides from content
    for slide_data in slides_content:
        layout_idx = slide_data.get("layout_index", 1)
        layout = prs.slide_layouts[layout_idx]
        slide = prs.slides.add_slide(layout)

        # Set title if present and placeholder exists
        title_text = slide_data.get("title")
        if title_text and slide.shapes.title:
            slide.shapes.title.text = title_text

        # Set body content if present
        body_text = slide_data.get("body")
        if body_text:
            for ph in slide.placeholders:
                if ph.placeholder_format.idx == 1:  # Content placeholder
                    ph.text = body_text
                    break

        # Add speaker notes if present
        notes_text = slide_data.get("notes")
        if notes_text:
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = notes_text

    prs.save(output_path)
    print(f"Created {output_path} with {len(slides_content)} slides")
```

### Step 3: Advanced — Preserve a background from a template slide

If the template has slides with custom backgrounds (images, gradients) that you want to reuse on new slides, copy the background XML from the template slide:

```python
from lxml import etree
import copy

def copy_slide_background(source_slide, target_slide):
    """Copy background properties from a source slide to a target slide."""
    source_bg = source_slide._element.find(
        '{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}bg',
    )
    if source_bg is None:
        # Try the presentation ML namespace
        source_bg = source_slide._element.find(
            '{http://schemas.openxmlformats.org/presentationml/2006/main}bg',
        )
    if source_bg is not None:
        # Remove existing background on target
        nsmap = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
        existing_bg = target_slide._element.find('p:bg', nsmap)
        if existing_bg is not None:
            target_slide._element.remove(existing_bg)
        # Insert copy of source background
        new_bg = copy.deepcopy(source_bg)
        # Background should be the first child after cSld opening
        target_slide._element.insert(0, new_bg)
```

### Step 4: Advanced — Multi-line body with bullet formatting

To add bullet points that inherit the template's bullet styling:

```python
from pptx.util import Pt

def set_body_bullets(placeholder, lines):
    """Set body text as bullet points, one per line.

    Clears existing text and adds each line as a separate paragraph,
    inheriting the placeholder's default paragraph formatting.
    """
    tf = placeholder.text_frame
    tf.clear()

    for i, line in enumerate(lines):
        if i == 0:
            para = tf.paragraphs[0]
        else:
            para = tf.add_paragraph()
        para.text = line
        # Inherit level from template; set level 0 for top-level bullets
        para.level = 0
```

### Step 5: Advanced — Add code blocks

For technical presentations, add code blocks as a text box with monospace font:

```python
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor

def add_code_block(slide, code_text, left=Inches(0.5), top=Inches(2),
                   width=Inches(9), height=Inches(4.5),
                   font_size=Pt(11), font_name="Consolas"):
    """Add a code block as a text box with monospace font and dark background."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    # Set background fill on the shape
    fill = txBox.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0x1E, 0x1E, 0x1E)  # Dark background

    para = tf.paragraphs[0]
    para.text = code_text
    run = para.runs[0]
    run.font.name = font_name
    run.font.size = font_size
    run.font.color.rgb = RGBColor(0xD4, 0xD4, 0xD4)  # Light text
```

## Typical workflow

1. User provides a template PPTX and slide content (ASCII plan, markdown, or structured data)
2. **Inspect** the template to discover layouts and placeholders
3. **Map** each piece of content to the appropriate layout
4. **Generate** the PPTX using the template as the base
5. **Review** the output and adjust as needed

## Layout mapping guide

Common layout conventions (indices vary per template — always inspect first):

| Layout name | Typical use | Key placeholders |
|---|---|---|
| Title Slide | First/last slide, section dividers | title (0), subtitle (1) |
| Title and Content | Most content slides | title (0), body (1) |
| Section Header | Topic transitions | title (0), subtitle (1) |
| Two Content | Side-by-side comparisons | title (0), left (1), right (2) |
| Blank | Diagrams, full-bleed images | none |
| Title Only | Slides with custom content below title | title (0) |

## Important notes

- Always inspect the template first — layout indices and placeholder indices vary between templates
- The template's slide master determines all default formatting; you rarely need to set fonts/colors explicitly
- If a template slide has images or shapes you want to preserve, keep that slide and modify its text rather than deleting and recreating
- Background images tied to the slide master (not individual slides) are automatically inherited by all new slides
- For complex slides (diagrams, tables, charts), consider keeping the template slide and modifying specific shapes by name

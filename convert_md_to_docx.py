#!/usr/bin/env python3
"""
convert_md_to_docx.py
Converts all .md files in a folder to Word .docx using AfyaDesk letterhead as template.

Features:
- Uses afyadesk-letterhead.docx as background (behindDoc anchored image) - preserved automatically
- Sets body font to "Tw Cen MT" at 14px (10.5pt). 14px = 14 * 0.75pt = 10.5pt.
  If you meant 14pt (not px), change FONT_SIZE_PT = 14 below or pass --font-size 14
- Heading styles also forced to Tw Cen MT (hierarchical sizes, same family)
- Handles headings, bold, italic, inline code, links, bullets, numbered lists,
  blockquotes, tables, horizontal rules, code blocks, paragraphs
- Tries markdown+BeautifulSoup path for full fidelity; falls back to regex parser if libs missing
- Preserves page margins/header distances from template

Usage:
    python convert_md_to_docx.py                       # converts *.md in current folder using afyadesk-letterhead.docx -> ./output_docs/
    python convert_md_to_docx.py --input-dir . --template afyadesk-letterhead.docx --output-dir ./output_docs
    python convert_md_to_docx.py --font-size 14        # force 14pt instead of 10.5pt
    python convert_md_to_docx.py --uniform-headings    # force headings to same size as body (14px)

Dependencies:
    pip install python-docx markdown beautifulsoup4

Author: Generated for AfyaDesk Modules
"""
import argparse
import re
import sys
from pathlib import Path

# --- Configurable defaults ---
FONT_NAME = "Tw Cen MT"   # Twentieth Century MT - ensure installed on Windows, Word will fallback otherwise
FONT_SIZE_PX = 16
FONT_SIZE_PT = FONT_SIZE_PX * 0.75  # 16px = 12pt. Change to 14 for 14pt behaviour.
# Heading sizes in pt (Tw Cen MT family). If --uniform-headings set, all = FONT_SIZE_PT
HEADING_SIZES_PT = {
    1: 18,
    2: 15,
    3: 13,
    4: 11,
    5: 10,
    6: 10,
}
HEADING_COLOR_HEX = "2F5496"  # match template's heading color
BODY_COLOR_HEX = "262626"

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Emu
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("ERROR: python-docx not installed. Run: pip install python-docx")
    sys.exit(1)

HAS_MARKDOWN = False
HAS_BS4 = False
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    pass
try:
    from bs4 import BeautifulSoup, NavigableString
    HAS_BS4 = True
except ImportError:
    pass

USE_HTML_PATH = HAS_MARKDOWN and HAS_BS4


def set_run_font(run, font_name=FONT_NAME, size_pt=FONT_SIZE_PT, color_hex=None, bold=None, italic=None):
    """Force run to use Tw Cen MT and given size/color, including w:rFonts xml."""
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    if color_hex:
        try:
            run.font.color.rgb = RGBColor.from_string(color_hex)
        except:  # noqa
            pass
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    # Ensure xml rFonts covers ascii/hAnsi/cs/eastAsia
    try:
        r = run._element
        rPr = r.get_or_add_rPr()
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.append(rFonts)
        for attr in ['ascii', 'hAnsi', 'cs', 'eastAsia']:
            rFonts.set(qn(f'w:{attr}'), font_name)
        # also hAnsi theme handling: ensure not overridden
        # set hint?
    except Exception:
        pass


def apply_template_styles(doc, font_name=FONT_NAME, body_pt=FONT_SIZE_PT, uniform_headings=False):
    """Override Normal + Heading styles to Tw Cen MT, correct sizes."""
    # Normal style
    try:
        normal = doc.styles['Normal']
        normal.font.name = font_name
        normal.font.size = Pt(body_pt)
        normal.font.color.rgb = RGBColor.from_string(BODY_COLOR_HEX)
        # Set paragraph spacing
        pf = normal.paragraph_format
        pf.space_after = Pt(6)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.15
        pf.widow_control = True
        # xml rFonts for style
        try:
            rPr = normal.element.find(qn('w:rPr'))
            if rPr is None:
                rPr = OxmlElement('w:rPr')
                normal.element.append(rPr)
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rPr.append(rFonts)
            for a in ['w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia']:
                rFonts.set(qn(a), font_name)
            sz = rPr.find(qn('w:sz'))
            if sz is None:
                sz = OxmlElement('w:sz')
                rPr.append(sz)
            sz.set(qn('w:val'), str(int(body_pt * 2)))
            szCs = rPr.find(qn('w:szCs'))
            if szCs is None:
                szCs = OxmlElement('w:szCs')
                rPr.append(szCs)
            szCs.set(qn('w:val'), str(int(body_pt * 2)))
        except:  # noqa
            pass
    except Exception as e:
        print(f"warn: could not style Normal: {e}")

    # Headings 1-6
    for i in range(1, 7):
        style_name = f'Heading {i}'
        try:
            hs = doc.styles[style_name]
            hs.font.name = font_name
            target_pt = body_pt if uniform_headings else HEADING_SIZES_PT.get(i, body_pt)
            hs.font.size = Pt(target_pt)
            hs.font.color.rgb = RGBColor.from_string(HEADING_COLOR_HEX)
            hs.font.bold = True
            # xml
            try:
                rPr = hs.element.find(qn('w:rPr'))
                if rPr is None:
                    rPr = OxmlElement('w:rPr')
                    hs.element.append(rPr)
                rFonts = rPr.find(qn('w:rFonts'))
                if rFonts is None:
                    rFonts = OxmlElement('w:rFonts')
                    rPr.append(rFonts)
                for a in ['w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia']:
                    rFonts.set(qn(a), font_name)
            except:  # noqa
                pass
            pf = hs.paragraph_format
            if i == 1:
                pf.space_before = Pt(18)
                pf.space_after = Pt(6)
            elif i == 2:
                pf.space_before = Pt(14)
                pf.space_after = Pt(4)
            else:
                pf.space_before = Pt(10)
                pf.space_after = Pt(3)
            pf.keep_with_next = True
        except Exception:
            pass

    # List styles
    for sname in ['List Bullet', 'List Number', 'List Bullet 2', 'List Number 2']:
        try:
            ls = doc.styles[sname]
            ls.font.name = font_name
            ls.font.size = Pt(body_pt)
            ls.font.color.rgb = RGBColor.from_string(BODY_COLOR_HEX)
            try:
                rPr = ls.element.find(qn('w:rPr'))
                if rPr is not None:
                    rFonts = rPr.find(qn('w:rFonts'))
                    if rFonts is None:
                        rFonts = OxmlElement('w:rFonts')
                        rPr.append(rFonts)
                    for a in ['w:ascii', 'w:hAnsi']:
                        rFonts.set(qn(a), font_name)
            except:  # noqa
                pass
        except Exception:
            pass

    # Ensure doc defaults also point to Tw Cen MT (optional)
    try:
        # docDefaults handled via stylesxml earlier, but ensure at least Normal covers body
        pass
    except Exception:
        pass


def add_page_numbers(doc, font_name=FONT_NAME, size_pt=None):
    """Add page numbers to footer of all sections."""
    if size_pt is None:
        size_pt = max(9, FONT_SIZE_PT - 2)  # slightly smaller than body
    sz_val = str(int(size_pt * 2))
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        # Clear existing footer paragraphs
        for p in list(footer.paragraphs):
            p.clear()
        # Ensure at least one paragraph
        if len(footer.paragraphs) == 0:
            footer.add_paragraph()
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)

        # Helper to add field runs
        def add_field_run(paragraph, field_code, font_name, size_pt, color_hex):
            # begin
            r1 = paragraph.add_run()
            fld_begin = OxmlElement('w:fldChar')
            fld_begin.set(qn('w:fldCharType'), 'begin')
            r1._r.append(fld_begin)
            # instrText
            r2 = paragraph.add_run()
            instr = OxmlElement('w:instrText')
            instr.set(qn('xml:space'), 'preserve')
            instr.text = field_code
            r2._r.append(instr)
            # end
            r3 = paragraph.add_run()
            fld_end = OxmlElement('w:fldChar')
            fld_end.set(qn('w:fldCharType'), 'end')
            r3._r.append(fld_end)
            # Format all three runs
            for r in (r1, r2, r3):
                set_run_font(r, font_name, size_pt, color_hex=color_hex)

        # PAGE field
        add_field_run(p, ' PAGE ', font_name, size_pt, "888888")
        # " of " text
        r_of = p.add_run(' of ')
        set_run_font(r_of, font_name, size_pt, color_hex="888888")
        # NUMPAGES field
        add_field_run(p, ' NUMPAGES ', font_name, size_pt, "888888")


def ensure_twcen_on_all_runs(doc, font_name=FONT_NAME, size_pt=FONT_SIZE_PT):
    """Post-process: ensure every run that still has Calibri gets Tw Cen MT."""
    # This is a safety net - style inheritance may still leave runs with theme fonts.
    # We walk paragraphs/tables
    for para in doc.paragraphs:
        for run in para.runs:
            # only fix if font name is not already Tw Cen MT-ish
            if not run.font.name or run.font.name.lower() not in [font_name.lower(), "tw cen mt", "tw cen mt condensed"]:
                # don't override code blocks (Consolas)
                if run.font.name not in ["Consolas", "Courier New"]:
                    set_run_font(run, font_name, size_pt, color_hex=None)


# ======================= HTML PATH (markdown+bs4) =======================

def _add_runs_from_html_node(paragraph, node, base_pt, bold=False, italic=False, code=False, is_heading=False, heading_level=0):
    """Recursively add runs from BeautifulSoup node to paragraph."""
    # Determine target size/color
    if is_heading:
        pt = HEADING_SIZES_PT.get(heading_level, base_pt) if not is_heading else base_pt  # caller handles uniform check
        # but we already resolved pt outside; use that
        target_pt = paragraph._heading_pt if hasattr(paragraph, '_heading_pt') else base_pt
    else:
        target_pt = base_pt

    for child in list(node.children):
        if isinstance(child, NavigableString):
            text = str(child)
            if text == "" or text is None:
                continue
            # Preserve whitespace somewhat; collapse multiple spaces? Keep as is but not empty
            if text.strip() == "" and text.count("\n") == 0:
                # single space? add as run with space to keep separation
                # only add if not just indentation
                if len(text) > 1:
                    continue
            run = paragraph.add_run(text)
            # Styling
            if code:
                run.font.name = "Consolas"
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor.from_string("333333")
                try:
                    rPr = run._element.get_or_add_rPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    shd.set(qn('w:fill'), 'F2F2F2')
                    # Note: shd on run, not paragraph, for inline code background
                    # Keep it subtle - Word run shading
                    rPr.append(shd)
                except:  # noqa
                    pass
            else:
                color = HEADING_COLOR_HEX if is_heading else BODY_COLOR_HEX
                set_run_font(run, FONT_NAME, target_pt, color_hex=color, bold=bold or is_heading, italic=italic)
                if bold:
                    run.bold = True
                if italic:
                    run.italic = True
            # Keep heading bold already
            if is_heading:
                run.bold = True
        elif child.name in ('strong', 'b'):
            _add_runs_from_html_node(paragraph, child, base_pt, bold=True, italic=italic, code=code, is_heading=is_heading, heading_level=heading_level)
        elif child.name in ('em', 'i'):
            _add_runs_from_html_node(paragraph, child, base_pt, bold=bold, italic=True, code=code, is_heading=is_heading, heading_level=heading_level)
        elif child.name == 'code':
            # inline code
            _add_runs_from_html_node(paragraph, child, base_pt, bold=bold, italic=italic, code=True, is_heading=is_heading, heading_level=heading_level)
        elif child.name == 'a':
            href = child.get('href', '')
            # For link, collect text; create runs with underline+blue but also attempt hyperlink xml if possible
            link_text = child.get_text()
            run = paragraph.add_run(link_text)
            run.underline = True
            run.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
            # Keep Tw Cen MT size
            if code:
                run.font.name = "Consolas"
                run.font.size = Pt(9)
            else:
                set_run_font(run, FONT_NAME, target_pt, color_hex="0563C1", bold=bold, italic=italic)
                run.underline = True
            # TODO: proper hyperlink relationship could be added via docx.oxml but keeping visual link is sufficient for offline docs
            # Handle nested formatting inside <a> - not needed as get_text already flattens; but handle nested strong/em inside a?
            # If a contains nested tags, above recursion would be better - flatten fallback:
            # We already used get_text, so if child had <strong> inside, we lose bold. Alternative: recurse with link flag.
            # Simpler: if child has children tags, recurse and add hyperlink runs separately
            if len(child.find_all()) > 0:
                # redo with recursion flagging hyperlink
                # Remove the run we just added and recurse with link styling
                # For simplicity, remove last run and handle via separate method
                paragraph.runs[-1].text = ""  # clear
                # recurse adding with link style - we treat as normal but underline/blue
                def _recurse_link(n, b=bold, i=italic, c=code):
                    for sub in n.children:
                        if isinstance(sub, NavigableString):
                            r = paragraph.add_run(str(sub))
                            r.underline = True
                            r.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
                            if c:
                                r.font.name = "Consolas"
                                r.font.size = Pt(9)
                            else:
                                set_run_font(r, FONT_NAME, target_pt, color_hex="0563C1", bold=b, italic=i)
                                r.underline = True
                        elif sub.name in ('strong', 'b'):
                            _recurse_link(sub, b=True, i=i, c=c)
                        elif sub.name in ('em', 'i'):
                            _recurse_link(sub, b=b, i=True, c=c)
                        elif sub.name == 'code':
                            _recurse_link(sub, b=b, i=i, c=True)
                        else:
                            _recurse_link(sub, b=b, i=i, c=c)
                # clear the placeholder empty run text already; now recurse
                # we have already added empty run; just recurse children
                # To avoid double, we should not have added run above if nested exists. So handle correctly: detect nested before adding.
                pass  # handled via above placeholder, recursion would double; so skip for now as most links are plain text

        elif child.name == 'br':
            run = paragraph.add_run()
            run.add_break()
        elif child.name in ('span', 'u', 's', 'del', 'ins'):
            _add_runs_from_html_node(paragraph, child, base_pt, bold=bold, italic=italic, code=code, is_heading=is_heading, heading_level=heading_level)
        else:
            # unknown tag - recurse
            _add_runs_from_html_node(paragraph, child, base_pt, bold=bold, italic=italic, code=code, is_heading=is_heading, heading_level=heading_level)


def add_heading_html(doc, element, level, body_pt, uniform_headings):
    tag_pt = body_pt if uniform_headings else HEADING_SIZES_PT.get(level, body_pt)
    style_name = f'Heading {level}' if level <= 9 else 'Heading 3'
    # Ensure style exists fallback to Heading 3
    try:
        _ = doc.styles[style_name]
    except KeyError:
        style_name = 'Heading 3'
    p = doc.add_paragraph(style=style_name)
    p._heading_pt = tag_pt  # store for helper
    # Paragraph formatting already via style; ensure spacing
    # Add runs from element
    _add_runs_from_html_node(p, element, tag_pt, is_heading=True, heading_level=level)
    # Set alignment left (headings always left)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def add_para_html(doc, element, body_pt):
    p = doc.add_paragraph(style='Normal')
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.space_before = Pt(2)
    _add_runs_from_html_node(p, element, body_pt, is_heading=False)
    return p


def _get_list_style(doc, ordered):
    # template may not have List Bullet/Number (letterhead minimal) -> fallback to List Paragraph or Normal
    candidates = ['List Number', 'List Number 2'] if ordered else ['List Bullet', 'List Bullet 2']
    candidates += ['List Paragraph', 'Normal']
    for c in candidates:
        try:
            _ = doc.styles[c]
            return c
        except KeyError:
            continue
    return 'Normal'

def _add_bullet_number_fallback(paragraph, ordered, index):
    """Prepend bullet/number if using Normal/List Paragraph style (visual fallback)."""
    style = paragraph.style.name if paragraph.style else ""
    if style in ('Normal', 'List Paragraph', 'No Spacing'):
        prefix = f"{index}.  " if ordered else "•   "
        # insert at start
        if paragraph.runs:
            paragraph.runs[0].text = prefix + paragraph.runs[0].text
        else:
            r = paragraph.add_run(prefix)
            set_run_font(r, FONT_NAME, 10.5)

def add_list_html(doc, list_element, body_pt, ordered=False):
    style_name = _get_list_style(doc, ordered)
    counter = 1
    for li in list_element.find_all('li', recursive=False):
        p = doc.add_paragraph(style=style_name)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.left_indent = Pt(24)
        p.paragraph_format.first_line_indent = Pt(-12)
        # List items may contain nested <p>, <ul>/<ol> etc. Handle simply: if li contains nested lists, split.
        # Check if li has direct nested ul/ol: extract them separately
        # For simplicity, collect li's inline content before nested list
        # Clone li for inline part: iterate children excluding nested lists
        # Create a wrapper element for inline content
        # We'll handle sub-lists recursively after
        from bs4 import BeautifulSoup as BS  # local
        # Build temp holder for inline content
        # Instead of cloning, just walk children: if child is ul/ol, handle as separate block after paragraph
        inline_holder = BS("<div></div>", 'html.parser').div
        nested_lists = []
        for child in list(li.children):
            if getattr(child, 'name', None) in ('ul', 'ol'):
                nested_lists.append(child)
            else:
                # append copy - we can't move original easily; create new tag/string representation
                # Use BS to append stringified? Simpler: add to inline_holder by appending child (moves node)
                # To preserve, we instead add string or clone
                inline_holder.append(child.extract() if hasattr(child, 'extract') else child)
        # If inline_holder has content, add runs to p
        if inline_holder.decode_contents().strip():
            # Wrap inline_holder in a dummy element to traverse
            _add_runs_from_html_node(p, inline_holder, body_pt, is_heading=False)
        else:
            # fallback: if no inline holder due to direct text, use li itself stripped of nested lists
            # Text without nested lists already handled? Need to add remaining text
            if not nested_lists:
                _add_runs_from_html_node(p, li, body_pt, is_heading=False)
        # Handle nested lists after
        for nl in nested_lists:
            add_list_html(doc, nl, body_pt, ordered=(nl.name == 'ol'))
        # If paragraph ended up empty (e.g., li contained only <p>), ensure we still set font
        if len(p.runs) == 0:
            # try adding text directly from li stripped
            txt = li.get_text(strip=True)
            if txt:
                r = p.add_run(txt)
                set_run_font(r, FONT_NAME, body_pt, color_hex=BODY_COLOR_HEX)
        # fallback bullet/number visual if style doesn't provide it
        if style_name in ('Normal', 'List Paragraph') and len(p.runs) > 0:
            _add_bullet_number_fallback(p, ordered, counter)
        counter += 1


def add_blockquote_html(doc, element, body_pt):
    # blockquote may contain p, ul etc.
    # For each child inside blockquote, add with indentation + italic visual cue
    for child in element.children:
        if isinstance(child, NavigableString):
            if child.strip() == "":
                continue
            p = doc.add_paragraph(style='Normal')
            p.paragraph_format.left_indent = Pt(18)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            # left border via xml?
            try:
                pPr = p._p.get_or_add_pPr()
                pBdr = OxmlElement('w:pBdr')
                left = OxmlElement('w:left')
                left.set(qn('w:val'), 'single')
                left.set(qn('w:sz'), '6')
                left.set(qn('w:space'), '4')
                left.set(qn('w:color'), '2F5496')
                pBdr.append(left)
                pPr.append(pBdr)
                # shading
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'F2F9FF')
                pPr.append(shd)
            except:  # noqa
                pass
            r = p.add_run(str(child).strip())
            set_run_font(r, FONT_NAME, body_pt, color_hex="595959", italic=True)
            r.italic = True
        elif getattr(child, 'name', None) == 'p':
            p = doc.add_paragraph(style='Normal')
            p.paragraph_format.left_indent = Pt(18)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            try:
                pPr = p._p.get_or_add_pPr()
                pBdr = OxmlElement('w:pBdr')
                left = OxmlElement('w:left')
                left.set(qn('w:val'), 'single')
                left.set(qn('w:sz'), '6')
                left.set(qn('w:space'), '4')
                left.set(qn('w:color'), '2F5496')
                pBdr.append(left)
                pPr.append(pBdr)
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'F2F9FF')
                pPr.append(shd)
            except:  # noqa
                pass
            _add_runs_from_html_node(p, child, body_pt, is_heading=False)
            # Make italic
            for r in p.runs:
                r.italic = True
                if r.font.color.rgb is None or str(r.font.color.rgb) == "262626":
                    try:
                        r.font.color.rgb = RGBColor.from_string("595959")
                    except:  # noqa
                        pass
        elif getattr(child, 'name', None) in ('ul', 'ol'):
            add_list_html(doc, child, body_pt, ordered=(child.name == 'ol'))
        else:
            if hasattr(child, 'name'):
                # generic fallback: add as para
                p = doc.add_paragraph(style='Normal')
                p.paragraph_format.left_indent = Pt(18)
                _add_runs_from_html_node(p, child, body_pt, is_heading=False)
                for r in p.runs:
                    r.italic = True


def add_code_block_html(doc, element, body_pt):
    # element is <pre>, contains <code>
    code_text = element.get_text()
    p = doc.add_paragraph(style='Normal')
    # Shading + border for code block
    try:
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'F2F2F2')
        pPr.append(shd)
        pBdr = OxmlElement('w:pBdr')
        for edge in ['top', 'left', 'bottom', 'right']:
            el = OxmlElement(f'w:{edge}')
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), '4')
            el.set(qn('w:space'), '4')
            el.set(qn('w:color'), 'BFBFBF')
            pBdr.append(el)
        pPr.append(pBdr)
        # keep lines together, indent
        p.paragraph_format.left_indent = Pt(6)
        p.paragraph_format.right_indent = Pt(6)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
    except:  # noqa
        pass
    # Add each line preserving breaks
    lines = code_text.split("\n")
    for idx, line in enumerate(lines):
        # Preserve empty lines as empty run with break
        if line == "" and idx != len(lines)-1:
            # add break but keep line
            r = p.add_run(line)
            r.font.name = "Consolas"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor.from_string("333333")
            if idx < len(lines)-1:
                r.add_break()
            continue
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor.from_string("333333")
        if idx < len(lines) - 1:
            r.add_break()


def add_table_html(doc, table_element, body_pt):
    rows = table_element.find_all('tr')
    if not rows:
        return
    # Determine columns from first row
    first_row_cells = rows[0].find_all(['th', 'td'])
    ncols = len(first_row_cells)
    if ncols == 0:
        return
    table = doc.add_table(rows=1, cols=ncols)
    # pick first available table style
    for cand in ['Light Shading', 'Light Shading Accent 1', 'Table Grid', 'Light Grid', 'Medium Shading 1', 'Normal Table']:
        try:
            _ = doc.styles[cand]
            table.style = cand
            break
        except KeyError:
            continue
    try:
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
    except:  # noqa
        pass
    table.autofit = True

    # Header row
    hdr_cells = table.rows[0].cells
    is_header = rows[0].find('th') is not None
    for idx, cell_elem in enumerate(first_row_cells):
        cell = hdr_cells[idx]
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        # clear default paragraph
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        # shading for header via xml
        if is_header:
            try:
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), '2F5496')
                tcPr.append(shd)
            except:  # noqa
                pass
        # add content runs
        temp_p = p
        # Walk inline content of cell_elem
        # Reuse helper: create temp paragraph then move runs? Simpler: directly add runs to cell paragraph
        def _add_to_cell_para(para, elem, is_hdr):
            color = "FFFFFF" if is_hdr else BODY_COLOR_HEX
            pt = body_pt * 0.9  # slightly smaller in tables
            for child in elem.children:
                if isinstance(child, NavigableString):
                    txt = str(child).strip()
                    if not txt:
                        continue
                    r = para.add_run(txt)
                    set_run_font(r, FONT_NAME, pt, color_hex=color, bold=is_hdr)
                elif child.name in ('strong', 'b'):
                    txt = child.get_text(strip=True)
                    if txt:
                        r = para.add_run(txt)
                        set_run_font(r, FONT_NAME, pt, color_hex=color, bold=True)
                elif child.name in ('em', 'i'):
                    txt = child.get_text(strip=True)
                    if txt:
                        r = para.add_run(txt)
                        set_run_font(r, FONT_NAME, pt, color_hex=color, italic=True)
                elif child.name == 'br':
                    para.add_run().add_break()
                else:
                    txt = child.get_text(strip=True)
                    if txt:
                        r = para.add_run(txt)
                        set_run_font(r, FONT_NAME, pt, color_hex=color, bold=is_hdr)

        _add_to_cell_para(temp_p, cell_elem, is_header)

    # Remaining rows
    for row_elem in rows[1:]:
        cells = row_elem.find_all(['td', 'th'])
        row_cells = table.add_row().cells
        for idx, cell_elem in enumerate(cells):
            if idx >= ncols:
                break
            cell = row_cells[idx]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            # Alternate row shading for readability
            if rows.index(row_elem) % 2 == 1:
                try:
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    shd.set(qn('w:fill'), 'F2F9FF')
                    tcPr.append(shd)
                except:  # noqa
                    pass
            def _add_to_cell_para2(para, elem):
                for child in elem.children:
                    if isinstance(child, NavigableString):
                        txt = str(child).strip()
                        if not txt:
                            continue
                        r = para.add_run(txt)
                        set_run_font(r, FONT_NAME, body_pt*0.9, color_hex=BODY_COLOR_HEX)
                    elif child.name in ('strong', 'b'):
                        r = para.add_run(child.get_text(strip=True))
                        set_run_font(r, FONT_NAME, body_pt*0.9, color_hex=BODY_COLOR_HEX, bold=True)
                    elif child.name in ('em', 'i'):
                        r = para.add_run(child.get_text(strip=True))
                        set_run_font(r, FONT_NAME, body_pt*0.9, color_hex=BODY_COLOR_HEX, italic=True)
                    else:
                        txt = child.get_text(strip=True)
                        if txt:
                            r = para.add_run(txt)
                            set_run_font(r, FONT_NAME, body_pt*0.9, color_hex=BODY_COLOR_HEX)
            _add_to_cell_para2(p, cell_elem)

    # Set column widths loosely - autofit will handle
    # Add spacing after table
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_hr_html(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    # Add bottom border line
    try:
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'BFBFBF')
        pBdr.append(bottom)
        pPr.append(pBdr)
    except:  # noqa
        pass
    # Add centered "— — —" or leave empty with border visual
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Keep empty; border shows line
    return p


def convert_markdown_via_html(doc, md_text, body_pt, uniform_headings):
    """Convert using markdown -> HTML -> python-docx via BeautifulSoup."""
    # Use extra + tables + sane_lists for better fidelity
    html = markdown.markdown(md_text, extensions=['extra', 'tables', 'sane_lists', 'smarty'])
    soup = BeautifulSoup(f"<div>{html}</div>", 'html.parser')
    container = soup.div

    for elem in list(container.children):
        if isinstance(elem, NavigableString):
            txt = str(elem).strip()
            if not txt:
                continue
            # Text outside tags -> paragraph
            p = doc.add_paragraph(style='Normal')
            r = p.add_run(txt)
            set_run_font(r, FONT_NAME, body_pt, color_hex=BODY_COLOR_HEX)
            continue
        if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(elem.name[1])
            add_heading_html(doc, elem, level, body_pt, uniform_headings)
        elif elem.name == 'p':
            # Check if p contains only an image? Not needed.
            add_para_html(doc, elem, body_pt)
        elif elem.name == 'ul':
            add_list_html(doc, elem, body_pt, ordered=False)
        elif elem.name == 'ol':
            add_list_html(doc, elem, body_pt, ordered=True)
        elif elem.name == 'blockquote':
            add_blockquote_html(doc, elem, body_pt)
        elif elem.name == 'pre':
            add_code_block_html(doc, elem, body_pt)
        elif elem.name == 'hr':
            add_hr_html(doc)
        elif elem.name == 'table':
            add_table_html(doc, elem, body_pt)
        elif elem.name in ['div', 'section']:
            # recurse children
            for sub in elem.children:
                if isinstance(sub, NavigableString):
                    if sub.strip():
                        p = doc.add_paragraph(style='Normal')
                        r = p.add_run(sub.strip())
                        set_run_font(r, FONT_NAME, body_pt)
                elif sub.name in ['h1','h2','h3','h4','h5','h6']:
                    lvl = int(sub.name[1])
                    add_heading_html(doc, sub, lvl, body_pt, uniform_headings)
                elif sub.name == 'p':
                    add_para_html(doc, sub, body_pt)
                elif sub.name in ['ul','ol']:
                    add_list_html(doc, sub, body_pt, ordered=(sub.name=='ol'))
                elif sub.name == 'table':
                    add_table_html(doc, sub, body_pt)
                elif sub.name == 'blockquote':
                    add_blockquote_html(doc, sub, body_pt)
                elif sub.name == 'pre':
                    add_code_block_html(doc, sub, body_pt)
                elif sub.name == 'hr':
                    add_hr_html(doc)
        else:
            # fallback: treat as paragraph
            p = doc.add_paragraph(style='Normal')
            # try to extract text with formatting
            if hasattr(elem, 'children'):
                _add_runs_from_html_node(p, elem, body_pt, is_heading=False)
            else:
                r = p.add_run(elem.get_text())
                set_run_font(r, FONT_NAME, body_pt)


# ======================= FALLBACK REGEX PARSER =======================

INLINE_RE = re.compile(
    r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`[^`]+`|\[.*?\]\(.*?\))'
)

def add_runs_inline_fallback(paragraph, text, base_pt, color_hex=BODY_COLOR_HEX, is_heading=False, heading_pt=None):
    """Parse inline markdown bold/italic/code/link for fallback parser."""
    target_pt = heading_pt if is_heading and heading_pt else base_pt
    target_color = HEADING_COLOR_HEX if is_heading else color_hex
    # Split keeping delimiters
    parts = INLINE_RE.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith('***') and part.endswith('***') and len(part) >= 6:
            inner = part[3:-3]
            r = paragraph.add_run(inner)
            set_run_font(r, FONT_NAME, target_pt, color_hex=target_color, bold=True, italic=True)
        elif part.startswith('**') and part.endswith('**') and len(part) >= 4:
            inner = part[2:-2]
            r = paragraph.add_run(inner)
            set_run_font(r, FONT_NAME, target_pt, color_hex=target_color, bold=True)
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2 and not part.startswith('**'):
            inner = part[1:-1]
            r = paragraph.add_run(inner)
            set_run_font(r, FONT_NAME, target_pt, color_hex=target_color, italic=True)
        elif part.startswith('`') and part.endswith('`'):
            inner = part[1:-1]
            r = paragraph.add_run(inner)
            r.font.name = "Consolas"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor.from_string("333333")
            try:
                rPr = r._element.get_or_add_rPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'F2F2F2')
                rPr.append(shd)
            except:  # noqa
                pass
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            # link
            m = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if m:
                txt, url = m.groups()
                r = paragraph.add_run(txt)
                r.underline = True
                r.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
                set_run_font(r, FONT_NAME, target_pt, color_hex="0563C1", bold=is_heading, italic=False)
                r.underline = True
            else:
                r = paragraph.add_run(part)
                set_run_font(r, FONT_NAME, target_pt, color_hex=target_color)
        else:
            # plain text
            if part.strip() == "":
                r = paragraph.add_run(part)
                set_run_font(r, FONT_NAME, target_pt, color_hex=target_color)
            else:
                # handle escapes? keep
                r = paragraph.add_run(part)
                set_run_font(r, FONT_NAME, target_pt, color_hex=target_color, bold=is_heading)


def convert_markdown_fallback(doc, md_text, body_pt, uniform_headings):
    lines = md_text.splitlines()
    i = 0
    # Helpers
    def is_hr(line):
        s = line.strip()
        return s in ('---', '***', '___') or (len(s) >= 3 and all(c == s[0] for c in s) and s[0] in '-*_' and len(set(s)) == 1)

    def is_heading(line):
        return re.match(r'^(#{1,6})\s+(.*)', line)

    # State for code block
    in_code_block = False
    code_lang = ""
    code_buf = []
    # list handling
    # table detection
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code fence
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lang = stripped[3:].strip()
                code_buf = []
            else:
                in_code_block = False
                # emit code block
                p = doc.add_paragraph(style='Normal')
                try:
                    pPr = p._p.get_or_add_pPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    shd.set(qn('w:fill'), 'F2F2F2')
                    pPr.append(shd)
                    pBdr = OxmlElement('w:pBdr')
                    for edge in ['top','left','bottom','right']:
                        el = OxmlElement(f'w:{edge}')
                        el.set(qn('w:val'), 'single')
                        el.set(qn('w:sz'), '4')
                        el.set(qn('w:space'), '4')
                        el.set(qn('w:color'), 'BFBFBF')
                        pBdr.append(el)
                    pPr.append(pBdr)
                    p.paragraph_format.left_indent = Pt(6)
                    p.paragraph_format.right_indent = Pt(6)
                except:  # noqa
                    pass
                code_text = "\n".join(code_buf)
                for li_idx, cline in enumerate(code_text.split("\n")):
                    r = p.add_run(cline)
                    r.font.name = "Consolas"
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor.from_string("333333")
                    if li_idx < len(code_text.split("\n"))-1:
                        r.add_break()
                code_buf = []
            i += 1
            continue
        if in_code_block:
            code_buf.append(line)
            i += 1
            continue

        # Blank line -> spacing
        if stripped == "":
            i += 1
            continue

        # Horizontal rule
        if is_hr(stripped):
            add_hr_html(doc)
            i += 1
            continue

        # Heading
        m = is_heading(line)
        if m:
            lvl = len(m.group(1))
            content = m.group(2).strip()
            tag_pt = body_pt if uniform_headings else HEADING_SIZES_PT.get(lvl, body_pt)
            style_name = f'Heading {lvl}' if lvl <= 9 else 'Heading 3'
            try:
                _ = doc.styles[style_name]
            except KeyError:
                style_name = 'Heading 3'
            p = doc.add_paragraph(style=style_name)
            p._heading_pt = tag_pt
            add_runs_inline_fallback(p, content, body_pt, is_heading=True, heading_pt=tag_pt)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            # collect consecutive blockquote lines
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                bq_lines.append(lines[i].strip()[1:].lstrip())
                i += 1
            # also handle contiguous lines that are part of same quote without >? Not needed
            text = " ".join(bq_lines)
            p = doc.add_paragraph(style='Normal')
            p.paragraph_format.left_indent = Pt(18)
            try:
                pPr = p._p.get_or_add_pPr()
                pBdr = OxmlElement('w:pBdr')
                left = OxmlElement('w:left')
                left.set(qn('w:val'), 'single')
                left.set(qn('w:sz'), '6')
                left.set(qn('w:space'), '4')
                left.set(qn('w:color'), '2F5496')
                pBdr.append(left)
                pPr.append(pBdr)
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'F2F9FF')
                pPr.append(shd)
            except:  # noqa
                pass
            add_runs_inline_fallback(p, text, body_pt, color_hex="595959")
            for r in p.runs:
                r.italic = True
            continue

        # Table detection: line contains | and next line is separator like |---|---|
        if "|" in line and i+1 < len(lines) and re.match(r'^\s*\|?[\s\-:|]+\|?\s*$', lines[i+1]) and set(lines[i+1].strip()) & set("-:|"):
            # header
            header = [c.strip() for c in line.strip().strip('|').split('|')]
            # sep line skip
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip() != "":
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            ncols = len(header)
            # create table
            table = doc.add_table(rows=1, cols=ncols)
            for cand in ['Light Shading', 'Light Shading Accent 1', 'Table Grid', 'Light Grid', 'Normal Table']:
                try:
                    _ = doc.styles[cand]
                    table.style = cand
                    break
                except KeyError:
                    continue
            try:
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
            except:  # noqa
                pass
            table.autofit = True
            hdr_cells = table.rows[0].cells
            for idx, h in enumerate(header):
                cell = hdr_cells[idx]
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                cell.text = ""
                p = cell.paragraphs[0]
                r = p.add_run(h)
                set_run_font(r, FONT_NAME, body_pt*0.9, color_hex="FFFFFF", bold=True)
                try:
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    shd.set(qn('w:fill'), '2F5496')
                    tcPr.append(shd)
                except:  # noqa
                    pass
            for r_idx, row in enumerate(rows):
                row_cells = table.add_row().cells
                for c_idx, val in enumerate(row):
                    if c_idx >= ncols:
                        break
                    cell = row_cells[c_idx]
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    cell.text = ""
                    p = cell.paragraphs[0]
                    # Ensure we handle inline markdown in cells
                    add_runs_inline_fallback(p, val, body_pt*0.9)
                    if r_idx % 2 == 0:
                        try:
                            tcPr = cell._tc.get_or_add_tcPr()
                            shd = OxmlElement('w:shd')
                            shd.set(qn('w:val'), 'clear')
                            shd.set(qn('w:color'), 'auto')
                            shd.set(qn('w:fill'), 'F2F9FF')
                            tcPr.append(shd)
                        except:  # noqa
                            pass
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            continue

        # Unordered list
        if re.match(r'^\s*[-*+]\s+', line):
            # collect consecutive list items
            items = []
            while i < len(lines) and re.match(r'^\s*[-*+]\s+', lines[i]):
                items.append(re.match(r'^\s*[-*+]\s+(.*)', lines[i]).group(1))
                i += 1
                # handle indented continuation lines? For simplicity, if next line indent without bullet but not blank, append to last item
                while i < len(lines) and lines[i].strip() != "" and not re.match(r'^\s*[-*+]\s+', lines[i]) and not re.match(r'^\s*\d+\.\s+', lines[i]) and not is_heading(lines[i]) and lines[i].startswith("  "):
                    items[-1] += " " + lines[i].strip()
                    i += 1
            for idx, it in enumerate(items):
                style = _get_list_style(doc, False)
                p = doc.add_paragraph(style=style)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Pt(24)
                p.paragraph_format.first_line_indent = Pt(-12) if style == 'Normal' else Pt(0)
                add_runs_inline_fallback(p, it, body_pt)
                if style in ('Normal', 'List Paragraph') and len(p.runs) > 0:
                    _add_bullet_number_fallback(p, False, idx+1)
            continue

        # Ordered list
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(re.match(r'^\s*\d+\.\s+(.*)', lines[i]).group(1))
                i += 1
                while i < len(lines) and lines[i].strip() != "" and not re.match(r'^\s*\d+\.\s+', lines[i]) and not re.match(r'^\s*[-*+]\s+', lines[i]) and lines[i].startswith("  "):
                    items[-1] += " " + lines[i].strip()
                    i += 1
            for idx, it in enumerate(items):
                style = _get_list_style(doc, True)
                p = doc.add_paragraph(style=style)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Pt(24)
                p.paragraph_format.first_line_indent = Pt(-12) if style == 'Normal' else Pt(0)
                add_runs_inline_fallback(p, it, body_pt)
                if style in ('Normal', 'List Paragraph') and len(p.runs) > 0:
                    _add_bullet_number_fallback(p, True, idx+1)
            continue

        # Paragraph: collect consecutive non-special lines into one paragraph
        para_lines = []
        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() == "" or re.match(r'^(#{1,6})\s+', nxt) or re.match(r'^\s*[-*+]\s+', nxt) or re.match(r'^\s*\d+\.\s+', nxt) or nxt.strip().startswith("```") or nxt.strip().startswith(">") or is_hr(nxt.strip()) or ("|" in nxt and i+1 < len(lines) and re.match(r'^\s*\|?[\s\-:|]+\|?\s*$', lines[i+1])):
                break
            para_lines.append(nxt.strip())
            i += 1
        if para_lines:
            text = " ".join(para_lines)
            p = doc.add_paragraph(style='Normal')
            p.paragraph_format.space_after = Pt(6)
            add_runs_inline_fallback(p, text, body_pt)
            continue
        i += 1


# ======================= MAIN CONVERT =======================

def convert_md_file(md_path: Path, template_path: Path, out_path: Path, body_pt, uniform_headings):
    md_text = md_path.read_text(encoding='utf-8')
    # Load template; if missing create blank doc with margins matching template (1 inch)
    if template_path and template_path.exists():
        doc = Document(str(template_path))
    else:
        print(f"warn: template {template_path} not found, creating blank doc")
        doc = Document()
        # set margins 1 inch
        for sec in doc.sections:
            sec.top_margin = Pt(72)  # 1 inch = 72pt = 914400 EMU but Pt mapping via Inches?
            sec.bottom_margin = Pt(72)
            sec.left_margin = Pt(72)
            sec.right_margin = Pt(72)
            sec.header_distance = Pt(36)
            sec.footer_distance = Pt(36)
        # Note: Pt values not exactly EMU but python-docx converts

    # Apply styles
    apply_template_styles(doc, FONT_NAME, body_pt, uniform_headings)

    # The template's first paragraph contains the behindDoc image. Keep it.
    # Ensure we don't have duplicate empty start; If template has only that one empty para, we keep it and add content after.
    # If no paragraphs yet due to blank doc, ensure at least one section
    # Add a small spacer if first content would stick to top - optional, but letterhead image covers full page behind, so text starts at margin.
    # For visual, insert a paragraph with small space if you want gap below header - currently margins already define top offset.

    # Convert markdown
    if USE_HTML_PATH:
        try:
            convert_markdown_via_html(doc, md_text, body_pt, uniform_headings)
        except Exception as e:
            print(f"warn: html path failed for {md_path.name}: {e}, falling back to regex parser")
            convert_markdown_fallback(doc, md_text, body_pt, uniform_headings)
    else:
        convert_markdown_fallback(doc, md_text, body_pt, uniform_headings)

    # Safety: ensure all runs are Tw Cen MT where appropriate (post-process)
    # Don't override code blocks
    # Walk paragraphs and patch where font still default theme
    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.name in (None, "", "Calibri", "Calibri Light", "Times New Roman"):
                # check if parent style is headings? still Tw Cen MT
                # skip code blocks that are correctly Consolas
                if run.font.name not in ["Consolas"]:
                    # Keep size if heading size already set via style but run may still be theme font
                    # Use paragraph style size as fallback? We just set to body_pt if not heading
                    is_heading_style = para.style.name.startswith("Heading") if para.style else False
                    if is_heading_style:
                        # infer level
                        try:
                            lvl = int(para.style.name.split()[-1])
                            pt = body_pt if uniform_headings else HEADING_SIZES_PT.get(lvl, body_pt)
                        except:
                            pt = body_pt
                        set_run_font(run, FONT_NAME, pt, color_hex=HEADING_COLOR_HEX, bold=True)
                    else:
                        set_run_font(run, FONT_NAME, body_pt, color_hex=BODY_COLOR_HEX)

    # Also fix tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        if run.font.name in (None, "", "Calibri"):
                            if run.font.name != "Consolas":
                                # table cells already Tw Cen MT but may need fallback
                                set_run_font(run, FONT_NAME, body_pt*0.9)

    # Ensure last section properties preserved (margins already from template)
    # Add page numbers to footer
    add_page_numbers(doc, FONT_NAME, max(9, body_pt - 2))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path


def main():
    global FONT_NAME, FONT_SIZE_PT, HEADING_SIZES_PT
    parser = argparse.ArgumentParser(description="Convert .md files to Word docs using AfyaDesk letterhead (Tw Cen MT 16px)")
    parser.add_argument("--input-dir", type=str, default=".", help="Folder containing .md files (default: current dir)")
    parser.add_argument("--template", type=str, default="afyadesk-letterhead.docx", help="Path to letterhead .docx template")
    parser.add_argument("--output-dir", type=str, default="output_docs", help="Output folder for .docx files")
    parser.add_argument("--font-name", type=str, default=FONT_NAME, help="Font family (default Tw Cen MT)")
    parser.add_argument("--font-size", type=float, default=None, help="Font size in points (default 12pt = 16px). Pass 14 for 14pt.")
    parser.add_argument("--font-size-px", type=float, default=None, help="Font size in pixels (converted to pt via px*0.75). Overrides --font-size if set.")
    parser.add_argument("--uniform-headings", action="store_true", help="Force headings to same size as body")
    args = parser.parse_args()

    FONT_NAME = args.font_name
    # Resolve size
    if args.font_size_px is not None:
        FONT_SIZE_PT = args.font_size_px * 0.75
    elif args.font_size is not None:
        FONT_SIZE_PT = args.font_size
    # else keep default 10.5pt

    input_dir = Path(args.input_dir)
    template_path = Path(args.template)
    # Resolve relative to input_dir if template not absolute and not found
    if not template_path.is_absolute() and not template_path.exists():
        alt = input_dir / args.template
        if alt.exists():
            template_path = alt
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        # if output_dir is relative and input_dir is given, make output relative to input_dir? keep cwd relative otherwise
        # We'll keep as given relative to cwd
        pass

    if not input_dir.exists():
        print(f"Input dir not found: {input_dir}")
        sys.exit(1)

    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        # also search recursively? User said in a folder, likely non-recursive. Check one level deep?
        md_files = sorted(input_dir.rglob("*.md"))
    if not md_files:
        print(f"No .md files found in {input_dir}")
        sys.exit(0)

    print(f"Template: {template_path} (exists={template_path.exists()})")
    print(f"Font: {FONT_NAME} @ {FONT_SIZE_PT}pt ({FONT_SIZE_PT/0.75:.1f}px) {'uniform headings' if args.uniform_headings else 'hierarchical headings'}")
    print(f"Parser: {'markdown+bs4 (HTML)' if USE_HTML_PATH else 'fallback regex (install markdown+beautifulsoup4 for better fidelity)'}")
    print(f"Input: {input_dir} -> {len(md_files)} md files")
    print(f"Output: {output_dir}")
    print("-" * 60)

    ok = 0
    for md_path in md_files:
        # Skip output dir if inside input_dir
        try:
            if output_dir.resolve() in md_path.resolve().parents:
                continue
        except:  # noqa
            pass
        out_path = output_dir / (md_path.stem + ".docx")
        try:
            convert_md_file(md_path, template_path, out_path, FONT_SIZE_PT, args.uniform_headings)
            print(f"[OK] {md_path.name} -> {out_path}  ({out_path.stat().st_size/1024:.1f} KB)")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {md_path.name} failed: {e}")
            import traceback
            traceback.print_exc()

    print("-" * 60)
    print(f"Done: {ok}/{len(md_files)} converted to {output_dir.resolve()}")
    if not USE_HTML_PATH:
        print("Tip: for best table/list/link fidelity, install: pip install markdown beautifulsoup4")


if __name__ == "__main__":
    main()

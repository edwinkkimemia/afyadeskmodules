#!/usr/bin/env python3
"""
convert_docx_to_pdf.py
Converts all .docx files in a folder to PDF using Microsoft Word COM automation (Windows).

Requirements:
- Microsoft Word installed
- pywin32: pip install pywin32

Usage:
    python convert_docx_to_pdf.py                    # output_docs/ -> output_pdfs/
    python convert_docx_to_pdf.py --input-dir output_docs --output-dir output_pdfs
"""
import argparse
import sys
from pathlib import Path

try:
    import win32com.client
    import pythoncom
except ImportError:
    print("ERROR: pywin32 not installed. Run: pip install pywin32")
    sys.exit(1)


def convert_docx_to_pdf(input_dir: Path, output_dir: Path):
    """Convert all .docx files in input_dir to PDF in output_dir using Word COM."""
    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()
    
    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        return 0, 0
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    docx_files = sorted(input_dir.glob("*.docx"))
    if not docx_files:
        print(f"No .docx files found in {input_dir}")
        return 0, 0
    
    print(f"Input:  {input_dir} ({len(docx_files)} files)")
    print(f"Output: {output_dir}")
    print("-" * 60)
    
    # Initialize COM
    pythoncom.CoInitialize()
    
    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False  # wdAlertsNone
        
        ok = 0
        failed = []
        
        for docx_path in docx_files:
            pdf_path = output_dir / (docx_path.stem + ".pdf")
            try:
                print(f"Converting: {docx_path.name} ... ", end="", flush=True)
                doc = word.Documents.Open(str(docx_path))
                # wdFormatPDF = 17
                doc.SaveAs(str(pdf_path), FileFormat=17)
                doc.Close(False)
                print("OK")
                ok += 1
            except Exception as e:
                print(f"FAILED: {e}")
                failed.append((docx_path.name, str(e)))
                try:
                    if 'doc' in locals():
                        doc.Close(False)
                except:
                    pass
        
        print("-" * 60)
        print(f"Done: {ok}/{len(docx_files)} converted to {output_dir}")
        if failed:
            print("Failed:")
            for name, err in failed:
                print(f"  - {name}: {err}")
        return ok, len(failed)
        
    except Exception as e:
        print(f"Failed to start Word: {e}")
        print("Ensure Microsoft Word is installed and licensed.")
        return 0, len(docx_files)
    finally:
        if word:
            try:
                word.Quit()
            except:
                pass
        pythoncom.CoUninitialize()


def main():
    parser = argparse.ArgumentParser(description="Convert .docx to PDF using Word COM (Windows)")
    parser.add_argument("--input-dir", type=str, default="output_docs", help="Folder with .docx files")
    parser.add_argument("--output-dir", type=str, default="output_pdfs", help="Output folder for PDFs")
    args = parser.parse_args()
    
    convert_docx_to_pdf(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
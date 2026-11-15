#!/usr/bin/env python3
"""Compile EN/ES papers and general-audience blog PDF using pandoc and weasyprint."""
from pathlib import Path
import subprocess

PAPER_DIR = Path(__file__).resolve().parent
LAB_ROOT = PAPER_DIR.parents[2]
BLOG_MD = LAB_ROOT / 'blog' / '2026-11-esfuerzo-de-razonamiento.md'
BLOG_PDF = LAB_ROOT / 'blog' / '2026-11-esfuerzo-de-razonamiento.pdf'


def build_css(footer_label, page_word, of_word):
    return f"""
@page {{
  size: A4;
  margin: 17mm 17mm 18mm 17mm;
  @bottom-center {{
    content: "{footer_label} · {page_word} " counter(page) " {of_word} " counter(pages);
    font-family: "DejaVu Sans", sans-serif;
    font-size: 8pt;
    color: #6b7280;
  }}
}}
* {{
  box-sizing: border-box;
}}
body {{
  font-family: "DejaVu Serif", Georgia, serif;
  font-size: 9.8pt;
  line-height: 1.48;
  color: #111827;
  max-width: 100%;
}}
h1 {{
  font-family: "DejaVu Sans", sans-serif;
  font-size: 16pt;
  line-height: 1.22;
  color: #0f172a;
  border-bottom: 2px solid #0f172a;
  padding-bottom: 7px;
  margin-bottom: 10px;
}}
h2 {{
  font-family: "DejaVu Sans", sans-serif;
  font-size: 11.8pt;
  color: #1e293b;
  margin-top: 15px;
  margin-bottom: 5px;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 3px;
  page-break-after: avoid;
}}
h3 {{
  font-family: "DejaVu Sans", sans-serif;
  font-size: 10.2pt;
  color: #334155;
  margin-top: 11px;
  margin-bottom: 4px;
  page-break-after: avoid;
}}
code {{
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8.4pt;
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
}}
blockquote {{
  margin: 10px 0;
  padding: 6px 12px;
  border-left: 3px solid #94a3b8;
  background: #f8fafc;
  color: #334155;
  font-size: 9.2pt;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 8.2pt;
  font-family: "DejaVu Sans", sans-serif;
  page-break-inside: avoid;
}}
th, td {{
  border: 1px solid #cbd5e1;
  padding: 4.5px 6px;
  text-align: left;
  vertical-align: top;
}}
th {{
  background: #f8fafc;
  font-weight: bold;
  color: #0f172a;
}}
figure, p img {{
  page-break-inside: avoid;
}}
figure {{
  margin: 10px 0;
  text-align: center;
}}
img {{
  display: block;
  width: 100%;
  max-width: 168mm;
  max-height: 102mm;
  height: auto;
  object-fit: contain;
  margin: 8px auto 4px auto;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}}
figcaption {{
  font-family: "DejaVu Sans", sans-serif;
  font-size: 8.3pt;
  color: #475569;
  margin-top: 4px;
}}
hr {{
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 10px 0;
}}
"""


def compile_one(md_path, pdf_path, title, footer_label, page_word, of_word):
    work_dir = md_path.parent
    html_path = work_dir / f'{md_path.stem}.tmp.html'
    css_path = work_dir / f'{md_path.stem}.tmp.css'
    css_path.write_text(build_css(footer_label, page_word, of_word), encoding='utf-8')
    subprocess.run(
        [
            'pandoc', str(md_path), '-f', 'gfm', '-t', 'html5', '--standalone',
            '--metadata', f'title={title}',
            '--css', str(css_path), '-o', str(html_path),
        ],
        check=True,
        cwd=work_dir,
    )
    subprocess.run(['weasyprint', str(html_path), str(pdf_path)], check=True, cwd=work_dir)
    html_path.unlink(missing_ok=True)
    css_path.unlink(missing_ok=True)
    print('Compiled', pdf_path, f'({pdf_path.stat().st_size} bytes)')


def main():
    compile_one(
        PAPER_DIR / 'paper-en.md',
        PAPER_DIR / 'paper-en.pdf',
        'Experiment 03: Reasoning Effort in Coding Agents (EN)',
        'CrisoLabs Lab · Experiment 03',
        'Page',
        'of',
    )
    compile_one(
        PAPER_DIR / 'paper-es.md',
        PAPER_DIR / 'paper-es.pdf',
        'Experimento 03: Esfuerzo de razonamiento en agentes de código (ES)',
        'CrisoLabs Lab · Experimento 03',
        'Página',
        'de',
    )
    compile_one(
        BLOG_MD,
        BLOG_PDF,
        'Subir el razonamiento al máximo no hace que la IA programe mejor',
        'CrisoLabs · Artículo para público general',
        'Página',
        'de',
    )


if __name__ == '__main__':
    main()

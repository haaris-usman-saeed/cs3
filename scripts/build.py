"""Build a single HTML file containing the lessons, data, and original slides."""
from pathlib import Path
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / 'index.html').read_text()
css = (ROOT / 'styles.css').read_text()
page = page.replace('<link rel="stylesheet" href="styles.css">', '<style>' + css + '</style>')
for name in ['data/penguins.js', 'math.js', 'content.js', 'app.js']:
    code = (ROOT / name).read_text().replace('</script', '<\\/script')
    page = page.replace(f'<script src="{name}"></script>', '<script>' + code + '</script>')
assets = {
    int(p.stem): 'data:image/jpeg;base64,' + base64.b64encode(p.read_bytes()).decode()
    for p in sorted((ROOT / 'assets/slides').glob('*.jpg'))
}
assert len(assets) == 68
pdf = 'data:application/pdf;base64,' + base64.b64encode((ROOT / 'assets/lecture.pdf').read_bytes()).decode()
embedded = '<script>window.SLIDE_ASSETS=' + json.dumps(assets) + ';window.LECTURE_PDF_ASSET=' + json.dumps(pdf) + ';</script>'
page = page.replace('<script>', embedded + '<script>', 1)
page = page.replace('src="assets/slides/01.jpg"', 'src="' + assets[1] + '"')
page = page.replace('href="assets/lecture.pdf"', 'href="' + pdf + '"')
assert not re.search(r'<(?:script|link)\b[^>]*(?:src|href)="(?!data:)', page)
destination = ROOT / 'dist/logistic-lab.html'
destination.parent.mkdir(exist_ok=True)
destination.write_text(page)
print(f'Built {destination} ({destination.stat().st_size / 1048576:.1f} MiB)')

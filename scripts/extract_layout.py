"""One-off helper used during the Squarespace migration.

Reads a saved Squarespace page and writes its section/block layout to JSON
so the Eleventy templates can render it. Not needed for day-to-day edits.
"""
import sys, os, re, json, hashlib, shutil, urllib.parse
from bs4 import BeautifulSoup
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
OUT_IMG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'images'))
SEEN = {}


def slug(name):
    base = os.path.splitext(name)[0]
    base = urllib.parse.unquote(base).lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    return base or 'image'


def register(files_dir, fname):
    """Copy/resize one saved image into src/images, return its public path."""
    raw = fname
    fname = urllib.parse.unquote(fname)
    src = os.path.join(files_dir, fname)
    if not os.path.exists(src) and os.path.exists(os.path.join(files_dir, raw)):
        src = os.path.join(files_dir, raw)
    if not os.path.exists(src):
        alt = os.path.join(files_dir, fname.replace('+', ' '))
        if os.path.exists(alt):
            src = alt
        else:
            return None
    key = hashlib.md5(open(src, 'rb').read()).hexdigest()
    if key in SEEN:
        return SEEN[key]
    im = Image.open(src)
    alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    ext = '.png' if alpha else '.jpg'
    name = slug(fname) + '-' + key[:5] + ext
    os.makedirs(OUT_IMG, exist_ok=True)
    dst = os.path.join(OUT_IMG, name)
    if max(im.size) > 2200:
        im.thumbnail((2200, 2200), Image.LANCZOS)
    if alpha:
        im.save(dst, optimize=True)
    else:
        im.convert('RGB').save(dst, quality=84, optimize=True, progressive=True)
    SEEN[key] = '/images/' + name
    return SEEN[key]


SITE = 'https://www.tenderpossibilities.ca'
LINK_FIXES = {
    '/2026-summer-series': '/2026-summer-series-at-evergreen-brickworks/',
    'mailto:info@tenderpossibilties.ca': 'mailto:info@tenderpossibilities.ca',
}


def local_href(h):
    h = h.strip()
    if 'engage.squarespace-mail.com' in h:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(h.replace('&amp;', '&')).query)
        if q.get('u'):
            h = q['u'][0]
    if h.startswith('https://tenderpossibilities.ca'):
        h = SITE + h[len('https://tenderpossibilities.ca'):]
    if h in LINK_FIXES:
        return LINK_FIXES[h]
    if h.startswith(SITE):
        h = h[len(SITE):] or '/'
        h = h.split('?')[0]
        h = LINK_FIXES.get(h.rstrip('/'), h)
        if not h.endswith('/') and '.' not in h.rsplit('/', 1)[-1] and '#' not in h:
            h += '/'
    return LINK_FIXES.get(h, h)


KEEP_STYLE = ('color', 'text-align', 'font-size', 'line-height', 'letter-spacing')


def clean(el):
    for x in [el] + el.find_all(True):
        keep = {}
        if x.name == 'a' and x.get('href'):
            keep['href'] = local_href(x['href'])
            if x.get('target'):
                keep['target'] = x['target']
        cls = [c for c in x.get('class', []) if c in ('sqsrte-large', 'sqsrte-small', 'sqsrte-scaled-text-container', 'sqsrte-scaled-text')]
        if cls:
            keep['class'] = cls
        st = x.get('style', '')
        decl = []
        for d in st.split(';'):
            if ':' in d:
                k, v = [s.strip() for s in d.split(':', 1)]
                if k in KEEP_STYLE:
                    decl.append(f'{k}: {v}')
        if decl:
            keep['style'] = '; '.join(decl)
        x.attrs = keep
    return el


def first_css(css, pat):
    return [m.group(1).strip() for m in re.finditer(pat, css)]


def parse(html_path, files_dir):
    soup = BeautifulSoup(open(html_path, encoding='utf-8', errors='replace').read(), 'lxml')
    css = '\n'.join(s.get_text() for s in soup.find_all('style'))
    main = soup.find('main')
    sections = []
    for sec in main.select('section.page-section'):
        s = {'theme': sec.get('data-section-theme', ''), 'blocks': []}
        cls = sec.get('class', [])
        for c in cls:
            for k in ('section-height', 'content-width', 'vertical-alignment', 'horizontal-alignment', 'background-width'):
                if c.startswith(k + '--'):
                    s[k.replace('-', '_')] = c.split('--', 1)[1]
        s['gallery'] = 'gallery-section' in cls
        cw = sec.select_one('.content-wrapper')
        if cw and cw.get('style'):
            s['wrapper_style'] = re.sub(r'\s+', ' ', cw['style']).strip()
        bg = sec.select_one('.section-background img')
        if bg and bg.get('src'):
            pos = re.search(r'object-position:\s*([^;]+)', bg.get('style', ''))
            s['bg'] = {'src': register(files_dir, bg['src'].split('/')[-1].split('?')[0]),
                       'pos': pos.group(1).strip() if pos else None}
        eng = sec.select_one('.fluid-engine')
        if eng:
            eid = [c for c in eng['class'] if c.startswith('fe-')][0][3:]
            m = re.search(r'\.fe-%s \{[^}]*?repeat\((\d+),' % eid, css)
            rows_m = int(m.group(1)) if m else None
            md = re.search(r'min-width: 768px\)[^{]*\{[\s\S]*?\.fe-%s \{[\s\S]*?repeat\((\d+),minmax\(calc\(var\(--container-width\) \* var\(--row-height-scaling-factor\)\)' % eid, css)
            rows_d = int(md.group(1)) if md else None
            f = re.search(r'\.fe-%s \{[\s\S]*?--row-height-scaling-factor:\s*([\d.]+)' % eid, css)
            g = re.search(r'\.fe-%s \{[^}]*?row-gap:\s*([\d.]+)px' % eid, css)
            s['engine'] = {'rows_m': rows_m, 'rows_d': rows_d, 'factor': float(f.group(1)) if f else None,
                           'gap': float(g.group(1)) if g else 11}
        for fb in sec.select('.fe-block'):
            bid = [c for c in fb['class'] if c.startswith('fe-block-')][0][len('fe-block-'):]
            areas = first_css(css, r'\.fe-block-%s \{[^}]*?grid-area:\s*([^;]+);' % re.escape(bid))
            just = first_css(css, r'\.fe-block-%s \.sqs-block \{\s*justify-content:\s*([^;]+);' % re.escape(bid))
            alig = first_css(css, r'\.fe-block-%s \.sqs-block-alignment-wrapper \{\s*align-items:\s*([^;]+);' % re.escape(bid))
            b = {'id': bid, 'area_m': areas[0] if areas else None,
                 'area_d': areas[-1] if areas else None,
                 'v_align': (just[-1] if just else None), 'h_align': (alig[-1] if alig else None)}
            if fb.get('style'):
                b['style'] = re.sub(r'\s+', ' ', fb['style']).strip()
            blk = fb.select_one('.sqs-block')
            bc = blk.get('class', [])
            if 'sqs-block-html' in bc:
                b['type'] = 'html'
                b['html'] = ''.join(str(clean(c)) for c in blk.select_one('.sqs-html-content').find_all(True, recursive=False))
            elif 'sqs-block-image' in bc:
                b['type'] = 'image'
                img = blk.find('img')
                b['src'] = register(files_dir, img['src'].split('/')[-1].split('?')[0])
                b['alt'] = img.get('alt', '')
                b['w'] = img.get('width'); b['h'] = img.get('height')
                a = img.find_parent('a')
                if a and a.get('href'):
                    b['href'] = local_href(a['href'])
                root = blk.select_one('.fluid-image-component-root')
                if root:
                    for pos in ('left', 'right', 'center'):
                        if f'image-position-{pos}' in root.get('class', []):
                            b['pos'] = pos
                st = root.get('style', '') if root else ''
                b['fit'] = 'contain' if 'object-fit: contain' in st else 'cover'
            elif 'sqs-block-accordion' in bc:
                b['type'] = 'accordion'
                b['items'] = []
                for it in blk.select('.accordion-item'):
                    b['items'].append({'title': it.select_one('.accordion-item__title').get_text(strip=True),
                                       'html': ''.join(str(clean(c)) for c in it.select_one('.accordion-item__description').find_all(True, recursive=False))})
            elif 'sqs-block-newsletter' in bc:
                b['type'] = 'newsletter'
            elif 'sqs-block-form' in bc:
                b['type'] = 'form'
            elif blk.select_one('.sqs-shape'):
                b['type'] = 'shape'
                svg = blk.select_one('svg')
                b['shape_w'] = re.search(r'width:\s*([^;]+)', svg.get('style', '')).group(1) if svg else None
            elif blk.select_one('.sqs-block-socialaccountlinks-content') or 'sqs-block-socialaccountlinks' in bc:
                b['type'] = 'social'
            else:
                b['type'] = 'unknown'
                b['classes'] = bc
            s['blocks'].append(b)
        if sec.get('data-sqsp-section') == 'events-list':
            s['kind'] = 'events'
        elif not eng:
            for blk in sec.select('.sqs-block-html'):
                s['blocks'].append({'id': blk.get('id', ''), 'type': 'html', 'flow': True,
                                    'html': ''.join(str(clean(c)) for c in blk.select_one('.sqs-html-content').find_all(True, recursive=False))})
        sections.append(s)
    return sections


if __name__ == '__main__':
    html_path, out_path = sys.argv[1], sys.argv[2]
    files_dir = os.path.splitext(html_path)[0] + '_files'
    data = parse(html_path, files_dir)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(data, open(out_path, 'w'), indent=1, ensure_ascii=False)
    print(out_path, len(data), 'sections', sum(len(s['blocks']) for s in data), 'blocks')

"""One-off helper used during the Squarespace migration.

Turns the saved event list pages into JSON files (one per series) with the
image paths already pointing into src/images.
"""
import sys, os, re, json, urllib.parse
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(__file__))
from extract_layout import register, clean


def events_from(html_path, group):
    files_dir = os.path.splitext(html_path)[0] + '_files'
    soup = BeautifulSoup(open(html_path, encoding='utf-8', errors='replace').read(), 'lxml')
    out = []
    for a in soup.select('article.eventlist-event'):
        link = a.select_one('h1.eventlist-title a')
        img = a.select_one('img.eventlist-thumbnail')
        d = a.select_one('time.event-date')
        s = a.select_one('time.event-time-localized-start')
        e = a.select_one('time.event-time-localized-end')
        m = a.select_one('.eventlist-meta-address-maplink')
        g = a.select_one('.eventlist-meta-export-google')
        ev = {
            'group': group,
            'title': link.get_text(strip=True),
            'url': urllib.parse.urlparse(link['href']).path,
            'image': register(files_dir, img['src'].split('/')[-1]) if img else None,
            'image_alt': img.get('alt') if img else '',
            'date': d['datetime'] if d else None,
            'date_text': d.get_text(strip=True) if d else None,
            'start': s.get_text(strip=True) if s else None,
            'end': e.get_text(strip=True) if e else None,
            'address': [x.get_text(strip=True) for x in a.select('.eventlist-meta-address-line')],
            'map': m['href'] if m else None,
            'gcal': g['href'] if g else None,
        }
        desc = a.select_one('.eventlist-description')
        body = []
        for h in (desc.select('.sqs-html-content') if desc else []):
            for ch in h.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'blockquote'], recursive=False):
                for im in ch.find_all('img'):
                    p = register(files_dir, im['src'].split('/')[-1])
                    im.attrs = {'src': p, 'alt': im.get('alt', '')}
                body.append(str(clean(ch)))
        if not body:
            ex = a.select_one('.eventlist-excerpt')
            if ex:
                ev['from_excerpt'] = True
                for ch in ex.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'blockquote'], recursive=False):
                    body.append(str(clean(ch)))
        ev['body'] = [re.sub(r'(<img[^>]*?)>', r'\1>', b) for b in body]
        out.append(ev)
    return out


def gallery_from(html_path):
    files_dir = os.path.splitext(html_path)[0] + '_files'
    soup = BeautifulSoup(open(html_path, encoding='utf-8', errors='replace').read(), 'lxml')
    items = []
    for fig in soup.select('figure.gallery-grid-item'):
        a = fig.find('a'); im = fig.find('img')
        href = a['href'] if a else ''
        p = urllib.parse.urlparse(href)
        link = None
        if 'itemId=' not in href and href:
            link = p.path if 'tenderpossibilities.ca' in p.netloc else href
        items.append({'src': register(files_dir, im['src'].split('/')[-1]), 'alt': im.get('alt', ''),
                      'w': im.get('width'), 'h': im.get('height'), 'link': link})
    return items


if __name__ == '__main__':
    S = sys.argv[1]
    def find(d):
        for r, _, fs in os.walk(os.path.join(S, d)):
            if '__MACOSX' in r or r.endswith('_files'):
                continue
            for f in fs:
                if f.endswith('.html') and not f.startswith(('saved', 'anchor')):
                    return os.path.join(r, f)
    outdir = os.path.join(os.path.dirname(__file__), '..', 'src', '_data', 'events')
    os.makedirs(outdir, exist_ok=True)
    for g, d in (('2024', 'pages/2024_Tender_Possibilities'), ('2025', 'pages/2025_Tender_Possibilities'),
                 ('2026', 'pages/2026_Tender_Possibilities'), ('upcoming', 'pages2/Upcoming_events_Tender_Possibilities')):
        ev = events_from(find(d), g)
        json.dump(ev, open(os.path.join(outdir, g + '.json'), 'w'), indent=1, ensure_ascii=False)
        print(g, len(ev))
    gal = gallery_from(find('pages/Past_events_Tender_Possibilities'))
    json.dump(gal, open(os.path.join(outdir, 'past_gallery.json'), 'w'), indent=1, ensure_ascii=False)
    print('past gallery', len(gal))

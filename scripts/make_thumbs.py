"""Makes smaller copies (src/images/thumbs) of the flyers used in lists and galleries,
and records them as "thumb" in the event data. Re-run after adding new flyers."""
import json, glob, os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'src', 'images', 'thumbs')
os.makedirs(OUT, exist_ok=True)


def thumb(path, width=1000):
    src = os.path.join(ROOT, 'src', path.lstrip('/'))
    name = os.path.splitext(os.path.basename(path))[0] + '.jpg'
    dst = os.path.join(OUT, name)
    im = Image.open(src)
    if im.width <= width:
        return path
    im = im.convert('RGB')
    im.thumbnail((width, width * 3), Image.LANCZOS)
    im.save(dst, quality=80, optimize=True, progressive=True)
    return '/images/thumbs/' + name


for f in glob.glob(os.path.join(ROOT, 'src', '_data', 'events', '*.json')):
    data = json.load(open(f))
    for item in data:
        if item.get('image'):
            item['thumb'] = thumb(item['image'])
        elif item.get('src'):
            item['thumb'] = thumb(item['src'])
    json.dump(data, open(f, 'w'), indent=1, ensure_ascii=False)
print('thumbs:', len(os.listdir(OUT)))

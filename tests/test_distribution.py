from pathlib import Path
import json
import math
import zipfile
from PIL import Image
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]

def test_atlas_covers_exactly_the_built_cmap():
    font=TTFont(ROOT/'fonts/TalynBrush-Regular.ttf')
    data=json.loads((ROOT/'specimen/coverage.json').read_text())
    entries=data['characters']; cps=[int(x['codepoint'][2:],16) for x in entries]
    assert cps==sorted(font.getBestCmap())
    assert data['count']==len(cps)==11863
    assert sum(p['count'] for p in data['pages'])==len(cps)
    assert len(data['pages'])==31
    assert sum(x['new'] for x in entries)==74
    assert all(x['glyph_id']>0 for x in entries)
    for x in entries:
        cp=int(x['codepoint'][2:],16)
        assert x['glyph']==font.getBestCmap()[cp]
        if 'CYRILLIC' in x['name']:assert x['has_ink']
    with Image.open(ROOT/'specimen/all-characters.png') as image:
        assert image.size==(64*64+80,math.ceil(len(cps)/64)*68+126)
        image.verify()
    for page in data['pages']:
        with Image.open(ROOT/'specimen/pages'/page['file']) as image:image.verify()

def test_release_package_includes_license_and_exact_font():
    with zipfile.ZipFile(ROOT/'build/TalynBrush-v0.1.0.zip') as archive:
        prefix='TalynBrush-v0.1.0/'
        for path in ['OFL.txt','FONTLOG.txt','docs/OFL-FAQ.txt','fonts/TalynBrush-Regular.ttf','fonts/TalynBrush-Regular.woff2']:
            assert archive.read(prefix+path)==(ROOT/path).read_bytes()
        assert not any('NanumBrushScript-Regular.ttf' in p for p in archive.namelist())

def test_site_has_no_missing_local_links():
    from html.parser import HTMLParser
    from urllib.parse import urlsplit
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for key,value in attrs:
                if key in ('href','src'):
                    p=urlsplit(value)
                    if not p.scheme and p.path:
                        assert (ROOT/'site'/p.path).exists(), value
    Links().feed((ROOT/'site/index.html').read_text())

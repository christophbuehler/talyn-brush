"""Release acceptance tests. No system-font fallback is used in these checks."""
from pathlib import Path
import hashlib
import json
import unicodedata
import freetype
import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT/'fonts/TalynBrush-Regular.ttf'
UPSTREAM = ROOT/'upstream/NanumBrushScript-Regular.ttf'
# Deliberately independent of the construction source: the 35-letter alphabet.
UPPER = 'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЩЪЫЬЭЮЯ'
LOWER = 'абвгдеёжзийклмноөпрстуүфхцчшщъыьэюя'
GERMAN = 'ÄÖÜäöüßẞ'

@pytest.fixture(scope='module')
def font(): return TTFont(FONT)

@pytest.fixture(scope='module')
def original(): return TTFont(UPSTREAM)

def shape(text, features=None):
    f=hb.Font(hb.Face(FONT.read_bytes()));f.scale=(1000,1000)
    b=hb.Buffer();b.add_str(text);b.guess_segment_properties();b.language='mn'
    hb.shape(f,b,features)
    return [(i.codepoint,p.x_advance,p.x_offset,p.y_offset) for i,p in zip(b.glyph_infos,b.glyph_positions)]

def test_upstream_hash_and_license():
    assert hashlib.sha256(UPSTREAM.read_bytes()).hexdigest() == '98e3c5323f813ff6a61486af27aa49073262686bf336eacb77b024fa624254bf'
    original=(ROOT/'upstream/OFL.txt').read_text()
    derived=(ROOT/'OFL.txt').read_text()
    assert original.split('PREAMBLE')[1] == derived.split('PREAMBLE')[1]
    assert original.split('This Font Software')[0].strip() in derived
    assert 'Cyrillic and German extensions and build tooling copyright (c) 2026 Christoph Bühler.' in derived


def test_original_characters_and_every_original_glyph_preserved(font, original):
    assert font.getGlyphOrder()[:len(original.getGlyphOrder())] == original.getGlyphOrder()
    for cp,gn in original.getBestCmap().items(): assert font.getBestCmap()[cp] == gn
    for gn in original.getGlyphOrder():
        assert font['glyf'][gn].compile(font['glyf']) == original['glyf'][gn].compile(original['glyf']), gn
        assert font['hmtx'][gn] == original['hmtx'][gn], gn
    assert font['GSUB'].compile(font) == original['GSUB'].compile(original)
    for table in ('fpgm','prep','cvt '): assert font[table].compile(font) == original[table].compile(original)


def test_complete_mongolian_alphabet(font):
    assert len(UPPER) == len(LOWER) == 35
    cmap=font.getBestCmap()
    for c in UPPER+LOWER:
        assert ord(c) in cmap, c
        g=font['glyf'][cmap[ord(c)]]
        assert g.numberOfContours > 0, c
        assert 200 <= font['hmtx'][cmap[ord(c)]][0] <= 700, c
        assert g.yMax <= font['OS/2'].usWinAscent, c
        assert -g.yMin <= font['OS/2'].usWinDescent, c
    assert len(cmap) == 11871
    for sub in font['cmap'].tables:
        if sub.isUnicode():
            for c in UPPER+LOWER: assert sub.cmap[ord(c)] == cmap[ord(c)]


def test_reserved_names_removed_from_every_primary_name(font):
    for n in font['name'].names:
        if n.nameID in (1,3,4,6,16,18,21):
            assert 'nanum' not in n.toUnicode().lower()
            assert 'talyn' in n.toUnicode().lower()
    assert font['name'].getDebugName(1) == 'Talyn Brush'
    assert font['name'].getDebugName(6) == 'TalynBrush-Regular'
    assert 'NHN Corporation' in font['name'].getDebugName(0)
    assert 'Reserved Font Name Nanum' in font['name'].getDebugName(13)
    assert font['name'].getDebugName(13) == (ROOT/'OFL.txt').read_text()
    assert 'trademark' in font['name'].getDebugName(7)
    assert font['OS/2'].fsType == 0
    assert font['OS/2'].ulUnicodeRange1 & (1 << 9)


@pytest.mark.parametrize('text',[
    UPPER,LOWER,'Монголын сайхан орон','Өглөөний нар, үдшийн салхи.',
    'Өвөл, хавар, зун, намар. Үүл, уул, ус.','Өө Оо Үү Уу Ёё Йй 10 000 ₮',
    'Съешь ещё этих мягких французских булок, да выпей чаю.',
    'Hello, Mongolia! 안녕하세요', 'Өдрөө тэмдэглээрэй',
    'Монгол сайхан шүү. Бб Ьь Пп Гг Шш Щщ Фф Жж Яя',
    GERMAN, 'Schöne Grüße aus Zürich! Äpfel, Öl und Übermut.', 'STRAẞE Straße groß süß',
])
def test_shaping_without_missing_glyphs(text):
    glyphs=shape(text)
    assert glyphs and all(g[0] != 0 for g in glyphs)
    assert sum(g[1] for g in glyphs) > 0


def test_normalized_forms_are_identical():
    text='ЁёЙй ёлка сайн ÄÖÜ äöü Schöne Grüße'
    assert shape(text) == shape(unicodedata.normalize('NFD',text))


def test_marks_have_zero_advance_and_actual_gpos_attachment(font):
    for c in '\u0306\u0308': assert font['hmtx'][font.getBestCmap()[ord(c)]][0] == 0
    # This pair has no precomposed codepoint, forcing mark positioning to run.
    positioned=shape('Н\u0308')
    without_mark=shape('Н\u0308',{'mark':False})
    assert len(positioned)==2 and positioned[1][1]==0
    assert positioned[1][3] > 400
    assert positioned != without_mark


def test_cyrillic_kerning_is_active():
    assert sum(x[1] for x in shape('ТА')) < sum(x[1] for x in shape('ТА',{'kern':False}))


@pytest.mark.parametrize('size',[24,48,96])
def test_all_new_letters_have_distinct_raster_forms(size):
    face=freetype.Face(str(FONT));face.set_pixel_sizes(0,size)
    def raster(c):
        face.load_char(c,freetype.FT_LOAD_RENDER)
        b=face.glyph.bitmap
        assert b.width and b.rows and any(b.buffer), c
        return b.width,b.rows,bytes(b.buffer)
    for c in UPPER+LOWER+GERMAN: raster(c)
    for a,b in [('О','Ө'),('о','ө'),('У','Ү'),('у','ү'),('И','Й'),('и','й'),('Е','Ё'),('е','ё'),('Б','Ь'),('б','ь'),('Ш','Щ'),('ш','щ'),('П','Г'),('п','г'),('A','Ä'),('a','ä'),('O','Ö'),('o','ö'),('U','Ü'),('u','ü'),('B','ẞ'),('b','ß'),('ß','ẞ')]:
        assert raster(a) != raster(b), (a,b)


def test_every_encoded_glyph_loads_in_freetype(font,original):
    face=freetype.Face(str(FONT));face.set_pixel_sizes(0,40)
    source=freetype.Face(str(UPSTREAM));source.set_pixel_sizes(0,40)
    for cp in font.getBestCmap():
        assert face.get_char_index(cp) != 0
        face.load_char(chr(cp),freetype.FT_LOAD_RENDER)
        if not any(face.glyph.bitmap.buffer):
            # Only preserve blank glyphs that were already blank upstream.
            if cp == 0xA0: continue
            assert cp in original.getBestCmap(), hex(cp)
            source.load_char(chr(cp),freetype.FT_LOAD_RENDER)
            assert not any(source.glyph.bitmap.buffer), hex(cp)


def test_woff2_matches_ttf(font):
    web=TTFont(ROOT/'fonts/TalynBrush-Regular.woff2')
    assert web.getBestCmap() == font.getBestCmap()
    assert web['hmtx'].metrics == font['hmtx'].metrics
    for c in UPPER+LOWER+GERMAN:
        gn=font.getBestCmap()[ord(c)]
        p,q=RecordingPen(),RecordingPen()
        font.getGlyphSet()[gn].draw(p);web.getGlyphSet()[gn].draw(q)
        assert p.value == q.value
    assert web['name'].getDebugName(13) == font['name'].getDebugName(13)


def test_manifest_checksums():
    manifest=json.loads((ROOT/'fonts/manifest.json').read_text())
    for filename,sha in manifest['files'].items():
        assert hashlib.sha256((ROOT/'fonts'/filename).read_bytes()).hexdigest() == sha


def test_joined_strokes_and_open_counters(font):
    # Mirrors used to cancel overlapping strokes, cutting hairline gaps through
    # stems and joins. Count outer contours and enclosed counters independently
    # of how the recipe assembles them. These are single connected bodies.
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.recordingPen import RecordingPen
    expected_holes={**dict.fromkeys('ГгПпЖжШшЩщЦцЧч',0),
                    **dict.fromkeys('ЬьЮюя',1), **dict.fromkeys('ӨөФф',2)}
    gs=font.getGlyphSet();cmap=font.getBestCmap()
    for char,holes in expected_holes.items():
        recording=RecordingPen();gs[cmap[ord(char)]].draw(recording)
        areas=[];pen=AreaPen(gs)
        for op,points in recording.value:
            getattr(pen,op)(*points)
            if op=='closePath':
                areas.append(pen.value);pen=AreaPen(gs)
        # TrueType outer contours run clockwise, counter contours anticlockwise.
        assert sum(a<0 for a in areas)==1, (char,areas)
        assert sum(a>0 for a in areas)==holes, (char,areas)


def test_german_letters_and_umlaut_metrics(font,original):
    cmap=font.getBestCmap();source=original.getBestCmap()
    for char in GERMAN:
        assert ord(char) in cmap
        glyph=font['glyf'][cmap[ord(char)]]
        assert glyph.numberOfContours>0
        assert glyph.yMax<=font['OS/2'].usWinAscent
        for sub in font['cmap'].tables:
            if sub.isUnicode(): assert sub.cmap[ord(char)]==cmap[ord(char)]
    for char,base in zip('ÄÖÜäöü','AOUaou'):
        accent=font['glyf'][cmap[ord(char)]];body=original['glyf'][source[ord(base)]]
        assert font['hmtx'][cmap[ord(char)]][0]==original['hmtx'][source[ord(base)]][0]
        # Two separate dots above the intact base, with room for the accent.
        assert accent.numberOfContours==body.numberOfContours+2
        assert accent.yMax>body.yMax+65
    assert shape('ÄÖÜäöü')==shape(unicodedata.normalize('NFD','ÄÖÜäöü'))


def test_latin_diaeresis_attachment_without_precomposition():
    # Force the decomposed shaping path by removing precomposed alternatives
    # from an in-memory test font; ordinary NFC tests alone would bypass GPOS.
    from io import BytesIO
    f=TTFont(FONT)
    for sub in f['cmap'].tables:
        for char in 'ÄÖÜäöü': sub.cmap.pop(ord(char),None)
    data=BytesIO();f.save(data)
    shaper=hb.Font(hb.Face(data.getvalue()));shaper.scale=(1000,1000)
    expected={'A':(246,595),'O':(204,445),'U':(229,480),
              'a':(167,427),'o':(147,356),'u':(175,366)}
    for base,(x,y) in expected.items():
        buf=hb.Buffer();buf.add_str(base+'\u0308');buf.guess_segment_properties();buf.language='de'
        hb.shape(shaper,buf)
        assert len(buf.glyph_infos)==2
        a,mark=buf.glyph_positions
        assert mark.x_advance==0
        assert (a.x_advance+mark.x_offset,mark.y_offset)==(x,y)


def test_added_strokes_keep_the_source_pen_weight():
    # Revision 0.400: strokes may be stretched along their length but never
    # squeezed across their thickness. The lightest regular source stroke (o)
    # has a median thickness of about 51 units; thin flags and crossbars in
    # 0.300 measured 25-35. Rasterise at 1 px per unit and take the median
    # run length across vertical and across horizontal strokes.
    import re
    from statistics import median
    from PIL import Image
    face=freetype.Face(str(FONT))
    def raster(f,c,size):
        f.set_pixel_sizes(0,size);f.load_char(c,freetype.FT_LOAD_RENDER|freetype.FT_LOAD_NO_HINTING)
        b=f.glyph.bitmap
        return Image.frombytes('L',(b.width,b.rows),bytes(b.buffer),'raw','L',b.pitch).point(lambda v:255 if v>127 else 0)
    # Letters that reuse an original outline unchanged (T, for instance, has
    # the source's own 32-unit stem) are the source's business, not ours.
    source=freetype.Face(str(UPSTREAM))
    native={raster(source,chr(cp),200).tobytes() for cp in range(0x41,0x7B)}
    def runs(image):
        data=image.tobytes();width=image.width
        return [len(m) for y in range(image.height)
                for m in re.findall(b'\\xff+',data[y*width:(y+1)*width])]
    for c in UPPER+LOWER+GERMAN:
        if raster(face,c,200).tobytes() in native: continue
        ink=raster(face,c,1000)
        across_vertical=median(runs(ink))
        across_horizontal=median(runs(ink.transpose(Image.Transpose.TRANSPOSE)))
        assert min(across_vertical,across_horizontal) >= 36, (c,across_vertical,across_horizontal)

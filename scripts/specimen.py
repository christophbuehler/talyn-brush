#!/usr/bin/env python3
"""Render the complete cmap directly through FreeType, without fallback fonts."""
from pathlib import Path
import json
import math
import unicodedata
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import freetype
import uharfbuzz as hb
from sources.cyrillic import UPPER, LOWER

ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'fonts/TalynBrush-Regular.ttf'
OUT=ROOT/'specimen'
INK='#162ECA'; TEXT='#172660'; QUIET='#536078'; WASH='#F1F4FF'

def label(size=16): return ImageFont.load_default(size=size)
def draw_text(image, xy, text, size):
    """Use the same HarfBuzz + FreeType path on every platform."""
    face=freetype.Face(str(FONT));face.set_pixel_sizes(0,size)
    font=hb.Font(hb.Face(FONT.read_bytes()));font.scale=(1000,1000)
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();buf.language='mn'
    hb.shape(font,buf)
    x,y=xy;y+=size*.63
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        if info.codepoint==0: raise ValueError(f'Missing glyph in proof: {text}')
        face.load_glyph(info.codepoint,freetype.FT_LOAD_RENDER)
        b=face.glyph.bitmap
        if b.width and b.rows:
            mask=Image.frombytes('L',(b.width,b.rows),bytes(b.buffer),'raw','L',b.pitch)
            image.paste(INK,(round(x+pos.x_offset*size/1000+face.glyph.bitmap_left),
                              round(y-pos.y_offset*size/1000-face.glyph.bitmap_top)),mask)
        x+=pos.x_advance*size/1000
def save(image,path):
    # Indexed PNG keeps the full, very tall atlas practical to download.
    image.convert('P',palette=Image.Palette.ADAPTIVE,colors=96).save(path,optimize=True)

def heading(draw,title,subtitle,width):
    draw.text((40,24),title,font=label(30),fill=TEXT)
    draw.text((40,65),subtitle,font=label(15),fill=QUIET)

def render():
    OUT.mkdir(exist_ok=True);(OUT/'pages').mkdir(exist_ok=True)
    font=TTFont(FONT);cmap=font.getBestCmap(); cps=sorted(cmap)
    original=TTFont(ROOT/'upstream/NanumBrushScript-Regular.ttf').getBestCmap()
    face=freetype.Face(str(FONT));face.set_pixel_sizes(0,48)
    tiles={};manifest=[]
    for cp in cps:
        face.load_char(chr(cp),freetype.FT_LOAD_RENDER)
        b=face.glyph.bitmap
        tile=None
        if b.width and b.rows:
            tile=Image.frombytes('L',(b.width,b.rows),bytes(b.buffer),'raw','L',b.pitch)
        tiles[cp]=tile
        manifest.append({'codepoint':f'U+{cp:04X}','character':chr(cp),
                         'name':unicodedata.name(chr(cp),'UNNAMED'),
                         'glyph':cmap[cp],'glyph_id':face.get_char_index(cp),
                         'new':cp not in original,'has_ink':bool(tile and tile.getbbox())})
    def sheet(items,cols,cw,ch,title,subtitle):
        im=Image.new('RGB',(cols*cw+80,math.ceil(len(items)/cols)*ch+126),'white')
        d=ImageDraw.Draw(im);heading(d,title,subtitle,im.width)
        for i,cp in enumerate(items):
            x=40+(i%cols)*cw;y=110+(i//cols)*ch
            if cp not in original:d.rectangle((x,y,x+cw-2,y+ch-2),fill=WASH)
            tile=tiles[cp]
            if tile is not None:
                tile=tile.copy();tile.thumbnail((cw-12,ch-24),Image.Resampling.LANCZOS)
                im.paste(INK,(x+(cw-tile.width)//2,y+4+(ch-25-tile.height)//2),tile)
            else:
                d.text((x+cw/2,y+ch/2-13),'space',font=label(9),fill=QUIET,anchor='mm')
            d.text((x+cw/2,y+ch-13),f'{cp:04X}',font=label(10),fill=QUIET,anchor='mm')
        return im
    save(sheet(cps,64,64,68,'Talyn Brush / Complete character set',
               f'{len(cps):,} Unicode mappings. Every glyph rendered from the built font. Pale blue = new. Labels are hexadecimal codepoints.'), OUT/'all-characters.png')
    pages=[]
    for i in range(0,len(cps),384):
        part=cps[i:i+384];filename=f'charset-{i//384+1:02d}.png'
        save(sheet(part,24,80,82,f'Talyn Brush / Character set {i//384+1:02d}',
                   f'U+{part[0]:04X} to U+{part[-1]:04X} / {len(part)} mappings. Pale blue = added to the original font.'),OUT/'pages'/filename)
        pages.append({'file':filename,'first':f'U+{part[0]:04X}','last':f'U+{part[-1]:04X}','count':len(part)})
    (OUT/'coverage.json').write_text(json.dumps({'count':len(cps),'renderer':'FreeType; direct character mapping; no fallback',
                                               'pages':pages,'characters':manifest},ensure_ascii=False,indent=2)+'\n')
    (OUT/'charset.txt').write_text('\n'.join(f"{m['codepoint']}\t{m['character']}\t{m['name']}" for m in manifest)+'\n')
    im=Image.new('RGB',(1680,1260),'white');d=ImageDraw.Draw(im)
    heading(d,'Talyn Brush / Mongolian Cyrillic','35 letters, both cases. Original Latin proportions, new Cyrillic outlines. Preview 0.400.',1680)
    for i,(upper,lower) in enumerate(zip(UPPER,LOWER)):
        x=45+(i%7)*231;y=135+(i//7)*190
        if upper in 'ӨҮ':d.rectangle((x-5,y-4,x+211,y+168),fill=WASH)
        draw_text(im,(x+12,y+10),upper+lower,154)
        d.text((x+12,y+145),f'U+{ord(upper):04X} / U+{ord(lower):04X}',font=label(15),fill=QUIET)
    draw_text(im,(50,1134),'Өө Оо    Үү Уу    Ии Йй    Ее Ёё    10 000 ₮',75)
    d.text((50,1220),'Modern Cyrillic only. Traditional vertical Mongolian is outside this release.',font=label(17),fill=QUIET)
    save(im,OUT/'cyrillic.png')
    im=Image.new('RGB',(1680,1100),'white');d=ImageDraw.Draw(im)
    d.text((70,46),'Talyn Brush',font=label(30),fill=TEXT)
    d.text((70,97),'An open brush font for Mongolian Cyrillic',font=label(19),fill=QUIET)
    draw_text(im,(64,188),'Монголын сайхан орон',175)
    draw_text(im,(70,380),'Өглөөний нар, үдшийн салхи.',116)
    draw_text(im,(70,555),'Өө Үү',250)
    draw_text(im,(710,580),'Аа Бб Вв Гг Дд Ее Ёё Жж Зз',72)
    draw_text(im,(710,685),'Ии Йй Кк Лл Мм Нн Оо Өө Пп',72)
    draw_text(im,(70,892),'Hello, Mongolia!   안녕하세요',105)
    d.text((70,1044),'11,871 characters  /  TTF + WOFF2  /  SIL Open Font License 1.1',font=label(18),fill=QUIET)
    save(im,OUT/'preview.png')
    word_proof()
    german_proof()
    print(f'Rendered all {len(cps):,} mappings, {len(pages)} detail sheets, and Cyrillic proofs.')

def word_proof():
    """Phrase rhythm, recognizability and joined outlines at display sizes."""
    im=Image.new('RGB',(1800,1600),'white');d=ImageDraw.Draw(im)
    heading(d,'Talyn Brush / Handwritten Cyrillic',
            'Revision 0.400. Full-weight brush strokes throughout, cursive lowercase, and the unchanged original Latin for comparison.',1800)
    for y,text,size in [(150,'Өдрөө тэмдэглээрэй',190),
                        (350,'Монголын сайхан орон',162),
                        (535,'Өглөөний нар, үдшийн салхи.',132),
                        (710,'Hello, Mongolia!  a b d g m n u',125),
                        (890,'Өө Оо  Үү Уу  Ии Йй  Ее Ёё',140),
                        (1060,'Бб Ьь  Пп Гг  Шш Щщ  Фф Жж Яя',125)]:
        draw_text(im,(48,y),text,size)
    d.line((50,1260,1750,1260),fill=WASH,width=2)
    phrase='Өвөл, хавар, зун, намар. Үүл, уул, ус.'
    for y,size in [(1290,96),(1410,48),(1510,24)]:
        d.text((50,y+12),f'{size} px',font=label(17),fill=QUIET)
        draw_text(im,(170,y),phrase,size)
    save(im,OUT/'words.png')

def german_proof():
    im=Image.new('RGB',(1850,1430),'white');d=ImageDraw.Draw(im)
    heading(d,'Talyn Brush / German',
            'Revision 0.400. Original Latin letters, native brush dots, and a long-s sharp S. NFC and NFD are both tested.',1850)
    for y,text,size in [(120,'Ää  Öö  Üü  ß  ẞ',215),
                        (360,'Grüße aus Zürich!',182),
                        (555,'Schöne Grüße, süße Träume.',156),
                        (740,'Äpfel, Öl und Übermut.',155),
                        (950,'STRAẞE   Straße   groß   großartig',115)]:
        draw_text(im,(50,y),text,size)
    d.line((50,1090,1800,1090),fill=WASH,width=2)
    for y,size in [(1120,96),(1240,48),(1340,24)]:
        d.text((50,y+12),f'{size} px',font=label(17),fill=QUIET)
        draw_text(im,(170,y),'ÄÖÜ äöü ß ẞ  Schöne Grüße aus Zürich!',size)
    save(im,OUT/'german.png')

if __name__=='__main__':render()

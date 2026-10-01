#!/usr/bin/env python3
"""Build Talyn Brush from the byte-preserved upstream font and outline recipes."""
from pathlib import Path
import hashlib
import json
import sys
from io import StringIO
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from sources.cyrillic import recipes, UPPER, LOWER

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / 'upstream/NanumBrushScript-Regular.ttf'
UPSTREAM_SHA = '98e3c5323f813ff6a61486af27aa49073262686bf336eacb77b024fa624254bf'
FAMILY = 'Talyn Brush'
VERSION = '0.200'
EPOCH = 3873657600  # 2026-10-01 00:00:00 UTC, seconds since 1904-01-01

def name(c):
    return f'uni{ord(c):04X}'

def build():
    assert hashlib.sha256(UPSTREAM.read_bytes()).hexdigest() == UPSTREAM_SHA, 'Upstream source changed'
    font = TTFont(UPSTREAM, recalcTimestamp=False)
    cmap = font.getBestCmap().copy()
    gs = font.getGlyphSet()
    drawings = recipes()
    added = []
    out = ROOT / 'fonts'; out.mkdir(exist_ok=True)
    svgs = ROOT / 'sources/svg'; svgs.mkdir(exist_ok=True)
    for c, d in drawings.items():
        if d.width == 0 and c not in '\u0306\u0308':
            d.width = font['hmtx'][cmap[ord(d.parts[0][1])]][0]
        elif d.width == -1:
            _, child, (sx,_,_,_,dx,_) = d.parts[0]
            d.width = round(child.width*sx+dx)
        elif d.width == -2:
            d.width = d.parts[0][1].width
        if c == '\u00a0': d.width = font['hmtx'][cmap[0x20]][0]
        path = pathops.Path()
        d.draw(path.getPen(), gs, cmap)
        # Union overlapping brush strokes, preserving holes and correct winding.
        path.simplify(fix_winding=True, keep_starting_points=False, clockwise=True)
        pen = TTGlyphPen(None)
        path.draw(Cu2QuPen(pen, max_err=.35, reverse_direction=False))
        glyph = pen.glyph()
        glyph.recalcBounds(font['glyf'])
        gn = name(c)
        font['glyf'][gn] = glyph
        font['hmtx'][gn] = (d.width, getattr(glyph, 'xMin', 0))
        for subtable in font['cmap'].tables:
            if subtable.isUnicode() and subtable.format in (4,12): subtable.cmap[ord(c)] = gn
        added.append({'codepoint': f'U+{ord(c):04X}', 'character': c, 'glyph': gn,
                      'advance': d.width, 'construction': d.note})
        svgpen = SVGPathPen(None); glyph.draw(svgpen, font['glyf'])
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -650 {max(d.width+100,400)} 1000">'
               f'<title>U+{ord(c):04X} — {d.note}</title><g transform="scale(1,-1)">'
               f'<path d="{svgpen.getCommands()}"/></g></svg>\n')
        (svgs / f'{ord(c):04X}.svg').write_text(svg)
    font.setGlyphOrder(list(font['glyf'].glyphOrder))
    font['maxp'].numGlyphs = len(font.getGlyphOrder())
    license_text = (ROOT / 'OFL.txt').read_text()
    original_copyright = 'Copyright © 2010 NHN Corporation. All rights reserved. Font designed by Sandoll Communications Inc.'
    fields = {
        0: original_copyright + '\nCyrillic extensions and build tooling copyright (c) 2026 Christoph Bühler.',
        1:FAMILY, 2:'Regular', 3:f'{VERSION};TALY;TalynBrush-Regular',
        4:FAMILY+' Regular', 5:'Version '+VERSION, 6:'TalynBrush-Regular',
        8:'Talyn Brush Project',
        9:'Original: Kwak Doo-yul; Nicolas Noh; Sandoll Communications Inc. Cyrillic extension: Talyn Brush Project.',
        10:'An independent OFL derivative of Nanum Brush Script with Mongolian Cyrillic. Preview release; native-speaker review is welcome. No endorsement by the original authors.',
        11:'https://github.com/christophbuehler/talyn-brush',
        12:'https://github.com/christophbuehler/talyn-brush',
        13:license_text, 14:'https://openfontlicense.org',
        16:FAMILY, 17:'Regular', 18:FAMILY+' Regular',21:FAMILY,22:'Regular',
    }
    font['name'].names = [n for n in font['name'].names if n.nameID not in fields]
    for id_, value in fields.items():
        font['name'].setName(value,id_,3,1,0x409)
        # Mac Roman cannot encode the complete original RFN/license text reliably.
        if id_ in (1,2,3,4,5,6,16,17,18,21,22): font['name'].setName(value,id_,1,0,0)
    font['head'].fontRevision = float(VERSION)
    font['head'].created = font['head'].modified = EPOCH
    font['OS/2'].achVendID = 'TALY'
    font['OS/2'].usMaxContext = max(2, font['OS/2'].usMaxContext)
    font['OS/2'].recalcUnicodeRanges(font)
    font['OS/2'].ulCodePageRange1 |= 1 << 2  # Windows Cyrillic
    font['OS/2'].usWinAscent = max(font['OS/2'].usWinAscent, max(getattr(font['glyf'][x['glyph']], 'yMax', 0) for x in added))
    font['OS/2'].usWinDescent = max(font['OS/2'].usWinDescent, -min(getattr(font['glyf'][x['glyph']], 'yMin', 0) for x in added))
    fea = ['languagesystem DFLT dflt;', 'languagesystem cyrl dflt;', 'languagesystem latn dflt;',
           'markClass uni0306 <anchor 0 0> @TOP;', 'markClass uni0308 <anchor 0 0> @TOP;', 'feature mark {']
    anchors = {'Е':(244,533),'е':(183,402),'И':(230,507),'и':(178,387)}
    for c in UPPER+LOWER:
        glyph = font['glyf'][name(c)]
        x,y = anchors.get(c,(round(drawings[c].width/2),getattr(glyph,'yMax',350)+66))
        fea.append(f'  pos base {name(c)} <anchor {x} {y}> mark @TOP;')
    fea.extend(['} mark;', 'feature kern {'])
    for left,right,kern in [('Т','А',-30),('Т','О',-20),('Т','о',-25),('Т','а',-25),('Г','А',-22),('Г','о',-22),('У','А',-22),('У','о',-18),('А','Т',-20),('Л','Т',-15),('Т','Ө',-20),('Т','ө',-25)]:
        fea.append(f'  pos {name(left)} {name(right)} {kern};')
    fea.append('} kern;')
    feature_text = '\n'.join(fea)+'\n'
    (ROOT/'sources/features.fea').write_text(feature_text)
    # The upstream GPOS is empty; retain its original GSUB (full-width forms).
    addOpenTypeFeaturesFromString(font, feature_text, tables=['GPOS','GDEF'])
    ttf = out / 'TalynBrush-Regular.ttf'
    font.save(ttf)
    font.flavor = 'woff2'; font.save(out / 'TalynBrush-Regular.woff2')
    manifest = {'family':FAMILY,'version':VERSION,'upstream_sha256':UPSTREAM_SHA,
                'original_characters':len(cmap),'characters':len(font.getBestCmap()),
                'added_characters':added,'alphabet_upper':UPPER,'alphabet_lower':LOWER,
                'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('TalynBrush-Regular.*'))}}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'Built {FAMILY} {VERSION}: {len(cmap)} original + {len(added)} new = {len(font.getBestCmap())} characters')

if __name__ == '__main__': build()

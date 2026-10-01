"""Talyn Brush outline recipes. Coordinates are font units, y up.

All outline material comes from the archived Nanum Brush Script. The recipes
adapt actual brush contours, not strokes or outlines from a second typeface.
SPDX-License-Identifier: OFL-1.1
"""
from dataclasses import dataclass, field
import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen

UPPER = 'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЩЪЫЬЭЮЯ'
LOWER = UPPER.lower()
IDENTITY = (1, 0, 0, 1, 0, 0)
# Optical dot positions are shared by precomposed outlines and GPOS marks.
UMLAUTS = {'Ä':('A',246,595), 'Ö':('O',204,445), 'Ü':('U',229,480),
           'ä':('a',167,427), 'ö':('o',147,356), 'ü':('u',175,366)}


@dataclass
class Drawing:
    width: int
    parts: list = field(default_factory=list)
    note: str = ''

    def native(self, char, transform=IDENTITY):
        self.parts.append(('native', char, transform))
        return self

    def fragment(self, char, *, crop=None, fit=None, warp=None, transform=IDENTITY):
        """Crop a real brush stroke; optionally reshape or fit its bounding box.

        Crops are made before point edits and affine transforms. They allow
        joins inside overlapping strokes without manufacturing new terminals.
        """
        self.parts.append(('fragment', (char, crop, fit, warp), transform))
        return self

    def child(self, drawing, transform=IDENTITY):
        self.parts.append(('child', drawing, transform))
        return self

    def draw(self, pen, glyphset, cmap):
        result = pathops.Path()
        for kind, value, transform in self.parts:
            part = pathops.Path()
            out = TransformPen(part.getPen(), transform)
            if kind == 'native':
                glyphset[cmap[ord(value)]].draw(out)
            elif kind == 'child':
                value.draw(out, glyphset, cmap)
            else:
                char, crop, fit, warp = value
                shape = pathops.Path()
                glyphset[cmap[ord(char)]].draw(shape.getPen())
                if crop:
                    x0, y0, x1, y1 = crop
                    box = pathops.Path(); p = box.getPen()
                    p.moveTo((x0, y0)); p.lineTo((x1, y0))
                    p.lineTo((x1, y1)); p.lineTo((x0, y1)); p.closePath()
                    shape = pathops.op(shape, box, pathops.PathOp.INTERSECTION)
                if warp:
                    recording = RecordingPen(); shape.draw(recording)
                    shape = pathops.Path(); p = shape.getPen()
                    for operation, points in recording.value:
                        getattr(p, operation)(*(warp(x, y) for x, y in points))
                if fit:
                    x0, y0, x1, y1 = shape.bounds
                    left, bottom, right, top = fit
                    sx, sy = (right-left)/(x1-x0), (top-bottom)/(y1-y0)
                    out = TransformPen(out, (sx, 0, 0, sy, left-sx*x0, bottom-sy*y0))
                shape.draw(out)
            # Reflections reverse contour winding. A true union per component
            # prevents opposite-winding strokes from punching holes in joins.
            result = pathops.op(result, part, pathops.PathOp.UNION)
        result.draw(pen)


def dash(d, box):
    return d.fragment('-', fit=box)


def tail(d, x, y=10, height=150):
    # A comma's curved falling stroke gives the tail a proper brush finish.
    return d.fragment(',', fit=(x, y-height, x+49, y+24))


def short_b(x, y):
    # Preserve the bowl's weight; shorten only the ascending stem.
    return x, y if y <= 235 else 235 + (y-235)*.31


def recipes():
    g = {}
    def put(c, d, note):
        d.note = note; g[c] = d
        return d

    for c, latin in zip('АВЕКМНОРСТХ', 'ABEKMHOPCTX'):
        put(c, Drawing(0).native(latin), f'Original {latin} brush outline and advance.')
    for c, latin in zip('аеорсху', 'aeopcxy'):
        put(c, Drawing(0).native(latin), f'Original {latin} brush outline and advance.')

    # Capitals keep the source's uneven cap line and individual pen movement.
    d = Drawing(427).native('b',(1.19,0,0,.94,0,-3))
    dash(d,(62,410,378,463))
    put('Б', d, 'Round native b lower bowl, rising stem, and a full-width brush flag.')
    d = Drawing(387).fragment('I',fit=(64,-23,134,446))
    dash(d,(48,410,355,463))
    put('Г', d, 'Native tapered stem and original brush dash, joined at the upper left.')
    put('И', Drawing(480).fragment('N', fit=(35,-20,440,460), transform=(-1,0,0,1,475,0)),
        'Reversed native N: rising diagonal with the original brush modulation.')
    put('Л', Drawing(410).native('V',(1,0,0,-.97,5,407)),
        'Native V turned into an open el, retaining the irregular flowing legs.')
    d = Drawing(467).child(g['Л'], (1,0,0,1,20,0))
    dash(d,(24,-13,428,32));tail(d,27,18,112);tail(d,401,20,110)
    put('Д', d, 'Open el body with a low brushed base and two falling feet.')
    d = Drawing(625)
    d.fragment('K',crop=(163,-150,580,550),fit=(300,-38,592,445))
    d.fragment('K',crop=(163,-150,580,550),fit=(300,-38,592,445),transform=(-1,0,0,1,610,0))
    d.fragment('I',fit=(278,-28,339,469))
    put('Ж',d,'Two original K branches with a full-weight central stem; open six-arm structure.')
    put('З',Drawing(372).native('3',(1,0,0,.94,0,0)),
        'Open double bowl adapted from the source 3, with its angular pressure changes intact.')
    d=Drawing(476).fragment('I',fit=(49,-15,123,459))
    d.fragment('I',fit=(363,-20,428,476))
    dash(d,(51,425,429,477))
    put('П',d,'Two full native brush stems joined by a free upper flag.')
    put('У',Drawing(420).native('y',(1.22,0,0,1.24,0,52)),
        'Native y movement lifted to cap height, retaining its hooked descender.')
    put('Ү',Drawing(480).native('Y'),'Original Y skeleton with the required straight stem.')
    d=Drawing(490).native('d',(1.04,0,0,.96,0,9))
    d.native('p',(1.04,0,0,.96,130,-21))
    put('Ф',d,'Asymmetric original d and p bowls joined on one long central stem.')
    d=Drawing(457).native('u',(1.20,0,0,1.44,0,16));tail(d,353,6,140)
    put('Ц',d,'Open bowl and full-height right stem with a short curved descender.')
    d=Drawing(451).fragment('u',warp=lambda x,y:(x*1.24,y*1.41+17 if x>237 else y*.80+207))
    put('Ч',d,'High open bowl and long right stroke with original brush edges.')
    d=Drawing(616)
    for box in [(49,-10,112,448),(272,2,334,433),(509,-15,578,455)]:
        d.fragment('I',fit=box)
    dash(d,(64,-17,568,40))
    put('Ш',d,'Three full-height brush stems joined by a low, freely drawn baseline.')
    put('Щ',tail(Drawing(641).child(g['Ш']),548,17,147),
        'Three-stem sha with a curved right descender.')
    put('Ь',Drawing(405).native('b',(1.23,0,0,.90,0,-5)),
        'Original b bowl and rising stroke, adjusted to cap proportions.')
    put('Ъ',dash(Drawing(471).child(g['Ь'],(1,0,0,1,54,0)),(19,407,190,455)),
        'Soft-sign bowl with a broad left-projecting shoulder.')
    d=Drawing(567).child(g['Ь']).fragment('I',fit=(439,-17,515,434))
    put('Ы',d,'Soft-sign body and a detached brush stem with breathing room.')
    d=Drawing(425).native('C',(-1,0,0,1,425,0));dash(d,(116,171,348,212))
    put('Э',d,'Original C reversed, with an organic middle tongue.')
    d=Drawing(592).fragment('H',crop=(-100,-100,256,600),transform=(.9,0,0,1,0,0))
    d.native('O',(1,0,0,1,184,25));dash(d,(133,201,258,240))
    put('Ю',d,'Original H entry and O bowl, joined at their optical middle.')
    put('Я',Drawing(532).native('R',(-.91,0,0,1,512,0)),
        'Reversed native R, with a broad bowl and freely falling diagonal leg.')

    # Lowercase is genuinely handwritten: n / u / m structures for п / и / т.
    # These are standard cursive Cyrillic skeletons, not font fallback.
    for c,latin in [('п','n'),('и','u'),('т','m'),('д','g')]:
        put(c,Drawing(0).native(latin),f'Handwritten {c} using the original {latin} brush skeleton at full stroke weight.')
    put('к',Drawing(403).fragment('k',warp=lambda x,y:(x,y if y<=285 else 285+(y-285)*.23)),
        'Original k branches and stem, with the ascender lowered to Cyrillic x-height.')
    put('л',Drawing(318).native('v',(1.08,0,0,-.94,1,288)),
        'Open handwritten el with curved, unequal legs adapted from native v.')
    put('м',Drawing(438).native('w',(.81,0,0,-.83,8,280)),
        'Flowing em with a deep central join and curved exterior strokes.')
    put('н',Drawing(351).native('H',(.75,0,0,.66,0,-2)),
        'Short en with the original H diagonal cross stroke and uneven stems.')
    put('г',Drawing(284).child(g['Г'],(.72,0,-.07,.67,22,0)),
        'Open handwritten ge with a flowing native flag and tapered downstroke.')
    d=Drawing(351).fragment('b',warp=lambda x,y:(x+max(0,y-290)*.28,y*.93))
    dash(d,(104,427,321,479))
    put('б',d,'Full-weight round bowl with a rising, right-turning flag.')
    d=Drawing(333).native('b').native('o',(.68,0,0,.64,48,284))
    put('в',d,'Ascending handwritten ve, with a small upper loop and generous lower bowl.')
    put('ж',Drawing(478).child(g['Ж'],(.76,0,0,.71,0,0)),
        'Six clear arms adapted from the native K branches, balanced at lowercase height.')
    put('з',Drawing(294).native('3',(.78,0,0,.69,0,0)),
        'Two unequal, open bowls with the source digit’s lively brush modulation.')
    put('ү',Drawing(344).fragment('Y',warp=lambda x,y:(x*.70, y-80 if y<=150 else (y-150)*.72+70)),
        'Native Y fork at x-height, with a long straight falling stem distinct from у.')
    d=Drawing(451).native('d',(.96,0,0,.90,0,0)).native('p',(.96,0,0,.90,120,-29))
    put('ф',d,'Asymmetric d and p bowls meet on one stem, with both ascender and descender.')
    put('ц',tail(Drawing(371).native('u'),287,7,131),
        'Rounded cursive tse with a compact right descender.')
    d=Drawing(336).fragment('u',crop=(-100,-100,241,500),transform=(1,0,0,.52,0,145))
    d.fragment('u',crop=(237,-100,400,500))
    put('ч',d,'High rounded bowl and long right stroke; retains native u brush weight.')
    put('ш',Drawing(548).native('u').native('u',(1,0,0,1,217,2)),
        'Two rounded troughs and three upright strokes sharing the native u rhythm.')
    put('щ',tail(Drawing(569).child(g['ш']),506,7,133),
        'Handwritten sha with a compact, clearly visible right descender.')
    put('ь',Drawing(319).fragment('b',warp=short_b),
        'Full-size original b bowl; only the ascender is lowered to x-height.')
    put('ъ',dash(Drawing(370).child(g['ь'],(1,0,0,1,47,0)),(18,282,157,328)),
        'Soft-sign bowl with an overhanging native brush shoulder.')
    d=Drawing(476).child(g['ь']).fragment('i',crop=(-100,-100,300,260),fit=(356,-14,427,315))
    put('ы',d,'Round soft-sign bowl and an undotted i stroke at full lowercase weight.')
    d=Drawing(314).native('c',(-1,0,0,1,314,0));dash(d,(79,122,250,157))
    put('э',d,'Native c reversed, with a tapered middle tongue and open apertures.')
    d=Drawing(463).fragment('i',crop=(-100,-100,300,260),fit=(40,-15,109,315))
    d.native('o',(1,0,0,1,153,0));dash(d,(83,124,219,162))
    put('ю',d,'Undotted i entry joined to the original o at full lowercase weight.')
    d=Drawing(357).fragment('p',warp=lambda x,y:(335-x, y if y>=30 else 30+(y-30)*.12))
    d.fragment('k',crop=(193,-50,440,153),fit=(46,-26,221,138),transform=(-1,0,0,1,254,0))
    put('я',d,'Full-weight upper bowl and right stem, with a falling left diagonal from native k.')

    for c,base,width,box in [('Ө','O',410,(65,139,342,175)),('ө','o',290,(48,119,252,149))]:
        put(c,dash(Drawing(width).native(base),box),
            'Original round bowl crossed by a native brush dash, with two open counters.')
    breve=Drawing(0).fragment('U',crop=(-100,-100,500,139),fit=(-86,-4,87,67))
    dots=Drawing(0)
    dots.fragment('i',crop=(-100,280,300,400),fit=(-79,-3,-36,44))
    dots.fragment('i',crop=(-100,280,300,400),fit=(35,1,81,48))
    put('\u0306',breve,'Zero-width breve adapted from the rounded bottom of native U.')
    put('\u0308',dots,'Two distinct original i brush dots, aligned at the attachment anchor.')
    for c,base,mark,center,height in [('Ё','Е',dots,244,533),('ё','е',dots,183,402),
                                      ('Й','И',breve,230,507),('й','и',breve,178,387)]:
        put(c,Drawing(-2).child(g[base]).child(mark,(1,0,0,1,center,height)),
            f'{base} with the matching original-brush diacritic and clear separation.')
    for c,(base,center,height) in UMLAUTS.items():
        put(c,Drawing(0).native(base).child(dots,(1,0,0,1,center,height)),
            f'Original Latin {base} with optically placed native brush dots; original advance.')
    d=Drawing(449).fragment('f',crop=(80,241,300,600))
    d.fragment('I',fit=(110,-45,182,294))
    d.fragment('s',warp=lambda x,y:(x-35*max(0,min(1,(y-140)/110)),y),fit=(192,-13,409,459))
    put('ß',d,'Long-s head and falling stroke joined to a native s; open lower bowl.')
    put('ẞ',Drawing(503).child(d,(1.13,0,0,.84,0,18)),
        'Broader capital sharp S with a lower cap-height roof, distinct from B and SS.')
    d=Drawing(490).native('T');dash(d,(97,155,350,187));dash(d,(99,66,351,99))
    put('₮',d,'Original T with two separate native brush dashes across the stem.')
    put('\u00a0',Drawing(250),'Nonbreaking space, same advance as upstream space.')
    return g

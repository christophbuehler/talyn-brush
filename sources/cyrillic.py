"""Talyn Brush outline recipes. Coordinates are font units, y up.

All outline material comes from the archived Nanum Brush Script. The recipes
adapt actual brush contours, not strokes or outlines from a second typeface.

Weight rule (revision 0.400): the source pen leaves strokes of roughly 55-70
units. A stroke may be stretched or shortened along its own length, cropped,
reflected, or moved, but it is never squeezed across its thickness. Stems are
therefore only scaled vertically and bars only horizontally; `fit` is reserved
for pieces whose proportions are deliberately changed (tails, marks).
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


def _polygon(points):
    path = pathops.Path(); p = path.getPen()
    p.moveTo(points[0])
    for point in points[1:]: p.lineTo(point)
    p.closePath()
    return path


def _box(x0, y0, x1, y1):
    return _polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


@dataclass
class Drawing:
    width: int
    parts: list = field(default_factory=list)
    note: str = ''

    def native(self, char, transform=IDENTITY):
        self.parts.append(('native', char, transform))
        return self

    def fragment(self, char, *, crop=None, cut=(), fit=None, warp=None, transform=IDENTITY):
        """Crop a real brush stroke; optionally reshape or fit its bounding box.

        `crop` keeps a rectangle (x0, y0, x1, y1); `cut` removes polygons given
        as point lists, which lets one stroke be separated from another along
        its own edge. Crops and cuts happen before point edits and affine
        transforms. They allow joins inside overlapping strokes without
        manufacturing new terminals.
        """
        self.parts.append(('fragment', (char, crop, tuple(cut), fit, warp), transform))
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
                char, crop, cut, fit, warp = value
                shape = pathops.Path()
                glyphset[cmap[ord(char)]].draw(shape.getPen())
                if crop:
                    shape = pathops.op(shape, _box(*crop), pathops.PathOp.INTERSECTION)
                for polygon in cut:
                    shape = pathops.op(shape, _polygon(polygon), pathops.PathOp.DIFFERENCE)
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


# --- Reusable strokes, each measured on the original outlines -------------
# Hyphen: a lens-shaped brush dash, x 59-478, centred on y 221, 67 units thick.
HYPHEN = (59, 478, 221)
# E middle bar, cropped where it leaves the stem: x 130-400, centred on y 220,
# about 60 units thick, blunt where it was cut and tapering to the right.
FLAG = (130, 400, 220)
# Ascender stem of l: x 56-173, y -6 to 496, 70 units thick, leaning like
# every stem in the source. Bottom centre x 135, top centre x 72.
# Stem of i without its dot: x 69-155, y -11 to 220, 70 units thick.


def bar(d, x0, x1, yc, sy=.9, mirror=False):
    """Hyphen stretched along its length only; sy keeps thickness within 90%."""
    left, right, mid = HYPHEN
    sx = (x1-x0)/(right-left)
    if mirror:
        return d.fragment('-', transform=(-sx, 0, 0, sy, x1+sx*left, yc-sy*mid))
    return d.fragment('-', transform=(sx, 0, 0, sy, x0-sx*left, yc-sy*mid))


def flag(d, x0, x1, yc, sy=1.0, mirror=False):
    """E's middle bar, blunt end at x0 (hidden inside a stem), tapering to x1."""
    left, right, mid = FLAG
    sx = (x1-x0)/(right-left)
    if mirror:
        return d.fragment('E', crop=(130, 165, 420, 290),
                          transform=(-sx, 0, 0, sy, x1+sx*left, yc-sy*mid))
    return d.fragment('E', crop=(130, 165, 420, 290),
                      transform=(sx, 0, 0, sy, x0-sx*left, yc-sy*mid))


def stem(d, x, bottom, top):
    """Ascender stem of l, scaled along its length only; x is the bottom centre."""
    sy = (top-bottom)/502
    return d.native('l', (1, 0, 0, sy, x-135, bottom+6*sy))


def short_stem(d, x, bottom=-11, top=290):
    """Dotless i stem for x-height letters; x is the bottom centre."""
    sy = (top-bottom)/231
    return d.fragment('i', crop=(-100, -100, 300, 262),
                      transform=(1, 0, 0, sy, x-104, bottom+11*sy))


def tail(d, x, y=10, height=150):
    # A comma's curved falling stroke gives the tail a proper brush finish.
    return d.fragment(',', fit=(x, y-height, x+49, y+24))


def short_b(x, y):
    # Preserve the bowl's weight; shorten only the ascending stem.
    return x, y if y <= 235 else 235 + (y-235)*.31


# The crossbar of A, removed along the edges of both legs so the brush legs
# keep their own contours. Leg edges are interpolated between y 150 and 230.
A_CUTS = [
    [(-60, 146), (80, 146), (98, 220), (-60, 220)],
    [(600, 146), (424, 146), (405, 220), (600, 220)],
    [(118, 146), (362, 146), (344, 220), (139, 220)],
]
# The crossbar of f, removed along both edges of the stem, leaves a long s.
F_BAR_CUT = [[(-60, 185), (123, 185), (107, 250), (-60, 250)],
             [(600, 185), (186, 185), (176, 250), (600, 250)]]
# The middle bar of F, removed along the right edge of the stem.
F_CUT = [[(600, 165), (176, 165), (166, 195), (161, 225), (157, 255), (153, 275), (600, 275)]]


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
    d = Drawing(427).native('b', (1.19, 0, 0, .94, 0, -3))
    flag(d, 70, 392, 440)
    put('Б', d, 'Round native b lower bowl and rising stem; the flag is the original E bar at full weight.')
    put('Г', Drawing(390).fragment('F', cut=F_CUT),
        'Original F with its middle bar removed along the stem: the same pen as E, F and T.')
    put('И', Drawing(480).fragment('N', fit=(35,-20,440,460), transform=(-1,0,0,1,475,0)),
        'Reversed native N: rising diagonal with the original brush modulation.')
    put('Л', Drawing(425).fragment('A', cut=A_CUTS, transform=(.9, 0, 0, .72, -5, 48)),
        'Original A without its crossbar: a bowed left leg with a brush foot and a longer right leg.')
    d = Drawing(480).fragment('A', cut=A_CUTS, transform=(.9, 0, 0, .66, 22, 93))
    bar(d, 24, 452, 12, sy=.95)
    for x in (62, 436):
        d.fragment('l', crop=(-100, -100, 400, 110), transform=(1, 0, 0, 1, x-135, -84))
    put('Д', d, 'Open A body on a brushed base, with the brush ends of two l stems as feet.')
    d = Drawing(625)
    d.fragment('K',crop=(163,-150,580,550),fit=(300,-38,592,445))
    d.fragment('K',crop=(163,-150,580,550),fit=(300,-38,592,445),transform=(-1,0,0,1,610,0))
    stem(d, 325, -28, 469)
    put('Ж',d,'Two original K branches with a full-weight central stem; open six-arm structure.')
    put('З',Drawing(372).native('3',(1,0,0,.94,0,0)),
        'Open double bowl adapted from the source 3, with its angular pressure changes intact.')
    d = Drawing(476); stem(d, 110, -15, 459); stem(d, 400, -20, 466)
    bar(d, 60, 440, 440, sy=.95)
    put('П',d,'Two full native l stems joined by a free upper brush bar.')
    put('У',Drawing(420).native('y',(1.22,0,0,1.24,0,52)),
        'Native y movement lifted to cap height, retaining its hooked descender.')
    put('Ү',Drawing(480).native('Y'),'Original Y skeleton with the required straight stem.')
    d=Drawing(490).native('d',(1.04,0,0,.96,0,9))
    d.native('p',(1.04,0,0,.96,130,-21))
    put('Ф',d,'Asymmetric original d and p bowls joined on one long central stem.')
    d=Drawing(462).native('U',(1,0,0,1.05,0,0)); tail(d,322,42,150)
    put('Ц',d,'Original U bowl, drawn to cap height, with a short curved descender.')
    d=Drawing(451).fragment('u',warp=lambda x,y:(x*1.24,y*1.41+17 if x>237 else y*.80+207))
    put('Ч',d,'High open bowl and long right stroke with original brush edges.')
    d=Drawing(616)
    for x, top in [(110, 452), (330, 440), (550, 458)]:
        stem(d, x, -12, top)
    bar(d, 60, 585, 18, sy=.95)
    put('Ш',d,'Three full-height l stems joined by a low, freely drawn brush base.')
    put('Щ',tail(Drawing(641).child(g['Ш']),565,17,147),
        'Three-stem sha with a curved right descender.')
    put('Ь',Drawing(405).native('b',(1.23,0,0,.90,0,-5)),
        'Original b bowl and rising stroke, adjusted to cap proportions.')
    d = Drawing(471).child(g['Ь'],(1,0,0,1,54,0))
    flag(d, 15, 190, 430, mirror=True)
    put('Ъ', d, 'Soft-sign bowl with a broad left-projecting shoulder cut from the E bar.')
    d=Drawing(567).child(g['Ь']); stem(d, 495, -17, 440)
    put('Ы',d,'Soft-sign body and a detached full-weight brush stem with breathing room.')
    d=Drawing(425).native('C',(-1,0,0,1,425,0)); flag(d, 125, 345, 200, sy=.9, mirror=True)
    put('Э',d,'Original C reversed, with a tongue cut from the E bar that tapers into the counter.')
    d=Drawing(592).fragment('H',crop=(-100,-100,256,600),transform=(.9,0,0,1,0,0))
    d.native('O',(1,0,0,1,184,25)); bar(d, 120, 265, 225, sy=.85)
    put('Ю',d,'Original H entry and O bowl, joined at their optical middle.')
    put('Я',Drawing(532).native('R',(-.91,0,0,1,512,0)),
        'Reversed native R, with a broad bowl and freely falling diagonal leg.')

    # Lowercase is genuinely handwritten: n / u / m structures for п / и / т.
    # These are standard cursive Cyrillic skeletons, not font fallback.
    for c,latin in [('п','n'),('и','u'),('т','m')]:
        put(c,Drawing(0).native(latin),f'Handwritten {c} using the original {latin} brush skeleton at full stroke weight.')
    put('д',Drawing(320).fragment('g',warp=lambda x,y:(x, y if y>=0 else y*.74)),
        'Handwritten д on the original g skeleton; the descender is shortened to sit with р.')
    d = Drawing(372); short_stem(d, 112, -11, 292)
    d.fragment('k', crop=(130,-100,500,500), transform=(1,0,0,.8,0,16))
    put('к',d,'Original k branches on a dotless i stem, the upper arm lowered to x-height.')
    put('л',Drawing(318).native('v',(-1.08,0,0,-.94,300,290)),
        'Native v turned through 180 degrees: a thin rising entry and a heavy falling right leg.')
    put('м',Drawing(438).native('w',(.81,0,0,-.83,8,280)),
        'Flowing em with a deep central join and curved exterior strokes.')
    d = Drawing(350); short_stem(d, 92, -11, 300); short_stem(d, 282, -4, 300)
    bar(d, 70, 300, 150, sy=.85)
    put('н', d, 'Short en from two dotless i stems and a brush crossbar at full weight.')
    d = Drawing(290); short_stem(d, 110, -11, 292); flag(d, 80, 285, 270, sy=.95)
    put('г',d,'Open handwritten ge: dotless i stem with the E bar as its flag, both at full weight.')
    d=Drawing(351).fragment('b',warp=lambda x,y:(x+max(0,y-290)*.28,y*.93))
    flag(d, 105, 325, 448)
    put('б',d,'Full-weight round bowl with a rising, right-turning brush flag.')
    put('в',Drawing(340).native('B',(.8,0,0,.66,8,0)),
        'Print-form ve from the original B, kept broad so its bowls stay open at x-height.')
    put('ж',Drawing(478).child(g['Ж'],(.76,0,0,.71,0,0)),
        'Six clear arms adapted from the native K branches, balanced at lowercase height.')
    put('з',Drawing(310).native('3',(.9,0,0,.74,-10,-10)),
        'Two unequal, open bowls with the source digit’s lively brush modulation.')
    d=Drawing(292).native('v'); short_stem(d, 130, -225, 12)
    put('ү',d,'Native v fork at x-height on a straight dotless i stem, distinct from у.')
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
    d = Drawing(370).child(g['ь'],(1,0,0,1,47,0)); flag(d, 15, 150, 305, sy=.9, mirror=True)
    put('ъ', d, 'Soft-sign bowl with an overhanging brush shoulder cut from the E bar.')
    d=Drawing(476).child(g['ь']); short_stem(d, 400, -14, 315)
    put('ы',d,'Round soft-sign bowl and a dotless i stem at full lowercase weight.')
    d=Drawing(314).native('c',(-1,0,0,1,314,0)); flag(d, 85, 250, 140, sy=.85, mirror=True)
    put('э',d,'Native c reversed, with a tapered tongue cut from the E bar.')
    d=Drawing(463); short_stem(d, 85, -15, 300)
    d.native('o',(1,0,0,1,153,0)); bar(d, 75, 215, 142, sy=.8)
    put('ю',d,'Dotless i entry joined to the original o at full lowercase weight.')
    d=Drawing(357).fragment('p',warp=lambda x,y:(335-x, y if y>=30 else 30+(y-30)*.12))
    d.fragment('k',crop=(193,-50,440,153),fit=(46,-26,221,138),transform=(-1,0,0,1,254,0))
    put('я',d,'Full-weight upper bowl and right stem, with a falling left diagonal from native k.')

    for c,base,width,x0,x1,yc,sy in [('Ө','O',410,62,345,163,.9),('ө','o',290,42,252,138,.8)]:
        put(c,bar(Drawing(width).native(base),x0,x1,yc,sy),
            'Original round bowl crossed by the native brush dash at its full weight; two open counters.')
    breve=Drawing(0).fragment('U',crop=(-100,-100,500,139),fit=(-86,-4,87,67))
    dots=Drawing(0)
    dots.fragment('i',crop=(-100,280,300,400),fit=(-79,-3,-36,44))
    dots.fragment('i',crop=(-100,280,300,400),fit=(35,1,81,48))
    put('̆',breve,'Zero-width breve adapted from the rounded bottom of native U.')
    put('̈',dots,'Two distinct original i brush dots, aligned at the attachment anchor.')
    for c,base,mark,center,height in [('Ё','Е',dots,244,533),('ё','е',dots,183,402),
                                      ('Й','И',breve,230,507),('й','и',breve,178,387)]:
        put(c,Drawing(-2).child(g[base]).child(mark,(1,0,0,1,center,height)),
            f'{base} with the matching original-brush diacritic and clear separation.')
    for c,(base,center,height) in UMLAUTS.items():
        put(c,Drawing(0).native(base).child(dots,(1,0,0,1,center,height)),
            f'Original Latin {base} with optically placed native brush dots; original advance.')
    d=Drawing(440).fragment('f',cut=F_BAR_CUT).native('s',(.92,0,0,1.25,150,12))
    put('ß',d,'Original f without its crossbar as a long s, joined to the native s drawn up to the hook.')
    put('ẞ',Drawing(503).child(d,(1.13,0,0,.84,0,18)),
        'Broader capital sharp S with a lower cap-height roof, distinct from B and SS.')
    d=Drawing(490).native('T'); bar(d, 95, 352, 170, sy=.85); bar(d, 97, 353, 82, sy=.85)
    put('₮',d,'Original T with two separate native brush dashes across the stem.')
    put(' ',Drawing(250),'Nonbreaking space, same advance as upstream space.')
    return g

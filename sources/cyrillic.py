"""Editable outline recipes for Talyn Brush. Coordinates are font units, y up.

Native components refer only to the archived Nanum Brush Script. Brush paths
are hand-positioned pressure knots, not outlines from another Cyrillic font.
SPDX-License-Identifier: OFL-1.1
"""
from dataclasses import dataclass, field
from math import hypot
from fontTools.pens.transformPen import TransformPen

UPPER = 'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЩЪЫЬЭЮЯ'
LOWER = UPPER.lower()
IDENTITY = (1, 0, 0, 1, 0, 0)

@dataclass
class Drawing:
    width: int
    parts: list = field(default_factory=list)
    note: str = ''

    def native(self, char, transform=IDENTITY):
        self.parts.append(('native', char, transform))
        return self

    def brush(self, *knots):
        self.parts.append(('brush', knots, IDENTITY))
        return self

    def child(self, drawing, transform=IDENTITY):
        self.parts.append(('child', drawing, transform))
        return self

    def draw(self, pen, glyphset, cmap):
        for kind, value, transform in self.parts:
            out = TransformPen(pen, transform)
            if kind == 'native':
                glyphset[cmap[ord(value)]].draw(out)
            elif kind == 'child':
                value.draw(out, glyphset, cmap)
            else:
                ribbon(out, value)


def ribbon(pen, knots):
    """A smooth, asymmetric pressure ribbon through explicitly designed knots."""
    sides = [[], []]
    for i, (x, y, width) in enumerate(knots):
        before, after = knots[max(0, i-1)], knots[min(len(knots)-1, i+1)]
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        sides[0].append((x + nx*width*.53*1.28, y + ny*width*.53*1.28))
        sides[1].append((x - nx*width*.47*1.28, y - ny*width*.47*1.28))
    points = sides[0] + sides[1][::-1]
    # A closed Catmull-Rom spline gives editable knots with continuous edges.
    pen.moveTo(points[0])
    for i in range(len(points)):
        p0, p1, p2, p3 = [points[j % len(points)] for j in (i-1, i, i+1, i+2)]
        pen.curveTo((p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6),
                    (p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6), p2)
    pen.closePath()


def stem(d, x, top=445, bottom=-10, width=49, lean=18):
    # Preserve the actual upstream brush edge and taper. I spans x89..177,
    # y-28..490; skew follows the pen's modest rightward fall.
    sy = (top-bottom)/518
    sx = width/65
    shear = -lean/518
    return d.native('I', (sx, 0, shear, sy, x-sx*133-shear*490, bottom+28*sy))


def bar(d, left, right, y, width=40, rise=12):
    return d.brush((left, y-5, 5), (left+25, y+2, width*.85),
                   ((left+right)/2, y+rise, width), (right, y+rise+4, 3))


def recipes():
    g = {}
    def put(c, d, note):
        d.note = note
        g[c] = d
        return d
    # Shared Latin/Cyrillic skeletons retain the exact upstream outlines.
    for c, latin in zip('АВЕКМНОРСТХ', 'ABEKMHOPCTX'):
        put(c, Drawing(0).native(latin), f'Unchanged upstream {latin} outline and advance.')
    for c, latin in zip('аеорсху', 'aeopcxy'):
        put(c, Drawing(0).native(latin), f'Unchanged upstream {latin} outline and advance.')

    d = stem(Drawing(455), 97, 444, -10, 55)
    bar(d, 62, 404, 435, 42)
    d.brush((102,258,10),(260,262,40),(370,221,44),(367,132,38),(287,44,45),(117,-4,11))
    put('Б',d,'Open flag and generous lower bowl; native I stem.')
    put('Г',bar(stem(Drawing(400),85,435,-15,53),58,370,439,45),'Open right angle; long tapered flag.')
    d=Drawing(495)
    d.brush((77,28,6),(133,155,38),(189,306,42),(221,448,20))
    d.brush((221,448,12),(273,425,45),(324,202,57),(378,17,7))
    bar(d,31,445,10,46,17)
    d.brush((48,32,20),(45,-30,43),(30,-111,3))
    d.brush((423,35,26),(443,-24,44),(433,-102,3))
    put('Д',d,'Triangular handwritten de with two visible feet below the baseline.')

    d=stem(Drawing(620),293,440,-30,53,16)
    for pts in [((48,430,8),(137,349,40),(285,202,24)),
                ((536,439,7),(454,337,40),(305,204,24)),
                ((283,224,14),(144,103,52),(33,-20,3)),
                ((298,221,16),(430,105,57),(568,-31,3))]: d.brush(*pts)
    put('Ж',d,'Six-branched zhe with open joins and differentiated diagonals.')

    d=Drawing(420)
    d.brush((60,375,5),(152,441,33),(295,438,37),(340,365,42),
            (292,290,32),(184,229,22),(284,240,23),(363,160,49),
            (313,59,39),(178,-3,48),(52,25,6))
    put('З',d,'Two open bowls; deliberately not a substituted digit 3.')

    d=stem(stem(Drawing(470),76,442,-2,49),384,445,-22,52)
    d.brush((90,18,9),(153,108,44),(277,317,46),(374,442,5))
    put('И',d,'Ascending diagonal, distinct from Latin N.')
    d=Drawing(440)
    d.brush((35,-12,4),(103,149,39),(161,322,42),(202,445,19))
    d.brush((202,445,10),(242,397,36),(291,224,53),(371,-18,5))
    put('Л',d,'Pointed el with a light entry and a heavy descending right leg.')
    d=stem(stem(Drawing(470),85,448,-15,54),383,468,-25,52)
    bar(d,49,421,444,44)
    put('П',d,'Flat open counter and independently tapered stems.')

    d=Drawing(455)
    d.brush((35,444,7),(129,326,47),(231,208,38))
    d.brush((408,456,6),(333,316,38),(235,139,49),(148,-17,45),(54,-66,5))
    put('У',d,'Diagonal descending tail; explicitly distinct from straight Ү.')
    put('Ү',Drawing(480).native('Y'),'Native Y skeleton supplies the required straight stem.')
    # Lowercase straight u is not Latin y: the stem descends vertically.
    d=Drawing(340)
    d.brush((33,316,4),(94,234,35),(182,133,31))
    d.brush((304,315,5),(255,228,31),(183,132,21))
    d.brush((183,148,19),(185,16,39),(195,-148,4))
    put('ү',d,'Straight descender and fork, never the hooked Latin y / Cyrillic у.')

    d=Drawing(560).native('O',(1.37,0,0,.9,-1,62))
    stem(d,270,516,-103,49,10)
    put('Ф',d,'Oval bowl crossed by an extended native stem.')
    d=stem(stem(Drawing(465),81,442,8,48),365,444,3,49)
    bar(d,73,412,2,45,15)
    d.brush((399,29,14),(418,-44,46),(404,-126,3))
    put('Ц',d,'Open-topped tse, with a distinct right descender.')
    d=Drawing(454)
    d.brush((71,442,5),(69,322,47),(106,233,44),(216,232,35),(360,300,8))
    stem(d,363,451,-31,56)
    put('Ч',d,'Open upper bowl with a high joining stroke.')
    d=Drawing(620)
    for x,top,bottom,w in [(77,445,1,48),(286,434,17,49),(526,445,-5,52)]: stem(d,x,top,bottom,w)
    bar(d,69,568,1,47,12)
    put('Ш',d,'Three independently spaced native brush stems; flat baseline.')
    d=Drawing(641).child(g['Ш'])
    d.brush((559,28,20),(585,-40,46),(568,-125,3))
    put('Щ',d,'Sha construction with an unmistakable right descender.')
    d=stem(Drawing(406),84,444,-12,54)
    d.brush((98,250,6),(248,256,33),(337,198,47),(309,92,45),(220,21,44),(110,-6,7))
    put('Ь',d,'Lower bowl at mid-height, not the tall Latin b.')
    d=Drawing(485).child(g['Ь'],(1,0,0,1,67,0))
    bar(d,27,158,436,41,-4)
    put('Ъ',d,'Soft-sign bowl with a projecting upper-left shoulder.')
    d=Drawing(603).child(g['Ь'])
    stem(d,511,436,-19,54)
    put('Ы',d,'Soft-sign bowl and detached right stem, with open spacing.')
    d=Drawing(425).native('C',(-1,0,0,1,435,0))
    bar(d,86,364,194,37,10)
    put('Э',d,'Reversed native C with a tapered middle tongue.')
    d=Drawing(619).native('O',(1,0,0,1,206,0))
    stem(d,78,443,-18,53)
    bar(d,79,295,179,39,10)
    put('Ю',d,'Native O and I joined at optical middle height.')
    d=Drawing(475).native('R',(-1,0,0,1,475,0))
    put('Я',d,'Mirrored native R skeleton, the corresponding Cyrillic ya form.')
    for c,base in [('Ө','O'),('ө','o')]:
        d=Drawing(0).native(base)
        bar(d,61 if c=='Ө' else 49,344 if c=='Ө' else 250,154 if c=='Ө' else 126,33 if c=='Ө' else 27,8)
        put(c,d,'Native round outline plus a horizontal crossbar; no slash.')

    # Upright handwritten lowercase forms use cap skeletons, optical corrections,
    # and x-height proportions. This avoids ambiguous Latin cursive substitutes.
    lower_forms = {
        'в':('В',.72,.68,15,0), 'г':('Г',.74,.67,7,0),
        'д':('Д',.75,.69,0,0), 'ж':('Ж',.77,.72,0,0),
        'з':('З',.76,.71,0,0), 'и':('И',.76,.69,0,0),
        'к':('К',.72,.72,0,5), 'л':('Л',.76,.74,0,0),
        'м':('М',.81,.75,0,0), 'н':('Н',.75,.65,0,0),
        'п':('П',.76,.69,0,0), 'т':('Т',.76,.77,0,0),
        'ц':('Ц',.76,.70,0,0), 'ч':('Ч',.76,.70,0,0),
        'ш':('Ш',.80,.70,0,0), 'щ':('Щ',.80,.70,0,0),
        'ъ':('Ъ',.77,.70,0,0), 'ы':('Ы',.77,.70,0,0),
        'ь':('Ь',.78,.70,0,0), 'э':('Э',.76,.74,0,0),
        'ю':('Ю',.76,.76,0,0), 'я':('Я',.76,.73,0,0),
    }
    # Widths for native-based caps are resolved from the original hmtx by build.py.
    for c,(cap,sx,sy,dx,dy) in lower_forms.items():
        put(c,Drawing(-1).child(g[cap],(sx,0,0,sy,dx,dy)),f'Optically scaled upright {cap}; preserves recognizable Cyrillic skeleton.')
    d=Drawing(343).native('o',(1.03,0,0,1,10,0))
    d.brush((65,151,8),(64,280,34),(123,422,41),(216,465,39),(304,482,4))
    put('б',d,'Round lowercase bowl with a rising flag, distinct from ь and Latin b.')
    d=Drawing(453).native('o',(1.43,0,0,1.07,5,0))
    stem(d,213,446,-152,43,9)
    put('ф',d,'Lowercase bowl at x-height with ascender and descender.')

    breve=Drawing(0).brush((-88,69,4),(-61,14,23),(0,-4,31),(65,26,19),(91,71,3))
    dots=Drawing(0)
    for x,y in [(-58,17),(58,24)]:
        dots.brush((x-4,y+19,15),(x,y+3,39),(x+7,y-18,7))
    put('\u0306',breve,'Zero-width combining breve, centered at its attachment anchor.')
    put('\u0308',dots,'Zero-width combining diaeresis; two distinct brush touches.')
    for c,base,mark,center,height in [('Ё','Е',dots,244,533),('ё','е',dots,183,402),
                                      ('Й','И',breve,230,507),('й','и',breve,178,387)]:
        put(c,Drawing(-2).child(g[base]).child(mark,(1,0,0,1,center,height)),f'{base} plus matching brush diacritic, with clear separation.')
    d=Drawing(490).native('T')
    bar(d,94,356,166,29,22);bar(d,97,358,75,29,22)
    put('₮',d,'Tugrik sign with two separate bars across the native T stem.')
    put('\u00a0',Drawing(250),'Nonbreaking space, same advance as upstream space.')
    return g

# Letter design and review

Talyn Brush adds modern Mongolian Cyrillic to Nanum Brush Script. The source has no mapped Cyrillic letters. Outline construction is AI-assisted and inspected in rendered proofs; independent review by a native Mongolian type designer is still outstanding.

## Revision 0.200: a change of handwriting

The first preview relied too heavily on reduced capitals and smooth, constructed pressure ribbons. In words, the lowercase looked stiff beside the source's loose Latin brushwork. This revision changes the lowercase structure and rebuilds the added strokes from the actual original contours.

The handwritten forms of **и, п, т, д** use the source **u, n, m, g** movements at their original stroke weight. These are deliberate cursive Cyrillic skeletons. Lowercase **к** keeps the native branches but lowers the ascending stroke to Cyrillic x-height. **л** retains unequal curved legs; **м** has a deep central join; **ш** uses two rounded troughs with a shared middle stroke. **б** has a rising flag, while **в** has two loops and an ascender. A shortened **ь** keeps its bowl's original weight instead of compressing the whole letter.

Other letters need more than a Latin lookalike. The two bowls of **ф** meet on one ascending and descending stem. **ж** uses the native K's curved branches, with clear space around the central stroke. **я** combines a full-weight upper bowl with a falling left leg. **Өө** use the original O/o bowls and a thin horizontal brush dash, preserving two open counters. **Үү** have straight stems and stay distinct from **Уу** and their hooked tails.

All outline material comes from the archived Nanum font. Editable recipes crop, reshape, reflect, and combine actual source contours; no other typeface supplies glyphs or outline fragments. Each component is geometrically unioned before TrueType conversion. This matters when reflecting outlines: merely concatenating opposite-winding contours can punch holes through a join. Regression checks verify connected bodies and the intended number of counters in the affected forms.

## Revision 0.300: German

ÄÖÜ and äöü use the original AOU/aou bodies, unchanged advances, and two native i dots. Their accent positions are adjusted to each irregular body height and shared with the Latin GPOS anchors. Normalization tests compare NFC with base-plus-U+0308 sequences. The accents add two separate contours without changing the body's counters.

The sharp S combines a long-s head adapted from f (without its crossbar) with the original s movement. Its lower bowl stays open. The capital ẞ is broader and brought to cap height. It has its own Unicode mapping; no automatic substitution of SS is introduced. This follows the [Unicode description of ß's ligature structures and capital mapping](https://www.unicode.org/charts/nameslist/n_0080.html).

A [German proof](../specimen/german.png) covers all eight added characters, words such as “Grüße”, “Zürich” and “Straße”, and 24/48/96 px samples. Full Latin Extended coverage is not claimed.

## Revision 0.400: one pen for every letter

Review of the 0.300 proofs showed the construction's weak point. Several letters looked drawn with a different, finer pen: г and Г, the stems of П, Ш and Щ, and the crossbars of Ө, Э, Ю and the flags of Б and Ъ. The cause was mechanical. The recipes fitted a stroke into a bounding box, and when a tall stem was fitted into a narrow box or a dash into a flat one, the stroke was squeezed across its thickness. The source pen leaves strokes of roughly 55 to 70 units; г measured 27, Г 40, П and Ш 43 to 46, the ө crossbar 23.

The rule from 0.400 on: a stroke may be stretched or shortened along its own length, cropped, reflected or moved, but never scaled across its thickness. Stems are therefore only scaled vertically and bars only horizontally. Stems come from the original **l** (ascenders) and the dotless **i** (x-height); bars come from the hyphen (a lens-shaped dash, used for crossbars whose ends disappear into other strokes) and from the middle bar of **E** (blunt where it leaves a stem, tapering freely, used for flags). The recipe tool gained polygon cuts, so a stroke can be separated from a neighbouring one along its own edge instead of a rectangle.

That made better skeletons possible. **Г** is the original F with its middle bar cut away along the stem, so it carries the same heavy bar and lighter stem as E, F and T. **Л** and **Д** are the original A without its crossbar, keeping the bowed left leg and its brush foot; Д adds a brush base and the ends of two l stems as feet. **Ц** is drawn on the original U. **н** and **к** stand on dotless i stems, к keeping the native k branches. **ү** is the native v fork on a straight stem. **л** is the native v turned through 180 degrees, so the thin stroke is the rising entry and the heavy stroke the falling right leg, as in writing. **в** uses the print form from B, which stays legible at x-height. The **д** descender is shortened to sit with р. **ß** is the original f without its crossbar, a long s, joined to the native s drawn up to its hook.

A regression test now rasterises every added letter at one pixel per unit and rejects any letter whose median stroke thickness, across vertical or across horizontal strokes, falls below 36 units. Letters that reuse an original outline unchanged are exempt, since T's own 32-unit stem is the source's decision.

## Relationship to the original

The source varies its letter heights, pressure, terminals, proportions, and baseline. The revision follows those variations instead of imposing one uniform stroke or geometric grid. It remains in the original 1000-unit em. Shared skeletons such as А/A, В/B, Е/E, Н/H, О/O, Р/P, С/C, and Х/X use the original brush outlines.

All inherited glyphs, including their horizontal metrics, hinting, Unicode mappings and GSUB substitutions, remain byte-for-byte unchanged. Cyrillic advances are tuned to the individual forms. New letters are unhinted; this remains a display font for headings, invitations, and short text.

## Distinctions checked in proofs

| Pair | Design requirement |
| --- | --- |
| Оо / Өө | A horizontal crossbar, two open counters; no slash. |
| Уу / Үү | Hooked descending movement versus a straight stem. |
| Ии / Йй | Same body with a clearly separated breve. |
| Ее / Ёё | Same body with two separate brush dots. |
| Бб / Ьь | A projecting upper flag versus a plain ascending stroke. |
| Шш / Щщ | A visible right descender on Щщ. |
| Пп / Гг | A second full stroke on Пп; an open right side on Гг. |
| Дд / Лл | Capital Д has a base and feet; lowercase д descends below the baseline. |

Breve and diaeresis are zero-advance combining marks with GPOS anchors. Their outlines come from the native U bowl and i dots. Precomposed and decomposed Ё/Й strings are checked for identical HarfBuzz shaping. A small set of Cyrillic capital pairs is kerned.

## Proofs and limits

CI renders the complete built cmap, all 35 letters in both cases, and a [word proof](../specimen/words.png) with unchanged Latin alongside Cyrillic and samples at 24, 48, and 96 pixels. FreeType renders the actual font; HarfBuzz shapes the phrases. No system fallback is allowed in the image generator. Each revision is compared with the previous one using the same invitation phrases at the same size.

Coverage, contour, shaping, sanitization and reproducibility checks establish technical integrity. They do not establish cultural or typographic authority. The font remains a preview pending native-speaker and type-designer review. Traditional vertical Mongolian, all Cyrillic Extended languages, and alternative stylistic sets are outside this release's scope.

Use the [live type tester](https://christophbuehler.github.io/talyn-brush/) to review actual words. Useful feedback includes the text, character/codepoint, size, application, and a screenshot.

## References

- [Original Google Fonts specimen](https://fonts.google.com/specimen/Nanum+Brush+Script) and [upstream metadata](https://github.com/google/fonts/tree/main/ofl/nanumbrushscript).
- [Google Design: Scripting Cyrillic](https://design.google/library/scripting-cyrillic): handwritten Cyrillic development, the relationship to Latin brushwork, and the value of specialist review. Caveat and Bad Script were studied as visual references for Cyrillic skeletons; their outlines are not included.
- [Unicode CLDR 48 Mongolian exemplars](https://github.com/unicode-org/cldr/blob/release-48/common/main/mn.xml): modern Mongolian alphabet coverage. Auxiliary exemplars are not claimed.
- [Unicode Cyrillic chart](https://www.unicode.org/charts/PDF/U0400.pdf): U+04AE/U+04AF are straight U; U+04E8/U+04E9 are barred O.

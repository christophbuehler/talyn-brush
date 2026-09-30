# Letter design and review

The original font has no mapped Cyrillic letters. This extension draws a complete modern Mongolian Cyrillic alphabet, with no outlines imported from a second font. Construction was AI-assisted and reviewed in rendered proofs. It has not been independently reviewed by a native Mongolian type designer.

## Relationship to the original

The original is informal brush lettering: variable cap heights, triangular terminals, broad curves, irregular proportions, and little mechanical repetition. The extension works in the same 1000-unit em. Shared skeletons such as А/A, В/B, Е/E, Н/H, О/O, Р/P, С/C, and Х/X use original outlines. New stems adapt the source I; new branches and bowls use editable pressure knots that form smooth tapered outlines. Overlapping strokes are unioned before conversion to quadratic TrueType curves.

The lowercase mixes recognizable upright handwritten forms with the source's rounded Latin-compatible forms. Lowercase б has a rising flag; д has a triangular body and two feet; л has a pointed body; т uses the upright T-like skeleton. These are intentional forms, not accidental Latin fallback. New drawings follow the loose baseline and changing proportions rather than imposing a geometric grid on the source.

## Distinctions that must survive revisions

| Pair | Construction requirement |
| --- | --- |
| Оо / Өө | Өө retains the original round bowl and gains a horizontal bar, with both counters open. It must never look like Øø. |
| Уу / Үү | Уу has a descending tail; Үү has a straight stem. The uppercase Ү reuses the appropriate Y skeleton. Lowercase ү is separately drawn, not mapped to Latin y. |
| Ии / Йй | Same body; the breve sits above it with clear separation. |
| Ее / Ёё | Same body; two separate brush touches form the diaeresis. |
| Бб / Ьь | Б has an upper flag; б has a rising flag and round bowl. Ьь has only a lower bowl. |
| Шш / Щщ | Щщ adds a visible right descender. |
| Пп / Гг | Both stems of Пп reach its head stroke; Гг stays open on the right. |
| Дд / Лл | Дд has a base and two feet; Лл has neither. |

## Spacing and shaping

Inherited outlines and horizontal metrics are unchanged. New advances follow the original's proportional design. A small set of Cyrillic pairs is kerned, and breve/diaeresis are zero-advance marks with GPOS anchors. Precomposed and decomposed Ё/Й strings are checked for identical HarfBuzz shaping. The original GSUB full-width substitutions are preserved byte-for-byte.

New letters use unhinted outlines, while inherited hinting remains intact. The intended use is display lettering, headings, and short text. There are no Cyrillic cursive stylistic alternates or a claim of full support for every language that uses Cyrillic.

## Proofs and review status

The full atlas is generated from the built font's cmap rather than a manually curated sample. FreeType loads each character directly; HarfBuzz shapes the phrase proofs. Tests compare the critical pairs at 24, 48, and 96 pixels and verify that every added alphabetic character produces ink.

Visual review inspected the full alphabet, large pairs, Mongolian words, the original Latin alphabet beside the extension, and atlas sheets. An early pass had stems that were too light and a weak join in П; those were corrected before release. Tests establish coverage and rendering integrity. They do not establish cultural or typographic authority.

For review, use the [live type tester](https://christophbuehler.github.io/talyn-brush/) and [Cyrillic proof](../specimen/cyrillic.png). Report the actual word, character/codepoint, size, application, and a screenshot if possible. Native-speaker feedback should precede a stable 1.0 release.

## Sources

- [Original Google Fonts specimen](https://fonts.google.com/specimen/Nanum+Brush+Script) and [upstream project metadata](https://github.com/google/fonts/tree/main/ofl/nanumbrushscript).
- [Unicode CLDR 48 Mongolian exemplars](https://github.com/unicode-org/cldr/blob/release-48/common/main/mn.xml): modern Mongolian alphabet coverage. Auxiliary exemplars are not claimed.
- [Unicode Cyrillic chart](https://www.unicode.org/charts/PDF/U0400.pdf): U+04AE/U+04AF are straight U; U+04E8/U+04E9 are barred O.

The original TTF and the pressure-knot recipes, not any chart font, are the outline sources.

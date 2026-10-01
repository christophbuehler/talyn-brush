# Talyn Brush build plan

1. Archive and hash the exact user-supplied font and license. Audit Unicode coverage and name metadata. Research SIL OFL modification rules and Unicode's Mongolian repertoire.
2. Draw the 35-letter Mongolian Cyrillic alphabet in both cases (also covers the modern Russian alphabet). Preserve all upstream mappings, glyph outlines, advance widths, hinting and layout behavior. Add combining breve/diaeresis, nonbreaking space and the tugrik currency sign.
3. Reuse upstream outlines only where the letter skeleton is appropriate. Build the remaining forms with tapered, asymmetric brush outlines, matching the 1000-unit design space and informal Latin proportions. Keep Ө distinct from О and Ү distinct from У. Record glyph construction in editable source and design notes.
4. Build renamed TTF and WOFF2 distributions deterministically. Preserve attribution and reserved-name declarations, embed the OFL, and include a font log and license in every release.
5. Validate Unicode coverage, naming/license metadata, original-glyph preservation, contours, metrics, FreeType rendering, HarfBuzz shaping and normalization, and reproducible builds. Render every encoded character into a labeled atlas; produce a focused Cyrillic proof for visual inspection.
6. Publish the public GitHub repository, CI-generated specimens, GitHub Pages type tester, and a versioned release only after the release commit passes CI. Verify the published assets.

Scope: modern Mongolian Cyrillic. Traditional vertical Mongolian is a separate script and is not implemented. Automated and visual review cannot substitute for native-speaker/type-designer review; the first release is explicitly a preview.

## Specimen design

Palette: paper #FFFFFF; ink #162ECA; deep ink #172660; quiet text #536078; wash #F1F4FF.
Type: Talyn Brush for the writing itself; system sans-serif for controls and annotations. No outside font dependency.
Layout: a spacious, left-aligned brush specimen, an immediately editable Mongolian text field, then alphabet proofs and the complete atlas. The letters supply the visual identity. No decorative cards or animation.

    Talyn Brush                      Download / Source
    Монголын сайхан орон
    [editable specimen, generous writing area]
    [size] [Mongolian / Latin / Korean samples]
    Аа Бб Вв ... Өө ... Үү ...
    Full character atlas / license / design notes

Review: the bold element is the type itself. The page is a practical font proof and download surface; it does not need illustrative imagery, gradients, or dashboard chrome.

## Revision 0.200

1. Compare the invitation phrases against the first preview at equal sizes.
2. Replace miniature-cap lowercase with handwritten Cyrillic skeletons. Reuse the source's real brush contours; inspect joins, counters and pressure at large sizes.
3. Proof complete words, all 35 letter pairs, critical distinctions and small sizes. Add regression checks for the reflected-contour join failure.
4. Rebuild the full atlas and licensed package, run all release checks, and verify the deployed commit and versioned download after CI.

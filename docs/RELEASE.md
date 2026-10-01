Talyn Brush 0.400 redraws the Cyrillic and German additions at the original pen weight.

Review of the 0.300 proofs found that several constructed letters looked drawn with a different pen: г, Г, П, Ш and Щ had squeezed stems, and the flags and crossbars in Ө ө Э э Ю ю Б Ъ were thin, straight fitted dashes (г measured 27 units where the source pen leaves 55 to 70). This release fixes that at the root.

- Every stroke is now stretched only along its own length. Stems come from the original l and dotless i, bars from the hyphen and the middle bar of E, with no scaling across their thickness. A new regression test rasterises all 78 added letters and rejects any stroke thinner than the source pen.
- Г is the original F without its middle bar. Л and Д are the original A without its crossbar, with its bowed left leg and brush foot. Ц is drawn on the original U. н and к stand on dotless i stems; ү is a v fork on a straight stem; л is a rotated v with a thin entry and a heavy falling right leg.
- Ө ө carry a full-weight brush crossbar. Э э have a tongue that tapers into the counter. The д descender is shortened so it sits with р.
- ß is the original f without its crossbar, a long s, joined to the native s; the knotted head of 0.300 is gone. ẞ follows.
- в uses the print form from the original B, which stays legible at x-height.
- Every original glyph outline, metric, hint program and GSUB rule is preserved. The character count stays at 11,871.

[Try it](https://christophbuehler.github.io/talyn-brush/) · [Cyrillic word proof](https://christophbuehler.github.io/talyn-brush/specimen/words.png?v=0.400) · [German proof](https://christophbuehler.github.io/talyn-brush/specimen/german.png?v=0.400) · [Complete atlas](https://christophbuehler.github.io/talyn-brush/specimen/all-characters.png?v=0.400)

This remains a **preview**, with visual inspection and automated checks. Independent native Mongolian and type-designer review is welcome. Traditional vertical Mongolian and full Latin Extended coverage are outside this release's scope. No endorsement by the original font authors is implied.

Download the ZIP and verify it against `SHA256SUMS.txt`. Replace the previous installed TTF, or self-host the new WOFF2 with its license. The internal version is 0.400; the family remains Talyn Brush.

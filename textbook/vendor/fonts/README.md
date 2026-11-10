# Textbook fonts

`BookTitleSerif-600.ttf` is a compact Noto Serif SC subset at weight 600 for the title on the author frontispiece. Its internal family is `BookTitleSerif`. It is prepared by `prepare_author_fonts.py` and uses the Noto SIL Open Font License 1.1 included as `LICENSE.txt`. Latin words in that title use Georgia for natural proportional spacing.

`GreatVibes-Regular.ttf` is the Great Vibes calligraphic font used for the authors' names, Violet, Star, and Sapphire, on the author frontispiece. Upstream: https://github.com/google/fonts/tree/main/ofl/greatvibes . SIL Open Font License 1.1 is preserved as `GreatVibes-OFL.txt`. The unmodified font is embedded in the standalone HTML; PDF export embeds the used glyphs.

`BookSans-700.ttf` and `BookSans-900.ttf` are subsets instantiated from Noto Sans SC at weights 700 and 900. The former is used for chapter and section headings; the latter is used for the cover title. Internal family names are changed to `BookSans700` and `BookSans900` so PDF readers can distinguish the two static instances. Copyright and license records are retained. Source: https://github.com/notofonts/noto-cjk/tree/main/Sans ; license: SIL Open Font License 1.1, included in `LICENSE.txt`.

`prepare_style_fonts.py` prepares these fonts from the full variable font, installed locally as `C:\Windows\Fonts\NotoSansSC-VF.ttf`. Its subset includes the manuscript and layout vocabulary. There is no need to rerun this script when reading or rebuilding the unchanged edition.

The PDF uses system KaiTi for notes and SimSun for body text. The package does not redistribute either Windows font as a standalone file; the PDF embeds only required glyphs. HTML falls back to available compatible fonts on other operating systems.

`NotoSerifSC-Regular.ttf` is a text subset of Noto Serif SC, instantiated at `wght=400` from the variable font. It is used by numerical figures and embedded in the standalone HTML as a fallback for Chinese body text.

Upstream: https://github.com/notofonts/noto-cjk/tree/main/Serif

License: SIL Open Font License 1.1; see `LICENSE.txt`. Original copyright and name records are retained in the font. The source font used for this edition was installed locally at `C:\Windows\Fonts\NotoSerifSC-VF.ttf`.

The PDF is typeset with the system SimSun font where available. No standalone copy of the Windows SimSun font is distributed in this package. Mathematical and Latin plot symbols may use the DejaVu fonts bundled with Matplotlib.

The included subset is sufficient for the delivered book. If new characters are added, update `prepare_fonts.py` to point to a full Noto Serif SC variable font and regenerate the subset before rebuilding. Reading or rebuilding the unchanged book does not require running the font-preparation script.

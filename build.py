#!/usr/bin/env python3
"""Turn src/wet-ink.html into the self-hosted site/index.html.

The source is written to the claude.ai artifact contract: no <html>/<head>
wrapper (the viewer supplies one), libraries from a CDN, and file saving
through the viewer's `downloads` bridge. None of that holds when the page is
served off Chris's own machine, so this rewrites exactly three things and
leaves the rest byte-identical:

  1. the three library <script src> values  -> vendor/ on disk (works offline)
  2. the save path                          -> an ordinary object-URL download
  3. the missing document skeleton          -> added, with the viewer's reset

Run:  python3 build.py
"""
import datetime
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
SRC = HERE / "src" / "wet-ink.html"
OUT = HERE / "site" / "index.html"

CDN = {
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js": "vendor/pdf.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js": "vendor/pdf.worker.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js": "vendor/pdf-lib.min.js",
}

SAVE_OLD = """      if (!downloads) {
        toast("Saving is not available in this view.", true);
        return;
      }"""

SAVE_NEW = """      if (!downloads) {
        // Self-hosted: no sandbox, so a plain object-URL download is fine.
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = name;
        document.body.appendChild(a);
        a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 4000);
        toast("Saved " + name);
        return;
      }"""

RESET = """<style>
  /* Stands in for the reset the claude.ai wrapper used to supply. */
  * { box-sizing: border-box; }
  html { color-scheme: light dark; }
  :root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
  img { max-width: 100%; }
  [hidden] { display: none !important; }
</style>
"""


def main():
    src = SRC.read_text()

    # Version tag, shown next to the wordmark. Without it there is no way to
    # tell a bug in the new build from the phone quietly serving the old one.
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if "BUILDSTAMP" not in src:
        sys.exit("BUILDSTAMP placeholder missing from source")
    src = src.replace("BUILDSTAMP", "build " + stamp)

    for url, local in CDN.items():
        if url not in src:
            sys.exit("expected CDN url missing from source: %s" % url)
        src = src.replace(url, local)

    if SAVE_OLD not in src:
        sys.exit("save block not found — did the source change shape?")
    src = src.replace(SAVE_OLD, SAVE_NEW)

    marker = '<header class="bar top">'
    if marker not in src:
        sys.exit("header marker not found")
    head, body = src.split(marker, 1)
    body = marker + body

    out = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#2B4C7E">\n'
        '<link rel="manifest" href="manifest.webmanifest">\n'
        + RESET + head +
        "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )
    OUT.write_text(out)
    print("wrote %s (%d bytes)" % (OUT, len(out)))


if __name__ == "__main__":
    main()

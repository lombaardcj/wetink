# Wet Ink

Sign a PDF with a finger, on a phone, without handing the document to anyone.

The page opens a PDF, lets you draw a signature or place a date on it, and
writes a new PDF back out. All of it happens in the browser: there is no
server side, no upload, and no account. Load the page once and it keeps
working with the network off — the two PDF libraries are vendored in
`site/vendor/`, not pulled from a CDN.

It stamps **ink**, not a certificate. A drawn signature is what SARS, CIPC and
a bank ask for on a form. A cryptographic PAdES signature is a different job
and this does not pretend to do it.

## Layout

| Path | What it is |
|---|---|
| `src/wet-ink.html` | The source. Edit this. |
| `build.py` | Generates `site/index.html` from it. |
| `site/` | What is served. `index.html` is generated — do not hand-edit it. |
| `site/vendor/` | pdf.js 3.11.174 and pdf-lib 1.17.1, pinned and committed. |

```bash
python3 build.py        # after any change to src/
```

`build.py` rewrites exactly three things and leaves the rest byte-identical:
the library URLs become local paths, the save path becomes an ordinary browser
download, and the document skeleton the original host supplied is added back.
It also stamps the build time into the header — the only way to tell a bug in
a new build from a phone quietly serving the old one.

## How it is served

Static files behind the Lommies Warehouse Caddy on `sign.lan:5087`, which is
where the internal CA already trusted on the phone lives. See the site block in
`lommiesclassifieds/code/caddy/warehouse.Caddyfile` and
`~/secureme/wetink-serve.sh`. Off the LAN it is reached over Tailscale; nothing
is published to the internet.

Two things that file records and this one repeats, because both cost an
afternoon:

- The Caddyfile is a **bind-mounted single file**. Editing it replaces the
  inode, so the container serves the config it was created with while every
  `caddy reload` reports success. It needs `--force-recreate`.
- `index.html` is served **no-cache** on purpose.

## Things worth knowing about the code

- **Stamps are images, always.** A date is rendered to a transparent PNG and
  placed through the same machinery as a signature, so what lands in the file
  is what was positioned on screen, and there is only one set of placement
  maths to keep true.
- **Page rotation is handled explicitly.** `build()` maps screen coordinates
  into PDF user space for each of 0/90/180/270; a rotated scan would otherwise
  take the ink somewhere else entirely.
- **The pad is paper-coloured in both themes, deliberately.** The ink is
  near-black because it is going onto a white page. Taking the pad's
  background from the dark-mode token made it near-black ink on a near-black
  ground: the stroke recorded perfectly and was invisible, which reads exactly
  like a pad that does not respond.
- **Pointer capture is a convenience, not a requirement.** It is called after
  the drawing flags are set and inside a `try`, and move/release are watched on
  the window. With the call ahead of the flags, one thrown `NotFoundError`
  silently aborted every stroke.
- Signatures are kept in `localStorage`, up to four, per browser and per
  device. They never leave the machine, so the desktop and the phone each keep
  their own.

## Licence

© 2026 Chris Lombaard · [CC BY-NC 4.0](LICENSE)

Fork it, build on it, run it for yourself, your family or your church — credit
Chris Lombaard. Using any part of it in a commercial work needs his permission
first: <lombaardcj@gmail.com>.

The vendored libraries in `site/vendor/` are not covered by that and carry
their own licences — see [THIRD-PARTY.md](THIRD-PARTY.md).

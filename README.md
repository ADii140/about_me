# About Me — static site (cyberpunk)

Jinja2 template + Python build, output ready for GitHub Pages. A personal page,
not a resume: an intro, a longer story, things you like, what you're into
lately, and how to reach you.

```text
content.yml              all the copy — edit this, not the template
templates/about.html     the Jinja2 template (styling inline in <head>)
static/styles.css        Nocturne design tokens (type, spacing, radii)
build.py                 renders content.yml -> docs/index.html
.github/workflows/       CI: rebuilds docs/ on every PR to main
```

## Build

```bash
pip install -r requirements.txt
python build.py
```

Output lands in `docs/` (`index.html`, `static/`, `.nojekyll`).

## Publish

Commit `docs/` and set GitHub Pages to **Deploy from a branch → main → /docs**.

Every PR into `main` that touches `content.yml`, `templates/`, `static/`, `build.py`, or
`requirements.txt` runs [`.github/workflows/build-site.yml`](.github/workflows/build-site.yml),
which re-renders the site and pushes the updated `docs/` straight onto the PR branch. So in
practice: edit `content.yml`, open a PR, review the generated diff, merge — that merge is what
publishes.

If the site lives at `username.github.io/repo-name`, set `base_url: "/repo-name/"` in
`content.yml` so `static/styles.css` resolves.

## Template contract

| Variable | Shape |
| --- | --- |
| `site` | `title`, `description`, `lang`, `handle`, `footer_note`, `accent` (primary neon), `accent_2` (counter neon) |
| `nav` | list of `{label, href}` |
| `me` | `name`, `kicker`, `headline` (may contain `<em>…</em>` for the neon-glow words), `lede`, `actions` (list of `{label, href}`) |
| `story_heading`, `story` | heading string + list of paragraphs |
| `likes_heading`, `likes` | heading string + list of short strings (rendered as chips, alternating neon) |
| `lately_heading`, `lately` | heading string + list of `{label, text}` |
| `hello_heading`, `hello_note` | heading string + a lead-in line |
| `links` | list of `{label, value, href}` |
| `base_url` | top-level key in `content.yml`, default `""` (see Publish) |

`story`, `likes`, `lately` and `links` are each wrapped in `{% if %}` — drop a
section by removing its key from `content.yml`. Recolor the whole page from
`site.accent` / `site.accent_2`; every border, glow and chip derives from them.
The footer year is set client-side via a small inline script, so it's always current
without a rebuild.

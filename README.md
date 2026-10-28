# Tender Possibilities website

Source for [tenderpossibilities.ca](https://www.tenderpossibilities.ca), a poetry reading group in Toronto.
It's a static site built with [Eleventy](https://www.11ty.dev/) and published to GitHub Pages
every time something is pushed to the `main` branch.

## Making changes

You can do small edits straight on github.com without installing anything:
open a file, click the pencil icon, edit, and commit to `main`. The site rebuilds
and goes live in a few minutes (see the **Actions** tab for progress).

### Add or edit an event

Events live in `src/_data/events/`:

| File | Used for |
| --- | --- |
| `upcoming.json` | the Upcoming events page |
| `2026.json`, `2025.json`, `2024.json` | the Summer Series pages |

Each event is one block in the file:

```json
{
  "group": "upcoming",
  "title": "Water with Chris Kaputo",
  "url": "/upcoming-events/water-with-chris-kaputo",
  "image": "/images/kgosession3-xxxxx.jpg",
  "image_alt": "Water with Chris Kaputo",
  "date": "2026-09-20",
  "date_text": "Sunday, September 20, 2026",
  "start": "1:30 PM",
  "end": "4:00 PM",
  "address": ["292 Manse Road", "Toronto, Ontario, M1E 5A6", "Canada"],
  "map": "http://maps.google.com/?q=...",
  "body": ["<p>First paragraph.</p>", "<p>Second paragraph.</p>"]
}
```

To add an event, copy an existing block, change the values, and make sure `url` is
unique. The event page, the listing and the previous/next links are generated from it.
Put the flyer in `src/images/` and point `image` at it. Resize photos to about
2000px on the long side first so pages stay fast.

### Edit page text

Text for the home page, series intros, photos, contact and newsletter pages is in
`src/_data/pages/*.json`. Each page is a list of sections, and each section a list of
blocks with `html` for text and `src` for images. The `area_m` / `area_d` values are
the grid position of the block on phones and on desktop.

### Other places

- `src/_data/site.json`: site title, contact email, Instagram link
- `src/_data/nav.json`: the menu
- `src/css/main.css`: all styling (colours and fonts are at the top)
- `src/_includes/`: the page templates
- `src/assets/`: favicon and the image used when a link is shared

## Running it locally

```
npm install
npm start
```

then open http://localhost:8080. `npm run build` writes the finished site to `_site/`.

## Redesigns

The content (`src/_data`) and the look (`src/css`, `src/_includes`) are kept apart,
so a redesign mostly means replacing the CSS and templates while the events and text carry over.

## Hosting notes

- Domain: `src/CNAME` holds the custom domain. Don't delete it.
- DNS: `www` is a CNAME to `tender-possibilities.github.io`; the bare domain
  uses GitHub's four A records. Email (MX/TXT) records are separate and untouched.
- Contact form: GitHub Pages can't process forms. The contact page shows the email
  address instead. A form service can be connected by setting `contactFormAction`
  in `src/_data/site.json`.
- Newsletter: the signup block links to an email address until a mailing tool is chosen.

`scripts/` holds the helpers that were used once to convert the old Squarespace pages.
They aren't needed to run or update the site.

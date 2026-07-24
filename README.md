# The Rothenburg Series

Four hand-modelled environment packs for **Unreal Engine 5.8**, built to one shared scale so they
can sit in the same scene: a Parc-Monceau garden footbridge, a Rothenburg Fachwerk facade kit, an
animated courtyard fountain, and a plain stone crossing.

**→ [The catalogue, as a drawing set](https://4rev.github.io/rothenburg-series/)**

Per-sheet specs, dimensions, scale references, an honest account of what is and is not in each
box — and a revision block publishing every Fab review round, including the three that were
rejected and what each reviewer caught.

## The packs

| Sheet | Pack | Price | |
|---|---|---|---|
| 01 | Medieval Stone Bridge | Free | [Fab](https://www.fab.com/listings/4c64ce34-195b-4b45-8e14-70273cc984b5) |
| 02 | Hebe Fountain — animated water | Free | [Fab](https://www.fab.com/listings/cd1dc9b7-be6e-46c8-8e7d-7367b1c4ac92) |
| 03 | Medieval Windows & Doors — 21 meshes, 8 Blueprints | $12.99 | [Fab](https://www.fab.com/listings/e26b4923-ba19-44f7-973f-7341ddaf5c94) |
| 04 | Ornate Stone Footbridge — single Nanite hero mesh | $9.99 | [Fab](https://www.fab.com/listings/cd7969c8-9567-4a85-b295-5b9efa8d0f66) |

All four: [fab.com/sellers/Pierogi3](https://www.fab.com/sellers/Pierogi3)

## The rules every pack is built to

- **1 unreal unit = 1 cm**, every pack, pivots on the grid
- **Nanite** on all solid meshes, with full-detail fallbacks
- Channel-packed **ORM**, imported sRGB-off
- **Hand-authored collision** — fitted boxes and hulls, never auto-decomposition run over hand work
- **Unreal Engine 5.8+**, built for Lumen and dynamic lighting
- **No dependencies** — no Megascans, no Starter Content, no third-party assets
- Hand-modelled throughout. **No generative AI** in any asset.
- Fab Standard Licence — ships in commercial games

## What reviewers caught

Three of the submissions were rejected before approval. The reasons are published on the site
rather than buried, because they are the useful part:

1. **Auto-generated collision on a shutter**, plus `Complex as Simple` set on two Nanite meshes —
   invalid on Nanite, and silently bypassing twelve hand-authored hulls on the door frame.
2. **A reviewer flew a camera through the spandrel wall** above the footbridge's arch into the
   hollow interior. That bridge now ships 25 hand-authored collision primitives.
3. **An invalid project file link** — the corrected build had been uploaded as a new Drive file
   instead of a new version of the old one.

## About this repository

This repo hosts the catalogue page only — a single self-contained HTML file, no build step, no
dependencies, no trackers. The assets themselves are distributed through Fab.

Built by Krzysztof Macias.

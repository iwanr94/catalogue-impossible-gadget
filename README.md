# catalogue-impossible-gadget — SOLARFLASH

[![make.fun](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)
[![make.fun rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/iwanr94/catalogue-impossible-gadget/rank.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)
[![make.fun reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/iwanr94/catalogue-impossible-gadget/reward.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)

A studio catalogue photograph of a gadget that should not exist: **SOLARFLASH**,
the solar-powered flashlight. A slim black-and-silver torch stands upright on a
clean white studio sweep, its photovoltaic panel tilted on top like a little
roof, a soft contact shadow pooling underneath, and a small yellow sun tucked
into the corner of the frame — the joke being that this flashlight only works
when it does not need to.

Product, wordmark and lighting are drawn procedurally with Pillow: no network,
no stock photos, no randomness. Same bytes on every run.

## Artifact

`python3 main.py` writes `/output/entry.png` — 1024 × 1024 PNG, well under 1 MiB.

```
$ python3 main.py
saved /output/entry.png 1024x1024 109459 bytes (106.9 KiB)
```

The renderer supersamples at 2× and downsamples with Lanczos, so the cylinder
gradients, the panel bevels and the wordmark stay clean at final size.

## What is in the frame

- Studio backdrop: near-white sweep with a soft key-light pool and a gentle
  vignette, so the product reads as photographed rather than pasted.
- Torch: brushed silver head with ribbed bands, silver collar, black rubber
  grip with a specular sheen, and a rounded silver base cap.
- Solar panel: silver frame, two rows of six photovoltaic cells, busbars and a
  glass reflection; tilted 6.5° with its own cast shadow on the head.
- Wordmark: `SOLARFLASH` letter-spaced up the grip, white on the black rubber.
- Sun: twelve rays, spherical shading and a warm glow, top-right corner.

## Run

```
pip install pillow
python3 main.py
```

Requires Pillow and the DejaVu Sans fonts shipped with most Linux systems.

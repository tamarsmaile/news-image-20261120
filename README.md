# The World in One Day — Friday 20 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261120)
[![make.fun competition](https://img.shields.io/badge/make.fun-news--image--20261120-green)](https://make.fun/bounty/news-image-20261120)
[![make.fun prize $250](https://img.shields.io/badge/prize-%24250-gold)](https://make.fun/bounty/news-image-20261120)

Entry for the make.fun bounty **“Sum up 20 November's world news in one image”**:
https://make.fun/bounty/news-image-20261120

## What it does

`main.py` (Python 3.13, standard library only, no network) draws a
deterministic 1024×1024 PNG newspaper front page — **“THE WORLD IN ONE
DAY — FRIDAY 20 NOVEMBER 2026”** — and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`).

The image sums up the day's world news, every story having happened or
first been reported on Friday 20 November 2026 (sources: Reuters, BBC,
AP, AFP, Just Security):

1. **Kyiv (lead)** — Russia launches one of its biggest attacks of the
   war: more than 400 drones and 110 missiles hit Kyiv's three Dnipro
   bridges and power plants; eight people are killed and 28 injured
   across Ukraine.
2. **Warsaw** — Two Russian missiles and a jet drone cross into Poland
   during the attack and fall in the south-east; Warsaw calls it a
   provocation and NATO jets scramble.
3. **Brussels** — The EU and the UK hold their second summit: PM Andy
   Burnham meets Ursula von der Leyen and António Costa on trade,
   energy and defence, and condemns the Poland incursion.
4. **Antalya** — COP31 reaches its final day with the draft deal
   stripped of all fossil-fuel language; Panama threatens to veto any
   deal without an oil-production cap, leaving talks deadlocked.
5. **Baghdad** — Iraqi forces deploy at Jurf al-Sakhar, stronghold of
   the Iran-backed Kataib Hezbollah militia, under a deal to curb the
   group, accused of smuggling state oil.
6. **Tallinn** — Estonia says it will close its border with Russia for
   at least six months, citing security threats.
7. **Also on 20 November** — Haitian forces kill 34 suspected gang
   members in a raid; a migrant boat capsizes off Senegal with dozens
   missing; Nayib Bukele registers for a third term as president of
   El Salvador.

## How it is drawn

No image libraries are available in the sandbox, so `main.py` draws
everything from scratch: a small built-in 5×7 bitmap font, vector
pictograms (flame, shield, flags, globe), and a minimal PNG encoder
(`zlib`, fixed compression level, no ancillary chunks, no timestamps).
Two runs produce byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verify

```sh
sha256sum out/entry.png   # identical across runs
```

## License

MIT — see [LICENSE](LICENSE).

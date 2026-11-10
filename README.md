# Open Isn't Enough: Separation vs. the Sticks on 3rd Down

**NFL Big Data Bowl 2026 – Regional Event** · Skill-position (WR / TE / RB) analysis of 2021 NFL tracking data, Weeks 1–8

## Summary

On 3rd and 4th down with 3+ yards to go, a WR, TE or RB targeted 5 or more yards short of the line to gain converts only 14–27% of the time no matter how open he is, and just 18% even with 5+ yards of space (n = 195). A receiver 0–8 yards past the sticks converts 51–61% with only 1.5–3 yards of separation. Separation helps a short target only until about 3 yards of space. Beyond that, distance to the sticks matters far more, which is why running backs are the most open target on the field (4.4 yds vs 3.0 for WRs) and the most reliable (75% completion vs 58%) yet produce the fewest yards per target (5.9 vs 8.3). We found the intended receiver for 95.2% of pass plays by parsing play descriptions, measured separation as the distance to the nearest defender of any position at the moment of release, and judged every target by its outcome (yards and first downs) rather than how open he looked. The result is a 3rd-down decision grid a play-caller can use for route depth, plus a list of the skill players who actually turn short catches into first downs.

## Figures

| File | Question it answers |
|---|---|
| `figures/fig1_3rd_down_sticks.png` | **Main figure.** On 3rd down, when is an open receiver short of the sticks worth the throw? |
| `figures/fig2_checkdown_by_position.png` | Do the most open positions produce the most value? |
| `figures/fig3_open_vs_value.png` | Which individual players are open but low value, and which are covered but productive? |

Every panel is explained in **[FIGURES.md](FIGURES.md)**. Every column and metric is defined in **[CODEBOOK.md](CODEBOOK.md)**.

## Repository structure

```
├── README.md            ← this file
├── FIGURES.md           ← what each figure shows, how to read it, caveats
├── CODEBOOK.md          ← definitions of every column and derived metric
├── requirements.txt
├── run_all.sh           ← rebuilds every output and figure from raw data
├── scripts/
│   ├── 01_build_targets.py       parse intended receiver from play descriptions
│   ├── 02_build_separation.py    separation for every route runner at release
│   ├── 03_build_sticks.py        3rd/4th-down target position vs. line to gain
│   ├── 04_fig_3rd_down_sticks.py → figures/fig1
│   ├── 05_fig_checkdown.py       → figures/fig2
│   └── 06_fig_open_vs_value.py   → figures/fig3
├── output/              ← intermediate tables produced by scripts 01–03
└── figures/             ← final PNGs produced by scripts 04–06
```

## How to run

```bash
# 1. Get the data (~1 GB, excluded from this repo by .gitignore)
git clone https://github.com/ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data.git

# 2. Install dependencies (Python 3.10+)
pip install -r requirements.txt

# 3. Rebuild everything from the repo root (~3–5 minutes; scripts 02 and 03 read all tracking files)
bash run_all.sh
```

The `output/` tables are committed, so scripts 04–06 can be run on their own in seconds without the raw data.

## Data

[NFL Big Data Bowl regional event data](https://github.com/ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data): NFL Next Gen Stats player tracking (10 Hz) and PFF scouting data for 122 games, 2021 season Weeks 1–8. Only pass plays (complete, incomplete, intercepted) are used.

Built with Python, pandas, NumPy and Matplotlib.

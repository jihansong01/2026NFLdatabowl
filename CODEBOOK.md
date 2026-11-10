# Codebook

Definitions for every derived table in `output/` and every metric in the figures. Raw source fields follow the [data repository README](https://github.com/ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data).

## Conventions

| Item | Definition |
|---|---|
| Distance units | Yards. Tracking `x` runs 0–120 along the field, `y` runs 0–53.3 across it. |
| Frame rate | 10 frames per second (`frameId`). |
| Release frame | First frame tagged `pass_forward` or `autoevent_passforward`. |
| Snap frame | First frame tagged `ball_snap`. |
| Line of scrimmage (LOS) | Ball `x` at the snap frame. |
| Offense direction | `playDirection` from tracking. Depth is flipped so positive always means downfield. |
| Skill positions | `officialPosition` in {WR, TE, RB}. FB is used only for target matching. |
| Defender | Any player whose `team` differs from the offense (`possessionTeam`), excluding the ball. |
| Route runner | Player with `pff_role == "Pass Route"` in `pffScoutingData.csv` for that play. |

---

## `output/pass_plays_with_targets.csv`

Built by `scripts/01_build_targets.py`. One row per pass attempt (`passResult` in C, I, IN). 7,565 rows.

| Column | Type | Description |
|---|---|---|
| `gameId` | int | Game ID (join key). |
| `playId` | int | Play ID, unique within a game (join key). |
| `passResult` | str | `C` complete, `I` incomplete, `IN` intercepted. |
| `target_nflId` | float | `nflId` of the intended receiver. Blank when no receiver is named (throwaways, spikes) or the name couldn't be matched uniquely. |
| `pass_depth` | str | `short` / `deep` from the play description. |
| `pass_dir` | str | `left` / `middle` / `right` from the play description. |
| `down`, `yardsToGo`, `playResult` | int | Copied from `plays.csv`. |
| `pff_passCoverage`, `pff_passCoverageType`, `offenseFormation`, `pff_playAction` | str/int | Copied from `plays.csv`. |

**Target matching method:**
1. A regex pulls the receiver from phrases like `pass short middle to M.Evans`, `pass incomplete deep left to C.Lamb`, or `intended for T.Hockenson INTERCEPTED`.
2. Two-letter initials are normalized (`Ja.Williams` → `J.Williams`).
3. The abbreviation is matched against route runners **on that same play**, using `first initial + "." + last name` from `players.csv`.
4. Only unique matches are kept. This resolves cases like `A.Brown` (Antonio Brown vs. A.J. Brown) because only one of them runs a route on a given play.

**Match rate:** 95.2% overall (98.6% completions, 89.5% incompletions, 95.8% interceptions).

---

## `output/sep_all_defenders.csv`

Built by `scripts/02_build_separation.py`. One row per route runner per pass play, measured at the release frame. 34,754 rows.

| Column | Type | Description |
|---|---|---|
| `gameId`, `playId`, `nflId` | int | Join keys. `nflId` is the route runner. |
| `sep_all` | float | **Separation:** Euclidean distance (yards) from the route runner to the nearest defender of any position at the release frame. |
| `officialPosition` | str | Route runner's position. |

---

## `output/sticks_targets.csv`

Built by `scripts/03_build_sticks.py`. One row per **targeted** 3rd- or 4th-down pass. 2,131 rows. Figure 1 keeps WR/TE/RB with `yardsToGo >= 3` (1,830 rows).

| Column | Type | Description |
|---|---|---|
| `gameId`, `playId`, `nflId` | int | Join keys. `nflId` is the target. |
| `sep_release` | float | Target's separation (nearest defender, any position) at the release frame. |
| `sep_arrival` | float | Separation when the ball arrives. **Mostly blank:** tracking ends shortly after the throw, so this exists for only a small number of plays and is not used. |
| `depth` | float | Target's yards downfield of the LOS at the release frame. Negative means behind the LOS. |
| `vs_sticks` | float | `depth − yardsToGo`. Negative means short of the line to gain, positive means past it. |
| `converted` | int | 1 if `passResult == "C"` and `prePenaltyPlayResult >= yardsToGo`, else 0. |
| `down`, `yardsToGo`, `passResult`, `prePenaltyPlayResult`, `possessionTeam` | | Copied from `plays.csv`. |
| `displayName`, `officialPosition` | str | Target's name and position from `players.csv`. |

---

## Metrics used in the figures

| Metric | Formula | Figures |
|---|---|---|
| Separation | `sep_all` or `sep_release` (above) | 1, 2, 3 |
| Completion % | share of targets with `passResult == "C"` | 2 |
| Yards per target | mean of `prePenaltyPlayResult` on completions, with incompletions and interceptions counted as 0 | 2, 3 |
| First-down / conversion rate | mean of `converted` (or the same rule applied to all downs) | 1, 2, 3 |
| Position vs. sticks bins | `vs_sticks` cut at −5, −2, 0, 3, 8 | 1 |
| Separation bins | `sep_release` cut at 1.5, 3, 5 yards | 1 |
| Yards-to-go bins (3rd down) | 1–3, 4–7, 8–10, 11+ | 2 |
| Player inclusion | Figure 1 panel 3: 7+ short-of-sticks targets. Figure 3: 20+ targets. | 1, 3 |
| Correlation `r` | Pearson correlation of player average separation vs. yards per target | 3 |

**Why prePenaltyPlayResult:** it records the yards the play itself gained before any penalty yardage, so a defensive penalty on an incompletion doesn't count as receiving yards.

# Figure Guide

How to read each figure, what it shows, and where it falls short. All numbers come from a clean run of `run_all.sh`.

**Shared definitions** (full detail in [CODEBOOK.md](CODEBOOK.md)):
- **Target:** the intended receiver named in the play description. Matched on 7,203 of 7,565 pass attempts (95.2%).
- **Separation:** distance in yards from a route runner to the nearest defender of *any* position, at the frame the ball is released.
- **Converted:** a completed pass that gained at least the yards to go.
- **Yards per target:** yards gained, counting incompletions and interceptions as 0.

---

## Figure 1: 3rd down decision grid (main figure)

`figures/fig1_3rd_down_sticks.png` · 1,830 targeted 3rd/4th-down passes with 3+ yards to go

**Question:** On a money down, is an open receiver short of the sticks worth the throw, or is a tighter window past the sticks better?

### Panel 1: Decision grid
Columns show where the target was relative to the line to gain when the ball was thrown. Rows show how open he was. Each cell is the first-down conversion rate. Cells with fewer than 25 plays are greyed out. The dashed white line is the line to gain.

| Separation ↓ / Position vs sticks → | 5+ short | 2–5 short | 0–2 short | 0–3 past | 3–8 past | 8+ past |
|---|---|---|---|---|---|---|
| **5+ yds** | 18% | 42% | 55% | 60% | 62% | 50% |
| **3–5 yds** | 14% | 40% | 63% | 54% | 59% | 61% |
| **1.5–3 yds** | 27% | 36% | 47% | 51% | 61% | 23% |
| **0–1.5 yds** | 9%* | 24% | 34% | 28% | 35% | 36% |

\* n = 22, greyed out in the figure.

**How to read it:**
- **The left column is dead.** A target 5+ yards short converts 14–27% (excluding the greyed-out cell), and only 18% even when he has 5+ yards of space (n = 195, the largest cell in the grid).
- **2–5 yards short tops out near 40%,** no matter how open the receiver is.
- **0–2 yards short with 3+ yards of space converts 55–63%,** as well as a throw past the sticks. Here the receiver makes up the gap after the catch.
- **A modest window (1.5–3 yds) 0–8 yards past the sticks converts 51–61%,** better than any target 2+ yards short. Very deep shots (8+ past) fall back to 23–61% depending on space.
- **Separation beyond ~3 yards adds little.** Moving down the rows matters less than moving right across the columns.

### Panel 2: Does more space rescue a short target?
Same data collapsed into three zones (5+ short, 0–5 short, at/past sticks), with conversion plotted against separation. The red line (5+ short) stays low whatever the separation, so extra space doesn't fix a target that is too shallow.

### Panel 3: Who converts when targeted short of the sticks
Players with 7+ targets short of the sticks on 3rd/4th down. The dashed line is the league average (33.5%). Top: Justin Jefferson 71%, Calvin Ridley 67%, Tyreek Hill 62%, Ty Johnson 60%, D.J. Moore 60%. Bottom: Jakobi Meyers 11%, Diontae Johnson 12%, Aaron Jones 14%, DK Metcalf 14%, Noah Fant 20% (15 targets).

**Use:**
- **Play-callers:** on 3rd & 5+, design primary routes to break at or within 2 yards of the line to gain.
- **QBs:** a checkdown 5+ yards short is a near-certain punt, even if he's wide open.
- **Scouts:** Panel 3 separates players who create yards after the catch on short targets from those who don't.

**Caveats:**
- The tracking data ends shortly after the throw. Position is measured at release, not at the catch, so a receiver still running his route may have crossed the sticks later.
- Short throws are more often forced by pressure. Some of the low conversion reflects the situation, not the target.
- Panel 3 samples are small (7–15 targets per player). Treat it as illustrative, not as a ranking.

---

## Figure 2: The checkdown illusion, by position

`figures/fig2_checkdown_by_position.png` · 7,147 targeted passes (WR 4,363 · TE 1,559 · RB 1,225), all downs

**Question:** Does the most open position produce the most value?

| Panel | Metric | RB | TE | WR |
|---|---|---|---|---|
| 1 | Separation at release (all route runners) | **4.4 yds** | 3.1 | 3.0 |
| 2 | Completion % when targeted | **75%** | 67% | 58% |
| 3 | Yards per target | 5.9 | 7.4 | **8.3** |
| 4 | 3rd & 8–10 conversion | 28% | 29% | **41%** |
| 4 | 3rd & 11+ conversion | 14% | 8% | **26%** |

**How to read it:** The left two panels make RBs look like the best option. The right two show the opposite. The most open, most reliable target produces the fewest yards, and the gap is biggest on 3rd & long, when the checkdown is most tempting.

**Caveat:** Yards per target isn't adjusted for depth. RBs are targeted shorter by design, and that is the point: openness mostly reflects how short the throw is.

---

## Figure 3: Open vs. valuable, by player

`figures/fig3_open_vs_value.png` · 142 skill players with 20+ targets

**Question:** Which individual players are open but low value, and which are covered but productive?

Each bubble is one player. The x-axis is average separation when targeted. The y-axis is yards per target. Bubble size is the number of targets. Dashed lines are the medians, which split the chart into quadrants.

**How to read it:**
- **The overall trend runs downhill (r = −0.34).** Players who are more open when targeted average *fewer* yards per target.
- **Open but low value (bottom right):** Chuba Hubbard (5.6 yds separation, 3.7 yds/target), James Robinson (6.1, 4.2), Mike Davis (5.3, 4.3), Ryan Griffin (4.2, 3.9).
- **Covered but productive (top left):** Ja'Marr Chase averages only 2.6 yds of separation but 14.2 yds per target. Cedrick Wilson (14.2), David Njoku (12.6), C.J. Uzomah (12.5), Dallas Goedert (12.4) and Henry Ruggs (12.2) are also up there.
- **Position medians:** RB 5.2 sep / 5.9 yds / 30% first downs. WR 3.3 / 8.0 / 38%.

**Use:** A scouting view that ranks receivers by what their targets produce, not by how open they look on film.

**Caveat:** No adjustment for target depth, quarterback or scheme. The negative correlation is partly a depth effect, since deep targets are tighter and gain more.

---

## What we tested and rejected

Each of these was checked and dropped because it didn't survive a fair test. We list them so the remaining findings can be judged in context.

| Idea | Why it was dropped |
|---|---|
| "Smooth" route breaks (keeping speed through the cut) beat sharp plants | The "smooth" group was mostly shallow routes with ~5° of direction change. Among routes with a real cut (15°+), separation was the same at every break speed (4.4 vs 4.4 yds). |
| Backup QBs dump the ball to TEs and RBs more often | The position mix of route runners barely moved (TE share +2.6 points), and receiver separation didn't change league-wide. |
| Middle-of-field and crossing routes raise INT risk under pressure | INT rates were nearly identical (3.3% vs 3.2%). |
| RBs are the most open player on 55% of plays and get ignored | That number counted only cornerbacks and safeties as defenders. With linebackers included, RB separation fell from 10.5 to 4.4 yds, and Figure 2 shows that passing up the RB is usually the right call. |

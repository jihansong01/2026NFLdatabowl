"""The Checkdown Illusion: open does not mean valuable.
Separation = distance to nearest defender of ANY position at the pass-release frame.
Outcomes = per target (yards on incompletions/INTs = 0)."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

D = 'nfl-big-data-bowl-regional-event-data/data'
BG, PANEL, TEXT, GRID = '#0d1117', '#161b22', '#e6edf3', '#30363d'
COL = {'RB': '#2ecc71', 'TE': '#f39c12', 'WR': '#58a6ff'}
POS = ['RB', 'TE', 'WR']

players = pd.read_csv(f'{D}/players.csv')
plays = pd.read_csv(f'{D}/plays.csv')
sep = pd.read_csv('output/sep_all_defenders.csv')
t = pd.read_csv('output/pass_plays_with_targets.csv')
t = t[t['target_nflId'].notna() & (t['target_nflId'] != -1)].copy()
t['target_nflId'] = t['target_nflId'].astype(int)
t = t.merge(plays[['gameId', 'playId', 'prePenaltyPlayResult']], on=['gameId', 'playId'])
t = t.merge(players[['nflId', 'officialPosition']], left_on='target_nflId', right_on='nflId')
t = t[t['officialPosition'].isin(POS) & t['down'].isin([1, 2, 3, 4])]
t['yds'] = np.where(t['passResult'] == 'C', t['prePenaltyPlayResult'], 0)
t['fd'] = ((t['passResult'] == 'C') & (t['prePenaltyPlayResult'] >= t['yardsToGo'])).astype(int)

fig, axes = plt.subplots(1, 4, figsize=(22, 6.5), facecolor=BG)
fig.suptitle('The Checkdown Illusion: open does not mean valuable\n'
             'RBs are the most open and most reliable target, but produce the fewest yards and first downs',
             color=TEXT, fontsize=14, fontweight='bold', y=1.03)

def style(ax, title, ylabel):
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID)
    ax.set_title(title, color=TEXT, fontsize=11)
    ax.set_ylabel(ylabel, color=TEXT, fontsize=10)
    ax.tick_params(colors=TEXT)
    ax.grid(axis='y', color=GRID, lw=0.5, alpha=0.5)

def bars(ax, vals, fmt):
    b = ax.bar(POS, vals, color=[COL[p] for p in POS], width=0.55, zorder=3)
    for bar, v in zip(b, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.02, fmt.format(v),
                ha='center', va='bottom', color=TEXT, fontsize=12, fontweight='bold')
    ax.set_ylim(0, max(vals) * 1.25)

# 1. Separation (all route runners)
s = sep.groupby('officialPosition')['sep_all'].mean().reindex(POS)
style(axes[0], '1. Separation at throw', 'Yards to nearest defender')
bars(axes[0], s.values, '{:.1f} yds')

# 2. Completion rate per target
c = t.groupby('officialPosition')['passResult'].apply(lambda x: (x == 'C').mean() * 100).reindex(POS)
style(axes[1], '2. Completion rate when targeted', 'Completion %')
bars(axes[1], c.values, '{:.0f}%')

# 3. Yards per target
y = t.groupby('officialPosition')['yds'].mean().reindex(POS)
style(axes[2], '3. Yards per target', 'Yards (incompletions = 0)')
bars(axes[2], y.values, '{:.1f}')

# 4. 3rd-down conversion by distance
ax = axes[3]
style(ax, '4. 3rd-down conversion rate when targeted', 'First down %')
third = t[t['down'] == 3].copy()
third['ytg'] = pd.cut(third['yardsToGo'], [0, 3, 7, 10, 40], labels=['1-3', '4-7', '8-10', '11+'])
conv = third.groupby(['ytg', 'officialPosition'], observed=True)['fd'].mean().unstack()[POS] * 100
x = np.arange(len(conv)); w = 0.26
for i, p in enumerate(POS):
    ax.bar(x + (i - 1) * w, conv[p].values, w, color=COL[p], label=p, zorder=3)
ax.set_xticks(x); ax.set_xticklabels([f'3rd & {l}' for l in conv.index], color=TEXT)
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT)
ax.set_ylim(0, 80)

for ax in axes:
    for lb in ax.get_xticklabels() + ax.get_yticklabels(): lb.set_color(TEXT)

fig.text(0.5, -0.04,
         f'2021 NFL Weeks 1-8 · {len(t):,} targeted passes (receiver parsed from play descriptions) · '
         'Separation = distance to nearest defender of any position at pass release',
         color=TEXT, fontsize=8, ha='center', alpha=0.6)
plt.tight_layout()
plt.savefig('figures/fig2_checkdown_by_position.png', dpi=150, bbox_inches='tight', facecolor=BG)
print('Saved figures/fig2_checkdown_by_position.png')
print(pd.DataFrame({'sep': s, 'comp%': c, 'yds/tgt': y}).round(2))
print(conv.round(1))

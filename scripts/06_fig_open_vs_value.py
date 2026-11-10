"""Open vs. Valuable: every skill player plotted by separation when targeted
vs. yards per target. Shows that the most open players are not the most productive."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

D = 'nfl-big-data-bowl-regional-event-data/data'
BG, PANEL, TEXT, GRID = '#0d1117', '#161b22', '#e6edf3', '#30363d'
COL = {'RB': '#2ecc71', 'TE': '#f39c12', 'WR': '#58a6ff'}
MIN_TGT = 20

players = pd.read_csv(f'{D}/players.csv')
plays = pd.read_csv(f'{D}/plays.csv')
sep = pd.read_csv('output/sep_all_defenders.csv')
t = pd.read_csv('output/pass_plays_with_targets.csv')
t = t[t['target_nflId'].notna() & (t['target_nflId'] != -1)].copy()
t['nflId'] = t['target_nflId'].astype(int)
t = t.merge(plays[['gameId', 'playId', 'prePenaltyPlayResult']], on=['gameId', 'playId'])
t = t.merge(sep[['gameId', 'playId', 'nflId', 'sep_all']], on=['gameId', 'playId', 'nflId'])
t = t.merge(players[['nflId', 'officialPosition', 'displayName']], on='nflId')
t = t[t['officialPosition'].isin(COL) & t['down'].isin([1, 2, 3, 4])]
t['yds'] = np.where(t['passResult'] == 'C', t['prePenaltyPlayResult'], 0)
t['fd'] = ((t['passResult'] == 'C') & (t['prePenaltyPlayResult'] >= t['yardsToGo'])).astype(int)

p = t.groupby(['nflId', 'displayName', 'officialPosition']).agg(
    targets=('yds', 'size'), sep=('sep_all', 'mean'),
    ypt=('yds', 'mean'), fd=('fd', 'mean')).reset_index()
p = p[p['targets'] >= MIN_TGT]

fig, ax = plt.subplots(figsize=(15, 9), facecolor=BG)
ax.set_facecolor(PANEL)
for sp in ax.spines.values(): sp.set_edgecolor(GRID)

mx, my = p['sep'].median(), p['ypt'].median()
ax.axvline(mx, color=GRID, lw=1.2, ls='--'); ax.axhline(my, color=GRID, lw=1.2, ls='--')

for pos, c in COL.items():
    s = p[p['officialPosition'] == pos]
    ax.scatter(s['sep'], s['ypt'], s=s['targets'] * 4, c=c, alpha=0.65,
               edgecolors='white', lw=0.6, label=f'{pos} (n={len(s)})', zorder=3)

# Label the extremes in each quadrant
label = pd.concat([
    p.nlargest(6, 'ypt'),                                   # most productive
    p[p['sep'] > mx].nsmallest(5, 'ypt'),                   # open but low value
    p.nlargest(3, 'sep'),                                   # most open
]).drop_duplicates('nflId')
for _, r in label.iterrows():
    ax.annotate(r['displayName'], (r['sep'], r['ypt']), xytext=(6, 4),
                textcoords='offset points', color=TEXT, fontsize=8.5)

xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
q = dict(color=TEXT, fontsize=11, alpha=0.45, fontweight='bold')
ax.text(xmax, ymax, 'Open AND productive', ha='right', va='top', **q)
ax.text(xmax, ymin, 'Open but low value\n(the checkdown illusion)', ha='right', va='bottom', **q)
ax.text(xmin, ymax, 'Covered but productive\n(worth the tight window)', ha='left', va='top', **q)

ax.set_xlabel('Avg separation when targeted (yds to nearest defender at release)', color=TEXT, fontsize=11)
ax.set_ylabel('Yards per target (incompletions = 0)', color=TEXT, fontsize=11)
ax.set_title('Open does not mean valuable\nEvery skill player with 20+ targets, 2021 Weeks 1-8 · bubble size = targets',
             color=TEXT, fontsize=14, fontweight='bold', pad=12)
ax.tick_params(colors=TEXT); ax.grid(color=GRID, lw=0.5, alpha=0.4)
for lb in ax.get_xticklabels() + ax.get_yticklabels(): lb.set_color(TEXT)
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=10, loc='upper center',
          markerscale=0.5, ncol=3)

r = np.corrcoef(p['sep'], p['ypt'])[0, 1]
fig.text(0.5, 0.01, f'Correlation between separation and yards per target across players: r = {r:+.2f}',
         color=TEXT, fontsize=9, ha='center', alpha=0.7)
plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('figures/fig3_open_vs_value.png', dpi=150, bbox_inches='tight', facecolor=BG)
print(f'Saved figures/fig3_open_vs_value.png | players={len(p)} | r={r:+.2f}')
print(p.groupby('officialPosition')[['sep', 'ypt', 'fd']].median().round(2))
print('\nOpen but low value:'); print(p[p['sep'] > mx].nsmallest(5, 'ypt')[['displayName', 'officialPosition', 'targets', 'sep', 'ypt']].round(2).to_string(index=False))
print('\nMost productive:'); print(p.nlargest(6, 'ypt')[['displayName', 'officialPosition', 'targets', 'sep', 'ypt']].round(2).to_string(index=False))

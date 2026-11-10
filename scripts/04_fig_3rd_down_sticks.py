"""3rd-down decision grid: does an open receiver short of the sticks convert?
Input: sticks_targets.csv (built by build_sticks.py). Depth/separation measured at pass release."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

BG, PANEL, TEXT, GRID = '#0d1117', '#161b22', '#e6edf3', '#30363d'
COL = {'RB': '#2ecc71', 'TE': '#f39c12', 'WR': '#58a6ff'}
MIN_CELL = 25

d = pd.read_csv('output/sticks_targets.csv')
d = d[(d['yardsToGo'] >= 3) & d['officialPosition'].isin(COL)].copy()
loc_lbl = ['5+ yds\nshort', '2-5 yds\nshort', '0-2 yds\nshort', '0-3 yds\npast', '3-8 yds\npast', '8+ yds\npast']
sep_lbl = ['0-1.5 yds', '1.5-3 yds', '3-5 yds', '5+ yds']
d['loc'] = pd.cut(d['vs_sticks'], [-60, -5, -2, 0, 3, 8, 80], labels=loc_lbl)
d['sep'] = pd.cut(d['sep_release'], [0, 1.5, 3, 5, 60], labels=sep_lbl)

fig = plt.figure(figsize=(22, 8), facecolor=BG)
gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1, 0.9], wspace=0.28)
fig.suptitle('3rd down: being open short of the sticks is not enough\n'
             'First-down conversion rate when targeted, 3rd/4th & 3+, 2021 Weeks 1-8',
             color=TEXT, fontsize=15, fontweight='bold', y=1.04)

def style(ax, title):
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID)
    ax.set_title(title, color=TEXT, fontsize=11.5, pad=10)
    ax.tick_params(colors=TEXT)
    for lb in ax.get_xticklabels() + ax.get_yticklabels(): lb.set_color(TEXT)

# ── 1. Decision grid ───────────────────────────────────────
ax = fig.add_subplot(gs[0])
rate = d.pivot_table(index='sep', columns='loc', values='converted', aggfunc='mean', observed=True).reindex(index=sep_lbl[::-1], columns=loc_lbl)
cnt = d.pivot_table(index='sep', columns='loc', values='converted', aggfunc='size', observed=True).reindex(index=sep_lbl[::-1], columns=loc_lbl)
cmap = LinearSegmentedColormap.from_list('c', ['#3a1a1a', '#e74c3c', '#f39c12', '#2ecc71'])
masked = np.ma.masked_where(cnt.values < MIN_CELL, rate.values)
ax.imshow(masked, cmap=cmap, vmin=0.1, vmax=0.65, aspect='auto')
for i in range(len(sep_lbl)):
    for j in range(len(loc_lbl)):
        n = cnt.values[i, j]
        if n >= MIN_CELL:
            ax.text(j, i - 0.1, f'{rate.values[i, j]*100:.0f}%', ha='center', va='center', color='white', fontsize=14, fontweight='bold')
            ax.text(j, i + 0.25, f'n={n:.0f}', ha='center', va='center', color='white', fontsize=8, alpha=0.8)
        else:
            ax.text(j, i, f'n<{MIN_CELL}', ha='center', va='center', color=TEXT, fontsize=8, alpha=0.4)
ax.axvline(2.5, color='white', lw=2.5, ls='--')
ax.text(2.5, -0.65, 'LINE TO GAIN', color='white', ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(range(len(loc_lbl))); ax.set_xticklabels(loc_lbl, fontsize=9)
ax.set_yticks(range(len(sep_lbl))); ax.set_yticklabels(sep_lbl[::-1], fontsize=10)
ax.set_xlabel('Target position vs. the sticks at release', color=TEXT, fontsize=10)
ax.set_ylabel('Separation at release', color=TEXT, fontsize=10)
style(ax, '1. Decision grid: conversion rate')

# ── 2. Does more space rescue a short target? ──────────────
ax = fig.add_subplot(gs[1])
d['zone'] = np.select([d['vs_sticks'] < -5, d['vs_sticks'] < 0], ['5+ yds short', '0-5 yds short'], 'At / past sticks')
zc = {'5+ yds short': '#e74c3c', '0-5 yds short': '#f39c12', 'At / past sticks': '#2ecc71'}
for z, c in zc.items():
    s = d[d['zone'] == z].groupby('sep', observed=True)['converted'].agg(['mean', 'size']).reindex(sep_lbl)
    ax.plot(range(4), s['mean'] * 100, color=c, lw=3, marker='o', ms=9, label=f'{z} (n={int(s["size"].sum())})')
    for k, (m, n) in enumerate(zip(s['mean'], s['size'])):
        ax.text(k, m * 100 + 2.5, f'{m*100:.0f}%', ha='center', color=c, fontsize=9, fontweight='bold')
ax.set_xticks(range(4)); ax.set_xticklabels(sep_lbl)
ax.set_xlabel('Separation at release', color=TEXT, fontsize=10)
ax.set_ylabel('First-down conversion %', color=TEXT, fontsize=10)
ax.set_ylim(0, 75); ax.grid(color=GRID, lw=0.5, alpha=0.4)
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=9, loc='upper left')
style(ax, '2. More space does not rescue a deep checkdown')

# ── 3. Who converts when targeted short of the sticks ──────
ax = fig.add_subplot(gs[2])
sh = d[d['vs_sticks'] < 0].groupby(['displayName', 'officialPosition'])['converted'].agg(['size', 'mean']).reset_index()
sh = sh[sh['size'] >= 7].sort_values('mean')
show = pd.concat([sh.head(7), sh.tail(8)])
ax.barh(range(len(show)), show['mean'] * 100, color=[COL[p] for p in show['officialPosition']], zorder=3)
base = d[d['vs_sticks'] < 0]['converted'].mean() * 100
ax.axvline(base, color='white', lw=1.5, ls='--')
ax.text(base + 1, len(show) - 0.4, f'avg {base:.0f}%', color='white', fontsize=9)
for k, r in enumerate(show.itertuples()):
    ax.text(r.mean * 100 + 1, k, f'{r.mean*100:.0f}%  (n={r.size})', va='center', color=TEXT, fontsize=8.5)
ax.set_yticks(range(len(show))); ax.set_yticklabels(show['displayName'], fontsize=9)
ax.set_xlim(0, 95); ax.set_xlabel('Conversion % when targeted short of sticks', color=TEXT, fontsize=10)
ax.grid(axis='x', color=GRID, lw=0.5, alpha=0.4)
style(ax, '3. Who can turn a short catch into a first down\n(min 7 targets; small samples, illustrative)')
for p, c in COL.items(): ax.barh([], [], color=c, label=p)
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=9, loc='lower right')

fig.text(0.5, -0.03, f'{len(d):,} targeted 3rd/4th-down passes with 3+ yards to go · receiver parsed from play descriptions · '
         'position and separation (nearest defender, any position) measured at pass release, the last moment in the tracking data',
         color=TEXT, fontsize=8, ha='center', alpha=0.6)
plt.savefig('figures/fig1_3rd_down_sticks.png', dpi=150, bbox_inches='tight', facecolor=BG)
print('Saved figures/fig1_3rd_down_sticks.png')
print('\nConversion rate grid (rows = separation, cols = position vs sticks):')
print((rate * 100).round(0).to_string())
print('\nCell counts:')
print(cnt.to_string())
print(f'\nShort-of-sticks average conversion: {base:.1f}%')
print(show[['displayName', 'officialPosition', 'size', 'mean']].round(2).to_string(index=False))

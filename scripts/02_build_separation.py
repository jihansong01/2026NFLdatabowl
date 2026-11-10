"""Step 2: separation for every route runner at the moment of pass release.

Separation = distance (yards) from the route runner to the nearest defender of ANY
position (CB, S, LB, DL) at the pass_forward frame. Earlier drafts counted only CB/S,
which inflated RB separation because RBs are usually covered by linebackers.

Output: output/sep_all_defenders.csv
"""
import pandas as pd, numpy as np, glob
D = 'nfl-big-data-bowl-regional-event-data/data'
players = pd.read_csv(f'{D}/players.csv')
plays = pd.read_csv(f'{D}/plays.csv')
pff = pd.read_csv(f'{D}/pffScoutingData.csv')
cols = ['gameId','playId','nflId','frameId','x','y','event','team']
tr = pd.concat([pd.read_csv(f, usecols=cols) for f in sorted(glob.glob(f'{D}/tracking/*.csv'))], ignore_index=True)
pf = (tr[tr['event'].isin(['pass_forward','autoevent_passforward'])]
      .groupby(['gameId','playId'])['frameId'].min().reset_index().rename(columns={'frameId':'pf'}))
tr = tr.merge(pf, on=['gameId','playId'])
tr = tr[tr['frameId'] == tr['pf']]
tr = tr.merge(plays[['gameId','playId','possessionTeam']], on=['gameId','playId'])
routes = pff[pff['pff_role'] == 'Pass Route'][['gameId','playId','nflId']]
off = tr[(tr['team'] == tr['possessionTeam'])].merge(routes, on=['gameId','playId','nflId'])
dfn = tr[(tr['team'] != tr['possessionTeam']) & (tr['team'] != 'football')]
rows = []
for (g, p), grp in off.groupby(['gameId','playId']):
    d = dfn[(dfn['gameId'] == g) & (dfn['playId'] == p)][['x','y']].values
    if len(d) == 0: continue
    for _, r in grp.iterrows():
        rows.append((g, p, r['nflId'], np.linalg.norm(d - [r['x'], r['y']], axis=1).min()))
s = pd.DataFrame(rows, columns=['gameId','playId','nflId','sep_all'])
s = s.merge(players[['nflId','officialPosition']], on='nflId')
print(s.groupby('officialPosition')['sep_all'].agg(['count','mean','median']).round(2).loc[['RB','TE','WR']])
s.to_csv('output/sep_all_defenders.csv', index=False)

"""Step 3: per-target table for 3rd/4th down.

For each targeted 3rd/4th-down pass: where the target was relative to the line to gain,
how open he was, and whether the play converted. The tracking data ends shortly after
the throw, so position and separation are measured at pass release.

Output: output/sticks_targets.csv
"""
import pandas as pd, numpy as np, glob

D = 'nfl-big-data-bowl-regional-event-data/data'
players = pd.read_csv(f'{D}/players.csv')
plays = pd.read_csv(f'{D}/plays.csv')
t = pd.read_csv('output/pass_plays_with_targets.csv')
t = t[t['target_nflId'].notna() & (t['target_nflId'] != -1)].copy()
t['nflId'] = t['target_nflId'].astype(int)
t = t.merge(plays[['gameId', 'playId', 'possessionTeam', 'prePenaltyPlayResult']], on=['gameId', 'playId'])
t = t[t['down'].isin([3, 4])]
keys = t[['gameId', 'playId']].drop_duplicates()

cols = ['gameId', 'playId', 'nflId', 'frameId', 'x', 'y', 'event', 'team', 'playDirection']
tr = pd.concat([pd.read_csv(f, usecols=cols) for f in sorted(glob.glob(f'{D}/tracking/*.csv'))], ignore_index=True)
tr = tr.merge(keys, on=['gameId', 'playId'])

ev = tr[['gameId', 'playId', 'frameId', 'event']].dropna().drop_duplicates()
snap = ev[ev['event'] == 'ball_snap'].groupby(['gameId', 'playId'])['frameId'].min().rename('snap_f')
rel = ev[ev['event'].isin(['pass_forward', 'autoevent_passforward'])].groupby(['gameId', 'playId'])['frameId'].min().rename('rel_f')
arr = ev[ev['event'].isin(['pass_arrived', 'pass_outcome_caught', 'pass_outcome_incomplete',
                           'pass_outcome_interception', 'pass_outcome_touchdown'])]
f = pd.concat([snap, rel], axis=1).dropna().reset_index()
arr = arr.merge(f, on=['gameId', 'playId'])
arr = arr[arr['frameId'] > arr['rel_f']].groupby(['gameId', 'playId'])['frameId'].min().rename('arr_f').reset_index()
f = f.merge(arr, on=['gameId', 'playId'], how='left')
f['arr_f'] = f['arr_f'].fillna(f['rel_f'] + 10)  # fallback ~1s after release

# Line of scrimmage = ball x at snap
ball = tr[tr['team'] == 'football'].merge(f[['gameId', 'playId', 'snap_f']], on=['gameId', 'playId'])
los = ball[ball['frameId'] == ball['snap_f']][['gameId', 'playId', 'x']].rename(columns={'x': 'los_x'})
dirn = tr[['gameId', 'playId', 'playDirection']].drop_duplicates(['gameId', 'playId'])

t = t.merge(f, on=['gameId', 'playId']).merge(los, on=['gameId', 'playId']).merge(dirn, on=['gameId', 'playId'])
t['fwd'] = np.where(t['playDirection'] == 'right', 1, -1)

rows = []
for r in t.itertuples():
    p = tr[(tr['gameId'] == r.gameId) & (tr['playId'] == r.playId)]
    def at(frame):
        fr = p[p['frameId'] == frame]
        me = fr[fr['nflId'] == r.nflId]
        opp = fr[(fr['team'] != r.possessionTeam) & (fr['team'] != 'football')]
        if len(me) == 0 or len(opp) == 0: return None, None
        xy = me[['x', 'y']].values[0]
        return xy, np.linalg.norm(opp[['x', 'y']].values - xy, axis=1).min()
    xy_rel, sep_rel = at(r.rel_f)
    xy_arr, sep_arr = at(r.arr_f)
    if xy_rel is None: continue
    xy_t = xy_arr if xy_arr is not None else xy_rel
    rows.append(dict(gameId=r.gameId, playId=r.playId, nflId=r.nflId,
                     sep_release=sep_rel, sep_arrival=sep_arr,
                     depth=(xy_t[0] - r.los_x) * r.fwd))
out = pd.DataFrame(rows).merge(t[['gameId', 'playId', 'nflId', 'down', 'yardsToGo', 'passResult',
                                   'prePenaltyPlayResult', 'possessionTeam']], on=['gameId', 'playId', 'nflId'])
out = out.merge(players[['nflId', 'displayName', 'officialPosition']], on='nflId')
out['vs_sticks'] = out['depth'] - out['yardsToGo']          # negative = short of line to gain
out['converted'] = ((out['passResult'] == 'C') & (out['prePenaltyPlayResult'] >= out['yardsToGo'])).astype(int)
out.to_csv('output/sticks_targets.csv', index=False)
print(f'Saved output/sticks_targets.csv: {len(out)} 3rd/4th-down targets')

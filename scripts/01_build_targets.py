"""Step 1: identify the intended receiver on every pass play.

plays.csv has no target column, but playDescription names the receiver:
  "T.Brady pass short middle to M.Evans to TB 21 for 10 yards"
  "D.Prescott pass incomplete deep left to C.Lamb"
  "J.Goff pass short middle intended for T.Hockenson INTERCEPTED by ..."
The abbreviated name is matched to a route runner on that same play (pffScoutingData),
which resolves duplicates like "A.Brown" (Antonio Brown vs A.J. Brown).

Output: output/pass_plays_with_targets.csv
"""
import re
import numpy as np
import pandas as pd

DATA = 'nfl-big-data-bowl-regional-event-data/data'
plays = pd.read_csv(f'{DATA}/plays.csv')
players = pd.read_csv(f'{DATA}/players.csv')
pff = pd.read_csv(f'{DATA}/pffScoutingData.csv')

NAME = r"([A-Z][a-z]?\.[A-Za-z\-\']+)"
PATTERNS = [
    rf'pass\s+(?:incomplete\s+)?(deep|short)\s+(left|right|middle)\s+to\s+{NAME}',
    rf'pass\s+(?:incomplete\s+)?(deep|short)\s+()to\s+{NAME}',
    rf'pass\s+(deep|short)\s+(left|right|middle)\s+intended\s+for\s+{NAME}',
    rf'pass\s+(deep|short)\s+()intended\s+for\s+{NAME}',
    rf'()()intended\s+for\s+{NAME}',
]


def parse(desc):
    """Return (pass_depth, pass_dir, target_abbr) from a play description."""
    if pd.isna(desc):
        return None, None, None
    for pat in PATTERNS:
        m = re.search(pat, desc)
        if m:
            return m.group(1) or None, m.group(2) or None, m.group(3)
    return None, None, None


parsed = plays['playDescription'].apply(parse)
plays['pass_depth'] = parsed.str[0]
plays['pass_dir'] = parsed.str[1]
plays['target_abbr'] = parsed.str[2]

# "Mike Evans" -> "M.Evans" to match the play-description format
players['name_abbr'] = players['displayName'].apply(
    lambda n: f'{n.split()[0][0]}.{n.split()[-1]}' if isinstance(n, str) and len(n.split()) >= 2 else None)

routes = (pff[pff['pff_role'] == 'Pass Route'][['gameId', 'playId', 'nflId']]
          .merge(players[['nflId', 'officialPosition', 'name_abbr']], on='nflId'))
routes = routes[routes['officialPosition'].isin(['WR', 'TE', 'RB', 'FB'])]

# Normalise multi-letter first initials ("Aa.Rodgers", "Ju.Reid") to a single letter
plays['target_key'] = plays['target_abbr'].str.replace(r'^([A-Z])[a-z]?\.', r'\1.', regex=True)

cand = (plays[['gameId', 'playId', 'target_key']].dropna()
        .merge(routes, left_on=['gameId', 'playId', 'target_key'],
               right_on=['gameId', 'playId', 'name_abbr']))
counts = cand.groupby(['gameId', 'playId'])['nflId'].transform('size')
unique = cand[counts == 1][['gameId', 'playId', 'nflId']].rename(columns={'nflId': 'target_nflId'})

out = plays[plays['passResult'].isin(['C', 'I', 'IN'])].merge(unique, on=['gameId', 'playId'], how='left')
cols = ['gameId', 'playId', 'passResult', 'target_nflId', 'pass_depth', 'pass_dir', 'down', 'yardsToGo',
        'playResult', 'pff_passCoverage', 'pff_passCoverageType', 'offenseFormation', 'pff_playAction']
out[cols].to_csv('output/pass_plays_with_targets.csv', index=False)

matched = out['target_nflId'].notna()
print(f'Pass attempts: {len(out):,} | target matched: {matched.sum():,} ({matched.mean():.1%})')
print(out.assign(m=matched).groupby('passResult')['m'].mean().round(3).to_string())

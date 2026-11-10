"""
Data loading and preprocessing utilities
"""
import pandas as pd
import numpy as np
from pathlib import Path
import config

def load_base_data():
    """Load games, plays, players, and PFF data"""
    print("Loading base data files...")
    
    games = pd.read_csv(f'{config.DATA_DIR}/games.csv')
    plays = pd.read_csv(f'{config.DATA_DIR}/plays.csv')
    players = pd.read_csv(f'{config.DATA_DIR}/players.csv')
    pff = pd.read_csv(f'{config.DATA_DIR}/pffScoutingData.csv')
    
    print(f"  Games: {len(games)}")
    print(f"  Plays: {len(plays)}")
    print(f"  Players: {len(players)}")
    print(f"  PFF rows: {len(pff)}")
    
    return games, plays, players, pff

def get_skill_players(players):
    """Filter to skill position players"""
    skill = players[players['officialPosition'].isin(config.SKILL_POSITIONS)].copy()
    skill = skill[['nflId', 'officialPosition', 'displayName']]
    return skill

def load_tracking_data(game_ids):
    """Load tracking data for specified games"""
    print(f"\nLoading tracking data for {len(game_ids)} games...")
    
    dfs = []
    loaded = 0
    
    for gid in game_ids:
        try:
            filepath = f'{config.TRACKING_DIR}/tracking_{gid}.csv'
            df = pd.read_csv(filepath)
            dfs.append(df)
            loaded += 1
            if loaded % 10 == 0:
                print(f"  Loaded {loaded}/{len(game_ids)} games...")
        except FileNotFoundError:
            print(f"  Warning: Game {gid} tracking file not found")
            continue
    
    if len(dfs) == 0:
        raise ValueError("No tracking data loaded")
    
    tracking = pd.concat(dfs, ignore_index=True)
    print(f"  Total tracking rows: {len(tracking):,}")
    
    return tracking

def select_games_for_analysis(games, n_games=30):
    """Select games for analysis - prioritize early weeks for data quality"""
    games_sorted = games.sort_values(['week', 'gameId']).head(n_games)
    return games_sorted['gameId'].tolist()

def get_route_runners_and_coverage(pff, skill_players):
    """Identify route runners and coverage players"""
    # Route runners
    routes = pff[pff['pff_role'] == 'Pass Route'].merge(
        skill_players, 
        on='nflId', 
        how='inner'
    )
    
    # Coverage players by play
    coverage = pff[pff['pff_role'] == 'Coverage'].groupby(
        ['gameId', 'playId']
    )['nflId'].apply(list).to_dict()
    
    print(f"\nRoute runner instances: {len(routes)}")
    print(f"Plays with coverage data: {len(coverage)}")
    
    return routes, coverage

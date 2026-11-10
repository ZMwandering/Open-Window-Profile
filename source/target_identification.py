"""
Identify target receivers for each play
Priority: nflverse data > tracking-based inference
"""
import pandas as pd
import numpy as np
from event_detection import identify_target_from_tracking

def load_nflverse_targets():
    """
    Load target data from nflverse (if available)
    
    Returns:
        DataFrame or None if not available
    """
    try:
        # Try to load pre-downloaded nflverse data
        pbp = pd.read_csv('../data/nflverse_pbp_2021.csv')
        
        # Filter to relevant columns
        targets = pbp[pbp['week'].isin(range(1, 9))][
            ['old_game_id', 'play_id', 'receiver_player_id', 'receiver_player_name', 'complete_pass']
        ].copy()
        
        targets = targets[targets['receiver_player_id'].notna()]
        
        print(f"\nLoaded nflverse target data: {len(targets)} plays with identified targets")
        
        return targets
        
    except FileNotFoundError:
        print("\nWarning: nflverse data not found, will use tracking-based identification only")
        return None

def identify_targets_for_plays(tracking, valid_plays, route_runners):
    """
    Identify target receiver for each play
    
    Priority:
    1. nflverse data (if available)
    2. Tracking-based inference (ball proximity at pass_arrived)
    
    Returns:
        dict: {(gameId, playId): target_nflId}
    """
    print("\nIdentifying target receivers...")
    
    # Try nflverse first
    nflverse_targets = load_nflverse_targets()
    
    targets = {}
    method_counts = {'nflverse': 0, 'tracking': 0, 'failed': 0}
    
    for _, play_info in valid_plays.iterrows():
        game_id = play_info['gameId']
        play_id = play_info['playId']
        throw_frame = play_info['throw_frame']
        
        target_id = None
        
        # Method 1: nflverse
        if nflverse_targets is not None:
            nflverse_match = nflverse_targets[
                (nflverse_targets['old_game_id'] == game_id) &
                (nflverse_targets['play_id'] == play_id)
            ]
            
            if len(nflverse_match) > 0:
                target_id = nflverse_match.iloc[0]['receiver_player_id']
                method_counts['nflverse'] += 1
        
        # Method 2: Tracking inference
        if target_id is None:
            play_track = tracking[
                (tracking['gameId'] == game_id) &
                (tracking['playId'] == play_id)
            ]
            
            play_route_ids = route_runners[
                (route_runners['gameId'] == game_id) &
                (route_runners['playId'] == play_id)
            ]['nflId'].tolist()
            
            target_id = identify_target_from_tracking(
                play_track,
                throw_frame,
                play_route_ids
            )
            
            if target_id:
                method_counts['tracking'] += 1
            else:
                method_counts['failed'] += 1
        
        if target_id:
            targets[(game_id, play_id)] = target_id
    
    print(f"  Target identification:")
    print(f"    nflverse: {method_counts['nflverse']}")
    print(f"    tracking: {method_counts['tracking']}")
    print(f"    failed: {method_counts['failed']}")
    print(f"  Success rate: {len(targets)/len(valid_plays)*100:.1f}%")
    
    return targets

def add_target_labels_to_metrics(metrics_df, targets):
    """
    Add 'is_target' column to metrics dataframe
    
    Args:
        metrics_df: DataFrame with gameId, playId, nflId
        targets: dict {(gameId, playId): target_nflId}
    
    Returns:
        DataFrame with added 'is_target' column
    """
    def check_target(row):
        target_id = targets.get((row['gameId'], row['playId']))
        return row['nflId'] == target_id if target_id else False
    
    metrics_df['is_target'] = metrics_df.apply(check_target, axis=1)
    
    n_targets = metrics_df['is_target'].sum()
    print(f"\n  Labeled {n_targets} targeted receivers in metrics dataset")
    
    return metrics_df

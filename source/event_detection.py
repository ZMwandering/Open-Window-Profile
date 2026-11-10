"""
Event detection for snap and throw frames
"""
import pandas as pd
import numpy as np
import config

def detect_snap_frame(play_df):
    """Detect ball snap frame"""
    for keyword in config.SNAP_EVENTS:
        matches = play_df[
            play_df['event'].notna() & 
            play_df['event'].str.lower().str.contains(keyword, case=False, na=False)
        ]
        if len(matches) > 0:
            return matches.iloc[0]['frameId']
    return None

def detect_throw_frame(play_df):
    """Detect pass forward frame"""
    for keyword in config.THROW_EVENTS:
        matches = play_df[
            play_df['event'].notna() & 
            play_df['event'].str.lower().str.contains(keyword, case=False, na=False)
        ]
        if len(matches) > 0:
            return matches.iloc[0]['frameId']
    return None

def identify_valid_pass_plays(tracking):
    """
    Identify plays with valid snap and throw events
    
    Returns: DataFrame with columns [gameId, playId, snap_frame, throw_frame]
    """
    print("\nIdentifying valid pass plays...")
    
    valid_plays = []
    
    for game_id in tracking['gameId'].unique():
        game_plays = tracking[tracking['gameId'] == game_id]['playId'].unique()
        
        for play_id in game_plays:
            play_track = tracking[
                (tracking['gameId'] == game_id) & 
                (tracking['playId'] == play_id)
            ]
            
            snap_frame = detect_snap_frame(play_track)
            throw_frame = detect_throw_frame(play_track)
            
            # Valid only if both events exist and in correct order
            if snap_frame and throw_frame and throw_frame > snap_frame:
                valid_plays.append({
                    'gameId': game_id,
                    'playId': play_id,
                    'snap_frame': snap_frame,
                    'throw_frame': throw_frame,
                    'window_frames': throw_frame - snap_frame,
                    'window_seconds': (throw_frame - snap_frame) / config.FRAMES_PER_SECOND
                })
    
    valid_df = pd.DataFrame(valid_plays)
    
    print(f"  Valid pass plays: {len(valid_df)}")
    print(f"  Avg window: {valid_df['window_seconds'].mean():.2f}s")
    print(f"  Median window: {valid_df['window_seconds'].median():.2f}s")
    
    return valid_df

def identify_target_from_tracking(play_df, throw_frame, route_runner_ids):
    """
    Identify target receiver from tracking data
    Find player closest to ball at pass_arrived or throw frame
    """
    # Try pass_arrived first
    arrived_events = play_df[
        play_df['event'].notna() & 
        play_df['event'].str.lower().isin([e.lower() for e in config.ARRIVED_EVENTS])
    ]
    
    target_frame = arrived_events.iloc[0]['frameId'] if len(arrived_events) > 0 else throw_frame
    
    # Get ball position
    ball_pos = play_df[
        (play_df['frameId'] == target_frame) & 
        (play_df['team'] == 'football')
    ][['x', 'y']]
    
    if len(ball_pos) == 0:
        return None
    
    ball_x, ball_y = ball_pos.iloc[0]['x'], ball_pos.iloc[0]['y']
    
    # Get route runners positions
    routes_pos = play_df[
        (play_df['frameId'] == target_frame) & 
        (play_df['nflId'].isin(route_runner_ids))
    ][['nflId', 'x', 'y']]
    
    if len(routes_pos) == 0:
        return None
    
    # Calculate distances
    routes_pos['distance'] = np.sqrt(
        (routes_pos['x'] - ball_x)**2 + 
        (routes_pos['y'] - ball_y)**2
    )
    
    # Return closest player
    return routes_pos.loc[routes_pos['distance'].idxmin(), 'nflId']

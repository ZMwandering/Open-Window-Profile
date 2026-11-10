"""
Statistical analysis and classification
"""
import pandas as pd
import numpy as np
import config

def aggregate_player_stats(metrics_df, min_routes=10):
    """
    Aggregate metrics by player
    
    Args:
        metrics_df: DataFrame with per-play metrics
        min_routes: Minimum routes to include player
    
    Returns:
        DataFrame with player-level statistics by position
    """
    print(f"\nAggregating player statistics (min {min_routes} routes)...")
    
    player_stats = metrics_df.groupby(['nflId', 'player', 'position']).agg(
        routes=('playId', 'count'),
        avg_owa=('owa', 'mean'),
        std_owa=('owa', 'std'),
        avg_la=('la', 'mean'),
        std_la=('la', 'std'),
        avg_throw_sep=('throw_sep', 'mean'),
        avg_window=('window_seconds', 'mean'),
        targets=('is_target', 'sum'),
        target_rate=('is_target', 'mean')
    ).reset_index()
    
    # Filter by minimum routes
    player_stats = player_stats[player_stats['routes'] >= min_routes].copy()
    
    print(f"  Players by position:")
    print(player_stats['position'].value_counts().to_string())
    
    return player_stats

def classify_receivers_by_position(player_stats):
    """
    Classify receivers into quadrants using within-position medians
    
    Quadrants:
    1. Sustained Open (High OWA, High LA)
    2. Early Open (High OWA, Low LA)
    3. Late Open (Low OWA, High LA)
    4. Limited (Low OWA, Low LA)
    
    Returns:
        DataFrame with added columns: owa_class, la_class, quadrant
    """
    print("\nClassifying receivers by quadrants...")
    
    classified = []
    
    for pos in player_stats['position'].unique():
        pos_players = player_stats[player_stats['position'] == pos].copy()
        
        # Calculate position-specific medians
        owa_median = pos_players['avg_owa'].median()
        la_median = pos_players['avg_la'].median()
        
        # Classify
        pos_players['owa_class'] = pos_players['avg_owa'].apply(
            lambda x: 'High' if x >= owa_median else 'Low'
        )
        pos_players['la_class'] = pos_players['avg_la'].apply(
            lambda x: 'High' if x >= la_median else 'Low'
        )
        
        # Quadrant assignment
        def assign_quadrant(row):
            if row['owa_class'] == 'High' and row['la_class'] == 'High':
                return 'Sustained Open'
            elif row['owa_class'] == 'High' and row['la_class'] == 'Low':
                return 'Early Open'
            elif row['owa_class'] == 'Low' and row['la_class'] == 'High':
                return 'Late Open'
            else:
                return 'Limited'
        
        pos_players['quadrant'] = pos_players.apply(assign_quadrant, axis=1)
        
        # Store medians for reference
        pos_players['position_owa_median'] = owa_median
        pos_players['position_la_median'] = la_median
        
        classified.append(pos_players)
        
        print(f"  {pos}: OWA median={owa_median:.2f}, LA median={la_median:.2f}")
    
    result = pd.concat(classified, ignore_index=True)
    
    print("\n  Quadrant distribution:")
    print(result['quadrant'].value_counts().to_string())
    
    return result

def analyze_targeted_vs_nontargeted(metrics_df):
    """
    Compare targeted vs non-targeted receivers
    
    Returns:
        dict with comparison statistics
    """
    print("\nAnalyzing targeted vs non-targeted receivers...")
    
    targeted = metrics_df[metrics_df['is_target'] == True]
    not_targeted = metrics_df[metrics_df['is_target'] == False]
    
    comparison = {
        'targeted': {
            'n': len(targeted),
            'avg_owa': targeted['owa'].mean(),
            'avg_la': targeted['la'].mean(),
            'avg_throw_sep': targeted['throw_sep'].mean()
        },
        'not_targeted': {
            'n': len(not_targeted),
            'avg_owa': not_targeted['owa'].mean(),
            'avg_la': not_targeted['la'].mean(),
            'avg_throw_sep': not_targeted['throw_sep'].mean()
        }
    }
    
    # Calculate differences
    comparison['difference'] = {
        'owa': comparison['targeted']['avg_owa'] - comparison['not_targeted']['avg_owa'],
        'la': comparison['targeted']['avg_la'] - comparison['not_targeted']['avg_la'],
        'throw_sep': comparison['targeted']['avg_throw_sep'] - comparison['not_targeted']['avg_throw_sep']
    }
    
    print(f"  Targeted: n={comparison['targeted']['n']}, "
          f"OWA={comparison['targeted']['avg_owa']:.2f}, "
          f"LA={comparison['targeted']['avg_la']:.3f}")
    
    print(f"  Not-targeted: n={comparison['not_targeted']['n']}, "
          f"OWA={comparison['not_targeted']['avg_owa']:.2f}, "
          f"LA={comparison['not_targeted']['avg_la']:.3f}")
    
    print(f"  Difference: OWA={comparison['difference']['owa']:.2f}, "
          f"LA={comparison['difference']['la']:.3f}")
    
    return comparison

def calculate_within_play_ranks(metrics_df):
    """
    Calculate each receiver's rank within their play for OWA and LA
    
    Returns:
        DataFrame with added columns: owa_rank, la_rank
    """
    print("\nCalculating within-play rankings...")
    
    metrics_df['owa_rank'] = metrics_df.groupby(['gameId', 'playId'])['owa'].rank(
        ascending=False, method='min'
    )
    
    metrics_df['la_rank'] = metrics_df.groupby(['gameId', 'playId'])['la'].rank(
        ascending=False, method='min'
    )
    
    # How often is the targeted receiver ranked #1?
    targeted = metrics_df[metrics_df['is_target'] == True]
    
    owa_rank1_pct = (targeted['owa_rank'] == 1).mean() * 100
    la_rank1_pct = (targeted['la_rank'] == 1).mean() * 100
    
    print(f"  Targeted receiver ranked #1 in OWA: {owa_rank1_pct:.1f}%")
    print(f"  Targeted receiver ranked #1 in LA: {la_rank1_pct:.1f}%")
    
    return metrics_df

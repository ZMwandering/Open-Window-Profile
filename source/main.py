"""
Main execution script for Open Window Profile analysis
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Import modules
import config
from data_loader import (
    load_base_data, 
    get_skill_players,
    load_tracking_data,
    select_games_for_analysis,
    get_route_runners_and_coverage
)
from event_detection import identify_valid_pass_plays
from metrics import calculate_metrics_for_all_plays
from target_identification import identify_targets_for_plays, add_target_labels_to_metrics
from analysis import (
    aggregate_player_stats,
    classify_receivers_by_position,
    analyze_targeted_vs_nontargeted,
    calculate_within_play_ranks
)
from visualization import create_all_visualizations

def main():
    """
    Execute complete Open Window Profile analysis pipeline
    """
    print("="*70)
    print("OPEN WINDOW PROFILE ANALYSIS")
    print("Beyond Separation at the Moment of the Throw")
    print("="*70)
    
    # Phase 1: Data Loading
    print("\n" + "="*70)
    print("PHASE 1: DATA LOADING")
    print("="*70)
    
    games, plays, players, pff = load_base_data()
    skill_players = get_skill_players(players)
    
    # Select games for analysis
    game_ids = select_games_for_analysis(games, config.N_GAMES_TO_ANALYZE)
    print(f"\nSelected {len(game_ids)} games for analysis")
    
    # Load tracking data
    tracking = load_tracking_data(game_ids)
    
    # Get route runners and coverage
    route_runners, coverage = get_route_runners_and_coverage(pff, skill_players)
    
    # Phase 2: Event Detection
    print("\n" + "="*70)
    print("PHASE 2: EVENT DETECTION")
    print("="*70)
    
    valid_plays = identify_valid_pass_plays(tracking)
    
    if len(valid_plays) < 100:
        print(f"\nWarning: Only {len(valid_plays)} valid plays found. Consider adding more games.")
    
    # Phase 3: Target Identification
    print("\n" + "="*70)
    print("PHASE 3: TARGET IDENTIFICATION")
    print("="*70)
    
    targets = identify_targets_for_plays(tracking, valid_plays, route_runners)
    
    # Phase 4: Metric Calculation
    print("\n" + "="*70)
    print("PHASE 4: METRIC CALCULATION")
    print("="*70)
    
    metrics_df = calculate_metrics_for_all_plays(
        tracking,
        valid_plays,
        route_runners,
        coverage,
        threshold=config.DEFAULT_THRESHOLD
    )
    
    # Add target labels
    metrics_df = add_target_labels_to_metrics(metrics_df, targets)
    
    # Calculate within-play ranks
    metrics_df = calculate_within_play_ranks(metrics_df)
    
    # Phase 5: Analysis
    print("\n" + "="*70)
    print("PHASE 5: STATISTICAL ANALYSIS")
    print("="*70)
    
    player_stats = aggregate_player_stats(metrics_df, config.MIN_ROUTES_PER_PLAYER)
    player_stats = classify_receivers_by_position(player_stats)
    
    comparison = analyze_targeted_vs_nontargeted(metrics_df)
    
    # Phase 6: Visualization
    print("\n" + "="*70)
    print("PHASE 6: VISUALIZATION")
    print("="*70)
    
    create_all_visualizations(metrics_df, player_stats, config.OUTPUT_DIR)
    
    # Phase 7: Export Results
    print("\n" + "="*70)
    print("PHASE 7: EXPORT RESULTS")
    print("="*70)
    
    import os
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Save datasets
    metrics_df.to_csv(f'{config.OUTPUT_DIR}/metrics_detailed.csv', index=False)
    player_stats.to_csv(f'{config.OUTPUT_DIR}/player_statistics.csv', index=False)
    
    print(f"  Saved: {config.OUTPUT_DIR}/metrics_detailed.csv")
    print(f"  Saved: {config.OUTPUT_DIR}/player_statistics.csv")
    
    # Print summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    print(f"\nTotal plays analyzed: {len(valid_plays)}")
    print(f"Total receiver-play instances: {len(metrics_df)}")
    print(f"Players with {config.MIN_ROUTES_PER_PLAYER}+ routes: {len(player_stats)}")
    
    print("\nTop 5 by Open Window Area:")
    print(player_stats.nlargest(5, 'avg_owa')[
        ['player', 'position', 'routes', 'avg_owa', 'avg_la', 'quadrant']
    ].to_string(index=False))
    
    print("\nTop 5 by Late Availability:")
    print(player_stats.nlargest(5, 'avg_la')[
        ['player', 'position', 'routes', 'avg_owa', 'avg_la', 'quadrant']
    ].to_string(index=False))
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nKey outputs:")
    print(f"  - {config.OUTPUT_DIR}/quadrant_classification.png")
    print(f"  - {config.OUTPUT_DIR}/targeted_comparison.png")
    print(f"  - {config.OUTPUT_DIR}/position_distributions.png")
    print(f"  - {config.OUTPUT_DIR}/metrics_detailed.csv")
    print(f"  - {config.OUTPUT_DIR}/player_statistics.csv")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

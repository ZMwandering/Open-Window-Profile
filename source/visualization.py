"""
Visualization functions for Open Window Profile
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import config

sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 150

def plot_quadrant_scatter(player_stats, output_path):
    """
    Create main 2D scatter plot: OWA vs LA with quadrants
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    positions = ['WR', 'TE', 'RB']
    
    for idx, pos in enumerate(positions):
        ax = axes[idx]
        pos_data = player_stats[player_stats['position'] == pos]
        
        if len(pos_data) == 0:
            continue
        
        # Get position-specific median lines
        owa_median = pos_data['position_owa_median'].iloc[0]
        la_median = pos_data['position_la_median'].iloc[0]
        
        # Plot points
        for _, row in pos_data.iterrows():
            marker = config.TARGETED_MARKER if row['target_rate'] > 0.1 else config.NOT_TARGETED_MARKER
            size = row['routes'] * 2
            alpha = 0.7 if row['target_rate'] > 0 else 0.4
            
            ax.scatter(
                row['avg_owa'], 
                row['avg_la'],
                s=size,
                marker=marker,
                color=config.POSITION_COLORS[pos],
                alpha=alpha,
                edgecolors='black',
                linewidth=0.5
            )
        
        # Add median lines
        ax.axvline(x=owa_median, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
        ax.axhline(y=la_median, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
        
        # Quadrant labels
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        label_x_low = xlim[0] + (owa_median - xlim[0]) / 2
        label_x_high = owa_median + (xlim[1] - owa_median) / 2
        label_y_low = ylim[0] + (la_median - ylim[0]) / 2
        label_y_high = la_median + (ylim[1] - la_median) / 2
        
        ax.text(label_x_high, label_y_high, 'Sustained\\nOpen', 
                ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
        ax.text(label_x_high, label_y_low, 'Early\\nOpen',
                ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
        ax.text(label_x_low, label_y_high, 'Late\\nOpen',
                ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
        ax.text(label_x_low, label_y_low, 'Limited',
                ha='center', va='center', fontsize=9, alpha=0.5, style='italic')
        
        # Annotate extremes
        if len(pos_data) > 0:
            top_owa = pos_data.nlargest(1, 'avg_owa').iloc[0]
            top_la = pos_data.nlargest(1, 'avg_la').iloc[0]
            
            ax.annotate(
                top_owa['player'].split()[-1],
                xy=(top_owa['avg_owa'], top_owa['avg_la']),
                xytext=(10, 10), textcoords='offset points',
                fontsize=8, ha='left',
                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', lw=0.5)
            )
        
        ax.set_xlabel('Open Window Area (yard-seconds)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Late Availability (0-1)', fontsize=11, fontweight='bold')
        ax.set_title(f'{pos} (n={len(pos_data)})', fontsize=12, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()

def plot_targeted_comparison(metrics_df, output_path):
    """
    Create box plots comparing targeted vs non-targeted receivers
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    metrics = ['owa', 'la', 'throw_sep']
    titles = ['Open Window Area', 'Late Availability', 'Throw Separation']
    ylabels = ['yard-seconds', 'proportion (0-1)', 'yards']
    
    for idx, (metric, title, ylabel) in enumerate(zip(metrics, titles, ylabels)):
        ax = axes[idx]
        
        data = [
            metrics_df[metrics_df['is_target'] == True][metric].dropna(),
            metrics_df[metrics_df['is_target'] == False][metric].dropna()
        ]
        
        bp = ax.boxplot(
            data,
            labels=['Targeted', 'Not Targeted'],
            patch_artist=True,
            widths=0.6
        )
        
        # Color boxes
        colors = ['#2ecc71', '#95a5a6']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add mean markers
        means = [d.mean() for d in data]
        ax.plot([1, 2], means, 'ro-', markersize=8, linewidth=2, label='Mean')
        
        # Add text with difference
        diff = means[0] - means[1]
        diff_pct = (diff / means[1] * 100) if means[1] != 0 else 0
        ax.text(
            1.5, ax.get_ylim()[1] * 0.95,
            f'Δ = {diff:+.2f} ({diff_pct:+.1f}%)',
            ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()

def plot_position_distributions(player_stats, output_path):
    """
    Create distributions of OWA and LA by position
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    
    positions = ['WR', 'TE', 'RB']
    metrics = ['avg_owa', 'avg_la']
    titles = ['Open Window Area', 'Late Availability']
    
    for row_idx, (metric, title) in enumerate(zip(metrics, titles)):
        for col_idx, pos in enumerate(positions):
            ax = axes[row_idx, col_idx]
            pos_data = player_stats[player_stats['position'] == pos]
            
            if len(pos_data) > 0:
                ax.hist(
                    pos_data[metric],
                    bins=15,
                    color=config.POSITION_COLORS[pos],
                    alpha=0.7,
                    edgecolor='black'
                )
                
                # Add median line
                median = pos_data[metric].median()
                ax.axvline(median, color='red', linestyle='--', linewidth=2, label=f'Median: {median:.2f}')
                ax.legend()
            
            if row_idx == 0:
                ax.set_title(pos, fontsize=12, fontweight='bold')
            if col_idx == 0:
                ax.set_ylabel(title, fontsize=10)
            ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()

def create_all_visualizations(metrics_df, player_stats, output_dir):
    """
    Generate all visualization outputs
    """
    print("\nGenerating visualizations...")
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Panel 1: Quadrant scatter
    plot_quadrant_scatter(
        player_stats,
        f'{output_dir}/quadrant_classification.png'
    )
    
    # Panel 2: Targeted vs Not-targeted comparison
    plot_targeted_comparison(
        metrics_df,
        f'{output_dir}/targeted_comparison.png'
    )
    
    # Panel 3: Position distributions
    plot_position_distributions(
        player_stats,
        f'{output_dir}/position_distributions.png'
    )
    
    print("  All visualizations complete")

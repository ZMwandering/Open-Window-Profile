"""
Configuration file for Open Window Profile analysis
"""

# Data paths
DATA_DIR = '../data'
TRACKING_DIR = f'{DATA_DIR}/tracking'
OUTPUT_DIR = '../outputs'

# Analysis parameters
SEPARATION_THRESHOLDS = [2.0, 3.0, 4.0]  # yards - sensitivity analysis
DEFAULT_THRESHOLD = 3.0  # yards - primary analysis

LA_WINDOW = 1.0  # seconds - late availability window before throw

# Position filters
SKILL_POSITIONS = ['WR', 'TE', 'RB', 'FB']

# Sampling
MIN_ROUTES_PER_PLAYER = 10  # minimum routes to include player in analysis
N_GAMES_TO_ANALYZE = 30  # number of games for main analysis (balance speed vs sample size)

# Visualization
POSITION_COLORS = {
    'WR': '#1f77b4',  # blue
    'TE': '#2ca02c',  # green
    'RB': '#d62728',  # red
    'FB': '#ff7f0e'   # orange
}

TARGETED_MARKER = 'o'
NOT_TARGETED_MARKER = 'x'

# Event detection keywords
SNAP_EVENTS = ['ball_snap', 'ballsnap', 'autoevent_ballsnap']
THROW_EVENTS = ['pass_forward', 'passforward', 'autoevent_passforward']
ARRIVED_EVENTS = ['pass_arrived', 'pass_outcome_caught']

# Frame rate
FRAMES_PER_SECOND = 10

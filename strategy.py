
import pandas as pd
from utils import apply_indicators, detect_candlestick_patterns

def detect_levels(df, window=20):
    support, resistance = [], []
    if len(df) < 2 * window:
        return support, resistance  # Not enough data

    for i in range(window, len(df) - window):
        low_range = df['Low'].iloc[i - window:i + window]
        high_range = df['High'].iloc[i - window:i + window]
        current_low = df['Low'].iloc[i]
        current_high = df['High'].iloc[i]

        if pd.isna(current_low) or pd.isna(current_high):
            continue

        if current_low == low_range.min():
            support.append((df.index[i], current_low))
        if current_high == high_range.max():
            resistance.append((df.index[i], current_high))
    return support, resistance

def detect_zones(df):
    zones = []
    for i in range(2, len(df) - 2):
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]
        if pd.isna(low) or pd.isna(high):
            continue

        if low < df['Low'].iloc[i - 1] and low < df['Low'].iloc[i + 1]:
            zones.append(('demand', df.index[i], low))
        elif high> df['High'].iloc[i - 1] and high> df['High'].iloc[i + 1]:
            zones.append(('supply', df.index[i], high))
    return zones

def detect_liquidity_sweeps(df):
    sweeps = []
    for i in range(1, len(df) - 1):
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]
        close = df['Close'].iloc[i]
        open_ = df['Open'].iloc[i]
        if pd.isna(low) or pd.isna(high) or pd.isna(close) or pd.isna(open_):
            continue

        if low < df['Low'].iloc[i - 1] and close> open_:
            sweeps.append(('bullish_sweep', df.index[i]))
        elif high> df['High'].iloc[i - 1] and close < open_:
            sweeps.append(('bearish_sweep', df.index[i]))
    return sweeps

def calculate_reward_ratio(df):
    try:
        last_price = df['Close'].iloc[-1]
        potential_upside = df['High'].max() - last_price
        potential_downside = last_price - df['Low'].min()
        if potential_downside == 0:
            return 0
        return round(potential_upside / potential_downside, 2)
    except Exception:
        return 0

def generate_signal(df):
    if df.empty or len(df) < 30:
        return 'HOLD'

    df = apply_indicators(df)
    support, resistance = detect_levels(df)
    zones = detect_zones(df)
    sweeps = detect_liquidity_sweeps(df)
    patterns = detect_candlestick_patterns(df)
    reward_ratio = calculate_reward_ratio(df)

    last_price = df['Close'].iloc[-1]
    signal = 'HOLD'

    # Indicator-based logic
    if df['rsi'].iloc[-1] < 30 and df['macd'].iloc[-1]> 0 and reward_ratio>= 2.5:
        signal = 'BUY'
    elif df['rsi'].iloc[-1]> 70 and df['macd'].iloc[-1] < 0 and reward_ratio>= 2.5:
        signal = 'SELL'

    # Zone-based logic
    for zone_type, _, level in zones[-5:]:
        if zone_type == 'demand' and last_price < level and reward_ratio>= 2.5:
            signal = 'BUY'
        elif zone_type == 'supply' and last_price> level and reward_ratio>= 2.5:
            signal = 'SELL'

    # Liquidity sweep logic
    for sweep_type, _ in sweeps[-5:]:
        if sweep_type == 'bullish_sweep' and reward_ratio>= 2.5:
            signal = 'BUY'
        elif sweep_type == 'bearish_sweep' and reward_ratio>= 2.5:
            signal = 'SELL'

    # Candlestick pattern logic
    for pattern, _ in patterns[-5:]:
        if pattern.startswith('bullish') and reward_ratio>= 2.5:
            signal = 'BUY'
        elif pattern.startswith('bearish') and reward_ratio>= 2.5:

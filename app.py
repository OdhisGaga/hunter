```python
import streamlit as st
import yfinance as yf
from strategy import generate_signal

st.set_page_config(page_title="Xgaga Tech Signals", layout="wide")
st.title("📊 Xgaga Tech Signals")

st.markdown("This site analyzes USD/AUD using demand/supply zones, support/resistance, candlestick patterns, and liquidity sweeps.")

df = yf.download('AUDUSD=X', interval='1h', period='30d')
df = df[['Open', 'High', 'Low', 'Close']]

signal = generate_signal(df)

st.metric("Current Signal", signal)
st.line_chart(df['Close'])
```


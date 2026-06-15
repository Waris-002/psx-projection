# --- UPDATED TIMELINE GENERATION LOGIC ---
recent_data = df.tail(60)
last_date = recent_data.index[-1]

# Check if today's date (June 15) matches the last historical index date
current_date_normalized = pd.Timestamp.now().normalize()

# If the last historical date is already today, start the projection from tomorrow
if last_date.normalize() >= current_date_normalized:
    start_projection_date = last_date + pd.Timedelta(days=1)
else:
    # If today is a trading day that ended but isn't in yfinance yet, 
    # we force the projection to begin on the next business day (June 16)
    if current_date_normalized.dayofweek < 5:  # It's a weekday (Mon-Fri)
        start_projection_date = current_date_normalized + pd.Timedelta(days=1)
    else:
        start_projection_date = last_date + pd.Timedelta(days=1)

# Generate business days strictly onward from the calculated start target
future_dates = pd.date_range(start=start_projection_date, periods=forecast_days, freq='B')
future_y_values = [df['Close'].iloc[-1] + (slope * i) for i in range(1, forecast_days + 1)]

# Ensure the visual anchor connects smoothly without overriding current business hours
fig = go.Figure()
# ... (your standard line traces here) ...

# Plot the predictive slope starting strictly from the onward date parameters
fig.add_trace(go.Scatter(
    x=[recent_data.index[-1]] + list(future_dates),
    y=[recent_data['Close'].iloc[-1]] + future_y_values,
    name=f'{forecast_days}-Day Predictive Vector',
    line=dict(color='#00bfff', width=2.5, dash='dot')
))

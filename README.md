# Advanced Flask Stock Market Dashboard

This project is an advanced, mobile-friendly Flask dashboard for tracking stocks (uses Alpha Vantage).
It includes:
- Watchlist (add stocks)
- Trending stocks
- Alerts (keeps a simple in-memory alert history)
- Telegram integration (optional) for alerts

## How to deploy
1. Add your environment variables in Railway or your host:
   - alpha_vantage_api_key
   - telegram_bot_token (optional)
   - telegram_chat_id (optional)

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run locally:
   ```
   python app.py
   ```

4. For Railway/Heroku deploy, use the provided Procfile.

## Notes
- This project stores data in-memory; for persistent tracking across restarts, connect a database.
- Alpha Vantage free tier has rate limits. For many requests, consider caching or a paid plan.

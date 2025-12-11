# Telegram Expense Tracker Bot 💰

Automatically track your expenses by simply sending messages to your Telegram bot. The bot extracts amounts and categories, then logs everything to Google Sheets.

## Features

✨ **Smart Category Detection** - Automatically categorizes expenses based on keywords
💵 **Amount Extraction** - Extracts numerical values from natural language messages
📊 **Google Sheets Integration** - All expenses logged automatically with timestamps
🚀 **Simple Usage** - Just send a message like "Lunch 250" and you're done!

## Categories

The bot recognizes these expense categories:

- 🍔 **Food** - lunch, dinner, coffee, restaurant, cafe, snack
- 🚗 **Transport** - uber, taxi, metro, fuel, petrol, parking
- 🛒 **Groceries** - grocery, vegetables, fruits, supermarket
- 🛍️ **Shopping** - clothes, shoes, amazon, flipkart
- 🎬 **Entertainment** - movie, netflix, subscription, game
- 💡 **Bills** - electricity, internet, rent, phone bill
- 🏥 **Health** - medicine, doctor, hospital, pharmacy, gym
- 📦 **Other** - everything else

## Quick Start

### Prerequisites

1. **Telegram Bot Token** - Get one from [@BotFather](https://t.me/botfather)
2. **Google Cloud Account** - For Google Sheets API access
3. **Python 3.8+** - Installed on your system

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up credentials:**

   - Copy `.env.example` to `.env`
   - Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed credential setup

4. **Configure environment variables in `.env`:**

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

5. **Create your Google Sheet with these column headers:**

```
Timestamp | Date | Category | Amount | Message
```

6. **Share your Google Sheet with the service account email**

### Running the Bot

```bash
python expense_bot.py
```

You should see: `✅ Bot is running! Press Ctrl+C to stop.`

## Usage Examples

Simply send messages to your bot:

| Message                    | Category      | Amount |
| -------------------------- | ------------- | ------ |
| "Lunch 250"                | Food          | ₹250   |
| "Uber to office 180"       | Transport     | ₹180   |
| "Groceries 1500"           | Groceries     | ₹1500  |
| "Coffee ₹75"               | Food          | ₹75    |
| "Netflix subscription 199" | Entertainment | ₹199   |
| "Gym membership 2000"      | Health        | ₹2000  |

The bot will:

1. Extract the amount
2. Detect the category from keywords
3. Log to Google Sheets
4. Send you a confirmation with details

## Bot Commands

- `/start` - Welcome message and introduction
- `/help` - Usage instructions and examples

## Google Sheet Structure

Your expenses will be logged with:

| Column    | Description        | Example             |
| --------- | ------------------ | ------------------- |
| Timestamp | Full date and time | 2025-12-10 21:30:45 |
| Date      | Date only          | 2025-12-10          |
| Category  | Detected category  | Food                |
| Amount    | Expense amount     | 250                 |
| Message   | Original message   | Lunch 250           |

## Troubleshooting

**Bot doesn't respond:**

- Check if bot is running
- Verify TELEGRAM_BOT_TOKEN in `.env`
- Ensure you started a chat with your bot on Telegram

**Expenses not saving to Google Sheets:**

- Verify GOOGLE_SHEETS_ID is correct
- Check that `credentials.json` exists
- Ensure Google Sheet is shared with service account email
- Check console for error messages

**Category not detected correctly:**

- Add more keywords to the message
- Check CATEGORY_KEYWORDS in `expense_bot.py` to see available keywords
- Default category "Other" is used if no match found

## Customization

### Adding Custom Categories

Edit `expense_bot.py` and add to the `CATEGORY_KEYWORDS` dictionary:

```python
CATEGORY_KEYWORDS = {
    'Food': ['lunch', 'dinner', ...],
    'YourCategory': ['keyword1', 'keyword2', ...],
    # ... more categories
}
```

### Changing Currency Symbol

Update the emoji responses in the `handle_message` function.

## Security Notes

⚠️ **Never commit these files:**

- `.env` - Contains your bot token and credentials
- `credentials.json` - Your Google service account key

These are already listed in `.gitignore`.

## Need Help?

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions, including:

- How to create a Telegram bot
- How to set up Google Sheets API
- How to get your service account credentials

## License

Free to use for personal expense tracking!

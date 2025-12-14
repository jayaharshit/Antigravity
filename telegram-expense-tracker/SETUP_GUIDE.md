# Complete Setup Guide for Telegram Expense Tracker Bot

This guide walks you through every step needed to get your expense tracker bot up and running.

## Table of Contents

1. [Create Telegram Bot](#1-create-telegram-bot)
2. [Set Up Google Cloud Project](#2-set-up-google-cloud-project)
3. [Create Google Sheet](#3-create-google-sheet)
4. [Configure the Bot](#4-configure-the-bot)
5. [Run the Bot](#5-run-the-bot)

---

## 1. Create Telegram Bot

### Step 1.1: Open BotFather

1. Open Telegram on your phone or desktop
2. Search for `@BotFather` (official bot from Telegram)
3. Start a chat with BotFather

### Step 1.2: Create Your Bot

1. Send the command: `/newbot`
2. BotFather will ask for a **name** for your bot
   - Example: "My Expense Tracker"
3. Then it will ask for a **username** (must end with 'bot')
   - Example: "my_expense_tracker_bot"

### Step 1.3: Save Your Bot Token

- BotFather will give you a **Bot Token** that looks like:
  ```
  1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
  ```
- **SAVE THIS TOKEN** - You'll need it later
- ⚠️ Keep it secret! Anyone with this token can control your bot

### Step 1.4: Find Your Bot

1. Search for your bot's username in Telegram
2. Click **Start** to activate the bot
3. Keep this chat open - you'll test here later

---

## 2. Set Up Google Cloud Project

### Step 2.1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click **Select a project** → **New Project**
4. Enter project name: "Expense Tracker Bot"
5. Click **Create**

### Step 2.2: Enable Google Sheets API

1. In the Google Cloud Console, use the search bar
2. Search for "Google Sheets API"
3. Click **Enable**

### Step 2.3: Enable Google Drive API

1. Search for "Google Drive API"
2. Click **Enable**
   - (This is needed to access your Google Sheets)

### Step 2.4: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **+ Create Service Account**
3. Fill in details:
   - **Service account name**: expense-bot
   - **Service account ID**: (auto-filled)
4. Click **Create and Continue**
5. Skip optional steps, click **Done**

### Step 2.5: Create Service Account Key

1. Find your new service account in the list
2. Click on it to open details
3. Go to **Keys** tab
4. Click **Add Key** → **Create New Key**
5. Choose **JSON** format
6. Click **Create**
7. A JSON file will download automatically
8. **Rename this file to `credentials.json`**
9. **Move it to your project folder** (same folder as `expense_bot.py`)

### Step 2.6: Copy Service Account Email

1. Open the `credentials.json` file
2. Find the line with `"client_email":`
   ```json
   "client_email": "expense-bot@your-project.iam.gserviceaccount.com"
   ```
3. **Copy this email address** - you'll need it in the next section

---

## 3. Create Google Sheet

### Step 3.1: Create New Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **+ Blank** to create a new spreadsheet
3. Name it: "My Expenses" (or your preferred name)

### Step 3.2: Set Up Column Headers

In the first row, enter these exact headers:

| A         | B    | C        | D      | E       |
| --------- | ---- | -------- | ------ | ------- |
| Timestamp | Date | Category | Amount | Message |

### Step 3.3: Share with Service Account

1. Click the **Share** button (top right)
2. Paste the **service account email** you copied earlier
   - Example: `expense-bot@your-project.iam.gserviceaccount.com`
3. Set permission to **Editor**
4. **Uncheck** "Notify people"
5. Click **Share**

### Step 3.4: Get Sheet ID

1. Look at the URL of your Google Sheet:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
   ```
2. **Copy the SHEET_ID** from the URL
   - It's the long string of characters between `/d/` and `/edit`
3. **Save this ID** - you'll need it next

---

## 4. Configure the Bot

### Step 4.1: Verify File Structure

Make sure your project folder contains:

```
Personal Finance Tracker/
├── expense_bot.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── SETUP_GUIDE.md
└── credentials.json  ← Your downloaded file should be here
```

### Step 4.2: Create .env File

1. Copy `.env.example` to create a new file named `.env`
   - On Windows: `copy .env.example .env`
   - On Mac/Linux: `cp .env.example .env`

### Step 4.3: Fill in .env File

Open `.env` in a text editor and fill in your values:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GOOGLE_SHEETS_ID=your_sheet_id_from_url
GOOGLE_CREDENTIALS_FILE=credentials.json
```

**Replace:**

- `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` with your actual bot token
- `your_sheet_id_from_url` with your actual Google Sheet ID

### Step 4.4: Install Dependencies

Open a terminal/command prompt in your project folder and run:

```bash
pip install -r requirements.txt
```

Wait for all packages to install.

---

## 5. Run the Bot

### Step 5.1: Start the Bot

In your terminal, run:

```bash
python expense_bot.py
```

You should see:

```
Starting Expense Tracker Bot...
✅ Bot is running! Press Ctrl+C to stop.
```

### Step 5.2: Test the Bot

1. Go to your Telegram bot chat
2. Send a test message:
   ```
   Lunch 250
   ```
3. The bot should respond with:

   ```
   ✅ Expense recorded!

   🍔 Category: Food
   💰 Amount: ₹250.00
   📝 Note: Lunch 250
   ```

### Step 5.3: Verify Google Sheets

1. Open your Google Sheet
2. You should see a new row with:
   - Timestamp (current date/time)
   - Date (current date)
   - Category (Food)
   - Amount (250)
   - Message (Lunch 250)

### Step 5.4: Try More Examples

Test different categories:

- `Uber 180` (Transport)
- `Groceries 1500` (Groceries)
- `Netflix 199` (Entertainment)
- `Coffee ₹75` (Food)

---

## Troubleshooting

### Bot doesn't start

- **Error: "TELEGRAM_BOT_TOKEN not found"**
  - Check that `.env` file exists (not `.env.example`)
  - Verify the token is correct in `.env`

### Bot doesn't respond on Telegram

- Make sure the bot is running (terminal shows "Bot is running")
- Try sending `/start` command first
- Verify you copied the bot token correctly

### "Failed to save expense to Google Sheets"

- **Check credentials.json exists** in the project folder
- **Verify Sheet ID** is correct in `.env`
- **Confirm sharing**: Open Google Sheet → Click Share → Service account email should be listed
- Check the terminal for detailed error messages

### Module not found errors

- Run `pip install -r requirements.txt` again
- Ensure you're using Python 3.8 or higher: `python --version`

---

## Running the Bot 24/7

To keep your bot running continuously:

### Option 1: Run on Local Computer

Keep the terminal window open and the script running.

### Option 2: Deploy to Cloud (Recommended)

- **Free options:**
  - [Google Cloud Run](https://cloud.google.com/run)
  - [Railway.app](https://railway.app)
  - [Render.com](https://render.com)
  - [PythonAnywhere](https://www.pythonanywhere.com)

### Option 3: Run on Raspberry Pi

If you have a Raspberry Pi, you can run the bot there 24/7.

---

## Security Reminders

⚠️ **Never share:**

- Your `.env` file
- Your `credentials.json` file
- Your bot token

✅ **Safe to share:**

- Your bot's username
- Your Google Sheet (with others, not the service account)

---

## Next Steps

Once everything works:

1. Add more test expenses to see patterns
2. Create charts in Google Sheets for visualization
3. Customize categories in `expense_bot.py`
4. Set up data validation or formulas in your sheet

## Need More Help?

If you encounter issues not covered here:

1. Check the error message in the terminal
2. Verify each step was completed correctly
3. Make sure all credentials are correct
4. Try creating a new bot/sheet and starting fresh

Happy expense tracking! 💰📊

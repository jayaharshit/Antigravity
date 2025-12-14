# Deploying Telegram Bot to Google Cloud Run (24/7 Operation)

This guide shows you how to deploy your expense tracker bot to Google Cloud Run for continuous 24/7 operation.

## Why Google Cloud Run?

- **Always Free Tier**: 2 million requests/month free
- **Serverless**: No server management needed
- **Automatic scaling**: Scales to zero when not in use
- **Simple deployment**: Deploy with a single command

## Prerequisites

- Google Cloud account (free tier available)
- Bot already working locally
- `.env` file configured with your credentials

---

## Step 1: Prepare Your Project for Deployment

### 1.1 Create a Dockerfile

Create a file named `Dockerfile` in your project folder:

```dockerfile
# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY expense_bot.py .
COPY credentials.json .

# Run the bot
CMD ["python", "expense_bot.py"]
```

### 1.2 Create a .dockerignore file

Create `.dockerignore` to exclude unnecessary files:

```
.env
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
README.md
SETUP_GUIDE.md
```

### 1.3 Update Your Bot for Cloud Environment

Your bot is already configured to use environment variables, which is perfect for cloud deployment!

---

## Step 2: Set Up Google Cloud

### 2.1 Install Google Cloud CLI

**Windows:**

1. Download installer: https://cloud.google.com/sdk/docs/install
2. Run the installer
3. Open a new terminal and verify: `gcloud --version`

**Mac/Linux:**

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud --version
```

### 2.2 Initialize Google Cloud

```bash
gcloud init
```

Follow the prompts to:

- Log in to your Google account
- Select or create a project
- Set default region (choose closest to you, e.g., `asia-south1` for India)

### 2.3 Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## Step 3: Deploy to Google Cloud Run

### 3.1 Navigate to Your Project

```bash
cd "d:\Jaya Files\Personal FInance Tracker"
```

### 3.2 Deploy with One Command

```bash
gcloud run deploy expense-tracker-bot ^
  --source . ^
  --platform managed ^
  --region asia-south1 ^
  --allow-unauthenticated ^
  --set-env-vars TELEGRAM_BOT_TOKEN=your_token_here,GOOGLE_SHEETS_ID=your_sheet_id,MONTHLY_BUDGET=50000
```

**Replace:**

- `your_token_here` with your actual Telegram bot token
- `your_sheet_id` with your Google Sheet ID
- `50000` with your monthly budget amount

**Note:** You'll need to include your `credentials.json` in the deployment. See alternative method below for better security.

### 3.3 Alternative: Using Secret Manager (Recommended)

For better security, use Google Cloud Secret Manager:

```bash
# Create secrets
echo -n "your_bot_token" | gcloud secrets create telegram-bot-token --data-file=-
echo -n "your_sheet_id" | gcloud secrets create google-sheets-id --data-file=-
echo -n "50000" | gcloud secrets create monthly-budget --data-file=-

# Upload credentials.json as secret
gcloud secrets create google-credentials --data-file=credentials.json

# Deploy with secrets
gcloud run deploy expense-tracker-bot ^
  --source . ^
  --platform managed ^
  --region asia-south1 ^
  --update-secrets TELEGRAM_BOT_TOKEN=telegram-bot-token:latest,GOOGLE_SHEETS_ID=google-sheets-id:latest,MONTHLY_BUDGET=monthly-budget:latest
```

---

## Step 4: Verify Deployment

### 4.1 Check Deployment Status

After deployment completes, you'll see output like:

```
Service [expense-tracker-bot] revision [expense-tracker-bot-00001-xxx] has been deployed
Service URL: https://expense-tracker-bot-xxxxx-as.a.run.app
```

### 4.2 View Logs

```bash
gcloud run services logs read expense-tracker-bot --region asia-south1
```

You should see:

```
Starting Expense Tracker Bot...
Bot is running! Press Ctrl+C to stop.
```

### 4.3 Test the Bot

1. Open Telegram
2. Send `/start` to your bot
3. Send a test expense: `Test 100`
4. Check if it logs to your Google Sheet

---

## Step 5: Monitor and Manage

### View Real-Time Logs

```bash
gcloud run services logs tail expense-tracker-bot --region asia-south1
```

### Check Bot Status

```bash
gcloud run services describe expense-tracker-bot --region asia-south1
```

### Update the Bot

To deploy updates after code changes:

```bash
gcloud run deploy expense-tracker-bot ^
  --source . ^
  --region asia-south1
```

### Stop the Bot

```bash
gcloud run services delete expense-tracker-bot --region asia-south1
```

---

## Alternative: Google Compute Engine (VM)

If you prefer a traditional VM approach:

### Create a VM Instance

```bash
gcloud compute instances create expense-bot-vm ^
  --zone=asia-south1-a ^
  --machine-type=e2-micro ^
  --image-family=debian-11 ^
  --image-project=debian-cloud
```

### SSH into the VM

```bash
gcloud compute ssh expense-bot-vm --zone=asia-south1-a
```

### Install Python and Dependencies

```bash
sudo apt update
sudo apt install python3-pip -y
```

### Upload Your Files

On your local machine:

```bash
gcloud compute scp --recurse "d:\Jaya Files\Personal FInance Tracker\*" expense-bot-vm:~/bot --zone=asia-south1-a
```

### Run the Bot

```bash
cd ~/bot
pip3 install -r requirements.txt
nohup python3 expense_bot.py > bot.log 2>&1 &
```

### Make it Auto-Start on Reboot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/expense-bot.service
```

Add:

```ini
[Unit]
Description=Telegram Expense Tracker Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/bot
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/bot/expense_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable expense-bot
sudo systemctl start expense-bot
sudo systemctl status expense-bot
```

---

## Cost Comparison

### Google Cloud Run (Recommended)

- **Cost**: FREE for most use cases
- **Free tier**: 2M requests/month
- **Your usage**: ~0 requests (bot polls Telegram)
- **Actual cost**: $0/month

### Google Compute Engine (e2-micro)

- **Free tier**: 1 e2-micro instance free in US regions
- **Cost in Asia**: ~$7-10/month
- **More control, always running**

---

## Troubleshooting

### Bot Not Responding

1. Check logs:

```bash
gcloud run services logs read expense-tracker-bot --region asia-south1
```

2. Verify environment variables are set correctly

3. Test credentials locally first

### Deployment Fails

- Ensure Docker is installed (for Cloud Run)
- Check that all files are in the project directory
- Verify `credentials.json` exists

### Exceeded Free Tier

- Cloud Run charges after 2M requests (unlikely for this bot)
- Monitor usage: https://console.cloud.google.com/billing

---

## Recommended: Cloud Run

For your expense bot, **Google Cloud Run is the best option**:

- ✅ Free
- ✅ No server management
- ✅ Automatic updates
- ✅ Simple deployment

The bot will run 24/7 and cost you $0/month in most cases!

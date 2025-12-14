"""
Telegram Expense Tracker Bot
---------------------------
Automatically extracts expense amounts and categories from messages
and logs them to Google Sheets.
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import gspread
from google.oauth2.service_account import Credentials

# Python 3.13 compatibility fix for python-telegram-bot
import telegram.ext._updater as updater_module
if hasattr(updater_module.Updater, '__slots__'):
    # Remove __slots__ to allow dynamic attributes in Python 3.13
    updater_module.Updater.__slots__ = ()

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
MONTHLY_BUDGET = float(os.getenv('MONTHLY_BUDGET', '0'))

# Category keywords mapping
CATEGORY_KEYWORDS = {
    'Food': ['lunch', 'dinner', 'breakfast', 'food', 'restaurant', 'cafe', 'coffee', 'snack', 'meal', 'eat', 'omelette', 'omlette','juice', 'tea'],
    'Transport': ['uber', 'taxi', 'bus', 'metro', 'fuel', 'petrol', 'parking', 'ola', 'auto', 'train', 'flight'],
    'Groceries': ['grocery', 'groceries', 'vegetables', 'fruits', 'supermarket', 'veggies', 'market'],
    'Shopping': ['shopping', 'clothes', 'shoes', 'amazon', 'flipkart', 'shop', 'purchase'],
    'Entertainment': ['movie', 'netflix', 'subscription', 'game', 'entertainment', 'spotify', 'prime'],
    'Bills': ['electricity', 'water', 'internet', 'phone', 'bill', 'rent', 'emi', 'recharge'],
    'Health': ['medicine', 'doctor', 'hospital', 'pharmacy', 'health', 'gym', 'medical','haircut']
}

# Initialize Google Sheets client
def init_google_sheets():
    """Initialize and return Google Sheets client"""
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error initializing Google Sheets: {e}")
        return None

# Extract amount from message
def extract_amount(text):
    """Extract numerical amount from text"""
    # Remove currency symbols and find numbers (including decimals)
    text_cleaned = re.sub(r'[₹$€£,]', '', text)
    numbers = re.findall(r'\d+\.?\d*', text_cleaned)
    
    if numbers:
        return float(numbers[0])
    return None

# Detect category from message
def detect_category(text):
    """Detect category based on keywords in message"""
    text_lower = text.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return 'Other'

# Get monthly expenses total
def get_monthly_expenses():
    """Calculate total expenses for current month"""
    try:
        client = init_google_sheets()
        if not client:
            return 0
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        
        # Get all records
        records = sheet.get_all_records()
        
        # Get current month and year
        now = datetime.now()
        current_month = now.strftime('%Y-%m')
        
        # Sum expenses for current month
        total = 0
        for record in records:
            if record.get('Date', '').startswith(current_month):
                total += float(record.get('Amount', 0))
        
        return total
    except Exception as e:
        print(f"Error calculating monthly expenses: {e}")
        return 0

# Add expense to Google Sheets
def add_expense_to_sheet(amount, category, message):
    """Add expense record to Google Sheets"""
    try:
        client = init_google_sheets()
        if not client:
            return False
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        
        # Get current timestamp
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        date = now.strftime('%Y-%m-%d')
        
        # Append row: Timestamp, Date, Category, Amount, Message
        row = [timestamp, date, category, amount, message]
        sheet.append_row(row)
        
        return True
    except Exception as e:
        print(f"Error adding to sheet: {e}")
        return False

# Get recent transactions
def get_recent_transactions(limit=10):
    """Get the most recent transactions from Google Sheets"""
    try:
        client = init_google_sheets()
        if not client:
            return []
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        
        # Get all records
        records = sheet.get_all_records()
        
        # Return last N records with row numbers (row 2 = first data row)
        recent = []
        total_rows = len(records)
        start_index = max(0, total_rows - limit)
        
        for i in range(start_index, total_rows):
            record = records[i]
            row_number = i + 2  # +2 because: +1 for header, +1 for 0-indexing
            recent.append({
                'row': row_number,
                'date': record.get('Date', ''),
                'category': record.get('Category', ''),
                'amount': record.get('Amount', 0),
                'message': record.get('Message', '')
            })
        
        return recent
    except Exception as e:
        print(f"Error getting recent transactions: {e}")
        return []

# Delete transaction by row number
def delete_transaction_by_row(row_number):
    """Delete a transaction from Google Sheets by row number"""
    try:
        client = init_google_sheets()
        if not client:
            return False, "Failed to connect to Google Sheets"
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        
        # Validate row number (must be >= 2, as row 1 is header)
        if row_number < 2:
            return False, "Invalid row number"
        
        # Get the row data before deleting (for confirmation)
        try:
            row_data = sheet.row_values(row_number)
        except:
            return False, "Row not found"
        
        # Delete the row
        sheet.delete_rows(row_number)
        
        return True, row_data
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return False, str(e)

# Find and delete transaction by details
def find_and_delete_transaction(amount, category, message):
    """Find and delete a transaction by matching its details"""
    try:
        client = init_google_sheets()
        if not client:
            return False, "Failed to connect to Google Sheets"
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        
        # Get all records
        records = sheet.get_all_records()
        
        # Find matching transaction (search from most recent)
        for i in range(len(records) - 1, -1, -1):
            record = records[i]
            if (float(record.get('Amount', 0)) == amount and
                record.get('Category', '') == category and
                record.get('Message', '') == message):
                
                # Found the transaction, delete it
                row_number = i + 2  # +2 for header and 0-indexing
                sheet.delete_rows(row_number)
                return True, record
        
        return False, "Transaction not found"
    except Exception as e:
        print(f"Error finding and deleting transaction: {e}")
        return False, str(e)

def delete_all_transactions():
    """Delete all transactions from Google Sheets (keeps header row)"""
    try:
        client = init_google_sheets()
        if not client:
            return False, 0
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        
        # Get all values to count transactions (excluding header)
        all_values = sheet.get_all_values()
        transaction_count = len(all_values) - 1  # Subtract header row
        
        if transaction_count <= 0:
            return True, 0  # No transactions to delete
        
        # Delete all rows except the header (row 1)
        # Delete from bottom to top to avoid row number shifts
        sheet.delete_rows(2, len(all_values))
        
        return True, transaction_count
    except Exception as e:
        print(f"Error deleting all transactions: {e}")
        return False, 0

def update_transaction(amount, category, message, new_amount=None, new_category=None):
    """Update a transaction's amount and/or category in Google Sheets"""
    try:
        client = init_google_sheets()
        if not client:
            return False, "Failed to connect to Google Sheets", None
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        all_values = sheet.get_all_values()
        
        # Search for transaction from most recent backwards (skip header)
        for i in range(len(all_values) - 1, 0, -1):
            row = all_values[i]
            
            # Match: Timestamp, Date, Category, Amount, Message
            if (len(row) >= 5 and 
                float(row[3]) == amount and 
                row[2] == category and 
                row[4] == message):
                
                # Found the transaction at row i+1 (1-indexed)
                row_number = i + 1
                
                # Store old values
                old_amount = float(row[3])
                old_category = row[2]
                old_message = row[4]
                
                # Determine what changed
                amount_changed = new_amount is not None and new_amount != old_amount
                category_changed = new_category is not None and new_category != old_category
                
                if not amount_changed and not category_changed:
                    return False, "No changes detected", None
                
                # Update the row
                if amount_changed:
                    sheet.update_cell(row_number, 4, new_amount)  # Column 4 is Amount
                    
                    # Also update the message to reflect new amount
                    # Replace old amount with new amount in the message
                    import re
                    new_message = re.sub(r'\b' + str(int(old_amount)) + r'\b', str(int(new_amount)), old_message)
                    if new_message != old_message:
                        sheet.update_cell(row_number, 5, new_message)  # Column 5 is Message
                
                if category_changed:
                    sheet.update_cell(row_number, 3, new_category)  # Column 3 is Category
                
                # Return old and new values
                return True, {
                    'old_amount': old_amount,
                    'new_amount': new_amount if amount_changed else old_amount,
                    'old_category': old_category,
                    'new_category': new_category if category_changed else old_category,
                    'message': message,
                    'amount_changed': amount_changed,
                    'category_changed': category_changed
                }, None
        
        return False, "Transaction not found", None
        
    except Exception as e:
        print(f"Error updating transaction: {e}")
        return False, str(e), None



# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
Welcome to Expense Tracker Bot! 💰

Simply send me a message with your expense, and I'll automatically track it for you!

**Examples:**
• Lunch 250
• Uber 180
• Groceries 1500
• Coffee ₹150

**Categories I understand:**
🍔 Food | 🚗 Transport | 🛒 Groceries
🛍️ Shopping | 🎬 Entertainment | 💡 Bills
🏥 Health | 📦 Other

I'll extract the amount and category automatically!
"""
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
**How to use:**
Just send me any message with an expense amount!

**Examples:**
• "Lunch 250" → Food: ₹250
• "Uber to office 180" → Transport: ₹180
• "Bought groceries 1500" → Groceries: ₹1500

**Categories:**
Food, Transport, Groceries, Shopping, Entertainment, Bills, Health, Other

**Commands:**
/start - Start the bot
/help - Show this help message
/balance - Check monthly balance
/recent - View recent transactions
/delete - Delete a transaction
/deleteall - ⚠️ Delete ALL transactions (requires confirmation)
"""
    await update.message.reply_text(help_message)

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
    total_expenses = get_monthly_expenses()
    remaining = MONTHLY_BUDGET - total_expenses
    
    now = datetime.now()
    month_name = now.strftime('%B %Y')
    
    balance_message = f"""
**Monthly Budget Report - {month_name}**

💰 Budget: ₹{MONTHLY_BUDGET:,.2f}
💸 Spent: ₹{total_expenses:,.2f}
📊 Remaining: ₹{remaining:,.2f}

"""
    
    if remaining < 0:
        balance_message += "⚠️ You've exceeded your monthly budget!"
    elif remaining < MONTHLY_BUDGET * 0.2:
        balance_message += "⚠️ Warning: Less than 20% budget remaining!"
    else:
        percentage = (remaining / MONTHLY_BUDGET) * 100
        balance_message += f"✅ You have {percentage:.1f}% of your budget left."
    
    await update.message.reply_text(balance_message, parse_mode='Markdown')

async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /recent command - show recent transactions"""
    transactions = get_recent_transactions(limit=10)
    
    if not transactions:
        await update.message.reply_text(
            "📭 No transactions found.\n"
            "Start by logging an expense!"
        )
        return
    
    # Build message with transaction list
    message = "📋 **Recent Transactions:**\n\n"
    
    for idx, txn in enumerate(transactions, 1):
        emoji_map = {
            'Food': '🍔', 'Transport': '🚗', 'Groceries': '🛒',
            'Shopping': '🛍️', 'Entertainment': '🎬', 'Bills': '💡',
            'Health': '🏥', 'Other': '📦'
        }
        emoji = emoji_map.get(txn['category'], '📦')
        
        message += f"{idx}. {emoji} **{txn['category']}** - ₹{txn['amount']:.2f}\n"
        message += f"   {txn['date']} | {txn['message']}\n\n"
    
    message += "💡 To delete: `/delete <number>`\nExample: `/delete 3`"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delete command - delete a transaction"""
    # Check if row number was provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please specify which transaction to delete.\n\n"
            "Usage: `/delete <number>`\n"
            "Example: `/delete 3`\n\n"
            "Use `/recent` to see your transactions.",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Get the transaction number from user (1-based)
        txn_number = int(context.args[0])
        
        # Get recent transactions to map user number to row
        transactions = get_recent_transactions(limit=10)
        
        if txn_number < 1 or txn_number > len(transactions):
            await update.message.reply_text(
                f"❌ Invalid transaction number: {txn_number}\n\n"
                f"Please choose a number between 1 and {len(transactions)}.\n"
                "Use `/recent` to see your transactions.",
                parse_mode='Markdown'
            )
            return
        
        # Get the actual row number (0-indexed list to row number)
        txn = transactions[txn_number - 1]
        row_number = txn['row']
        
        # Delete the transaction
        success, result = delete_transaction_by_row(row_number)
        
        if success:
            await update.message.reply_text(
                f"✅ **Transaction deleted!**\n\n"
                f"🗑️ Removed: {txn['category']} - ₹{txn['amount']:.2f}\n"
                f"📝 {txn['message']}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to delete transaction.\n"
                f"Error: {result}"
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid number format.\n\n"
            "Usage: `/delete <number>`\n"
            "Example: `/delete 3`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error deleting transaction: {str(e)}"
        )

async def deleteall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /deleteall command - delete all transactions with confirmation"""
    try:
        # Get transaction count
        client = init_google_sheets()
        if not client:
            await update.message.reply_text(
                "❌ Failed to connect to Google Sheets.\n"
                "Please check your configuration."
            )
            return
        
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        all_values = sheet.get_all_values()
        transaction_count = len(all_values) - 1  # Exclude header
        
        if transaction_count <= 0:
            await update.message.reply_text(
                "ℹ️ No transactions to delete.\n"
                "Your sheet is already empty!"
            )
            return
        
        # Store pending confirmation in user context
        context.user_data['pending_deleteall'] = True
        context.user_data['deleteall_count'] = transaction_count
        
        await update.message.reply_text(
            f"⚠️ **DANGER: DELETE ALL TRANSACTIONS** ⚠️\n\n"
            f"You are about to delete **{transaction_count} transaction(s)**!\n"
            f"This action **CANNOT BE UNDONE**.\n\n"
            f"To confirm, reply with exactly:\n"
            f"```\nCONFIRM DELETE ALL\n```\n\n"
            f"To cancel, send any other message or wait 60 seconds.",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error checking transactions: {str(e)}"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and extract expense data"""
    text = update.message.text
    message_id = update.message.message_id
    
    # Initialize processed messages tracking
    if 'processed_messages' not in context.bot_data:
        context.bot_data['processed_messages'] = set()
    
    # Check if we've already processed this message (prevent duplicates)
    if message_id in context.bot_data['processed_messages']:
        print(f"DEBUG: Skipping duplicate message ID: {message_id}")
        return
    
    # Mark this message as processed
    context.bot_data['processed_messages'].add(message_id)
    
    # Clean up old processed message IDs (keep only last 100)
    if len(context.bot_data['processed_messages']) > 100:
        # Convert to list, remove oldest entries, convert back to set
        msg_list = list(context.bot_data['processed_messages'])
        context.bot_data['processed_messages'] = set(msg_list[-100:])
    
    # Check if user is confirming delete all
    if context.user_data.get('pending_deleteall'):
        if text.strip().upper() == 'CONFIRM DELETE ALL':
            # User confirmed deletion
            success, count = delete_all_transactions()
            
            # Clear pending status
            context.user_data['pending_deleteall'] = False
            
            if success:
                await update.message.reply_text(
                    f"✅ **All transactions deleted!**\n\n"
                    f"🗑️ Removed {count} transaction(s) from Google Sheets.\n"
                    f"Your expense tracker is now empty.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Failed to delete transactions.\n"
                    "Please try again or check your Google Sheets connection."
                )
            return
        else:
            # User sent something else - cancel the delete all
            context.user_data['pending_deleteall'] = False
            await update.message.reply_text(
                "❌ Delete all cancelled.\n"
                "Your transactions are safe!"
            )
            return

    
    # Check if this is a reply to a bot message with "Delete"
    if update.message.reply_to_message:
        with open('debug.txt', 'a') as f:
            f.write(f"DEBUG: Detected reply message. Text: '{text}'\n")
            f.write(f"DEBUG: Replied to message ID: {update.message.reply_to_message.message_id}\n")
            f.write(f"DEBUG: Is reply from bot: {update.message.reply_to_message.from_user.is_bot}\n")
        
        # Check if user wants to delete the transaction (check if 'delete' is in the message)
        if 'delete' in text.lower():
            with open('debug.txt', 'a') as f:
                f.write("DEBUG: 'delete' keyword found in message\n")
            
            # Initialize bot_data if it doesn't exist
            if 'transactions' not in context.bot_data:
                context.bot_data['transactions'] = {}
            
            with open('debug.txt', 'a') as f:
                f.write(f"DEBUG: Stored transactions: {list(context.bot_data['transactions'].keys())}\n")
            
            # Get the message ID being replied to
            replied_message_id = update.message.reply_to_message.message_id
            
            # Check if this message has stored transaction data
            if replied_message_id in context.bot_data['transactions']:
                with open('debug.txt', 'a') as f:
                    f.write(f"DEBUG: Found transaction data for message ID {replied_message_id}\n")
                print(f"DEBUG: Found transaction data for message ID {replied_message_id}")
                txn_data = context.bot_data['transactions'][replied_message_id]
                
                # Delete the transaction
                success, result = find_and_delete_transaction(
                    txn_data['amount'],
                    txn_data['category'],
                    txn_data['message']
                )
                
                if success:
                    await update.message.reply_text(
                        f"✅ **Transaction deleted!**\n\n"
                        f"🗑️ Removed: {txn_data['category']} - ₹{txn_data['amount']:.2f}\n"
                        f"📝 {txn_data['message']}",
                        parse_mode='Markdown'
                    )
                    # Clean up stored data
                    del context.bot_data['transactions'][replied_message_id]
                else:
                    await update.message.reply_text(
                        f"❌ Failed to delete transaction.\n"
                        f"Error: {result}"
                    )
                return
            else:
                print(f"DEBUG: No transaction data found for message ID {replied_message_id}")
                await update.message.reply_text(
                    "❌ Could not find transaction data for this message.\n"
                    "You can only delete recent transactions by replying with 'Delete'."
                )
                return
        
        # NEW: Check if this is an edit request (reply with number or category)
        # This should be at the same level as the delete check
        replied_message_id = update.message.reply_to_message.message_id
        if replied_message_id in context.bot_data.get('transactions', {}):
            txn_data = context.bot_data['transactions'][replied_message_id]
            
            # Try to detect what user wants to edit
            new_amount = extract_amount(text)
            new_category = detect_category(text)
            
            # Determine if this is an edit
            is_edit = False
            update_amount = False
            update_category = False
            
            # Check if it's primarily a number (amount edit)
            # Remove numbers and check if remaining text is short
            import re
            text_without_number = re.sub(r'\d+\.?\d*', '', text).strip()
            if new_amount and len(text_without_number) < 15:
                # Likely an amount edit
                is_edit = True
                update_amount = True
            
            # Check if category changed from original
            if new_category != 'Other' and new_category != txn_data['category']:
                is_edit = True
                update_category = True
            
            if is_edit:
                # Perform update
                success, result, _ = update_transaction(
                    txn_data['amount'],
                    txn_data['category'],
                    txn_data['message'],
                    new_amount=new_amount if update_amount else None,
                    new_category=new_category if update_category else None
                )
                
                if success:
                    # Build confirmation message
                    emoji_map = {
                        'Food': '🍔',
                        'Transport': '🚗',
                        'Groceries': '🛒',
                        'Shopping': '🛍️',
                        'Entertainment': '🎬',
                        'Bills': '💡',
                        'Health': '🏥',
                        'Other': '📦'
                    }
                    
                    changes = []
                    if result['category_changed']:
                        old_emoji = emoji_map.get(result['old_category'], '📦')
                        new_emoji = emoji_map.get(result['new_category'], '📦')
                        changes.append(f"{old_emoji} {result['old_category']} → {new_emoji} {result['new_category']}")
                    
                    if result['amount_changed']:
                        changes.append(f"₹{result['old_amount']:.2f} → ₹{result['new_amount']:.2f}")
                    
                    await update.message.reply_text(
                        f"✅ **Transaction updated!**\n\n"
                        f"📝 {result['message']}\n"
                        f"{chr(10).join(changes)}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"❌ {result}"
                    )
                return
    
    # Extract amount
    amount = extract_amount(text)
    
    if amount is None:
        await update.message.reply_text(
            "❌ I couldn't find an amount in your message.\n"
            "Please include a number. Example: 'Lunch 250'"
        )
        return
    
    # Detect category
    category = detect_category(text)
    
    # Add to Google Sheets
    success = add_expense_to_sheet(amount, category, text)
    
    if success:
        # Send confirmation
        emoji_map = {
            'Food': '🍔',
            'Transport': '🚗',
            'Groceries': '🛒',
            'Shopping': '🛍️',
            'Entertainment': '🎬',
            'Bills': '💡',
            'Health': '🏥',
            'Other': '📦'
        }
        
        emoji = emoji_map.get(category, '📦')
        
        # Calculate monthly balance
        total_expenses = get_monthly_expenses()
        remaining = MONTHLY_BUDGET - total_expenses
        
        balance_info = ""
        if MONTHLY_BUDGET > 0:
            balance_info = f"\n\n💰 **Monthly Balance:** ₹{remaining:,.2f} / ₹{MONTHLY_BUDGET:,.2f}"
            if remaining < 0:
                balance_info += "\n⚠️ Budget exceeded!"
            elif remaining < MONTHLY_BUDGET * 0.2:
                balance_info += "\n⚠️ Low budget warning!"
        
        confirmation_msg = await update.message.reply_text(
            f"✅ Expense recorded!\n\n"
            f"{emoji} **Category:** {category}\n"
            f"💰 **Amount:** ₹{amount:.2f}\n"
            f"📝 **Note:** {text}"
            f"{balance_info}\n\n"
            f"💡 _Reply with 'Delete' to remove this transaction_",
            parse_mode='Markdown'
        )
        
        # Store transaction data for potential deletion
        if 'transactions' not in context.bot_data:
            context.bot_data['transactions'] = {}
        
        user_message_id = update.message.message_id
        
        with open('debug.txt', 'a') as f:
            f.write(f"DEBUG: Storing transaction data for confirmation message ID {confirmation_msg.message_id}\n")
            f.write(f"DEBUG: Also storing for user's original message ID {user_message_id}\n")
            f.write(f"DEBUG: Transaction details - Amount: {amount}, Category: {category}, Message: {text}\n")
        
        transaction_data = {
            'amount': amount,
            'category': category,
            'message': text
        }
        
        # Store with bot's confirmation message ID
        context.bot_data['transactions'][confirmation_msg.message_id] = transaction_data
        
        # Also store with user's original message ID (so they can reply to their own message)
        context.bot_data['transactions'][user_message_id] = transaction_data
        
        with open('debug.txt', 'a') as f:
            f.write(f"DEBUG: Stored with confirmation ID: {confirmation_msg.message_id}\n")
            f.write(f"DEBUG: Stored with user message ID: {user_message_id}\n")
            f.write(f"DEBUG: All stored message IDs: {list(context.bot_data['transactions'].keys())}\n")
            f.write(f"DEBUG: Total stored transactions: {len(context.bot_data['transactions'])}\n")
    else:
        await update.message.reply_text(
            "❌ Failed to save expense to Google Sheets.\n"
            "Please check your configuration and try again."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f'Update {update} caused error {context.error}')

def main():
    """Start the bot"""
    # Validate environment variables
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    if not GOOGLE_SHEETS_ID:
        print("ERROR: GOOGLE_SHEETS_ID not found in environment variables!")
        return
    
    print("Starting Expense Tracker Bot...")
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('balance', balance_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('recent', recent_command))
    app.add_handler(CommandHandler('delete', delete_command))
    app.add_handler(CommandHandler('deleteall', deleteall_command))
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

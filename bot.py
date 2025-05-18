import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "7701209931:AAHZiitsOatS19ZXWhGSXSaQX1f2UcQYdzQ"
BASE_URL = "https://hartrans.gov.in/bus-time-table-depot-wise/"

# Fetch depot list from the site
def get_depot_links():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    depot_links = {}

    for link in soup.find_all("a", href=True):
        href = link["href"]
        name = link.get_text(strip=True)
        if "pdf" in href.lower() or "time-table" in href.lower():
            if name and "Depot" in name:
                depot_links[name] = href if href.startswith("http") else f"https://hartrans.gov.in{href}"

    return depot_links

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    depots = get_depot_links()
    context.user_data["depots"] = depots  # Store for later use

    keyboard = [
        [InlineKeyboardButton(name, callback_data=name)]
        for name in sorted(depots.keys())
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚌 Choose a depot to view its timetable:", reply_markup=reply_markup)

# Handle depot selection
async def depot_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    depot_name = query.data
    depots = context.user_data.get("depots", {})
    link = depots.get(depot_name)

    if link:
        await query.edit_message_text(
            text=f"📍 *{depot_name}*\n\n🗂️ [Click here to view timetable]({link})",
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )
    else:
        await query.edit_message_text("❌ Failed to retrieve the link. Please try again.")

# Main bot setup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(depot_selected))
    print("🚀 Bus Info Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

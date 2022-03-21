import os
import threading

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from scraper import prefetched_data, fetch_data, fetch_data_runner


TG_TOKEN = value = os.getenv('TG_TOKEN')


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("CAT / SOF / SAM Tourniquet",
                              callback_data='CAT / SOF / SAM Tourniquet')],
        [InlineKeyboardButton("SWAT Tourniquet",
                              callback_data='SWAT Tourniquet')],
        [InlineKeyboardButton("Emergency Bandages",
                              callback_data='Emergency Bandages')],
        [InlineKeyboardButton("Hemostatic Dressing",
                              callback_data='Hemostatic Dressing (QuikClot, Celox, HemCon, ChitoSam)')],
        [InlineKeyboardButton("Hemostatic Agents (Granules)",
                              callback_data='Hemostatic Agents (Granules)')],
        [InlineKeyboardButton("Chest Seal", callback_data='Chest Seal')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("💙💛 Please choose a tactical med item you'd like to search for"+
                              "(and then give me a minute to look though a few websites) 💛💙",
                              reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    query.edit_message_text(text="Please be patient with me, I'm looking through quite a few websites. 😉")

    reply = prefetched_data.get(query.data)
    if reply.count('\n') > 0:
        reply = "🇺🇦 Here are a few websites, where you can buy your chosen item: " \
                + query.data + '.\n' + reply + '\n\n' \
                + "For a new request click: /start"
    else:
        reply = 'Unfortunately, I could not find this item ('+query.data+') available online. :('

    query.edit_message_text(text=f"{reply}")


def main() -> None:
    """Run the bot."""
    print('main running')
    #Create the Updater and pass it your bot's token.
    updater = Updater(token=TG_TOKEN,
                      use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    fetch_data()
    t_data = threading.Thread(name='data_fetcher', target=fetch_data_runner)
    t_data.start()

    main()
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Simpan status user sementara di dict (buat deploy sederhana, kalau mau skala besar pakai DB)
user_data = {}

# Cerita dan pilihan
story_steps = {
    1: {
        "text": "Hari 1 - Pagi\nSasa sadar cuma 30 hari buat skripsi. Apa yang Sasa lakukan?\n\n1) Langsung nulis bab 1\n2) Scroll medsos sebentar\n3) Tiduran sambil dengerin lagu",
        "options": ["1", "2", "3"]
    },
    2: {
        "1": {
            "text": "Sasa mulai nulis, tapi capek. Mau?\n\na) Tetap lanjut (Progress +10)\nb) Istirahat sebentar (Semangat naik)",
            "options": ["a", "b"]
        },
        "2": {
            "text": "Scroll medsos lama, jadi 2 jam hilang. Mau?\n\na) Begadang malam ini (Stamina turun, Progress +15)\nb) Santai dulu (Motivasi turun)",
            "options": ["a", "b"]
        },
        "3": {
            "text": "Mood naik, tapi belum nulis.\n\na) Langsung nulis (Progress +5)\nb) Cari camilan dulu (Waktu hilang, motivasi naik sedikit)",
            "options": ["a", "b"]
        }
    },
    3: {
        "text": "Setelah 15 hari, progress skripsi cuma 30%. Teman kirim pesan:\n'Sasa, ayo semangat! Ingat target kita!' Apa respon Sasa?\n\n1) Bales semangat\n2) Bales alasan sibuk\n3) Abaikan dan main game",
        "options": ["1", "2", "3"]
    },
    4: {
        "text": "Hari ke-30, waktunya menentukan nasib skripsi.\n\n1) Begadang nonstop sampai selesai\n2) Ajukan perpanjangan waktu\n3) Serahkan setengah jadi",
        "options": ["1", "2", "3"]
    }
}

def get_keyboard(options):
    buttons = [
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in options
    ]
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {
        "step": 1,
        "progress": 0,
        "motivation": 50,  # skala 0-100
        "stamina": 50
    }
    await update.message.reply_text(
        story_steps[1]["text"], reply_markup=get_keyboard(story_steps[1]["options"])
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if chat_id not in user_data:
        await query.message.reply_text("Ketik /start dulu ya buat mulai game.")
        return

    step = user_data[chat_id]["step"]

    # Step 1: Pilih 1,2,3
    if step == 1:
        choice = query.data
        if choice == "1":
            user_data[chat_id]["step"] = 2
            user_data[chat_id]["substep"] = "1"
            await query.message.reply_text(story_steps[2]["1"]["text"], reply_markup=get_keyboard(story_steps[2]["1"]["options"]))
        elif choice == "2":
            user_data[chat_id]["step"] = 2
            user_data[chat_id]["substep"] = "2"
            await query.message.reply_text(story_steps[2]["2"]["text"], reply_markup=get_keyboard(story_steps[2]["2"]["options"]))
        elif choice == "3":
            user_data[chat_id]["step"] = 2
            user_data[chat_id]["substep"] = "3"
            await query.message.reply_text(story_steps[2]["3"]["text"], reply_markup=get_keyboard(story_steps[2]["3"]["options"]))

    # Step 2: Pilihan a,b dari substep
    elif step == 2:
        sub = user_data[chat_id]["substep"]
        choice = query.data
        if sub == "1":
            if choice == "a":
                user_data[chat_id]["progress"] += 10
                user_data[chat_id]["motivation"] -= 5
                user_data[chat_id]["stamina"] -= 10
            elif choice == "b":
                user_data[chat_id]["motivation"] += 10
                user_data[chat_id]["stamina"] += 5
            user_data[chat_id]["step"] = 3
            await query.message.reply_text(story_steps[3]["text"], reply_markup=get_keyboard(story_steps[3]["options"]))
        elif sub == "2":
            if choice == "a":
                user_data[chat_id]["progress"] += 15
                user_data[chat_id]["stamina"] -= 15
                user_data[chat_id]["motivation"] -= 5
            elif choice == "b":
                user_data[chat_id]["motivation"] -= 10
            user_data[chat_id]["step"] = 3
            await query.message.reply_text(story_steps[3]["text"], reply_markup=get_keyboard(story_steps[3]["options"]))
        elif sub == "3":
            if choice == "a":
                user_data[chat_id]["progress"] += 5
                user_data[chat_id]["motivation"] -= 5
                user_data[chat_id]["stamina"] -= 5
            elif choice == "b":
                user_data[chat_id]["motivation"] += 5
            user_data[chat_id]["step"] = 3
            await query.message.reply_text(story_steps[3]["text"], reply_markup=get_keyboard(story_steps[3]["options"]))

    # Step 3: Pilihan 1,2,3
    elif step == 3:
        choice = query.data
        if choice == "1":
            user_data[chat_id]["motivation"] += 15
            user_data[chat_id]["progress"] += 20
        elif choice == "2":
            user_data[chat_id]["motivation"] -= 10
        elif choice == "3":
            user_data[chat_id]["motivation"] -= 15
            user_data[chat_id]["progress"] -= 5

        user_data[chat_id]["step"] = 4
        await query.message.reply_text(story_steps[4]["text"], reply_markup=get_keyboard(story_steps[4]["options"]))

    # Step 4: Pilihan 1,2,3
    elif step == 4:
        choice = query.data
        progress = user_data[chat_id]["progress"]
        motivation = user_data[chat_id]["motivation"]
        stamina = user_data[chat_id]["stamina"]

        if choice == "1":
            user_data[chat_id]["progress"] += 50
            user_data[chat_id]["stamina"] -= 40
            user_data[chat_id]["motivation"] -= 10
        elif choice == "2":
            user_data[chat_id]["motivation"] -= 20
        elif choice == "3":
            user_data[chat_id]["progress"] -= 20
            user_data[chat_id]["motivation"] -= 20

        # Tentukan ending
        final_progress = user_data[chat_id]["progress"]
        if final_progress >= 90 and motivation > 30:
            ending = "🎉 Sukses! Skripsi selesai tepat waktu dan dapat nilai bagus! Selamat ya!"
        elif 50 <= final_progress < 90:
            ending = "⚠️ Skripsi selesai tapi telat. Ada konsekuensi kecil, tapi kamu masih bisa maju."
        else:
            ending = "❌ Gagal menyelesaikan skripsi. Harus mengulang semester depan."

        await query.message.reply_text(
            f"Progress akhir: {final_progress}%\nMotivasi: {motivation}\nStamina: {stamina}\n\n{ending}"
        )
        # Reset game
        del user_data[chat_id]

async def remind(context: ContextTypes.DEFAULT_TYPE):
    """Kirim pesan pengingat harian ke semua user yang main game"""
    for chat_id in user_data.keys():
        try:
            await context.bot.send_message(chat_id=chat_id, text="🌟 Ingat ya, jangan malas! Yuk lanjut kerjakan skripsimu hari ini!")
        except Exception as e:
            print(f"Gagal kirim pengingat ke {chat_id}: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ketik /start untuk mulai game interaktif skripsi Sasa!")

def main():
    import os
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))

    # Setup job queue untuk pengingat harian, mulai 24 jam setelah bot jalan
    job_queue = app.job_queue
    job_queue.run_repeating(remind, interval=86400, first=10)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

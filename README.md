# DM1 Multi - Advanced Telegram Bot v6.0 CLEAN

Sistema completo e organizado de ferramentas para Telegram com funcionalidades avançadas e interface limpa.

## 🎯 V6.0 MAJOR IMPROVEMENTS
- **PROMOTIONAL SYSTEM REMOVED** - All divulgacao/promotional features completely removed
- **INVALID COMMAND HANDLING REMOVED** - Cleaner UX without annoying command suggestions  
- **NEW URL SEARCH API** - Migrated from Orbi to external API (http://147.79.86.21:5019/search?term=)
- **ORGANIZED STRUCTURE** - All functions, systems, and buttons comprehensively reorganized
- **IMPROVED ERROR HANDLING** - Better error management throughout all systems

## 🚀 Funcionalidades

- ✅ Comandos básicos (`/start`, `/help`)
- ✅ Processamento de mensagens de texto
- ✅ Sistema de logging completo
- ✅ Tratamento de erros
- ✅ Configuração segura com variáveis de ambiente
- ✅ Estrutura extensível para novos comandos

## 📋 Pré-requisitos

1. Python 3.7 ou superior
2. Token do bot do Telegram (obtido do BotFather)
3. Bibliotecas Python necessárias:
   - `python-telegram-bot`
   - `python-dotenv`

## 🔧 Instalação

1. **Clone ou baixe os arquivos do projeto**

2. **Instale as dependências:**
   ```bash
   pip install python-telegram-bot python-dotenv
   ```

3. **Configure o token do bot:**
   - Copie o arquivo `.env.example` para `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edite o arquivo `.env` e configure seu token:
     ```
     BOT_TOKEN=seu_token_aqui
     ```

## 🤖 Como obter o Token do BotFather

1. Abra o Telegram e procure por `@BotFather`
2. Inicie uma conversa com `/start`
3. Crie um novo bot com `/newbot`
4. Escolha um nome para seu bot
5. Escolha um username único (deve terminar com 'bot')
6. Copie o token fornecido pelo BotFather
7. Cole o token no arquivo `.env`

## ▶️ Executando o Bot

```bash
python main.py

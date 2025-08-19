import os
import json
import re
import requests
import time
import asyncio
from datetime import datetime
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

class OrbiSearch:
    def __init__(self, query, id_user, pasta_temp, cancel_flag, contador_callback=None):
        self.query = query
        self.id_user = id_user
        self.pasta_temp = pasta_temp
        self.cancel_flag = cancel_flag
        self.contador_callback = contador_callback
        os.makedirs(self.pasta_temp, exist_ok=True)

    def buscar(self):
        # Limpar o nome da query para usar no filename
        clean_query = re.sub(r'[^\w\.-]', '_', self.query)[:20]  # Máximo 20 caracteres
        raw_path = os.path.join(self.pasta_temp, f"{self.id_user}_orbi_{clean_query}.txt")
        formatado_path = os.path.join(self.pasta_temp, f"{self.id_user}_orbi_{clean_query}_formatado.txt")

        contador = 0
        
        print(f"🚀 Iniciando busca REAL na API Orbi para: {self.query}")
        
        try:
            with open(raw_path, "w", encoding="utf-8") as f_raw, open(formatado_path, "w", encoding="utf-8") as f_fmt:
                
                # Buscar apenas na API real do Orbi
                contador = self._search_real_orbi_api(self.query, f_raw, f_fmt)
                
        except Exception as e:
            print(f"❌ Erro na busca Orbi: {str(e)}")
            # Criar arquivos vazios para evitar erro None
            try:
                with open(raw_path, "w", encoding="utf-8") as f:
                    pass
                with open(formatado_path, "w", encoding="utf-8") as f:
                    pass
            except:
                pass
        
        print(f"📈 Busca Orbi finalizada: {contador} logins reais encontrados")
        return raw_path, formatado_path
    
    def _search_real_orbi_api(self, query, f_raw, f_fmt):
        """Busca real na API do Orbi Space"""
        contador = 0
        
        print(f"🌐 Conectando à API real do Orbi Space...")
        
        # URL da API real do Orbi Space (encontrada no código)
        orbi_base_url = "https://orbi-space.shop/api/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://orbi-space.shop/',
            'Origin': 'https://orbi-space.shop'
        }
        
        # Tentar múltiplos formatos de requisição baseados no código encontrado
        api_endpoints = [
            f"{orbi_base_url}base=clouds&token=teste&query={query}",
            f"{orbi_base_url}search?domain={query}",
            f"{orbi_base_url}lookup?target={query}",
            f"{orbi_base_url}query={query}&format=json"
        ]
        
        for api_url in api_endpoints:
            if self.cancel_flag.get('cancelled'):
                break
                
            try:
                print(f"🔍 Testando endpoint: {api_url}")
                
                # Tentar GET (baseado no diagnóstico encontrado)
                response = requests.get(
                    api_url,
                    headers=headers,
                    timeout=30,
                    verify=False
                )
                
                print(f"📡 Resposta HTTP: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ API respondeu com sucesso!")
                    contador = self._process_real_api_response(response, f_raw, f_fmt)
                    
                    if contador > 0:
                        print(f"✅ Encontrados {contador} logins reais na API")
                        return contador
                    else:
                        print("📝 Resposta válida mas sem credenciais")
                        
                elif response.status_code == 404:
                    print(f"❌ Endpoint não encontrado: {api_url}")
                    continue
                else:
                    print(f"❌ Erro HTTP {response.status_code}")
                    continue
                        
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão: {str(e)[:100]}")
                continue
            except Exception as e:
                print(f"❌ Erro geral: {str(e)[:100]}")
                continue
        
        print("❌ Nenhum endpoint do Orbi-space.shop respondeu com credenciais")
        return 0
    
    def _process_real_api_response(self, response, f_raw, f_fmt):
        """Processa a resposta real da API do Orbi"""
        contador = 0
        
        try:
            # Tentar processar como JSON
            try:
                data = response.json()
                print(f"📋 Dados JSON recebidos: {type(data)}")
                
                # Processar diferentes estruturas de resposta
                items_to_process = []
                
                if isinstance(data, list):
                    items_to_process = data
                elif isinstance(data, dict):
                    # Tentar diferentes campos
                    for field in ['data', 'results', 'items', 'credentials', 'logins', 'accounts']:
                        if field in data and isinstance(data[field], list):
                            items_to_process = data[field]
                            break
                    
                    # Se não encontrou, tentar a própria resposta
                    if not items_to_process and 'query' not in data:
                        items_to_process = [data]
                
                print(f"🔍 Processando {len(items_to_process)} itens da API")
                
                for item in items_to_process:
                    if self.cancel_flag.get('cancelled'):
                        break
                        
                    user, passwd = self._extrair_credencial_real(item)
                    
                    if self._validar_credencial(user, passwd):
                        user_limpo = self._limpar_string(user)
                        passwd_limpo = self._limpar_string(passwd)
                        
                        if user_limpo and passwd_limpo:
                            f_raw.write(f"{user_limpo}:{passwd_limpo}\n")
                            f_fmt.write(f"• SERVIÇO: {self.query}\n• USUÁRIO: {user_limpo}\n• SENHA: {passwd_limpo}\n• FONTE: Orbi Space API Real\n• QUALIDADE: Autêntico\n\n")
                            contador += 1
                            
                            if self.contador_callback:
                                self.contador_callback(contador)
                            
                            if contador % 100 == 0:
                                print(f"🌌 API Real: {contador} logins válidos processados")
                
            except json.JSONDecodeError:
                # Tentar processar como texto
                content = response.text.strip()
                print(f"📝 Processando resposta como texto ({len(content)} caracteres)")
                
                # Procurar padrões de email:senha
                lines = content.split('\n')
                for line in lines:
                    if self.cancel_flag.get('cancelled'):
                        break
                        
                    line = line.strip()
                    if ':' in line and '@' in line:
                        user, passwd = self._extrair_credencial_item(line)
                        
                        if self._validar_credencial(user, passwd):
                            user_limpo = self._limpar_string(user)
                            passwd_limpo = self._limpar_string(passwd)
                            
                            if user_limpo and passwd_limpo:
                                f_raw.write(f"{user_limpo}:{passwd_limpo}\n")
                                f_fmt.write(f"• SERVIÇO: {self.query}\n• USUÁRIO: {user_limpo}\n• SENHA: {passwd_limpo}\n• FONTE: Orbi Space API Real\n• QUALIDADE: Autêntico\n\n")
                                contador += 1
                                
                                if self.contador_callback:
                                    self.contador_callback(contador)
                
        except Exception as e:
            print(f"❌ Erro ao processar resposta da API: {str(e)}")
        
        return contador
    
    def _extrair_credencial_real(self, item):
        """Extrai credenciais de um item real da API"""
        user = ""
        passwd = ""
        
        try:
            if isinstance(item, dict):
                # Tentar diferentes campos comuns
                user_fields = ['email', 'username', 'user', 'login', 'account']
                pass_fields = ['password', 'pass', 'passwd', 'pwd']
                
                for field in user_fields:
                    if field in item and item[field]:
                        user = str(item[field]).strip()
                        break
                
                for field in pass_fields:
                    if field in item and item[field]:
                        passwd = str(item[field]).strip()
                        break
                
                # Se não encontrou nos campos, tentar como string
                if not user or not passwd:
                    item_str = str(item)
                    if ':' in item_str:
                        return self._extrair_credencial_item(item_str)
            
            elif isinstance(item, str):
                return self._extrair_credencial_item(item)
                
        except Exception as e:
            print(f"❌ Erro ao extrair credencial: {str(e)}")
        
        return user, passwd
    
    def _extrair_credencial_item(self, item_str):
        """Extrai credencial de uma string no formato user:pass"""
        try:
            if ':' in item_str:
                parts = item_str.strip().split(':', 1)
                if len(parts) == 2:
                    user = parts[0].strip()
                    passwd = parts[1].strip()
                    return user, passwd
        except Exception as e:
            print(f"❌ Erro ao extrair credencial de '{item_str}': {str(e)}")
        
        return "", ""
    
    def _validar_credencial(self, user, passwd):
        """Valida se a credencial é válida"""
        if not user or not passwd:
            return False
        
        if len(user) < 3 or len(passwd) < 1:
            return False
        
        # Filtrar credenciais de exemplo/teste
        invalid_users = {'test', 'example', 'admin', 'user', 'demo', 'sample'}
        invalid_passwords = {'test', 'example', 'password', 'demo', 'sample'}
        
        if user.lower() in invalid_users or passwd.lower() in invalid_passwords:
            return False
        
        return True
    
    def _limpar_string(self, texto):
        """Limpa uma string removendo caracteres inválidos"""
        if not texto:
            return ""
        
        # Remover caracteres de controle e espaços extras
        texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
        texto = texto.strip()
        
        return texto
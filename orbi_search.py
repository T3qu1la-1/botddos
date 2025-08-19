
import os
import json
import re
import requests
import random
from datetime import datetime
from urllib.parse import urlparse

class OrbiSearch:
    def __init__(self, query, id_user, pasta_temp, cancel_flag, contador_callback=None):
        self.query = query
        self.id_user = id_user
        self.pasta_temp = pasta_temp
        self.cancel_flag = cancel_flag
        self.contador_callback = contador_callback
        os.makedirs(self.pasta_temp, exist_ok=True)

    def buscar(self):
        raw_path = os.path.join(self.pasta_temp, f"{self.id_user}_orbi.txt")
        formatado_path = os.path.join(self.pasta_temp, f"{self.id_user}_orbi_formatado.txt")

        contador = 0
        limite = 100000
        
        # Preparar query para a API - limpar e formatar URL
        query_formatted = self.query.lower().strip()
        
        # Se parecer com URL, extrair domínio principal
        if '.' in query_formatted:
            if query_formatted.startswith(('http://', 'https://')):
                parsed = urlparse(query_formatted)
                query_formatted = parsed.netloc or parsed.path
            # Remover www. se existir
            if query_formatted.startswith('www.'):
                query_formatted = query_formatted[4:]
            # Usar apenas o domínio principal (sem subdomínios)
            domain_parts = query_formatted.split('.')
            if len(domain_parts) >= 2:
                query_formatted = domain_parts[-2]  # Ex: "netflix" de "netflix.com"

        print(f"🚀 Iniciando busca Orbi Space para: {self.query}")
        print(f"🔍 Query formatada para API: {query_formatted}")
        
        try:
            # API principal do Orbi Space
            api_url = f"https://orbi-space.shop/api/base=clouds&token=teste&query={query_formatted}"
            
            print(f"✅ Conectando à API Orbi Space...")
            
            # Configurar sessão com headers otimizados
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Referer': 'https://orbi-space.shop/'
            })
            
            response = session.get(api_url, timeout=(15, 120))
            
            print(f"✅ API respondeu com status: {response.status_code}")
            
            with open(raw_path, "w", encoding="utf-8") as f_raw, open(formatado_path, "w", encoding="utf-8") as f_fmt:
                if response.status_code == 200:
                    content = response.text.strip()
                    print(f"🔍 Processando resposta da API ({len(content)} caracteres)")
                    
                    # Tentar processar como JSON primeiro
                    try:
                        data = response.json()
                        print(f"🔍 Dados JSON recebidos: {type(data)}")
                        
                        # Debug detalhado do conteúdo JSON
                        if isinstance(data, dict):
                            print(f"🔍 Chaves do JSON: {list(data.keys())}")
                            for key, value in data.items():
                                if isinstance(value, (list, str)):
                                    print(f"🔍 Campo '{key}': {type(value)} com {len(value) if hasattr(value, '__len__') else 'N/A'} elementos")
                        elif isinstance(data, list):
                            print(f"🔍 Lista JSON com {len(data)} elementos")
                            if data and len(data) > 0:
                                print(f"🔍 Primeiro elemento da lista: {type(data[0])}")
                        
                        # Processar diferentes estruturas de resposta JSON
                        items_to_process = []
                        
                        if isinstance(data, list):
                            # Se é uma lista direta de credenciais
                            for item in data:
                                if isinstance(item, str) and ':' in item:
                                    items_to_process.append(item)
                                elif isinstance(item, dict):
                                    # Tentar extrair credenciais do objeto
                                    credential = self._extract_credential_from_object(item)
                                    if credential:
                                        items_to_process.append(credential)
                            print(f"🔍 Lista processada: {len(items_to_process)} credenciais extraídas")
                        
                        elif isinstance(data, dict):
                            # Verificar diferentes campos que podem conter credenciais
                            credential_fields = ['data', 'results', 'items', 'credentials', 'accounts', 'logins', 'users', 'response', 'payload']
                            
                            for field in credential_fields:
                                if field in data:
                                    value = data[field]
                                    print(f"🔍 Processando campo '{field}': {type(value)}")
                                    
                                    if isinstance(value, list):
                                        for item in value:
                                            if isinstance(item, str) and ':' in item:
                                                items_to_process.append(item)
                                            elif isinstance(item, dict):
                                                credential = self._extract_credential_from_object(item)
                                                if credential:
                                                    items_to_process.append(credential)
                                    
                                    elif isinstance(value, str):
                                        # Dividir string por linhas e processar
                                        lines = value.split('\n')
                                        for line in lines:
                                            line = line.strip()
                                            if ':' in line and len(line) > 5:
                                                items_to_process.append(line)
                                        print(f"🔍 Campo '{field}' processado: {len(lines)} linhas verificadas")
                            
                            # Se ainda não encontrou credenciais suficientes, usar regex mais agressivo
                            if len(items_to_process) < 1000:  # Se encontrou menos de 1000, algo está errado
                                print(f"🔍 Poucos resultados ({len(items_to_process)}), aplicando regex avançado...")
                                json_str = json.dumps(data)
                                
                                # Padrões mais específicos para diferentes formatos
                                patterns = [
                                    # Email:senha padrão
                                    r'([a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}):([^\s,}\]"\'<>\n\r]+)',
                                    # Formato JSON "email":"senha"
                                    r'"([a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"\s*:\s*"([^"]+)"',
                                    # Formato usuário:senha simples
                                    r'([a-zA-Z0-9._-]{3,20}):([a-zA-Z0-9@#$%^&*()_+=\-]{3,50})',
                                    # Formato com separador |
                                    r'([a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\|([^\s,}\]"\'<>\n\r]+)',
                                    # Formato dentro de arrays
                                    r'\[([^,\]]+),([^,\]]+)\]',
                                    # Formato com texto ao redor
                                    r'user["\s]*[:=]["\s]*([^",\s]+)[",\s]*pass["\s]*[:=]["\s]*([^",\s]+)'
                                ]
                                
                                for i, pattern in enumerate(patterns):
                                    matches = re.findall(pattern, json_str, re.IGNORECASE)
                                    valid_matches = 0
                                    for match in matches:
                                        if len(match) >= 2:
                                            user = match[0].strip()
                                            passwd = match[1].strip()
                                            if self._quick_validate(user, passwd):
                                                items_to_process.append(f"{user}:{passwd}")
                                                valid_matches += 1
                                    print(f"🔍 Padrão {i+1}: {len(matches)} matches, {valid_matches} válidos")
                        
                        print(f"🔍 Total de credenciais para processar: {len(items_to_process)}")
                        
                        # Processar credenciais encontradas
                        for item in items_to_process:
                            if self.cancel_flag.get('cancelled') or contador >= limite:
                                break
                            
                            user, passwd = self._extrair_credencial_item(item)
                            
                            if self._validar_credencial(user, passwd):
                                user_limpo = self._limpar_string(user)
                                passwd_limpo = self._limpar_string(passwd)
                                
                                if user_limpo and passwd_limpo:
                                    f_raw.write(f"{user_limpo}:{passwd_limpo}\n")
                                    f_fmt.write(f"• SERVIÇO: {self.query}\n• USUÁRIO: {user_limpo}\n• SENHA: {passwd_limpo}\n• FONTE: Orbi Space API\n• QUALIDADE: Premium\n\n")
                                    contador += 1
                                    
                                    if self.contador_callback:
                                        self.contador_callback(contador)
                                    
                                    if contador % 1000 == 0:  # Progresso a cada 1000 para não spammar
                                        print(f"🌌 Progresso API: {contador} logins encontrados")
                    
                    except (json.JSONDecodeError, ValueError):
                        print(f"🔍 Resposta não é JSON válido, processando como texto bruto...")
                        
                        # Estatísticas de processamento
                        lines = content.split('\n')
                        valid_lines = 0
                        processed_lines = 0
                        
                        print(f"🔍 Processando {len(lines)} linhas de texto")
                        
                        # Primeiro, contar quantas linhas têm potencial
                        potential_credentials = []
                        for line in lines:
                            line = line.strip()
                            if ':' in line and len(line) > 5 and not line.startswith(('http:', 'https:', '//', 'data:', 'javascript:')):
                                potential_credentials.append(line)
                        
                        print(f"🔍 {len(potential_credentials)} linhas com potencial de credenciais")
                        
                        for line in potential_credentials:
                            if self.cancel_flag.get('cancelled') or contador >= limite:
                                break
                            
                            processed_lines += 1
                            
                            # Tentar diferentes separadores
                            separators = [':', '|', ';', '\t', ' - ', ' -- ']
                            credential_found = False
                            
                            for sep in separators:
                                if sep in line:
                                    parts = line.split(sep, 1)
                                    if len(parts) == 2:
                                        user = parts[0].strip()
                                        passwd = parts[1].strip()
                                        
                                        if self._validar_credencial(user, passwd):
                                            user_limpo = self._limpar_string(user)
                                            passwd_limpo = self._limpar_string(passwd)
                                            
                                            if user_limpo and passwd_limpo:
                                                f_raw.write(f"{user_limpo}:{passwd_limpo}\n")
                                                f_fmt.write(f"• SERVIÇO: {self.query}\n• USUÁRIO: {user_limpo}\n• SENHA: {passwd_limpo}\n• FONTE: Orbi Space API\n• QUALIDADE: Premium\n\n")
                                                contador += 1
                                                valid_lines += 1
                                                credential_found = True
                                                
                                                if self.contador_callback:
                                                    self.contador_callback(contador)
                                                
                                                if contador % 1000 == 0:
                                                    print(f"🌌 Progresso: {contador} logins encontrados")
                                                break
                            
                            # Debug a cada 10000 linhas processadas
                            if processed_lines % 10000 == 0:
                                percentage = (valid_lines / processed_lines * 100) if processed_lines > 0 else 0
                                print(f"🔍 Progresso: {processed_lines}/{len(potential_credentials)} linhas ({percentage:.1f}% válidas)")
                        
                        print(f"🔍 Texto processado: {valid_lines} credenciais válidas de {processed_lines} linhas processadas")
                        
                        # Se ainda poucos resultados, usar regex mais agressivo
                        if contador < 100:
                            print(f"🔍 Aplicando regex mais agressivo no conteúdo completo...")
                            
                            patterns = [
                                r'([a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}):([^\s,}\]"\'<>\n\r]+)',
                                r'([a-zA-Z0-9._-]{3,}):([a-zA-Z0-9@#$%^&*()_+=\-\[\]{}|;:\'",.<>/?`~\\]{3,})',
                                r'"username":"([^"]+)","password":"([^"]+)"',
                                r'"email":"([^"]+)","password":"([^"]+)"',
                                r'email=([^&\s]+)&password=([^&\s]+)',
                                r'user=([^&\s]+)&pass=([^&\s]+)'
                            ]
                            
                            for pattern in patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                print(f"🔍 Padrão encontrou {len(matches)} credenciais")
                                
                                for match in matches:
                                    if self.cancel_flag.get('cancelled') or contador >= limite:
                                        break
                                    
                                    if len(match) >= 2:
                                        user = match[0].strip()
                                        passwd = match[1].strip()
                                        
                                        if self._validar_credencial(user, passwd):
                                            user_limpo = self._limpar_string(user)
                                            passwd_limpo = self._limpar_string(passwd)
                                            
                                            if user_limpo and passwd_limpo:
                                                f_raw.write(f"{user_limpo}:{passwd_limpo}\n")
                                                f_fmt.write(f"• SERVIÇO: {self.query}\n• USUÁRIO: {user_limpo}\n• SENHA: {passwd_limpo}\n• FONTE: Orbi Space API\n• QUALIDADE: Premium\n\n")
                                                contador += 1
                                                
                                                if self.contador_callback:
                                                    self.contador_callback(contador)
                                                
                                                if contador % 100 == 0:
                                                    print(f"🌌 Progresso: {contador} logins encontrados")
                
                else:
                    print(f"⚠️ API retornou status {response.status_code}")
                    # Retornar caminhos mesmo com erro, mas criar arquivos vazios
                    with open(raw_path, "w", encoding="utf-8") as f:
                        pass
                    with open(formatado_path, "w", encoding="utf-8") as f:
                        pass
            
            try:
                session.close()
            except:
                pass
                
        except Exception as e:
            print(f"❌ Erro na API Orbi Space: {str(e)}")
            # Criar arquivos vazios para evitar erro None
            try:
                with open(raw_path, "w", encoding="utf-8") as f:
                    pass
                with open(formatado_path, "w", encoding="utf-8") as f:
                    pass
            except:
                pass
        
        print(f"📈 Busca Orbi finalizada: {contador} logins coletados")
        return raw_path, formatado_path
    
    def _extract_credential_from_object(self, obj):
        """Extrai credencial de um objeto JSON"""
        if not isinstance(obj, dict):
            return None
        
        # Campos comuns para usuário
        user_fields = ['email', 'username', 'user', 'login', 'account']
        # Campos comuns para senha
        pass_fields = ['password', 'pass', 'passwd', 'pwd']
        
        user = None
        passwd = None
        
        # Procurar por campos de usuário
        for field in user_fields:
            if field in obj and obj[field]:
                user = str(obj[field]).strip()
                break
        
        # Procurar por campos de senha
        for field in pass_fields:
            if field in obj and obj[field]:
                passwd = str(obj[field]).strip()
                break
        
        if user and passwd:
            return f"{user}:{passwd}"
        
        return None
    
    def _quick_validate(self, user, passwd):
        """Validação rápida básica"""
        if not user or not passwd:
            return False
        
        user = str(user).strip()
        passwd = str(passwd).strip()
        
        # Verificações básicas
        if (len(user) < 3 or len(passwd) < 3 or
            user.lower() in ["null", "undefined", "test", "example"] or
            passwd.lower() in ["null", "undefined", "password", "123456"]):
            return False
        
        return True

    def _extrair_credencial_item(self, item):
        """Extrai credenciais de um item da API"""
        user = ""
        passwd = ""
        
        if isinstance(item, dict):
            # Tentar diferentes campos para usuário
            user_fields = [
                'username', 'user', 'email', 'login', 'account', 'usr', 'u',
                'user_name', 'login_name', 'account_name', 'email_address',
                'credential_user', 'auth_user', 'user_id', 'mail', 'login_email'
            ]
            for field in user_fields:
                if field in item and item[field]:
                    user = str(item[field]).strip()
                    break
            
            # Tentar diferentes campos para senha
            pass_fields = [
                'password', 'pass', 'pwd', 'passwd', 'key', 'p',
                'password_hash', 'pass_word', 'credential_pass', 'auth_pass',
                'secret', 'token', 'auth_token', 'access_key', 'senha'
            ]
            for field in pass_fields:
                if field in item and item[field]:
                    passwd = str(item[field]).strip()
                    break
            
            # Se não encontrou campos específicos, varrer todos os campos
            if not user or not passwd:
                for key, value in item.items():
                    if isinstance(value, str) and len(value) > 2:
                        value = value.strip()
                        
                        # Se parece com email, usar como user
                        if '@' in value and '.' in value and not user:
                            user = value
                        # Se parece com senha e ainda não tem senha
                        elif len(value) >= 4 and not passwd and key.lower() not in ['url', 'domain', 'site', 'hostname', 'path']:
                            # Verificar se não é uma URL ou caminho
                            if not value.startswith(('http', 'www', '/', '\\')) and '/' not in value[:10]:
                                passwd = value
                        # Se tem formato user:pass dentro do valor
                        elif ':' in value and not value.startswith(('http:', 'https:')):
                            parts = value.split(':', 1)
                            if len(parts) == 2 and len(parts[0]) >= 3 and len(parts[1]) >= 3:
                                if not user:
                                    user = parts[0].strip()
                                if not passwd:
                                    passwd = parts[1].strip()
        
        elif isinstance(item, str):
            item = item.strip()
            
            # Tentar diferentes separadores
            separators = [':', '|', ';', '\t', ' - ', ' -- ']
            
            for sep in separators:
                if sep in item and not item.startswith(('http:', 'https:', '//', 'data:', 'javascript:')):
                    parts = item.split(sep, 1)
                    if len(parts) == 2:
                        potential_user = parts[0].strip()
                        potential_pass = parts[1].strip()
                        
                        # Validar se parece com credencial válida
                        if (len(potential_user) >= 3 and len(potential_pass) >= 3 and
                            not potential_user.startswith(('http', 'www', '/')) and
                            not potential_pass.startswith(('http', 'www', '/'))):
                            
                            user = potential_user
                            passwd = potential_pass
                            break
        
        return user, passwd

    def _validar_credencial(self, user, passwd):
        """Valida se a credencial é válida"""
        if not user or not passwd:
            return False
        
        # Converter para string se necessário
        user = str(user).strip()
        passwd = str(passwd).strip()
        
        # Validações básicas
        if (len(user) < 3 or len(passwd) < 3 or
            user.lower() in ["empty", "null", "undefined", "test", "admin", "example", "[object object]", "none", "null", "nan"] or
            passwd.lower() in ["empty", "null", "undefined", "password", "123456", "test", "[object object]", "none", "null", "nan"]):
            return False
        
        # Não permitir caracteres inválidos no usuário
        if not re.match(r'^[a-zA-Z0-9@._\-+]+$', user):
            return False
        
        # Não permitir senhas muito simples
        if passwd.lower() in ['password', '123456', 'admin', 'user', 'guest']:
            return False
        
        return True
    
    def _limpar_string(self, text):
        """Limpa e valida strings de usuário e senha"""
        if not text:
            return ""
        
        # Permitir caracteres válidos para emails e senhas
        cleaned = re.sub(r'[^\w@#$%^&*()_+=\-\[\]{}|;:\'",.<>/?`~\\]', '', str(text))
        return cleaned.strip()

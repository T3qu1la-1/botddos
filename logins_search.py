import os
import json
import re
import urllib3
from sseclient import SSEClient

class LoginSearch:
    def __init__(self, url, id_user, pasta_temp, cancel_flag, contador_callback=None):
        self.url = url
        self.id_user = id_user
        self.pasta_temp = pasta_temp
        self.cancel_flag = cancel_flag
        self.contador_callback = contador_callback
        os.makedirs(self.pasta_temp, exist_ok=True)

    def buscar(self):
        raw_path = os.path.join(self.pasta_temp, f"{self.id_user}.txt")
        formatado_path = os.path.join(self.pasta_temp, f"{self.id_user}_formatado.txt")

        contador = 0
        limite = 80000
        regex_valido = re.compile(r'^[a-zA-Z0-9!@#$%^&*()\-_=+\[\]{}|;:\'\",.<>/?`~\\]+$')

        http = urllib3.PoolManager()

        response = None
        print(f"🔄 Iniciando busca de logins para URL: {self.url}")
        
        try:
            api_url = f"https://patronhost.online/logs/api_sse.php?url={self.url}"
            print(f"📡 Conectando à API: {api_url}")
            
            response = http.request('GET', api_url, preload_content=False)
            client = SSEClient(response)

            with open(raw_path, "w", encoding="utf-8") as f_raw, open(formatado_path, "w", encoding="utf-8") as f_fmt:
                dados_processados = set()  # Evitar duplicatas
                
                for event in client:
                    if self.cancel_flag.get('cancelled'):
                        print("⏹️ Busca cancelada pelo usuário")
                        break
                    if contador >= limite:
                        print(f"⚠️ Limite de {limite} logins atingido")
                        break
                    
                    try:
                        if event.data and event.data.strip():
                            data = json.loads(event.data)
                            url_ = data.get("url", "").strip()
                            user = data.get("user", "").strip()
                            passwd = data.get("pass", "").strip()
                            
                            # Validações melhoradas
                            if (url_ and user and passwd and 
                                user.upper() not in ["EMPTY", "NULL", "UNDEFINED"] and
                                len(user) >= 3 and len(passwd) >= 1):
                                
                                # Limpar credenciais
                                user_limpo = self._clean_credential(user, regex_valido)
                                passwd_limpo = self._clean_credential(passwd, regex_valido)
                                
                                # Criar chave única para evitar duplicatas
                                credential_key = f"{user_limpo}:{passwd_limpo}"
                                
                                if (user_limpo and passwd_limpo and 
                                    credential_key not in dados_processados and
                                    self._validate_credential_quality(user_limpo, passwd_limpo)):
                                    
                                    dados_processados.add(credential_key)
                                    
                                    # Escrever nos arquivos
                                    f_raw.write(f"{user_limpo}:{passwd_limpo}\n")
                                    f_fmt.write(
                                        f"• URL: {url_}\n"
                                        f"• USUÁRIO: {user_limpo}\n"
                                        f"• SENHA: {passwd_limpo}\n"
                                        f"• QUALIDADE: {'✅ Alta' if len(passwd_limpo) > 8 else '⚠️ Média'}\n"
                                        f"• FONTE: Patronhost\n\n"
                                    )
                                    contador += 1
                                    
                                    if self.contador_callback:
                                        self.contador_callback(contador)
                                    
                                    # Log a cada 50 logins para acompanhar progresso
                                    if contador % 50 == 0:
                                        print(f"📊 Progresso: {contador} logins válidos encontrados")
                                        
                    except json.JSONDecodeError:
                        # Log de dados inválidos apenas se houver dados
                        if event.data and len(event.data.strip()) > 10:
                            print(f"⚠️ Dados JSON inválidos recebidos: {event.data[:50]}...")
                        continue
                    except Exception as e:
                        print(f"❌ Erro ao processar evento: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"❌ Erro na conexão com API: {str(e)}")
        finally:
            if response:
                try:
                    response.release_conn()
                except:
                    pass

        print(f"✅ Busca concluída: {contador} logins únicos encontrados")
        return raw_path, formatado_path
    
    def _clean_credential(self, credential, regex_valido):
        """Limpa uma credencial removendo caracteres inválidos"""
        if not credential:
            return ""
        
        # Remover espaços e caracteres especiais desnecessários
        cleaned = ''.join(ch for ch in credential if regex_valido.match(ch)).replace(" ", "")
        
        # Remover caracteres de controle
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        return cleaned.strip()
    
    def _validate_credential_quality(self, user, passwd):
        """Valida a qualidade das credenciais"""
        if not user or not passwd:
            return False
        
        # Filtrar credenciais comuns/inválidas
        invalid_users = {
            'test', 'admin', 'user', 'guest', 'demo', 'example', 
            'root', 'administrator', 'null', 'undefined'
        }
        invalid_passwords = {
            'password', 'pass', '123456', 'admin', 'test', 
            'guest', 'demo', 'example', '12345', 'qwerty'
        }
        
        if (user.lower() in invalid_users or 
            passwd.lower() in invalid_passwords or
            len(user) < 3 or len(passwd) < 1):
            return False
        
        # Verificar se não é apenas números ou letras repetidas
        if user == user[0] * len(user) or passwd == passwd[0] * len(passwd):
            return False
        
        return True

    

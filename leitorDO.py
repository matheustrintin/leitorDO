import os
import requests
import re # Importação necessária para o re.sub
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configurações
DATA_HOJE = datetime.now().strftime("%d/%m/%Y")
URL = f"https://www.mpsp.mp.br/w/{DATA_HOJE.replace('/', '/')}"

# Lista de palavras-chave
PALAVRAS_CHAVE = ["são carlos", "tiago de azevedo", "araraquara",
    "matheus rocateli trintin", "lara goncalves monteiro", "neiva paula paccola carnielli pereira",
    "marcos vinicios marcolino", "natalia batista borges", "aisla massariolli palmieri parisi", "mario jose correa de paula",
    "jose raphael da silva", "bruno sant anna barbosa ferreira", "antonio marcos ocanha", "marco aurelio bernarde de almeida",
    "marinilda aparecida barbosa borges", "rogerio geraldo loreti", "marcelo buffulin mizuno"]

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensagem,
        "parse_mode": "HTML" 
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

def verificar_mpsp():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"Acessando MPSP em: {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            blocos = page.query_selector_all("div, li") 
            mensagens_encontradas = []
            
            for bloco in blocos:
                texto_bloco = bloco.inner_text()
                texto_min = texto_bloco.lower()
                
                if any(palavra in texto_min for palavra in PALAVRAS_CHAVE):
                    linhas = [l.strip() for l in texto_bloco.split('\n') 
                              if any(palavra in l.lower() for palavra in PALAVRAS_CHAVE)]
                    
                    for linha in linhas:
                        if linha not in mensagens_encontradas:
                            mensagens_encontradas.append(linha)
            
            if mensagens_encontradas:
                texto_final = f"🔔 <b>Publicação DOMPSP de {DATA_HOJE}:</b>\n\n"
                
                for linha in mensagens_encontradas:
                    linha_formatada = linha
                    for palavra in PALAVRAS_CHAVE:
                        if palavra in linha.lower():
                            termo_destaque = f"<b>{palavra.upper()}</b>"
                            linha_formatada = re.sub(re.escape(palavra), termo_destaque, linha_formatada, flags=re.IGNORECASE)
                    
                    texto_final += f"• {linha_formatada}\n\n"
                
                enviar_telegram(texto_final)
                print("Alerta completo enviado com sucesso!")
                
                with open("historicoDO.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n--- Data: {DATA_HOJE} ---\n{texto_final}\n")
            else:
                # Nova funcionalidade: notifica que nada foi encontrado
                msg_vazia = f"📭 Nada encontrado no dia {DATA_HOJE}."
                enviar_telegram(msg_vazia)
                print(f"Nenhuma ocorrência encontrada para {DATA_HOJE}.")
                
        except Exception as e:
            print(f"Erro ao processar: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verificar_mpsp()

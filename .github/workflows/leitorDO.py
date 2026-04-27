import os
import requests
from playwright.sync_api import sync_playwright

# Configurações com suas credenciais
DATA_FIXA = "27/04/2026"
URL = f"https://www.mpsp.mp.br/w/{DATA_FIXA.replace('/', '/')}"
PALAVRA_ALVO = "são carlos"

# O script lerá os dados do ambiente do GitHub
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

def verificar_mpsp():
    with sync_playwright() as p:
        # Lança o navegador em modo invisível
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"Acessando MPSP em: {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            # Captura os blocos de texto (divs e itens de lista)
            blocos = page.query_selector_all("div, li") 
            mensagens_encontradas = []
            
            for bloco in blocos:
                texto_bloco = bloco.inner_text()
                # Verifica se o termo está presente no bloco inteiro
                if PALAVRA_ALVO.lower() in texto_bloco.lower():
                    # Quebra o bloco em linhas e filtra apenas as que contêm a palavra
                    linhas = [l.strip() for l in texto_bloco.split('\n') if PALAVRA_ALVO.lower() in l.lower()]
                    for linha in linhas:
                        if linha not in mensagens_encontradas:
                            mensagens_encontradas.append(linha)
            
            if mensagens_encontradas:
                # Montagem da mensagem final incluindo todas as ocorrências coletadas
                texto_final = f"🔔 Alerta MPSP - {DATA_FIXA}:\n\n"
                for msg in mensagens_encontradas:
                    texto_final += f"• {msg}\n"
                
                enviar_telegram(texto_final)
                print("Alerta completo enviado com sucesso!")
                
                # Salva em arquivo de histórico
                with open("historicoDO.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n--- Data: {DATA_FIXA} ---\n{texto_final}\n")
            else:
                print(f"Nenhuma ocorrência encontrada para {DATA_FIXA}.")
                
        except Exception as e:
            print(f"Erro ao processar: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verificar_mpsp()
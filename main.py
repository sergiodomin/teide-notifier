import time
import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        r = requests.post(url, data=data)
        print("Mensaje enviado" if r.status_code == 200 else f"Fallo al enviar: {r.text}")
    except Exception as e:
        print("Error al enviar mensaje:", e)

def revisar_teide():
    print(f"\nEjecutando comprobación a las {time.strftime('%H:%M:%S')}...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Página previa
        page.goto("https://reservasparquesnacionales.es/real/ParquesNac/usu/html/Previo-inicio-reserva-oapn.aspx?cen=2&act=%201")
        page.click("input[value*='PASO SIGUIENTE']")
        page.wait_for_selector("text=de 2025")

        # 2. Avanzar dos meses
        for _ in range(2):
            page.click("a[title*='Ir al mes siguiente']")
            time.sleep(1.5)

        # 3. Verificar días activos
        page.wait_for_selector("td.dias >> text='1'")
        dias = page.query_selector_all("td.dias a")
        dias_numeros = [int(d.inner_text()) for d in dias if d.inner_text().isdigit()]

        print(f"Días activos: {sorted(dias_numeros)}")
        print(f"Total: {len(dias_numeros)} días\n")

        # 4. Verificar tramos con plazas
        plazas = page.query_selector_all("td.plazas span:text('Plazas disponibles')")
        if plazas:
            print(f"¡Hay {len(plazas)} tramos con plazas!")
            enviar_telegram(f"¡{len(plazas)} tramos disponibles para subir al Teide!\nhttps://reservasparquesnacionales.es/")
        else:
            print("No hay plazas disponibles.")
            enviar_telegram("No hay plazas para septiembre del Teide.")

        browser.close()

# Bucle cada 30 min
while True:
    revisar_teide()
    time.sleep(1800)
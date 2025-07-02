# main.py
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            print("📩 Mensaje enviado por Telegram")
        else:
            print("Fallo al enviar mensaje:", r.text)
    except Exception as e:
        print("Error al enviar mensaje:", e)


def revisar_teide():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://reservasparquesnacionales.es/real/ParquesNac/usu/html/Previo-inicio-reserva-oapn.aspx?cen=2&act=%201")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and contains(@value, 'PASO SIGUIENTE')]"))).click()
        time.sleep(2)

        wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'de 2025')]")))
        for _ in range(2):
            next_month = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@href, '__doPostBack') and contains(@title, 'Ir al mes siguiente')]"
            )))
            driver.execute_script("arguments[0].click();", next_month)
            time.sleep(1.5)

        wait.until(EC.presence_of_element_located((By.XPATH, "//td[@class='dias']/a[contains(text(), '1')]")))
        dias_septiembre = driver.find_elements(By.XPATH, "//td[@class='dias']/a")
        numeros = [int(d.text.strip()) for d in dias_septiembre if d.text.strip().isdigit()]

        print(f"\nDías activos de septiembre: {sorted(numeros)}")
        print(f"Total: {len(numeros)} días\n")

        plazas_disponibles = driver.find_elements(By.XPATH, "//td[@class='plazas']/span[contains(text(), 'Plazas disponibles')]")

        if plazas_disponibles:
            print("¡Se han detectado horarios con PLAZAS disponibles!")
            mensaje = f"¡Hay {len(plazas_disponibles)} tramos disponibles para septiembre del Teide!\nhttps://reservasparquesnacionales.es/"
            enviar_telegram(mensaje)
        else:
            print("No hay plazas disponibles visibles.")

    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        enviar_telegram(f"Error al revisar disponibilidad del Teide:\n{e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    while True:
        print(f"\nEjecutando comprobación a las {time.strftime('%H:%M:%S')}...")
        revisar_teide()
        print("Esperando 30 minutos...\n")
        time.sleep(1800)
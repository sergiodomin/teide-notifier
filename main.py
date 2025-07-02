import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Lee las variables del entorno (asegúrate de configurarlas en Railway)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        r = requests.post(url, data=data)
        print("Mensaje enviado" if r.status_code == 200 else f"Fallo al enviar: {r.text}")
    except Exception as e:
        print("❌ Error al enviar mensaje:", e)

def revisar_teide():
    print(f"\nEjecutando comprobación a las {time.strftime('%H:%M:%S')}...\n")

    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")
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
        dias_sept = driver.find_elements(By.XPATH, "//td[@class='dias']/a")
        numeros = [int(d.text.strip()) for d in dias_sept if d.text.strip().isdigit()]

        print(f"Días activos: {sorted(numeros)}")
        print(f"Total: {len(numeros)} días\n")

        plazas = driver.find_elements(By.XPATH, "//td[@class='plazas']/span[contains(text(), 'Plazas disponibles')]")
        if plazas:
            print(f"¡Hay {len(plazas)} tramos con plazas!")
            enviar_telegram(f"¡{len(plazas)} tramos disponibles para subir al Teide!\nhttps://reservasparquesnacionales.es/")
        else:
            print("❌ No hay plazas disponibles.")
            enviar_telegram("No hay plazas para septiembre del Teide.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

# Ejecuta cada 30 minutos
while True:
    revisar_teide()
    time.sleep(1800)  # 30 minutos

import time
import random
import os
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import telebot
from fake_useragent import UserAgent
from urllib.parse import urlparse

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN is None:
    raise ValueError("No se pudo cargar el token. Verifica el archivo .env")

bot = telebot.TeleBot(TOKEN)

PRODUCT_URLS = [
    "https://www.mercadolibre.cl/samsung-galaxy-s24-ultra-5g-dual-sim-256-gb-titanium-yellow-12-gb-ram/p/MLC34491097",
    "https://catalogo.movistar.cl/tienda/samsung-galaxy-s24-ultra-256-gb-gray-lamina-seminuevo",
    "https://www.falabella.com/falabella-cl/product/prod101890768/Celular-Samsung-Galaxy-S24-Ultra-5G-256GB/17007784",
    "https://tienda.clarochile.cl/catalogo/equiposclaro/samsung-s24ultra-256gb-titanium-gray-70012345pre",
    "https://www.paris.cl/samsung-galaxy-s24-ultra-5g-256gb-violeta-reacondicionado-MKONVK42H5.html",
    "https://store.wom.cl/equipos/SM-S928B-256GB/Samsung-Galaxy-S24-Ultra-5G-256GB",
    "https://catalogo.movistar.cl/tienda/samsung-galaxy-s24-ultra-512-gb-titanium-black-lamina-seminuevo",
    "https://miportal.entel.cl//personas/celulares/galaxy-s24-ultra-5g-512gb/prod2230052"
]

USE_PROXY = False
PROXY = "http://usuario:contraseña@ip:puerto"


def setup_driver():
    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument(f"user-agent={UserAgent().random}")

    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    if USE_PROXY:
        options.add_argument(f"--proxy-server={PROXY}")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# Función de extracción por sitio
def extract_price(driver, url):
    try:
        driver.get(url)
        domain = urlparse(url).netloc
        el = None

        if "mercadolibre" in domain:
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "andes-money-amount__fraction"))
            )

        elif "movistar.cl" in domain:
            el = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.price"))
            )

        elif "falabella.com" in domain:
            el = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-cmr-price] span.copy12'))
            )

        elif "clarochile.cl" in domain:
            try:
                el = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.price"))
                )
            except TimeoutException:
                return None

        elif "paris.cl" in domain:
            try:
                el = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h2[data-testid="paris-text"]'))
                )
            except TimeoutException:
                return None

        elif "wom.cl" in domain:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
            time.sleep(1)
            try:
                el = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.select-details-module--value--1lDtu"))
                )
            except TimeoutException:
                print("No se pudo encontrar el precio en wom.cl")
                return None

        else:
            print(f"❌ No hay extractor para: {url}")
            return None

        if el:
            text = el.text.strip().replace("\n", "")
            return int(''.join(filter(str.isdigit, text)))
        else:
            return None

    except Exception as e:
        print(f"❌ Error extrayendo precio de {url}: {e}")
        return None


# Variables de control
previous_prices = {url: None for url in PRODUCT_URLS}
monitoring = False


# Hilo de monitoreo
def monitor_prices(chat_id):
    global monitoring
    driver = setup_driver()

    while monitoring:
        for url in PRODUCT_URLS:
            price = extract_price(driver, url)

            if price is None:
                bot.send_message(chat_id, f"⚠️ No se pudo obtener el precio de:\n{url}")
                continue

            if previous_prices[url] is None:
                previous_prices[url] = price
                bot.send_message(chat_id, f"📌 Precio inicial de:\n{url}\n💰 ${price}")
            elif price != previous_prices[url]:
                bot.send_message(
                    chat_id,
                    f"🔔 Precio cambiado:\n{url}\nAntes: ${previous_prices[url]} → Ahora: ${price}"
                )
                previous_prices[url] = price
            else:
                bot.send_message(chat_id, f"✅ Sin cambios en:\n{url}\n💰 ${price}")

            delay = random.randint(30, 60)
            print(f"Esperando {delay}s...")
            time.sleep(delay)

        wait_time = random.randint(1200, 1800)
        print(f"⏳ Esperando {wait_time}s para el siguiente ciclo...")
        time.sleep(wait_time)

    driver.quit()


# Comandos del bot
@bot.message_handler(commands=['monitor'])
def monitor_command(message):
    global monitoring
    chat_id = message.chat.id
    if not monitoring:
        monitoring = True
        bot.send_message(chat_id, "🔎 Iniciando monitoreo de precios...")
        threading.Thread(target=monitor_prices, args=(chat_id,)).start()
    else:
        bot.send_message(chat_id, "⚠️ El monitoreo ya está en curso.")


@bot.message_handler(commands=['stop'])
def stop_command(message):
    global monitoring
    monitoring = False
    bot.send_message(message.chat.id, "🛑 Monitoreo detenido.")


# Iniciar bot
try:
    print("🤖 Bot ejecutándose...")
    bot.polling()
except Exception as e:
    print(f"Error en el bot: {e}")
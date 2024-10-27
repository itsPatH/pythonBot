import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import telebot
import os
from dotenv import load_dotenv
import threading

load_dotenv()

# Token de tu bot de Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN is None:
    raise ValueError("No se pudo cargar el token. Verifica el archivo .env")

bot = telebot.TeleBot(TOKEN)

# URL del producto en MercadoLibre
product_url = "https://www.mercadolibre.cl/samsung-galaxy-s24-ultra-5g-dual-sim-256-gb-titanium-yellow-12-gb-ram/p/MLC34491097"

# Variable para almacenar el precio anterior
previous_price = None
monitoring = False  # Variable para controlar el monitoreo

# Configuración de Selenium
def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Cambia a false si deseas ver la ventana
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Función para obtener el precio actual con Selenium
def get_price(driver):
    driver.get(product_url)
    time.sleep(3)  # Esperar a que la página cargue completamente
    
    try:
        price_element = driver.find_element(By.CLASS_NAME, "andes-money-amount__fraction")
        price = int(price_element.text.replace(".", "").replace("$", "").strip())  # Ajustar formato
        return price
    except Exception as e:
        print(f"Error al obtener el precio: {e}")
        return None

# Función para monitorear el precio y enviar alertas
def monitor_price(chat_id):
    global previous_price, monitoring
    driver = setup_driver()
    
    while monitoring:
        current_price = get_price(driver)
        
        if current_price is None:
            bot.send_message(chat_id, "No se pudo obtener el precio actual.")
            break

        if previous_price is None:
            previous_price = current_price

        if current_price != previous_price:
            bot.send_message(
                chat_id,
                f"El precio ha cambiado: {previous_price} -> {current_price}\nRevisa el producto aquí: {product_url}"
            )
            previous_price = current_price
        
        time.sleep(3600)  # Espera 1 hora antes de verificar nuevamente
    
    driver.quit()

# Comando para iniciar el monitoreo
@bot.message_handler(commands=['monitor'])
def monitor(message):
    global monitoring
    chat_id = message.chat.id
    bot.send_message(chat_id, "Iniciando monitoreo de precio...")
    monitoring = True
    thread = threading.Thread(target=monitor_price, args=(chat_id,))
    thread.start()

# Comando para detener el monitoreo
@bot.message_handler(commands=['stop'])
def stop_monitor(message):
    global monitoring
    chat_id = message.chat.id
    monitoring = False
    bot.send_message(chat_id, "Deteniendo el monitoreo de precio.")

# Inicia el bot
try:
    bot.polling()
except Exception as e:
    print(f"Ocurrió un error en el bot: {e}")
# Price Monitor Bot

Bot de Telegram para monitorear precios de productos en distintas tiendas online (MercadoLibre, Movistar, Falabella, etc.) usando Selenium y notificando cambios o problemas.

---

## Contenido

- [Requisitos](#requisitos)  
- [Creación del Bot de Telegram](#creación-del-bot-de-telegram)  
- [Configuración](#configuración)  
- [Instalación](#instalación)  
- [Uso](#uso)  
- [Comandos del bot](#comandos-del-bot)  
- [Notas](#notas)

---

## Requisitos

- Python 3.8 o superior  
- Google Chrome instalado  
- Cuenta de Telegram para crear un bot  
- Conexión a internet  
- Archivo `.env` con variables de entorno  

---

## Creación del Bot de Telegram

1. Abre Telegram y busca el usuario [@BotFather](https://t.me/BotFather).  
2. Envía el comando `/newbot`.  
3. Sigue las instrucciones para darle nombre y username a tu bot.  
4. Al terminar, BotFather te entregará un **token de acceso** parecido a `123456789:ABCDefGhIJKLmnoPQRstUvwxYZ`.  
5. Guarda este token, lo necesitarás para configurar el bot.  

---

## Configuración

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

env
TELEGRAM_TOKEN=TU_TOKEN_AQUI
Reemplaza TU_TOKEN_AQUI con el token que obtuviste de BotFather.

## Instalación
Clona o descarga este repositorio.

Abre una terminal y navega a la carpeta del proyecto.

Crea un entorno virtual (opcional pero recomendado):
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
Instala las dependencias:

pip install -r requirements.txt
Si no tienes el archivo requirements.txt, instala estas librerías manualmente:
pip install selenium webdriver-manager python-dotenv pyTelegramBotAPI fake-useragent

## Uso
Asegúrate de tener Google Chrome instalado.

Ejecuta el script principal (price_monitor_bot.py o el nombre que le hayas dado):

python price_monitor_bot.py
Abre Telegram y busca tu bot por su username.

Envía el comando /monitor para iniciar el monitoreo de precios.

El bot te enviará mensajes con precios iniciales y cambios detectados.

Envía /stop para detener el monitoreo.

## Comandos del bot
/monitor → Inicia el monitoreo continuo de precios.

/stop → Detiene el monitoreo.

## Notas importantes
El bot abre Chrome en modo headless (sin ventana visible).

Los selectores de precio pueden cambiar con el tiempo, es necesario actualizarlos si deja de funcionar.

El script usa tiempos de espera aleatorios para evitar bloqueo por parte de las tiendas.

Usa el bot bajo tu responsabilidad, respeta los términos de uso de las tiendas web.

Si usas proxy, configura la variable USE_PROXY y PROXY en el script.

Puedes agregar o quitar URLs en la lista PRODUCT_URLS dentro del script.

Si tienes dudas o problemas, ¡avísame para ayudarte!

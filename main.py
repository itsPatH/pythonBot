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

        # Enviar un mensaje si el precio baja a 900.000 o menos
        if current_price <= 900000:
            bot.send_message(
                chat_id,
                f"¡El precio ha bajado a {current_price}! Revisa el producto aquí: {product_url}"
            )
        
        # Notificar si el precio ha cambiado
        if current_price != previous_price:
            bot.send_message(
                chat_id,
                f"El precio ha cambiado: {previous_price} -> {current_price}\nRevisa el producto aquí: {product_url}"
            )
            previous_price = current_price
        
        time.sleep(3600)  # Espera 1 hora antes de verificar nuevamente
    
    driver.quit()
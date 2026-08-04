from datetime import datetime
import threading
import time
from flask import Flask
import schedule
import telebot

TOKEN = "7691909067:AAG4EdkF0-_lpefI9ewFpo6AMhqawBZztAM"
CANAL = "@agenciafyd"
ENLACE_CANAL = "https://t.me/+x4A5d5Jpu44yNzc5"

bot = telebot.TeleBot(TOKEN)

# --- 3 ESTRUCTURAS DE DATOS SEPARADAS PARA LOS 3 BLOQUES ---
resultados_bloque_1 = {}  # Minutos 00 a 10
resultados_bloque_2 = {}  # Minutos 10 a 20
resultados_bloque_3 = {}  # Minutos 30 a 40

LOTERIAS_COMPLETAS = [
    "Lotto Activo", "La Granjita", "Selva Plus", "Lotto Real",
    "Guácharo Activo", "Loto Chaima", "Monje Millonario",
    "Lotto RD", "Lotto Inter", "Guacharito Millonario",
    "Guaca Activa", "Mega Guaca",
]

# --- MENSAJES DE INICIO, CIERRE Y DÓLAR ---
def enviar_mensaje_buenos_dias():
    msg = (
        "🍀 **¡BUENOS DÍAS, CARGADOS DE BUENA SUERTE!** 🍀\n\n"
        "☀️ Arrancamos un nuevo día con la mejor energía para ganar.\n"
        f"🎯 Únete a nuestro canal oficial y entérate de todo: {ENLACE_CANAL}\n\n"
        "¡Que la suerte esté de tu lado hoy!"
    )
    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar buenos días: {e}")

def enviar_mensaje_buenas_noches():
    msg = (
        "🌙 **¡FIN DE LA JORNADA!** 🌙\n\n"
        "🍀 Gracias a todos por acompañarnos hoy en Agencia F&D.\n"
        "✨ ¡Que descansen y nos vemos mañana con más suerte y grandes premios! 🎯"
    )
    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar buenas noches: {e}")

def enviar_tasa_dolar():
    # Aquí puedes actualizar o integrar tu función de tasa del dólar si la tienes automatizada
    msg = (
        "💵 **TASA MONITOR DOLAR** 💵\n\n"
        "📊 Mantente atento a nuestras referencias para el pago de tus jugadas.\n"
        "🍀 Agencia F&D"
    )
    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar dólar: {e}")

def enviar_resultado_individual(nombre_loteria, hora_resultado, resultado):
    msg = (
        f"🎯 **NUEVO RESULTADO** 🎯\n\n"
        f"🎲 **Lotería:** {nombre_loteria}\n"
        f"⏰ **Hora:** {hora_resultado}\n"
        f"🏆 **Resultado:** {resultado}\n\n"
        f"🍀 Agencia F&D"
    )
    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar resultado individual: {e}")

# --- GUARDAR Y CLASIFICAR SEGÚN EL MINUTO EXACTO ---
def guardar_resultado_en_memoria(nombre_loteria, hora_resultado, resultado):
    enviar_resultado_individual(nombre_loteria, hora_resultado, resultado)
    
    try:
        dt = datetime.strptime(hora_resultado, "%H:%M")
        minuto = dt.minute
        slot_hora = dt.strftime("%H:%M")

        if 0 <= minuto <= 10:
            if slot_hora not in resultados_bloque_1:
                resultados_bloque_1[slot_hora] = {}
            resultados_bloque_1[slot_hora][nombre_loteria] = resultado

        elif 10 < minuto <= 20:
            if slot_hora not in resultados_bloque_2:
                resultados_bloque_2[slot_hora] = {}
            resultados_bloque_2[slot_hora][nombre_loteria] = resultado

        elif 20 < minuto <= 40:
            if slot_hora not in resultados_bloque_3:
                resultados_bloque_3[slot_hora] = {}
            resultados_bloque_3[slot_hora][nombre_loteria] = resultado
    except Exception as e:
        print(f"Error al clasificar resultado: {e}")

# --- CONSTRUCTOR Y ENVÍO DE LAS 3 TABLAS ---
def construir_y_enviar_tabla(bloque_id):
    hoy = datetime.now().strftime("%d/%m/%Y")
    
    if bloque_id == 1:
        slots_dict = resultados_bloque_1
        titulo_seccion = "📊 **RESULTADOS - BLOQUE (00 a 10)**"
    elif bloque_id == 2:
        slots_dict = resultados_bloque_2
        titulo_seccion = "📊 **RESULTADOS - BLOQUE (10 a 20)**"
    else:
        slots_dict = resultados_bloque_3
        titulo_seccion = "📊 **RESULTADOS - BLOQUE (hasta 40)**"

    slots_activos = [s for s in sorted(slots_dict.keys()) if slots_dict[s]]

    if not slots_activos:
        slots_activos = ["08:00"]
        slots_dict["08:00"] = {lot: "12🐎" for lot in LOTERIAS_COMPLETAS[:4]}

    msg = f"🍀 **AGENCIA F&D** 🍀\n"
    msg += f"✨ ¡La suerte comienza aquí! ✨\n"
    msg += f"{titulo_seccion}\n"
    msg += f"📅 {hoy}\n\n"

    bloques_loterias = [
        LOTERIAS_COMPLETAS[0:4],
        LOTERIAS_COMPLETAS[4:8],
        LOTERIAS_COMPLETAS[8:12]
    ]

    for bloque in bloques_loterias:
        msg += "------------------------------------------\n"
        header = f"{'HORA':<8}"
        for lot in bloque:
            nombre_corto = (lot[:8] + '..') if len(lot) > 8 else lot[:8]
            header += f"{nombre_corto:<9}"
        msg += f"`{header}`\n"

        for slot in slots_activos:
            row = f"{slot:<8}"
            for lot in bloque:
                res = slots_dict[slot].get(lot, "----")
                row += f"{res:<9}"
            msg += f"`{row}`\n"
        
        msg += "\n"

    msg += "🍀 Gracias por preferir Agencia F&D\n"
    msg += "🎯 ¡Mucha suerte en cada jugada!\n"

    try:
        bot.send_message(CANAL, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error al enviar tabla del bloque {bloque_id}: {e}")

    slots_dict.clear()

# --- COMANDOS DE PRUEBA DESDE TELEGRAM ---
@bot.message_handler(commands=['tabla1'])
def probar_tabla_1(message):
    construir_y_enviar_tabla(1)
    bot.reply_to(message, "Tabla del Bloque 1 enviada.")

@bot.message_handler(commands=['tabla2'])
def probar_tabla_2(message):
    construir_y_enviar_tabla(2)
    bot.reply_to(message, "Tabla del Bloque 2 enviada.")

@bot.message_handler(commands=['tabla3'])
def probar_tabla_3(message):
    construir_y_enviar_tabla(3)
    bot.reply_to(message, "Tabla del Bloque 3 enviada.")

@bot.message_handler(commands=['dia'])
def probar_dia(message):
    enviar_mensaje_buenos_dias()
    bot.reply_to(message, "Mensaje de buenos días enviado.")

@bot.message_handler(commands=['noche'])
def probar_noche(message):
    enviar_mensaje_buenas_noches()
    bot.reply_to(message, "Mensaje de buenas noches enviado.")

@bot.message_handler(commands=['dolar'])
def probar_dolar(message):
    enviar_tasa_dolar()
    bot.reply_to(message, "Tasa del dólar enviada.")

# --- PROGRAMACIÓN DE ENVÍOS CON SCHEDULE ---
schedule.every().day.at("07:30").do(enviar_mensaje_buenos_dias)
schedule.every().day.at("09:00").do(enviar_tasa_dolar)
schedule.every().day.at("20:00").do(enviar_mensaje_buenas_noches)

# Tablas automáticas
schedule.every().hour.at(":10").do(lambda: construir_y_enviar_tabla(1))
schedule.every().hour.at(":20").do(lambda: construir_y_enviar_tabla(2))
schedule.every().hour.at(":40").do(lambda: construir_y_enviar_tabla(3))

def ejecutar_programador():
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- SERVIDOR FLASK Y BUCLE DE TELEGRAM ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Telegram activo y operando 24/7."

if __name__ == "__main__":
    hilo_schedule = threading.Thread(target=ejecutar_programador)
    hilo_schedule.daemon = True
    hilo_schedule.start()

    hilo_bot = threading.Thread(target=bot.infinity_polling)
    hilo_bot.daemon = True
    hilo_bot.start()

    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

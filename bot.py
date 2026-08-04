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

# --- NUEVA ESTRUCTURA PARA LAS TABLAS ---
resultados_memoria = {
    "08:00": {},
    "08:30": {},
    "09:00": {},
    "09:30": {},
    "10:00": {},
    "10:30": {},
    "11:00": {},
    "11:30": {},
    "12:00": {},
    "12:30": {},
    "13:00": {},
    "13:30": {},
    "14:00": {},
    "14:30": {},
    "15:00": {},
    "15:30": {},
    "16:00": {},
    "16:30": {},
    "17:00": {},
    "17:30": {},
    "18:00": {},
    "18:30": {},
    "19:00": {},
}

LOTERIAS_BLOQUES = [
    "Lotto Activo",
    "La Granjita",
    "Selva Plus",
    "Lotto Real",
    "Guácharo Activo",
    "Loto Chaima",
    "Monje Millonario",
    "Lotto RD",
    "Lotto Inter",
    "Guacharito Millonario",
    "Guaca Activa",
    "Mega Guaca",
]


def redondear_a_media_hora(hora_str):
  try:
    dt = datetime.strptime(hora_str, "%H:%M")
    minuto = 0 if dt.minute < 30 else 30
    return dt.replace(minute=minuto, second=0).strftime("%H:%M")
  except:
    ahora = datetime.now()
    minuto = 0 if ahora.minute < 30 else 30
    return ahora.replace(minute=minuto, second=0).strftime("%H:%M")


def guardar_resultado_en_memoria(nombre_loteria, hora_resultado, resultado):
  slot_tiempo = redondear_a_media_hora(hora_resultado)
  if slot_tiempo not in resultados_memoria:
    resultados_memoria[slot_tiempo] = {}
  resultados_memoria[slot_tiempo][nombre_loteria] = resultado


def construir_y_enviar_tabla(rango_minutos_desc):
  hoy = datetime.now().strftime("%d/%m/%Y")
  slots_activos = [
      s for s in sorted(resultados_memoria.keys()) if resultados_memoria[s]
  ]

  if not slots_activos:
    slots_activos = ["08:00", "08:30"]
    resultados_memoria["08:00"] = {
        "Lotto Activo": "12🐎",
        "La Granjita": "25🐔",
        "Selva Plus": "34🦌",
        "Lotto Real": "09🦅",
    }
    resultados_memoria["08:30"] = {
        "Lotto Activo": "31🦫",
        "La Granjita": "18🫏",
        "Selva Plus": "10🐯",
        "Lotto Real": "24🦎",
    }

  columnas = LOTERIAS_BLOQUES[:4]

  texto_tabla = (
      f"🍀 AGENCIA F&D 🍀\n"
      f"✨ ¡La suerte comienza aquí! ✨\n"
      f"📊 RESULTADOS ANIMALITOS\n"
      f"📅 {hoy}\n\n"
  )

  header_row = "┌───────" + "┬──────────" * len(columnas) + "┐\n"
  header_row += "│ HORA  "
  for lot in columnas:
    header_row += f"│{lot[:9]:<10}"
  header_row += "│\n"
  header_row += "├───────" + "┼──────────" * len(columnas) + "┤\n"

  texto_tabla += header_row

  for slot in slots_activos[:6]:
    fila = f"│{slot}   "
    for lot in columnas:
      res = resultados_memoria[slot].get(lot, "----")
      fila += f"│{res:<10}"
    fila += "│\n"
    texto_tabla += fila

  footer_row = "└───────" + "┴──────────" * len(columnas) + "┘\n"
  texto_tabla += footer_row + "\n"

  texto_tabla += (
      "🍀 Gracias por preferir Agencia F&D\n"
      "🎯 ¡Mucha suerte en cada jugada!"
  )

  try:
    bot.send_message(CANAL, texto_tabla)
  except Exception as e:
    print(f"Error al enviar tabla automática: {e}")

  for slot in slots_activos:
    resultados_memoria[slot].clear()


# --- COMANDO DE PRUEBA DESDE TELEGRAM ---
@bot.message_handler(commands=["tabla", "probar"])
def enviar_prueba_manual(message):
  try:
    construir_y_enviar_tabla("Manual")
    bot.reply_to(
        message, "¡Tabla de prueba enviada con éxito al canal configurado!"
    )
  except Exception as e:
    bot.reply_to(message, f"Error al generar la prueba: {e}")


# --- PROGRAMACIÓN DE ENVÍOS CON SCHEDULE ---
schedule.every().hour.at(":10").do(
    lambda: construir_y_enviar_tabla("00 a 10")
)
schedule.every().hour.at(":20").do(
    lambda: construir_y_enviar_tabla("11 a 20")
)
schedule.every().hour.at(":40").do(
    lambda: construir_y_enviar_tabla("30 a 40")
)


def ejecutar_programador():
  while True:
    schedule.run_pending()
    time.sleep(1)


# --- SERVIDOR FLASK Y BUCLE DE TELEGRAM ---
app = Flask(__name__)


@app.route("/")
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

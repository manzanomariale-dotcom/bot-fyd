from datetime import datetime
import threading
import time
from flask import Flask
import schedule
import telebot

TOKEN = '7691909067:AAG4EdkF0-_lpefI9ewFpo6AMhqawBZztAM'
CANAL = '@agenciafyd'
ENLACE_CANAL = 'https://t.me/+x4A5d5Jpu44yNzc5'

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

# Orden estricto de las loterías agrupadas por bloques
LOTERIAS_BLOQUES = [
    # Bloque 1
    "Lotto Activo",
    "La Granjita",
    "Selva Plus",
    "Lotto Real",
    # Bloque 2
    "Guácharo Activo",
    "Loto Chaima",
    "Monje Millonario",
    # Bloque 3
    "Lotto RD",
    "Lotto Inter",
    "Guacharito Millonario",
    # Bloque 4
    "Guaca Activa",
    "Mega Guaca",
]


def redondear_a_media_hora(hora_str):
  """Ajusta la hora del resultado al formato de 30 minutos (ej: 08:05 -> 08:00)"""
  try:
    dt = datetime.strptime(hora_str, "%H:%M")
    minuto = 0 if dt.minute < 30 else 30
    return dt.replace(minute=minuto, second=0).strftime("%H:%M")
  except:
    ahora = datetime.now()
    minuto = 0 if ahora.minute < 30 else 30
    return ahora.replace(minute=minuto, second=0).strftime("%H:%M")


def guardar_resultado_en_memoria(nombre_loteria, hora_resultado, resultado):
  """Función que debes llamar cada vez que obtengas un resultado individual."""
  slot_tiempo = redondear_a_media_hora(hora_resultado)
  if slot_tiempo not in resultados_memoria:
    resultados_memoria[slot_tiempo] = {}
  resultados_memoria[slot_tiempo][nombre_loteria] = resultado


def construir_y_enviar_tabla(rango_minutos_desc):
  """Genera y envía la tabla en formato Unicode según el rango de tiempo acumulado."""
  hoy = datetime.now().strftime("%d/%m/%Y")

  slots_activos = [
      s for s in sorted(resultados_memoria.keys()) if resultados_memoria[s]
  ]

  if not slots_activos:
    return  # Si no hay datos, no envía nada.

  columnas = LOTERIAS_BLOQUES[:4]  # Muestra un bloque de 4 loterías por tabla

  texto_tabla = (
      f"🍀 AGENCIA F&D 🍀\n"
      f"✨ ¡La suerte comienza aquí! ✨\n"
      f"📊 RESULTADOS ANIMALITOS\n"
      f"📅 {hoy}\n\n"
      f"```text\n"
  )

  header_row = "┌───────" + "┬──────" * len(columnas) + "┐\n"
  header_row += "│ HORA  "
  for lot in columnas:
    header_row += f"│{lot[:5]:<6}"
  header_row += "│\n"
  header_row += "├───────" + "┼──────" * len(columnas) + "┤\n"

  texto_tabla += header_row

  for slot in slots_activos[:6]:
    fila = f"│{slot}   "
    for lot in columnas:
      res = resultados_memoria[slot].get(lot, "----")
      fila += f"│{res:<6}"
    fila += "│\n"
    texto_tabla += fila

  footer_row = "└───────" + "┴──────" * len(columnas) + "┘\n"
  texto_tabla += footer_row
  texto_tabla += "```\n"

  texto_tabla += (
      "🍀 Gracias por preferir Agencia F&D\n"
      "🎯 ¡Mucha suerte en cada jugada!"
  )

  # Enviar al canal usando la variable correcta (CANAL)
  try:
    bot.send_message(CANAL, texto_tabla, parse_mode="Markdown")
  except Exception as e:
    print(f"Error al enviar tabla automática: {e}")

  for slot in slots_activos:
    resultados_memoria[slot].clear()


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
    
# --- COMANDO DE PRUEBA DESDE TELEGRAM ---
@bot.message_handler(commands=['tabla', 'probar'])
def enviar_prueba_manual(message):
  try:
    construir_y_enviar_tabla('Manual')
  except Exception as e:
    bot.reply_to(message, f'Error al generar la prueba: {e}')

# --- SERVIDOR FLASK PARA MANTENERSE ACTIVO EN RENDER ---
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot de Telegram activo y operando 24/7."


if __name__ == "__main__":
  hilo_schedule = threading.Thread(target=ejecutar_programador)
  hilo_schedule.daemon = True
  hilo_schedule.start()

  import os

  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)

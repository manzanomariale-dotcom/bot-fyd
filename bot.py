from datetime import datetime
import json
import os
import random
import re
from threading import Thread
import time
from bs4 import BeautifulSoup
from flask import Flask
import requests
import schedule
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "7691909067:AAG4EdkF0-_lpefI9ewFpo6AMhqawBZztAM"
CANAL = "@agenciafyd"
ENLACE_CANAL = "https://t.me/+x4A5d5Jpu44yNzc5"

URL_LOTERIA = "https://lotery.winbigvzla.com/resultados"
URL_BCV = "https://www.bcv.org.ve/"

ARCH_REGISTRO = "resultados_enviados.json"

HEADER_FyD = (
    "Resultado: AGENCIA FyD\n"
    "JUEGA AQUI\n"
    "RESULTADOS ANIMALITOS\n\n"
    "🎲 *{nombre_loteria}* 🎲\n"
    "Hora: {hora}\n"
    "Animalito: *{resultado}*\n\n"
    f"{ENLACE_CANAL}"
)

app = Flask("")


@app.route("/")
def home():
  return "Bot Agencia FyD activo y en línea."


@app.route("/test/madrugada")
def test_madrugada():
  enviar_saludo_madrugada()
  return "Prueba de madrugada ejecutada."


@app.route("/test/piramide")
def test_piramide():
  enviar_piramide_diaria()
  return "Prueba de pirámide ejecutada."


@app.route("/test/regalo")
def test_regalo():
  enviar_datos_regalo()
  return "Prueba de regalo automático ejecutada."


@app.route("/test/saludo")
def test_saludo():
  enviar_saludo_matutino()
  return "Prueba de saludo ejecutada."


@app.route("/test/bcv")
def test_bcv():
  enviar_tasa_dolar()
  return "Prueba de BCV ejecutada."


@app.route("/test/cierre")
def test_cierre():
  enviar_mensaje_cierre()
  return "Prueba de cierre ejecutada."


@app.route("/test/forzar")
def test_forzar():
  """Ruta manual para forzar la revisión y envío inmediato desde el navegador"""
  verificar_y_enviar_resultados_individuales()
  return (
      "Revisión de resultados forzada ejecutada. Revisa el canal y los logs."
  )


def limpiar_texto(texto):
  return " ".join(texto.split())


def enviar_telegram(mensaje, disable_web_preview=True):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {
      "chat_id": CANAL,
      "text": mensaje,
      "parse_mode": "Markdown",
      "disable_web_page_preview": disable_web_preview,
  }
  try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Telegram respuesta: {response.status_code} - {response.text}")
  except Exception as e:
    print(f"⚠️ Excepción en Telegram: {e}")


def enviar_saludo_madrugada():
  enviar_telegram(
      "🎯 AGENCIA FyD\n_Trabajamos para tí_\n\n🌅 ¡Despertando con la mejor"
      " energía! 🌅\nTaquilla Activa\n\nWHATSAPP: 0424-9611372"
  )


def generar_piramide():
  ahora = datetime.now()
  fecha_str = ah_str = ahora.strftime("%d/%m/%Y")
  digitos = [int(c) for c in fecha_str if c.isdigit()]
  filas = [digitos]
  while len(filas[-1]) > 1:
    actual = filas[-1]
    siguiente = [
        (actual[i] + actual[i + 1]) % 10 for i in range(len(actual) - 1)
    ]
    filas.append(siguiente)

  lineas_formateadas = []
  for i, f in enumerate(filas):
    nums_str = "  ".join(str(d) for d in f)
    dots_count = 3 + (i * 2)
    lineas_formateadas.append(f"{'.' * dots_count}  {nums_str}  {'.' * dots_count}")

  cuerpo_piramide = "\n".join(lineas_formateadas)
  return (
      f"*AGENCIA FyD*\n📢 REPORTE TÁCTICO - LA PIRÁMIDE"
      f" 📢\n\n📅 Fecha: {fecha_str}\n\n{cuerpo_piramide}\n\nWHATSAPP:"
      " 04249611372"
  )


def enviar_piramide_diaria():
  enviar_telegram(generar_piramide())


def enviar_datos_regalo():
  tabla_animalitos = {
      0: "0 - Delfín / 00 - Ballena",
      1: "1 - Carnero",
      2: "2 - Toro",
      3: "3 - Ciempiés",
      4: "4 - Alacrán",
      5: "5 - León",
      6: "6 - Rana",
      7: "7 - Perico",
      8: "8 - Ratón",
      9: "9 - Águila",
      10: "10 - Tigre",
      11: "11 - Gato",
      12: "12 - Caballo",
      13: "13 - Mono",
      14: "14 - Paloma",
      15: "15 - Zorro",
      16: "16 - Oso",
      17: "17 - Pavo",
      18: "18 - Burro",
      19: "19 - Chivo",
      20: "20 - Cochino",
      21: "21 - Gallo",
      22: "22 - Camello",
      23: "23 - Cebra",
      24: "24 - Iguana",
      25: "25 - Gallina",
      26: "26 - Vaca",
      27: "27 - Perro",
      28: "28 - Zamuro",
      29: "29 - Elefante",
      30: "30 - Caimán",
      31: "31 - Lapa",
      32: "32 - Ardilla",
      33: "33 - Pescado",
      34: "34 - Venado",
      35: "35 - Girafa",
      36: "36 - Culebra",
  }

  ahora = datetime.now()
  fecha_str = ahora.strftime("%d/%m/%Y")
  digitos = [int(c) for c in fecha_str if c.isdigit()]

  num_1 = (digitos[0] + digitos[2] + digitos[4]) % 37
  num_2 = (sum(digitos)) % 37
  num_3 = abs(digitos[1] - digitos[3] + digitos[5]) % 37

  regalo_1 = tabla_animalitos.get(num_1, "12 - Caballo")
  regalo_2 = tabla_animalitos.get(num_2, "24 - Iguana")
  regalo_3 = tabla_animalitos.get(num_3, "0 - Delfín")

  mensaje = (
      "*AGENCIA FyD*\n"
      "🎁 ¡REGALO TÁCTICO DEL DÍA! 🎁\n\n"
      "Selección automática basada en la fecha de hoy:\n\n"
      f"🎯 *{regalo_1}*\n"
      f"🎯 *{regalo_2}*\n"
      f"🎯 *{regalo_3}*\n\n"
      "¡Mucha suerte a todos nuestros jugadores!\n\n"
      "📲 WHATSAPP: 0424-9611372\n\n"
      f"{ENLACE_CANAL}"
  )
  enviar_telegram(mensaje)


def enviar_saludo_matutino():
  enviar_telegram(
      "*🎯 AGENCIA FyD 🎯*\n☀️ ¡Buenos días! Arrancamos la jornada con la mejor"
      " actitud.\n\n📲 WHATSAPP: 0424-9611372"
  )


def enviar_tasa_dolar():
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL_BCV, headers=headers, timeout=15, verify=False)
    precio_dolar = "742,23"
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      dolar_div = soup.find("div", id="dolar")
      if dolar_div and dolar_div.find("strong"):
        precio_dolar = dolar_div.find("strong").get_text(strip=True)
    enviar_telegram(
        f"*💵 TASA OFICIAL BCV 💵*\n📈 Precio Oficial: Bs."
        f" {precio_dolar}\nVerifica la tasa oficial en: {URL_BCV}"
    )
  except Exception as e:
    print(f"Error BCV: {e}")


def enviar_mensaje_cierre():
  enviar_telegram(
      "*AGENCIA FyD*\n🌙 ¡FINAL DE JORNADA! 🌙\nGracias por jugar con nosotros."
  )


def cargar_registros():
  if os.path.exists(ARCH_REGISTRO):
    try:
      with open(ARCH_REGISTRO, "r") as f:
        data = json.load(f)
        if data.get("fecha") == datetime.now().strftime("%d-%m-%Y"):
          return set(data.get("enviados", []))
    except Exception:
      pass
  return set()


def guardar_registros(enviados_set):
  data = {
      "fecha": datetime.now().strftime("%d-%m-%Y"),
      "enviados": list(enviados_set),
  }
  try:
    with open(ARCH_REGISTRO, "w") as f:
      json.dump(data, f)
  except Exception as e:
    print(f"Error al guardar registros: {e}")


def verificar_y_enviar_resultados_individuales():
  enviados_hoy = cargar_registros()

  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    respuesta = requests.get(URL_LOTERIA, headers=headers, timeout=15)
    if respuesta.status_code != 200:
      print(f"Error HTTP lotería: {respuesta.status_code}")
      return

    soup = BeautifulSoup(respuesta.text, "html.parser")
    # Buscamos todos los textos posibles o elementos de la página
    textos = [
        t.get_text(" ", strip=True) for t in soup.find_all(["div", "span", "p"])
    ]
    texto_completo = " ".join(textos).upper()

    print(
        f"DEBUG: Longitud texto extraído: {len(texto_completo)}"
    )  # Para verlo en los logs de Render

    # Buscamos patrones del tipo: Lotería ... Hora ... Número - Animalito
    # O buscamos bloques que contengan horas y animalitos de forma flexible
    # Intento de extracción general de horas y animalitos cercanos
    coincidencias = re.findall(
        r"(\d{1,2}:\d{2}\s*(?:AM|PM))\D{1,30}(\d{1,2}\s-\s[A-ZÁÉÍÓÚÑa-zñáéíóú]+)",
        texto_completo,
    )

    hubo_cambios = False
    for hora_match, res_match in coincidencias:
      hora = hora_match.upper()
      resultado = limpiar_texto(res_match).upper()
      nombre_loteria = (
          "WINBIG"  # Nombre genérico de respaldo si no se aísla la lotería
      )

      id_resultado = f"{hora}_{resultado}"

      if id_resultado not in enviados_hoy:
        mensaje = HEADER_FyD.format(
            nombre_loteria=nombre_loteria, hora=hora, resultado=resultado
        )
        enviar_telegram(mensaje)
        enviados_hoy.add(id_resultado)
        hubo_cambios = True
        time.sleep(2)

    if hubo_cambios:
      guardar_registros(enviados_hoy)

  except Exception as e:
    print(f"Error al verificar resultados individuales: {e}")


def loop_bot():
  schedule.every().day.at("06:30").do(enviar_saludo_madrugada)
  schedule.every().day.at("06:31").do(enviar_piramide_diaria)
  schedule.every().day.at("06:35").do(enviar_datos_regalo)
  schedule.every().day.at("07:00").do(enviar_saludo_matutino)
  schedule.every().day.at("16:30").do(enviar_tasa_dolar)
  schedule.every().day.at("20:00").do(enviar_mensaje_cierre)

  schedule.every(1).minute.do(verificar_y_enviar_resultados_individuales)

  while True:
    try:
      schedule.run_pending()
    except Exception as e:
      print(f"Error en schedule: {e}")
    time.sleep(1)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  t_schedule = Thread(target=loop_bot)
  t_schedule.daemon = True
  t_schedule.start()

  app.run(host="0.0.0.0", port=port)

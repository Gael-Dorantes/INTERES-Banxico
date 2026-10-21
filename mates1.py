"""
V1
Autor: Jesus Gael Dorantes Quiroz
Fecha: 7 de Octubre del 2026
Solicitud: Consultar series de Banxico y calcular interes simple.
Datos de entrada: Capital y correo de destino.
Datos de salida: Consulta de tasas y reporte de interes simple.
"""

import os
import time
import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


SERIE_CONSULTA = "SF60648" 
SERIE_CETES = "SF60633"     


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


TOKEN_BANXICO = os.getenv("BANXICO_TOKEN")
CORREO_ORIGEN = os.getenv("CORREO_ORIGEN")
CORREO_PASSWORD = os.getenv("CORREO_PASSWORD")

continuar_programa = True


def consulta_banxico(serie):
    """
    Consulta una serie de Banxico y muestra
    el dato mas reciente disponible.
    """
    if not TOKEN_BANXICO:
        print("Falta configurar BANXICO_TOKEN en el archivo .env")
        return None

    url = (
        "https://www.banxico.org.mx/SieAPIRest/service/v1/"
        f"series/{serie}/datos"
    )

    encabezados = {
        "Bmx-Token": TOKEN_BANXICO,
        "Accept": "application/json"
    }

    try:
        respuesta = requests.get(
            url,
            headers=encabezados,
            timeout=15
        )

        respuesta.raise_for_status()

        datos = respuesta.json()["bmx"]["series"][0]["datos"]

        if not datos:
            print("Banxico no devolvio datos.")
            return None

        dato_reciente = datos[-1]

        print("\nConexion con Banxico correcta.")
        print("Serie consultada:", serie)
        print("Fecha del dato:", dato_reciente["fecha"])
        print("Dato mas reciente:", dato_reciente["dato"])

        valor = dato_reciente["dato"].replace(",", "")

        if valor.upper() in ("N/E", "NA", ""):
            print("El dato mas reciente no es numerico.")
            return None

        return float(valor)

    except requests.exceptions.RequestException as error:
        print("Error al consultar Banxico:", error)

    except (KeyError, IndexError, ValueError, TypeError) as error:
        print("Error al leer los datos:", error)

    return None


def consultar_serie():
    """
    Consulta la TIIE a 28 dias definida en el codigo.
    No solicita ninguna serie al usuario.
    """
    print("\nCONSULTA DE TIIE A 28 DIAS")
    consulta_banxico(SERIE_CONSULTA)


def enviar_reporte(reporte):
    """
    Guarda el reporte en un archivo y permite
    enviarlo por correo electronico.
    """
    nombre_archivo = "reporte_interes_simple.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(reporte)

    print("\nReporte guardado en:", nombre_archivo)

    if not CORREO_ORIGEN or not CORREO_PASSWORD:
        print("Faltan los datos del correo en el archivo .env.")
        print("El reporte se guardo, pero no se envio.")
        return

    correo_destino = input(
        "Introduce el correo al que deseas enviar el reporte: "
    ).strip()

    if not correo_destino:
        print("No escribiste el correo de destino.")
        print("El reporte se guardo, pero no se envio.")
        return

    mensaje = EmailMessage()
    mensaje["Subject"] = "Reporte de interes simple con CETES"
    mensaje["From"] = CORREO_ORIGEN
    mensaje["To"] = correo_destino

    mensaje.set_content(
        "Hola.\n\n"
        "Le envio el reporte de interes simple "
        "calculado con la tasa consultada de Banxico."
    )

    with open(nombre_archivo, "rb") as archivo:
        contenido = archivo.read()

    mensaje.add_attachment(
        contenido,
        maintype="text",
        subtype="plain",
        filename=nombre_archivo
    )

    try:
        print("Conectando con Gmail...")

        with smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=30
        ) as servidor:

            servidor.login(
                CORREO_ORIGEN.strip(),
                CORREO_PASSWORD.strip().replace(" ", "")
            )

            servidor.send_message(mensaje)

        print("Reporte enviado correctamente.")
        print("Destinatario:", correo_destino)

    except smtplib.SMTPAuthenticationError:
        print("Error de autenticacion.")
        print("Verifica el correo y la contrasena de aplicacion.")

    except (smtplib.SMTPException, OSError) as error:
        print("No se pudo enviar el correo:", error)
        print("El reporte sigue guardado en el archivo de texto.")

    except Exception as error:
        print("Ocurrio un error inesperado:", error)
        print("El reporte sigue guardado en el archivo de texto.")


def calcula_interes_cetes():
    """
    Consulta CETES a 28 dias y calcula el interes simple.
    """
    print("\nCALCULO DE INTERES SIMPLE CON CETES")

    tasa = consulta_banxico(SERIE_CETES)

    if tasa is None:
        print("No se pudo obtener una tasa valida de CETES.")
        return

    try:
        capital = float(input("Escribe el capital inicial: $"))

        if capital <= 0:
            print("El capital debe ser mayor que cero.")
            return

        dias = 28

        
        interes = capital * (tasa / 100) * (dias / 360)
        monto_total = capital + interes

        reporte = (
            "REPORTE DE INTERES SIMPLE CON CETES\n"
            "-----------------------------------\n"
            f"Serie de Banxico: {SERIE_CETES}\n"
            f"Tasa anual consultada: {tasa:.4f}%\n"
            f"Capital inicial: ${capital:,.2f}\n"
            f"Plazo: {dias} dias\n"
            f"Interes simple estimado: ${interes:,.2f}\n"
            f"Monto total estimado: ${monto_total:,.2f}\n"
        )

        print("\n" + reporte)
        print("Esperando 5 segundos...")
        time.sleep(5)

        enviar_reporte(reporte)

    except ValueError:
        print("Escribe un capital numerico valido.")


while continuar_programa:
    print("\n--- MENU PRINCIPAL ---")
    print("1. Consultar TIIE a 28 dias")
    print("2. Calcular interes simple con CETES a 28 dias")
    print("3. Salir")

    try:
        opcion = int(input("Selecciona una opcion: "))

        if opcion == 1:
            consultar_serie()

        elif opcion == 2:
            calcula_interes_cetes()

        elif opcion == 3:
            print("Saliste del programa. Hasta luego.")
            continuar_programa = False

        else:
            print("Selecciona una opcion entre 1 y 3.")

    except ValueError:
        print("Debes escribir un numero del 1 al 3.")
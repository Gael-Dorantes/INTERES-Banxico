"""
V1
Autor: Jesus Gael Dorantes Quiroz
Fecha: 7 de Octubre del 2026
Solicitud: Consulta Banxico tiempo real serie X y calcular IS.
Datos de entrada: Serie de Banxico, capital y dias.
Datos de salida: Consulta de serie y reporte de interes simple.
"""

import os
import time
import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


series = "SF60648"

TOKEN_BANXICO = os.getenv("BANXICO_TOKEN")
CORREO_ORIGEN = os.getenv("CORREO_ORIGEN")
CORREO_PASSWORD = os.getenv("CORREO_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

continuar_programa = True


def consulta_banxico():
    """
    Consulta la serie seleccionada en Banxico
    y muestra el dato mas reciente.
    """
    if not TOKEN_BANXICO:
        print("Falta configurar BANXICO_TOKEN en el archivo .env")
        return None

    url = (
        "https://www.banxico.org.mx/SieAPIRest/service/v1/"
        f"series/{series}/datos"
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

        print("Codigo de respuesta:", respuesta.status_code)
        respuesta.raise_for_status()

        datos = respuesta.json()["bmx"]["series"][0]["datos"]

        if not datos:
            print("Banxico no devolvio datos.")
            return None

        dato_reciente = datos[-1]

        print("Conexion con Banxico correcta.")
        print("Serie:", series)
        print("Fecha:", dato_reciente["fecha"])
        print("Dato mas reciente:", dato_reciente["dato"])

        return float(dato_reciente["dato"].replace(",", ""))

    except requests.exceptions.RequestException as error:
        print("Error al consultar Banxico:", error)

    except (KeyError, IndexError, ValueError, TypeError) as error:
        print("Error al leer los datos:", error)

    return None


def enviar_reporte(reporte):
    """
    Guarda el reporte en un archivo,
    solicita el correo de destino y envia
    el archivo.
    """
    nombre_archivo = "reporte_interes_simple.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(reporte)

    print("Reporte guardado en:", nombre_archivo)

    if not CORREO_ORIGEN or not CORREO_PASSWORD:
        print("Faltan datos del correo de origen en el archivo .env.")
        print("El reporte se guardo, pero no se envio por correo.")
        return

    correo_destino = input(
        "Introduce el correo al que deseas enviar el reporte: "
    ).strip()

    if not correo_destino:
        print("No introdujiste un correo de destino.")
        print("El reporte se guardo, pero no se envio por correo.")
        return

    mensaje = EmailMessage()
    mensaje["Subject"] = "Reporte de interes simple"
    mensaje["From"] = CORREO_ORIGEN
    mensaje["To"] = correo_destino

    mensaje.set_content(
        "Hola.\n\n"
        "Le envio el reporte de interes simple generado "
        "con los datos consultados de Banxico."
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
        print("Conectando con Gmail")

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

        print("Reporte enviado por correo correctamente.")
        print("Destinatario:", correo_destino)

    except smtplib.SMTPAuthenticationError:
        print("Error de autenticacion.")
        print("Verifica el correo de origen y la contrasena de aplicacion.")

    except (smtplib.SMTPException, OSError) as error:
        print("No se pudo enviar el correo:", error)
        print("El reporte sigue guardado en el archivo de texto.")

    except Exception as error:
        print("Ocurrio un error inesperado:", error)
        print("El reporte sigue guardado en el archivo de texto.")


def calcula_interes_x():
    """
    Consulta la tasa de Banxico, calcula el interes simple,
    genera el reporte y lo envia.
    """
    tasa = consulta_banxico()

    if tasa is None:
        print("No se puede calcular el interes sin una tasa valida.")
        return

    try:
        capital = float(input("Escribe el capital inicial: $"))
        dias = int(input("Escribe el numero de dias (7 a 28): "))

        if capital <= 0:
            print("El capital debe ser mayor que cero.")
            return

        if dias < 7 or dias > 28:
            print("El plazo debe ser de 7 a 28 dias.")
            return

        interes = capital * (tasa / 100) * (dias / 360)
        monto_total = capital + interes

        reporte = (
            "REPORTE DE INTERES SIMPLE\n"
            "-------------------------\n"
            f"Serie de Banxico: {series}\n"
            f"Tasa anual consultada: {tasa:.4f}%\n"
            f"Capital inicial: ${capital:,.2f}\n"
            f"Plazo: {dias} dias\n"
            f"Interes simple: ${interes:,.2f}\n"
            f"Monto total: ${monto_total:,.2f}\n"
        )

        print("\n" + reporte)
        print("Esperando 5 segundos para guardar el reporte...")
        time.sleep(5)

        enviar_reporte(reporte)

    except ValueError:
        print("Escribe cantidades numericas validas.")


while continuar_programa:
    print("\n")
    print("Bienvenido a mi programa de consulta Banxico")
    print("Seleccione una opcion")
    print("1. Consulta Banxico serie X")
    print("2. Calcula interes simple")
    print("3. Salir")

    try:
        Opcion_Menu = int(input("Opcion: "))

        if Opcion_Menu == 1:
            consulta_banxico()

        elif Opcion_Menu == 2:
            calcula_interes_x()

        elif Opcion_Menu == 3:
            print("\nYa saliste del programa, bye <:)")
            continuar_programa = False

        else:
            print("Debes seleccionar una opcion entre 1 y 3.")

    except ValueError:
        print("Solo escribe un numero del 1 al 3.")

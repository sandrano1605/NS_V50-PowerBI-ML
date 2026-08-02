# -*- coding: utf-8 -*-
"""
Helper de conexion SQL para scripts de test NS.

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
Si no estan definidas, usa valores de ejemplo LOCAL (no commiteables).
NUNCA hardcodear credenciales de produccion en el repositorio.
"""
import os
import pyodbc

SERVER = os.environ.get("NS_SQL_SERVER", "128.1.3.21")
DATABASE = os.environ.get("NS_SQL_DB", "DMF_VTA_PRD")
UID = os.environ.get("NS_SQL_UID", "a_moya")
PWD = os.environ.get("NS_SQL_PWD", "")


def conectar(timeout=30):
    """Retorna conexion pyodbc o lanza excepcion."""
    if not PWD:
        raise RuntimeError(
            "Variable NS_SQL_PWD no definida. Ejecuta:\n"
            "  $env:NS_SQL_UID = 'tu_usuario'\n"
            "  $env:NS_SQL_PWD = 'tu_password'"
        )
    cs = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        f"UID={UID};PWD={PWD};Connection Timeout={timeout};"
    )
    return pyodbc.connect(cs)

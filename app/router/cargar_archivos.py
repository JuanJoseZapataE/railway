from fastapi import APIRouter, UploadFile, File, Depends
import pandas as pd
from sqlalchemy.orm import Session
from io import BytesIO
from app.crud.cargar_archivos import insertar_datos_en_bd
from core.database import get_db

router = APIRouter()

@router.post("/upload-excel-estado-normas/")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()

    df = pd.read_excel(
        BytesIO(contents),
        engine="openpyxl",
        skiprows=0,
        usecols=[
            "CODIGO_PROGRAMA",
            "CODIGO_VERSION",
            "FECHA_ELABORACION",
            "ANIO",
            "RED_CONOCIMIENTO",
            "NOMBRE_NCL",
            "CODIGO_NCL",
            "VERSION_NCL",
            "NORMA_CORTE_NOVIEMBRE",
            "VERSION",
            "NORMA_VERSION",
            "MESA_SECTORIAL",
            "TIPO_NORMA",
            "OBSERVACION",
            "FECHA_REVISION",
            "TIPO_COMPETENCIA",
            "VIGENCIA",
            "FECHA_INDICE"
        ],
        dtype=str
    )

    # Renombrar columnas según tu tabla SQL
    df = df.rename(columns={
        "CODIGO_PROGRAMA": "cod_programa",
        "CODIGO_VERSION": "cod_version",
        "FECHA_ELABORACION": "fecha_elaboracion",
        "ANIO": "anio",
        "RED_CONOCIMIENTO": "red_conocimiento",
        "NOMBRE_NCL": "nombre_ncl",
        "CODIGO_NCL": "cod_ncl",
        "VERSION_NCL": "ncl_version",
        "NORMA_CORTE_NOVIEMBRE": "norma_corte_noviembre",
        "VERSION": "verion",
        "NORMA_VERSION": "norma_version",
        "MESA_SECTORIAL": "mesa_sectorial",
        "TIPO_NORMA": "tipo_norma",
        "OBSERVACION": "observacion",
        "FECHA_REVISION": "fecha_revision",
        "TIPO_COMPETENCIA": "tipo_competencia",
        "VIGENCIA": "vigencia",
        "FECHA_INDICE": "fecha_indice",
    })


    print(df.head())  # paréntesis

    # si quieren que funcione en todos los centros de pais 
    # crear codigo para llenar regionales centros y eliminar la siguiente linea.
    df = df[df["cod_centro"] == '9121']

    print(df.head())

    # Eliminar filas con valores faltantes en campos obligatorios
    required_fields = [
        "cod_ficha", "cod_centro", "cod_programa", "la_version", "nombre", 
        "fecha_inicio", "fecha_fin", "etapa", "responsable", "nombre_municipio"
    ]
    df = df.dropna(subset=required_fields)

    # Convertir columnas a tipo numérico
    for col in ["cod_ficha", "cod_programa", "la_version", "cod_centro"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    print(df.head())  # paréntesis
    print(df.dtypes)

    # Convertir fechas
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").dt.date

    # Asegurar columnas no proporcionadas
    df["hora_inicio"] = "00:00:00"
    df["hora_fin"] = "00:00:00"
    df["aula_actual"] = ""

    # Crear DataFrame de programas únicos
    df_programas = df[["cod_programa", "la_version", "nombre"]].drop_duplicates()
    df_programas["horas_lectivas"] = 0
    df_programas["horas_productivas"] = 0

    print(df_programas.head())

    # Eliminar la columna nombre del df.
    df = df.drop('nombre', axis=1)
    print(df.head())

    resultados = insertar_datos_en_bd(db, df_programas, df)
    return resultados

import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.doctoralia.com.mx/tratamientos-servicios/visita-de-primera-vez/ciudad-de-mexico"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

tarjetas = soup.find_all(
    "div",
    class_="result-column"
)

datos = []

for tarjeta in tarjetas:

    nombre_elemento = tarjeta.find(
        "span",
        itemprop="name"
    )

    if not nombre_elemento:
        continue

    nombre = nombre_elemento.get_text(
        " ",
        strip=True
    )

    especialidad_elemento = tarjeta.find(
        "span",
        attrs={"data-test-id": "doctor-specializations"}
    )

    especialidad = (
        especialidad_elemento.get_text(
            " ",
            strip=True
        )
        if especialidad_elemento
        else None
    )

    procedimientos_elemento = tarjeta.find(
        "span",
        class_="hide"
    )

    procedimientos = (
        procedimientos_elemento.get_text(
            " ",
            strip=True
        )
        if procedimientos_elemento
        else None
    )

    if procedimientos:
        procedimientos = procedimientos.strip("() ")

    ubicaciones = tarjeta.find_all(
        "div",
        attrs={
            "data-id": "address-navigation-target"
        }
    )

    for ubicacion in ubicaciones:

        calle_elemento = ubicacion.find(
            "meta",
            itemprop="streetAddress"
        )

        ciudad_elemento = ubicacion.find(
            "meta",
            itemprop="addressLocality"
        )

        calle = (
            calle_elemento.get("content")
            if calle_elemento
            else ""
        )

        ciudad = (
            ciudad_elemento.get("content")
            if ciudad_elemento
            else ""
        )

        ubicacion_texto = ", ".join(
            parte
            for parte in [calle, ciudad]
            if parte
        )

        servicio_elemento = ubicacion.find(
            "p",
            attrs={
                "data-test-id": "available-service"
            }
        )

        servicio = (
            servicio_elemento.get_text(
                " ",
                strip=True
            )
            if servicio_elemento
            else None
        )

        precio_elemento = (
            servicio_elemento.find_next("p")
            if servicio_elemento
            else None
        )

        precio = (
            precio_elemento.get_text(
                " ",
                strip=True
            )
            if precio_elemento
            else None
        )

        datos.append({
            "nombre": nombre,
            "especialidad": especialidad,
            "procedimientos": procedimientos,
            "ubicacion": ubicacion_texto,
            "servicio": servicio,
            "precio": precio
        })

df = pd.DataFrame(datos)

df["precio_original"] = df["precio"]

df["precio_numerico"] = (
    df["precio"]
    .str.replace(",", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)

df["precio_numerico"] = pd.to_numeric(
    df["precio_numerico"],
    errors="coerce"
)

df["tipo_precio"] = "exacto"

df.loc[
    df["precio"].fillna("").str.startswith("desde"),
    "tipo_precio"
] = "desde"

df.loc[
    df["precio"].eq("Precio sin especificar"),
    "tipo_precio"
] = "no especificado"

df_final = df[
    [
        "nombre",
        "especialidad",
        "procedimientos",
        "ubicacion",
        "servicio",
        "precio_original",
        "precio_numerico",
        "tipo_precio"
    ]
]

df_final.to_csv(
    "doctoralia_cdmx.csv",
    index=False,
    encoding="utf-8-sig"
)

print(
    f"Scraping exitoso. "
    f"{len(df_final)} registros encontrados. "
    f"Archivo doctoralia_cdmx.csv creado."
)

"""Funciones de carga, validación y limpieza del dataset.

Dataset utilizado: Breast Cancer Wisconsin Diagnostic, distribuido por
scikit-learn. La variable objetivo se renombra como ``diagnostico``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split


TARGET = "diagnostico"


def cargar_datos(ruta: str | Path) -> pd.DataFrame:
    """Carga un CSV y valida que exista la variable objetivo."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    df = pd.read_csv(ruta)
    if TARGET not in df.columns:
        raise ValueError(f"El dataset debe contener la columna '{TARGET}'.")
    return df


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia duplicados, valores faltantes y tipos no numéricos.

    Estrategia:
    - Elimina filas duplicadas.
    - Convierte predictores a numérico.
    - Imputa valores faltantes con la mediana.
    - Valida que la variable objetivo solo contenga 0 y 1.
    """
    limpio = df.copy().drop_duplicates().reset_index(drop=True)

    predictores = [c for c in limpio.columns if c != TARGET]
    for columna in predictores:
        limpio[columna] = pd.to_numeric(limpio[columna], errors="coerce")
        limpio[columna] = limpio[columna].fillna(limpio[columna].median())

    limpio[TARGET] = pd.to_numeric(limpio[TARGET], errors="raise").astype(int)
    clases = set(limpio[TARGET].unique())
    if not clases.issubset({0, 1}):
        raise ValueError(
            f"La variable objetivo debe ser binaria (0/1). Valores encontrados: {clases}"
        )

    return limpio


def guardar_datos(df: pd.DataFrame, ruta: str | Path) -> None:
    """Guarda el dataframe y crea el directorio de destino si es necesario."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)


def separar_xy(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Separa predictores X y variable objetivo y."""
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    return X, y


def dividir_datos(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.20,
    random_state: int = 42,
):
    """Genera una partición estratificada de entrenamiento y prueba."""
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def preparar_archivo(
    ruta_entrada: str | Path,
    ruta_salida: str | Path,
) -> pd.DataFrame:
    """Ejecuta el flujo completo de carga, limpieza y guardado."""
    df = cargar_datos(ruta_entrada)
    limpio = limpiar_datos(df)
    guardar_datos(limpio, ruta_salida)
    return limpio

"""Entrenamiento, ajuste y registro de modelos de clasificación con MLflow."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from datos_prep import preparar_archivo, separar_xy, dividir_datos


RANDOM_STATE = 42


def construir_modelos(columnas):
    """Define pipelines y espacios de hiperparámetros."""
    preprocesador = ColumnTransformer(
        transformers=[("numericas", StandardScaler(), list(columnas))],
        remainder="drop",
    )

    regresion = Pipeline(
        steps=[
            ("preprocesamiento", preprocesador),
            (
                "modelo",
                LogisticRegression(
                    max_iter=5000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    bosque = Pipeline(
        steps=[
            ("preprocesamiento", preprocesador),
            (
                "modelo",
                RandomForestClassifier(
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                ),
            ),
        ]
    )

    return {
        "regresion_logistica": {
            "pipeline": regresion,
            "param_grid": {
                "modelo__C": [0.1, 1.0],
                "modelo__solver": ["liblinear"],
                "modelo__class_weight": [None, "balanced"],
            },
        },
        "random_forest": {
            "pipeline": bosque,
            "param_grid": {
                "modelo__n_estimators": [20, 50],
                "modelo__max_depth": [None, 10],
                "modelo__min_samples_split": [2, 5],
                "modelo__class_weight": [None, "balanced"],
            },
        },
    }


def calcular_metricas(y_true, y_pred, y_prob):
    """Calcula métricas estandarizadas para clasificación binaria."""
    return {
        "accuracy_test": accuracy_score(y_true, y_pred),
        "precision_test": precision_score(y_true, y_pred, zero_division=0),
        "recall_test": recall_score(y_true, y_pred, zero_division=0),
        "f1_test": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc_test": roc_auc_score(y_true, y_prob),
    }


def guardar_matriz_confusion(modelo, X_test, y_test, destino):
    """Guarda la matriz de confusión como artefacto PNG."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_estimator(
        modelo,
        X_test,
        y_test,
        display_labels=["maligno", "benigno"],
        cmap="Blues",
        ax=ax,
    )
    ax.set_title("Matriz de confusión")
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def entrenar_y_registrar(
    nombre,
    configuracion,
    X_train,
    X_test,
    y_train,
    y_test,
    cv,
    carpeta_resultados,
):
    """Ejecuta GridSearchCV y registra parámetros, métricas y modelo."""
    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }

    busqueda = GridSearchCV(
        estimator=configuracion["pipeline"],
        param_grid=configuracion["param_grid"],
        scoring=scoring,
        refit="f1",
        cv=cv,
        n_jobs=1,
        return_train_score=True,
        verbose=1,
    )

    inicio = time.perf_counter()
    busqueda.fit(X_train, y_train)
    duracion = time.perf_counter() - inicio

    mejor_modelo = busqueda.best_estimator_
    pred = mejor_modelo.predict(X_test)
    prob = mejor_modelo.predict_proba(X_test)[:, 1]
    metricas = calcular_metricas(y_test, pred, prob)
    metricas["tiempo_entrenamiento_seg"] = duracion
    metricas["mejor_f1_cv"] = busqueda.best_score_

    carpeta_modelo = carpeta_resultados / nombre
    carpeta_modelo.mkdir(parents=True, exist_ok=True)

    resultados_cv = pd.DataFrame(busqueda.cv_results_)
    ruta_cv = carpeta_modelo / "resultados_gridsearch.csv"
    resultados_cv.to_csv(ruta_cv, index=False)

    ruta_matriz = carpeta_modelo / "matriz_confusion.png"
    guardar_matriz_confusion(mejor_modelo, X_test, y_test, ruta_matriz)

    ruta_modelo = carpeta_modelo / "modelo.joblib"
    joblib.dump(mejor_modelo, ruta_modelo)

    with mlflow.start_run(run_name=nombre):
        mlflow.set_tags(
            {
                "tipo_problema": "clasificacion_binaria",
                "dataset": "Breast Cancer Wisconsin Diagnostic",
                "algoritmo": nombre,
                "metodo_ajuste": "GridSearchCV",
                "cv": "StratifiedKFold_5",
            }
        )
        mlflow.log_params(busqueda.best_params_)
        mlflow.log_param("criterio_refit", "f1")
        mlflow.log_param("numero_folds", cv.get_n_splits())
        mlflow.log_metrics(metricas)
        mlflow.log_artifact(str(ruta_cv), artifact_path="validacion_cruzada")
        mlflow.log_artifact(str(ruta_matriz), artifact_path="evaluacion")
        mlflow.log_artifact(str(ruta_modelo), artifact_path="modelo_joblib")

        firma = infer_signature(X_train, mejor_modelo.predict(X_train))
        mlflow.sklearn.log_model(
            sk_model=mejor_modelo,
            name="modelo",
            signature=firma,
            input_example=X_train.head(3),
        )

    fila = {
        "modelo": nombre,
        **busqueda.best_params_,
        **metricas,
    }
    return fila


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entrada",
        default="datos/datos_ini/cancer_mama_original.csv",
        help="Ruta del CSV original.",
    )
    parser.add_argument(
        "--limpio",
        default="datos/datos_limp/cancer_mama_limpio.csv",
        help="Ruta del CSV limpio.",
    )
    parser.add_argument(
        "--tracking-uri",
        default="sqlite:///mlflow.db",
        help="URI de MLflow. Ejemplo: sqlite:///mlflow.db",
    )
    parser.add_argument(
        "--experimento",
        default="Actividad5_Clasificacion",
        help="Nombre del experimento en MLflow.",
    )
    args = parser.parse_args()

    raiz = Path(__file__).resolve().parents[1]
    entrada = raiz / args.entrada
    limpio = raiz / args.limpio
    resultados = raiz / "resultados"
    resultados.mkdir(exist_ok=True)

    df = preparar_archivo(entrada, limpio)
    X, y = separar_xy(df)
    X_train, X_test, y_train, y_test = dividir_datos(X, y)

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experimento)

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    resumen = []
    for nombre, configuracion in construir_modelos(X.columns).items():
        fila = entrenar_y_registrar(
            nombre,
            configuracion,
            X_train,
            X_test,
            y_train,
            y_test,
            cv,
            resultados,
        )
        resumen.append(fila)

    resumen_df = pd.DataFrame(resumen).sort_values(
        by="f1_test",
        ascending=False,
    )
    resumen_df.to_csv(resultados / "comparacion_modelos.csv", index=False)

    mejor = resumen_df.iloc[0].to_dict()
    with open(resultados / "mejor_modelo.json", "w", encoding="utf-8") as archivo:
        json.dump(mejor, archivo, indent=2, ensure_ascii=False, default=str)

    print("\nComparación final:")
    print(resumen_df.to_string(index=False))
    print("\nPara abrir MLflow:")
    print("mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000")


if __name__ == "__main__":
    main()

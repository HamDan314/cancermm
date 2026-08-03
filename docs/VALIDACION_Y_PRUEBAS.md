# Documento de validación y pruebas

## Alcance

Validar la carga del modelo, contrato de API, integración frontend-backend y comportamiento ante entradas inválidas.

## Entorno usado

- Python 3.11
- FastAPI
- scikit-learn 1.8.0 (misma versión usada para serializar el modelo)
- Pruebas automatizadas con pytest
- Contenedores Linux basados en imágenes oficiales Python slim y Nginx Alpine

## Casos funcionales

| ID | Caso | Entrada | Resultado esperado |
|---|---|---|---|
| CP-01 | Salud | GET `/health` | HTTP 200 y modelo cargado |
| CP-02 | Predicción válida | 30 números | HTTP 200, clase y probabilidades |
| CP-03 | Información | GET `/model-info` | Variables, versión y métricas |
| CP-04 | Integración web | Formulario → API | Resultado mostrado en pantalla |
| CP-05 | Proxy de integración | GET `/api/health` en puerto 8080 | HTTP 200 reenviado al backend |

## Casos extremos

| ID | Caso | Resultado esperado |
|---|---|---|
| CE-01 | Menos de 30 variables | HTTP 422 |
| CE-02 | Más de 30 variables | HTTP 422 |
| CE-03 | Valores no numéricos | HTTP 422 |
| CE-04 | NaN o infinito | HTTP 422 |
| CE-05 | Modelo ausente | El contenedor no inicia o responde 503 |
| CE-06 | Campo inesperado | HTTP 422 |

## Resultados del modelo

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.9825 |
| Precision | 0.9861 |
| Recall | 0.9861 |
| F1-score | 0.9861 |
| ROC-AUC | 0.9954 |

## Criterios de aceptación

1. Todos los tests automatizados deben aprobar.
2. `/health` debe reportar `model_loaded: true`.
3. Una solicitud correcta debe devolver probabilidades entre 0 y 1.
4. Entradas con cardinalidad incorrecta deben ser rechazadas.
5. El frontend debe consumir el endpoint `/predict`.

## Conclusión

La solución separa presentación, servicio de inferencia y artefacto de ML. La contenerización reduce diferencias entre ambientes y facilita el despliegue en servicios administrados.

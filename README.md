# Actividad 6: despliegue de un modelo con Docker

Aplicación web desplegable basada en un modelo de clasificación del dataset **Breast Cancer Wisconsin Diagnostic** (569 registros, 30 variables numéricas). El backend utiliza FastAPI y un pipeline de scikit-learn; el frontend consume la API mediante HTTP. Ambos componentes se ejecutan como contenedores independientes con Docker Compose.

## Arquitectura

```text
Usuario → Frontend Nginx (puerto 8080, proxy /api) → API FastAPI (puerto 8000) → modelo joblib
```

## Contenido

```text
Actividad6_Despliegue_Docker/
├── backend/
│   ├── app/main.py
│   ├── model/modelo_cancer.joblib
│   ├── model/metadata.json
│   ├── tests/test_api.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── nginx.conf
│   └── Dockerfile
├── docs/
├── docker-compose.yml
└── README.md
```

## Requerimientos

- Git 2.40 o superior.
- Docker Desktop 4.x o Docker Engine 24+.
- Docker Compose v2.
- 2 GB de RAM disponibles.
- Puertos 8000 y 8080 libres.

## Ejecución local con Docker

```bash
git clone https://github.com/USUARIO/Actividad6-Despliegue-Docker.git
cd Actividad6-Despliegue-Docker
docker compose build --no-cache
docker compose up -d
docker compose ps
```

Abrir:

- Frontend: `http://localhost:8080`
- Documentación Swagger: `http://localhost:8000/docs`
- Estado de la API: `http://localhost:8000/health`
- API desde el proxy del frontend: `http://localhost:8080/api/health`

Detener:

```bash
docker compose down
```

## Prueba rápida de la API

```bash
curl -X POST http://localhost:8000/predict   -H "Content-Type: application/json"   -d '{"features": [19.55, 28.77, 133.6, 1207.0, 0.0926, 0.2063, 0.1784, 0.1144, 0.1893, 0.06232, 0.8426, 1.199, 7.158, 106.4, 0.006356, 0.04765, 0.03863, 0.01519, 0.01936, 0.005252, 25.05, 36.27, 178.6, 1926.0, 0.1281, 0.5329, 0.4251, 0.1941, 0.2818, 0.1005] }'
```

## Endpoints

| Método | Endpoint | Función |
|---|---|---|
| GET | `/` | Información básica |
| GET | `/health` | Salud del servicio |
| GET | `/model-info` | Versión, variables y métricas |
| POST | `/predict` | Inferencia con 30 variables |

## Pruebas

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Despliegue

El manual detallado está en `docs/MANUAL_DESPLIEGUE_NUBE.md`. Se documentan alternativas con contenedores administrados y PaaS.

## Evidencias y documentación

- `docs/VALIDACION_Y_PRUEBAS.md`: plan, casos funcionales, casos extremos y criterios de aceptación.
- `docs/RESULTADO_PRUEBAS.txt`: salida reproducible de Pytest.
- `docs/EVIDENCIA_CONTENEDOR.md`: comandos para comprobar imagen, contenedores, endpoints e integración.
- `docs/USO_COPILOT_Y_DOCUMENTACION.md`: uso responsable de asistentes de documentación.
- `.github/workflows/ci.yml`: pruebas y construcción automática de las dos imágenes.

## Métricas del artefacto incluido

- Accuracy: 0.9825
- Precision: 0.9861
- Recall: 0.9861
- F1-score: 0.9861
- ROC-AUC: 0.9954

## Aviso

Proyecto académico. La salida no constituye diagnóstico médico.

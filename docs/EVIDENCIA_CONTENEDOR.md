# Evidencia de construcción, ejecución e integración

Este documento indica cómo producir evidencia comprobable sin depender de capturas preparadas.

## 1. Construcción de imágenes

```bash
docker compose build --no-cache
docker images --filter reference='actividad6*'
```

Resultado esperado: construcción exitosa de las imágenes del backend y frontend.

## 2. Ejecución local

```bash
docker compose up -d
docker compose ps
```

Resultado esperado: `backend` y `frontend` en ejecución; el backend debe aparecer como `healthy`.

## 3. Prueba de endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/model-info
curl http://localhost:8080/api/health
```

El tercer comando demuestra integración a través del proxy del frontend.

## 4. Predicción completa

```bash
curl -X POST http://localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[19.55,28.77,133.6,1207.0,0.0926,0.2063,0.1784,0.1144,0.1893,0.06232,0.8426,1.199,7.158,106.4,0.006356,0.04765,0.03863,0.01519,0.01936,0.005252,25.05,36.27,178.6,1926.0,0.1281,0.5329,0.4251,0.1941,0.2818,0.1005]}'
```

Resultado esperado: HTTP 200 con clase, diagnóstico, probabilidades, latencia y versión del modelo.

## 5. Pruebas automatizadas

```bash
docker compose exec backend pytest -q
```

## 6. Evidencias sugeridas para el reporte

Conservar capturas de `docker compose build`, `docker compose ps`, Swagger (`/docs`), el frontend mostrando una predicción y la salida de Pytest. Las capturas deben obtenerse en el equipo donde se ejecute el proyecto.

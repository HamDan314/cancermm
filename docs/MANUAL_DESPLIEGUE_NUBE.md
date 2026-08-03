# Manual de despliegue en la nube

## 1. Objetivo

Publicar el frontend y el backend como servicios portables, reproducibles y escalables.

## 2. Estrategia recomendada

Se recomienda un servicio de contenedores administrado, por ejemplo Google Cloud Run, Azure Container Apps o AWS App Runner. Esta estrategia evita administrar servidores, permite escalado automático y conserva la misma imagen validada localmente.

## 3. Construcción y publicación de imágenes

```bash
docker build -t hamdan314/cancer-api:1.0.0 ./backend
docker build -t hamdan314/cancer-frontend:1.0.0 ./frontend
docker login
docker push hamdan314/cancer-api:1.0.0
docker push hamdan314/cancer-frontend:1.0.0
```

## 4. Opción A: servicios separados en Cloud Run

```bash
gcloud auth login
gcloud config set project ID_PROYECTO
gcloud run deploy cancer-api   --image docker.io/hamdan314/cancer-api:1.0.0   --platform managed   --region us-central1   --allow-unauthenticated   --port 8000   --memory 1Gi   --cpu 1
```

Registrar la URL pública generada, por ejemplo `https://cancer-api-xxxxx.run.app`.

## 5. Configuración del frontend en servicios separados

Si el frontend y el backend se publican como servicios separados, sustituir temporalmente en `frontend/app.js`:

```javascript
const API_URL = "https://URL_PUBLICA_DEL_BACKEND";
```

Reconstruir, publicar y desplegar:

```bash
docker build -t hamdan314/cancer-frontend:1.0.1 ./frontend
docker push hamdan314/cancer-frontend:1.0.1
gcloud run deploy cancer-frontend   --image docker.io/hamdan314/cancer-frontend:1.0.1   --platform managed   --region us-central1   --allow-unauthenticated   --port 80
```

La configuración incluida está optimizada para Docker Compose: el navegador llama a `/api` y Nginx reenvía la solicitud al servicio `backend`. Esto evita URLs fijas y problemas de CORS. Para una plataforma que permita desplegar el archivo Compose completo, no se modifica el código.

## 6. Alternativa PaaS

Render o Railway pueden desplegar directamente desde GitHub. Para el backend:

- Root directory: `backend`
- Environment: Docker
- Health check: `/health`
- Puerto: variable `PORT`

Para el frontend:

- Root directory: `frontend`
- Environment: Docker
- Puerto interno: `80`

## 7. Seguridad y operación

- Restringir CORS a la URL real del frontend.
- Usar HTTPS administrado por la plataforma.
- Publicar imágenes con etiquetas semánticas, no únicamente `latest`.
- Ejecutar el contenedor con usuario sin privilegios.
- Configurar límites de CPU y memoria.
- Registrar logs y alertas por errores 5xx.
- Incorporar autenticación si se procesan datos reales.
- No almacenar datos clínicos en logs.

## 8. Validación posterior

```bash
curl https://URL_BACKEND/health
curl https://URL_BACKEND/model-info
```

Abrir el frontend y enviar el caso de ejemplo. Confirmar respuesta HTTP 200, diagnóstico, probabilidades, versión del modelo y latencia.

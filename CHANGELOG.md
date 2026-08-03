# Changelog

## 1.1.0 - 2026-08-01

- Se alineó scikit-learn 1.8.0 con la versión usada para serializar el modelo.
- Se integró el frontend y backend mediante proxy Nginx `/api`.
- Se parametrizaron los puertos de Docker Compose mediante `.env`.
- Se ampliaron las pruebas de contrato, probabilidades y campos inesperados.
- Se agregó evidencia reproducible de construcción, ejecución e integración.
- El workflow ahora construye las imágenes de backend y frontend.

## 1.0.0 - 2026-07-12

- Se agregó API FastAPI con endpoints de salud, metadatos y predicción.
- Se incorporó modelo serializado y metadatos versionados.
- Se creó frontend estático conectado al backend.
- Se agregaron Dockerfiles independientes y Docker Compose.
- Se añadieron pruebas funcionales y casos extremos.
- Se documentó despliegue local y en nube.

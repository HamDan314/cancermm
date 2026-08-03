from fastapi.testclient import TestClient
from app.main import app

SAMPLE = [19.55, 28.77, 133.6, 1207.0, 0.0926, 0.2063, 0.1784, 0.1144, 0.1893, 0.06232, 0.8426, 1.199, 7.158, 106.4, 0.006356, 0.04765, 0.03863, 0.01519, 0.01936, 0.005252, 25.05, 36.27, 178.6, 1926.0, 0.1281, 0.5329, 0.4251, 0.1941, 0.2818, 0.1005]

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["model_loaded"] is True

def test_root_and_model_info():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        response = client.get("/model-info")
        assert response.status_code == 200
        assert len(response.json()["feature_names"]) == 30

def test_valid_prediction():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": SAMPLE})
        assert response.status_code == 200
        body = response.json()
        assert body["diagnosis"] in ("maligno", "benigno")
        assert 0 <= body["probability_benign"] <= 1
        assert 0 <= body["probability_malignant"] <= 1
        assert abs(body["probability_benign"] + body["probability_malignant"] - 1) < 1e-5

def test_missing_features():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": [1.0, 2.0]})
        assert response.status_code == 422

def test_non_numeric_value():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": ["x"] * 30})
        assert response.status_code == 422

def test_extra_features():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": SAMPLE + [1.0]})
        assert response.status_code == 422

def test_missing_body_and_unexpected_field():
    with TestClient(app) as client:
        assert client.post("/predict").status_code == 422
        response = client.post("/predict", json={"features": SAMPLE, "patient_name": "dato no permitido"})
        assert response.status_code == 422

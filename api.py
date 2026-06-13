import requests

API_URL = "http://localhost:8000"

def listar_mapa():
    return requests.get(f"{API_URL}/mapa").json()

def listar_focos():
    return requests.get(f"{API_URL}/focos").json()

def dashboard():
    return requests.get(f"{API_URL}/dashboard").json()

def cadastrar(dados):
    return requests.post(
        f"{API_URL}/focos",
        json=dados
    )

def resolver(id):
    return requests.put(
        f"{API_URL}/focos/{id}/resolver"
    )

def excluir(id):
    return requests.delete(
        f"{API_URL}/focos/{id}"
    )
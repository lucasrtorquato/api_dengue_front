import requests

API_URL = "https://api-dengue-z2ly.onrender.com"

def listar_mapa():
    return requests.get(f"{API_URL}/mapa").json()

def listar_focos():
    return requests.get(f"{API_URL}/focos").json()

def dashboard():
    return requests.get(f"{API_URL}/dashboard").json()

def cadastrar(dados):

    response = requests.post(
        f"{API_URL}/focos",
        json=dados
    )

    print(response.status_code)
    print(response.text)

    return response

def resolver(id):
    return requests.put(
        f"{API_URL}/focos/{id}/resolver"
    )

def excluir(id):
    return requests.delete(
        f"{API_URL}/focos/{id}"
    )

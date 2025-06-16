import requests
import re
from bs4 import BeautifulSoup
from settings import BASE_URL, API_KEY
from packaging import version as packaging_version

class WPScanAPI:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY

    def get_wordpress_version(self, version):
        """
        Obtiene los detalles de una versión específica de WordPress desde la API de WPScan.
        """
        url = f"{self.base_url}/wordpresses/{version}"
        headers = {"Authorization": f"Token token={API_KEY}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: No se pudo obtener la versión {version}, {response.text}")
            return None

    def get_plugin(self, plugin_slug):
        """
        Obtiene los detalles de un plugin específicow desde la API de WPScan.
        """
        url = f"{self.base_url}/plugins/{plugin_slug}"
        headers = {"Authorization": f"Token token={API_KEY}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: No se pudo obtener el plugin {plugin_slug}")
            return None
class WordpressAPI:
    def __init__(self):
        self.base_url = "https://api.wordpress.org/plugins/info/1.2/"
        self.per_page = 250  # Máximo permitido

    def get_all_plugins(self):
        page = 1
        all_plugins = []
        # Lista de campos que se desean obtener:
        campos = [
            "slug", "version", "author", "author_profile",
            "requires", "tested", "requires_php", "rating", "ratings",
            "num_ratings", "support_threads", "support_threads_resolved",
            "active_installs", "downloaded", "last_updated", "added",
            "homepage", "short_description", "description", "download_link",
            "tags", "donate_link", "icons"
        ]
        
        while True:
            print(f"Obteniendo plugins de la página {page}...")
            # Parámetros básicos de la consulta
            params = {
                "action": "query_plugins",
                "request[page]": page,
                "request[per_page]": self.per_page,
            }
            # Agregar cada campo a la solicitud
            for campo in campos:
                params[f"request[fields][{campo}]"] = True

            response = requests.get(self.base_url, params=params)
            if response.status_code != 200:
                print(f"Error en la petición: {response.status_code}")
                break

            data = response.json()
            if "plugins" not in data or not data["plugins"]:
                print("No hay más plugins disponibles.")
                break

            all_plugins.extend(data["plugins"])
            page += 1
        return all_plugins
    def get_all_versions(self):
        """
        Scrapea la página oficial de WordPress con el archivo histórico de versiones
        y devuelve una lista completa filtrada con versiones solo del tipo n.n.n.
        """
        url = "https://wordpress.org/download/releases/"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error {response.status_code}: No se pudo obtener las versiones.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        versions_set = set()

        sections = soup.select("div.wp-block-wporg-release-tables__section")

        for section in sections:
            rows = section.select("table tbody tr")
            for row in rows:
                version_cell = row.find("th", class_="wp-block-wporg-release-tables__cell-version")
                if version_cell:
                    version_text = version_cell.get_text(strip=True)
                    if version_text:
                        versions_set.add(version_text)

        pattern = re.compile(r"^\d+\.\d+\.\d+$")
        filtered_versions = [v for v in versions_set if pattern.match(v)]

        try:
            filtered_versions.sort(key=packaging_version.parse, reverse=True)
        except ImportError:
            filtered_versions.sort(reverse=True)

        print(f"Se han obtenido {len(filtered_versions)} versiones filtradas (n.n.n).")
        return filtered_versions
    
    

wpscan = WPScanAPI()
wordpress = WordpressAPI()

if __name__ == "__main__":
    wordpress = WordpressAPI()
    versions = wordpress.get_all_versions()
    lista = []
    for v in versions:
        lista.append(v)
    print(lista)

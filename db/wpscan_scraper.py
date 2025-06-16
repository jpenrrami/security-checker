import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_slugs():
    """
    Para cada filtro (0-9, a, b, …, z), se carga la primera página para extraer el
    número total de páginas (filter_max) a partir de la paginación. Luego se recorre de la
    página 1 hasta filter_max, extrayendo en cada una el texto del enlace (columna “slug”)
    de cada fila de la tabla de vulnerabilidades.
    
    Devuelve una lista con todos los slugs extraídos.
    """
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    all_slugs = []
    base_url = "https://wpscan.com/plugins"
    filters = [None] + list("abcdefghijklmnopqrstuvwxyz")

    for f in filters:
        filtro = f if f is not None else "0-9"
        print("\nProcesando filtro:", filtro)
        if f is None:
            url_first = f"{base_url}?page=1&get"
        else:
            url_first = f"{base_url}?get={f}"
        print("Abriendo URL:", url_first)
        driver.get(url_first)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.vulnerabilities__table--body"))
            )
        except Exception:
            print("No se pudo cargar el contenido en:", url_first)
            continue
        pagination_links = driver.find_elements(By.CSS_SELECTOR, "ul.vulnerabilities__pagination li a")
        page_numbers = []
        for link in pagination_links:
            txt = link.text.strip()
            if txt.isdigit():
                page_numbers.append(int(txt))
        if page_numbers:
            filter_max = max(page_numbers)
        else:
            filter_max = 1 
        print("Filtro:", filtro, "tiene máximo de páginas:", filter_max)
        for page in range(1, filter_max + 1):
            if page == 1:
                if f is None:
                    url = f"{base_url}?page=1&get"
                else:
                    url = f"{base_url}?get={f}"
            else:
                if f is None:
                    url = f"{base_url}?page={page}&get"
                else:
                    url = f"{base_url}?page={page}&get={f}"
            print("Abriendo URL:", url)
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.vulnerabilities__table--body"))
                )
            except Exception:
                print("No se pudo cargar el contenido en:", url)
                break

            rows = driver.find_elements(By.CSS_SELECTOR, "div.vulnerabilities__table--row")
            if not rows:
                print("No se encontraron filas en:", url)
                break
            for row in rows:
                try:
                    slug_elem = row.find_element(By.CSS_SELECTOR, "div.vulnerabilities__table--slug a")
                    slug = slug_elem.text.strip()
                    if slug:
                        all_slugs.append(slug)
                except Exception as e:
                    print("Error extrayendo slug:", e)
                    continue
            time.sleep(1)
    driver.quit()
    return all_slugs

if __name__ == "__main__":
    print(list(set(extract_slugs())))

def extract_plugins():
    return list(set(extract_slugs()))

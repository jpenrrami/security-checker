from wpscan_scraper import extract_slugs
from wpscan_api import wordpress

def test_scraper_output(scraper_func, scraper_name):
    print(f"Probando scraper: {scraper_name} ...")
    result = scraper_func()
    if isinstance(result, list) and len(result) > 0:
        print(f"[OK] {scraper_name} devuelve una lista con {len(result)} elementos.")
    else:
        print(f"[ERROR] {scraper_name} no devuelve una lista válida o está vacía.")

if __name__ == "__main__":
    test_scraper_output(extract_slugs, "wpscan_scraper.extract_slugs")
    test_scraper_output(wordpress.get_all_versions(), "wpscan_api.get_all_versions")
    test_scraper_output(wordpress.get_all_plugins(), "wpscan_api.get_all_plugins")

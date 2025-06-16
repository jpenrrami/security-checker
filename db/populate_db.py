from database import neo4j_conn
from wpscan_api import wpscan, wordpress
from wpscan_scraper import extract_plugins
import random

def insert_wordpress_version(version, release_date, changelog_url, status):

    query = """
    MERGE (wp:WordPressVersion {version: $version})
    SET wp.release_date = $release_date,
        wp.changelog_url = $changelog_url,
        wp.status = $status
    """
    neo4j_conn.query(query, {
        "version": version,
        "release_date": release_date,
        "changelog_url": changelog_url,
        "status": status
    })

def insert_plugin(slug, name, version, author, last_updated_wp, rating, num_ratings, downloaded, active_installs, homepage, short_description, latest_version_wpscan=None, last_updated_wpscan=None, popular_wpscan=None):
 
    query = """
    MERGE (p:Plugin {slug: $slug})
    SET p.name = COALESCE($name, p.name),
        p.version = COALESCE($version, p.version),
        p.author = COALESCE($author, p.author),
        p.last_updated_wp = COALESCE($last_updated_wp, p.last_updated_wp),
        p.rating = COALESCE($rating, p.rating),
        p.num_ratings = COALESCE($num_ratings, p.num_ratings),
        p.downloaded = COALESCE($downloaded, p.downloaded),
        p.active_installs = COALESCE($active_installs, p.active_installs),
        p.homepage = COALESCE($homepage, p.homepage),
        p.short_description = COALESCE($short_description, p.short_description),
        p.latest_version_wpscan = COALESCE($latest_version_wpscan, p.latest_version_wpscan),
        p.last_updated_wpscan = COALESCE($last_updated_wpscan, p.last_updated_wpscan),
        p.popular_wpscan = COALESCE($popular_wpscan, p.popular_wpscan)
    """
    
    params = {
        "slug": slug,
        "name": name,
        "version": version,
        "author": author,
        "last_updated_wp": last_updated_wp,
        "rating": rating,
        "num_ratings": num_ratings,
        "downloaded": downloaded,
        "active_installs": active_installs,
        "homepage": homepage,
        "short_description": short_description,
        "latest_version_wpscan": latest_version_wpscan,
        "last_updated_wpscan": last_updated_wpscan,
        "popular_wpscan": popular_wpscan
    }

    neo4j_conn.query(query, params)

def insert_plugin_relationships(plugin_slug, vulnerabilities):
    """
    Crea la relación :HAS_VULNERABILITY entre el nodo Plugin identificado por 'plugin_slug'
    y cada vulnerabilidad de la lista 'vulnerabilities'.
    """
    for v in vulnerabilities:
        query = """
        MATCH (p:Plugin {slug: $plugin_slug}), (v:Vulnerability {id: $v_id})
        MERGE (p)-[:HAS_VULNERABILITY]->(v)
        """
        neo4j_conn.query(query, {"plugin_slug": plugin_slug, "v_id": v["id"]})


def version_to_int(version):
    """
    Convierte una cadena de versión en un entero usando la fórmula:
      entero = major * 10000 + minor * 100 + patch.
    Si algún componente no es numérico (por ejemplo, 'x'), se toma como 0.
    Se asegura además de tener tres componentes, completando con "0" si es necesario.
    """
    parts = version.split('.')
    # Aseguramos que haya 3 partes (completamos con "0" si falta)
    while len(parts) < 3:
        parts.append("0")
    
    def safe_int(x):
        try:
            return int(x)
        except ValueError:
            return 0

    major = safe_int(parts[0])
    minor = safe_int(parts[1])
    patch = safe_int(parts[2])
    return major * 10000 + minor * 100 + patch

def extraer_rango_compatibilidad(plugin):
    """
    A partir de los atributos 'requires' y 'tested' del plugin,
    devuelve una tupla (requires_full, tested_full) en formato x.y.z, completando a tres dígitos.
    
    La lógica es la siguiente:
      - Si existe 'requires' pero no 'tested': se devuelve (requires_completo, None)
      - Si existe 'tested' pero no 'requires': se devuelve ("0.0.0", tested_completo)
      - Si no existe ninguno: se devuelve (None, None)
    """
    requires = plugin.get("requires")
    tested = plugin.get("tested")
    
    # Normalizar requires:
    if requires and requires.strip():
        requires = requires.strip()
        if requires.count('.') == 1:
            requires_full = requires + ".0"
        else:
            requires_full = requires
    else:
        requires_full = None
    
    # Normalizar tested:
    if tested and tested.strip():
        tested = tested.strip()
        if tested.count('.') == 1:
            tested_full = tested + ".0"
        else:
            tested_full = tested
    else:
        tested_full = None
    
    return requires_full, tested_full

def fetch_all_plugins():
    plugins = wordpress.get_all_plugins()
    
    for plugin in plugins:
        slug = plugin.get("slug")
        requires_full, tested_full = extraer_rango_compatibilidad(plugin)
        
        # Determinar el rango de compatibilidad según la lógica definida:
        if requires_full is None and tested_full is None:
            # Sin información, se asume que es compatible con todas las versiones
            lower_int = 0
            upper_int = 999999
        elif requires_full and tested_full:
            lower_int = version_to_int(requires_full)
            upper_int = version_to_int(tested_full)
        elif requires_full and not tested_full:
            lower_int = version_to_int(requires_full)
            upper_int = 999999  # Compatible desde 'requires' en adelante
        elif not requires_full and tested_full:
            lower_int = 0  # Asumimos compatibilidad desde "0.0.0"
            upper_int = version_to_int(tested_full)
        else:
            lower_int = 0
            upper_int = 999999
        
        update_query = """
            MATCH (p:Plugin {slug: $slug})
            MATCH (wp:WordPressVersion)
            WITH p, wp, 
              (toInteger(split(wp.version, '.')[0]) * 10000 +
               toInteger(split(wp.version, '.')[1]) * 100 +
               toInteger(split(wp.version, '.')[2])) AS wp_int
            WHERE wp_int >= $lower_int AND wp_int <= $upper_int
            MERGE (p)-[r:IS_COMPATIBLE]->(wp)
            SET r.compatible = true
        """
        neo4j_conn.query(update_query, {
            "slug": slug,
            "lower_int": lower_int,
            "upper_int": upper_int
        })

def insert_vulnerability(v):
 
    query = """
    MERGE (v:Vulnerability {id: $id})
    SET v.title = $title
    """

    # Diccionario de parámetros con valores predeterminados para evitar errores
    params = {
        "id": v.get("id", "unknown"),  # Si no tiene ID, se asigna "unknown"
        "title": v.get("title", "No title available"),  # Si no tiene título, se asigna un mensaje
        "created_at": v.get("created_at"),
        "updated_at": v.get("updated_at"),
        "published_date": v.get("published_date"),
        "description": v.get("description"),
        "vuln_type": v.get("vuln_type"),
        "url": v.get("references", {}).get("url"),
        "cve": v.get("references", {}).get("cve"),
        "score": v.get("cvss", {}).get("score") if v.get("cvss") else None,
        "vector": v.get("cvss", {}).get("vector") if v.get("cvss") else None,
        "severity": v.get("cvss", {}).get("severity") if v.get("cvss") else None,
        "verified": v.get("verified"),
        "fixed_in": v.get("fixed_in"),
        "introduced_in": v.get("introduced_in"),
        "closed_reason": v.get("closed", {}).get("closed_reason"),
    }

    # Filtrar los valores None para evitar que Neo4j inserte valores vacíos
    params = {key: value for key, value in params.items() if value is not None}

    # Agregar dinámicamente los campos SET a la consulta si existen valores
    if params:
        query += "\nSET " + ",\n    ".join([f"v.{key} = ${key}" for key in params.keys() if key not in ["id", "title"]])

    neo4j_conn.query(query, params)

def insert_relationships(version, vulnerabilities):

    for v in vulnerabilities:
        query = """
        MATCH (wp:WordPressVersion {version: $version}), (v:Vulnerability {id: $v_id})
        MERGE (wp)-[:HAS_VULNERABILITY]->(v)
        """
        neo4j_conn.query(query, {
            "version": version,
            "v_id": v["id"]
        })

def populate_wordpress(version):
    data = wpscan.get_wordpress_version(version)
    if data:
        for v, details in data.items():
            insert_wordpress_version(v, details["release_date"], details["changelog_url"], details["status"])
            if "vulnerabilities" in details:
                for vulnerability in details["vulnerabilities"]:
                    insert_vulnerability(vulnerability)
                insert_relationships(v, details["vulnerabilities"])
        print(f"La versión {version} se ha insertado correctamente en la base de datos.")
    else:
        print(f"Error 404: No se pudo obtener la versión {version}, {data}")



def populate_plugin(plugin_slug):
    data = wpscan.get_plugin(plugin_slug)

    if not data or plugin_slug not in data:
        print(f"El plugin '{plugin_slug}' no se encuentra en la API de WPScan.")
        return

    details = data[plugin_slug]

    # Inserta (o actualiza) el nodo del plugin
    insert_plugin(
        slug=plugin_slug,
        name=None,
        version=None,
        author=None,
        last_updated_wp=None,
        rating=None,
        num_ratings=None,
        downloaded=None,
        active_installs=None,
        homepage=None,
        short_description=None,
        latest_version_wpscan=details.get("latest_version"),
        last_updated_wpscan=details.get("last_updated"),
        popular_wpscan=details.get("popular")
    )

    # Para cada vulnerabilidad:
    if "vulnerabilities" in details:
        for vulnerability in details["vulnerabilities"]:
            insert_vulnerability(vulnerability)
        # Crear la relación entre el plugin y cada vulnerabilidad
        insert_plugin_relationships(plugin_slug, details["vulnerabilities"])

    print(f"El plugin '{plugin_slug}' ha sido añadido a la base de datos con sus respectivas vulnerabilidades.")


def check_versions(version_list):
    """
    Para cada versión en version_list, comprueba si está en Neo4j.
    Si no está, llama a populate_wordpress para insertarla.
    """
    versions = wp_versions[:]
    random.shuffle(versions)

    for version in versions:
        query_check = """
        MATCH (wp:WordPressVersion {version: $version})
        RETURN wp LIMIT 1
        """
        result = neo4j_conn.fetch_query(query_check, {"version": version})

        if not result:
            print(f"La versión {version} no está en la base de datos. Insertando...")
            populate_wordpress(version)
        else:
            print(f"La versión {version} ya está en la base de datos. No se hace nada.")

def check_plugins(plugins_list):
    newP = 0
    oldP = 0

    plugins_random = plugins_list[:]  
    random.shuffle(plugins_random)    

    for plugin_slug in plugins_random:
        query_check = """
        MATCH (p:Plugin {slug: $slug})
        RETURN p LIMIT 1
        """
        result = neo4j_conn.fetch_query(query_check, {"slug": plugin_slug})
        
        if not result:
            print(f"El plugin '{plugin_slug}' no está en la base de datos. Se añadirá...")
            populate_plugin(plugin_slug)
            newP +=1
        else:
            print(f"El plugin '{plugin_slug}' ya está en la base de datos. Se omite.")
            oldP += 1

    print(f"Se han añadido {newP} plugins y se han descartado porque ya estaban {oldP}")

if __name__ == "__main__":
    wp_versions = wordpress.get_all_versions()
    plugins = extract_plugins()
    check_plugins(plugins)
    check_versions(wp_versions)
    fetch_all_plugins()
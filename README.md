# Security Checker for WordPress

Este proyecto tiene como objetivo desarrollar una herramienta para la detección y gestión de vulnerabilidades en plugins de WordPress, con un enfoque particular en los plugins de terceros. La herramienta se integra con WPScan para identificar vulnerabilidades y utiliza Neo4j como base de datos gráfica para almacenar y gestionar la información sobre los plugins, sus versiones y las vulnerabilidades asociadas.

## Descripción

El Security Checker permite a los administradores de sitios web en WordPress detectar vulnerabilidades en sus plugins instalados. La herramienta se conecta a la API de WPScan para obtener datos sobre vulnerabilidades conocidas y utiliza Neo4j para almacenar y visualizar las relaciones entre plugins, versiones y vulnerabilidades.

### Componentes principales:
- **Scrapers**: Recopilan información sobre vulnerabilidades desde la API de WPScan y la API de WordPress.
- **Neo4j**: Base de datos gráfica para almacenar las relaciones entre plugins, versiones y vulnerabilidades.
- **Plugin de WordPress**: Interfaz para que los administradores de WordPress puedan gestionar las vulnerabilidades de forma sencilla.

## Instalación

### Requisitos
- PHP 7.4 o superior
- WordPress 4.9 o superior
- Neo4j (para la base de datos gráfica)
- Python 3.x
- WPScan API

### Pasos para la instalación
1. Clona el repositorio:
    ```bash
    git clone https://github.com/jpenrrami/security-checker.git
    ```

2. Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```

3. Configura Neo4j y conéctalo a tu proyecto editanto el archivo `settings.py`.

4. Configura las credenciales de WordPress API en el archivo `Neo4jConnector.php`.

5. Activa el plugin en tu instalación de WordPress.

## Uso

Una vez instalado, el plugin aparecerá en el panel de administración de WordPress, donde podrás ver la lista de plugins instalados, las vulnerabilidades asociadas, y los detalles de cada vulnerabilidad.

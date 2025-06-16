from neo4j import GraphDatabase
from settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jConnection:

    def __init__(self):
        self._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            return session.run(query, parameters)
    
    def fetch_query(self, query, parameters=None):
        """
        Ejecuta una consulta y devuelve los resultados como una lista de diccionarios,
        asegurando que los resultados no estén consumidos.
        """
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

neo4j_conn = Neo4jConnection()
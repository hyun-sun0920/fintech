import pymysql
from neo4j import GraphDatabase, basic_auth
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re

# --- Configuration ---
MAX_WORKERS = 5
BATCH_SIZE = 10000
DB_NAME = 'test02'

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "dev",
    "password": "pwd",
    "database": "orders",
}

NEO4J_CONFIG = {
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": "gustjs21@",
    "database": 'test02',
}

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler('migration.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# --- Helper Functions ---
def clean_property_name(name):
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if not cleaned_name:
        return "prop" + name
    if not re.match(r'^[a-zA-Z]', cleaned_name[0]):
        cleaned_name = '_' + cleaned_name
    return cleaned_name

def clear_neo4j_database(driver):
    with driver.session(database=NEO4J_CONFIG["database"]) as session:
        session.run("MATCH (n) DETACH DELETE n")
        logger.info("Cleared Neo4j database.")

def create_constraints(driver, mysql_conn):
    cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SHOW TABLES")
    tables = [list(row.values())[0] for row in cursor]
    for table in tables:
        cursor.execute(f"SHOW KEYS FROM `{table}` WHERE Key_name = 'PRIMARY'")
        pk_info = cursor.fetchone()
        if pk_info:
            pk_column = clean_property_name(pk_info['Column_name'])
            try:
                with driver.session(database=NEO4J_CONFIG["database"]) as session:
                    session.run(f"CREATE CONSTRAINT IF NOT EXISTS ON (n:{table.capitalize()}) ASSERT n.{pk_column} IS UNIQUE")
                    logger.info(f"Created constraint on {table.capitalize()}({pk_column})")
            except Exception as e:
                logger.warning(f"Constraint creation failed on {table}.{pk_column}: {e}")

def migrate_nodes_batched(mysql_conn, driver, table_name, node_label, primary_key='id'):
    offset = 0
    cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
    futures = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            cursor.execute(f"SELECT * FROM {table_name} WHERE deletedAt IS NULL LIMIT {BATCH_SIZE} OFFSET {offset}")
            rows = cursor.fetchall()
            if not rows:
                break

            cleaned_rows = []
            for row in rows:
                cleaned = {clean_property_name(k): json.dumps(v, default=str) if isinstance(v, (dict, list)) else v for k, v in row.items()}
                cleaned_rows.append(cleaned)

            futures.append(executor.submit(create_nodes_batch, driver, node_label, cleaned_rows, primary_key))
            offset += BATCH_SIZE

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                logger.error(f"Node creation error: {exc}")

def create_nodes_batch(driver, label, records, primary_key):
    logger.info(f"Creating {len(records)} nodes for {label}")
    with driver.session(database=NEO4J_CONFIG["database"]) as session:
        cypher = (
            f"UNWIND $rows AS row\n"
            f"CREATE (n:{label})\n"
            f"SET n = row, n.{primary_key} = row.{primary_key}"
        )
        session.run(cypher, rows=records)

def migrate_relationship(mysql_conn, driver, from_table, from_label, from_key, to_label, to_key, relationship_type):
    cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
    offset = 0

    with driver.session(database=NEO4J_CONFIG["database"]) as session:
        while True:
            cursor.execute(f"SELECT {from_key}, {to_key} FROM {from_table} WHERE {from_key} IS NOT NULL AND {to_key} IS NOT NULL LIMIT {BATCH_SIZE} OFFSET {offset}")
            rows = cursor.fetchall()
            if not rows:
                break

            query = f"""
            UNWIND $batch AS rel
            MATCH (a:{from_label} {{{from_key}: rel.{from_key}}})
            MATCH (b:{to_label} {{{to_key}: rel.{to_key}}})
            MERGE (a)-[:{relationship_type}]->(b)
            """
            session.run(query, batch=rows)
            offset += BATCH_SIZE

def main():
    logger.info("🔥 진입")
    mysql_conn = None
    neo4j_driver = None
    try:
        logger.info("Connecting to MySQL...")
        mysql_conn = pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)

        logger.info("Connecting to Neo4j...")
        neo4j_driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"], auth=basic_auth(NEO4J_CONFIG["username"], NEO4J_CONFIG["password"])
        )
        neo4j_driver.verify_connectivity()

        clear_neo4j_database(neo4j_driver)
        create_constraints(neo4j_driver, mysql_conn)

        table_mapping = {
            "stores": "Store",
            "customers": "Customer",
            "orders": "Order",
            "order_items": "OrderItem",
            "menus": "Menu",
            "categories": "Category",
            "payments": "Payment",
            "store_tables": "StoreTable",
            "coupons": "Coupon"
        }

        for table, label in table_mapping.items():
            migrate_nodes_batched(mysql_conn, neo4j_driver, table, label)

        migrate_relationship(mysql_conn, neo4j_driver, "orders", "Customer", "customerId", "Order", "id", "PLACED")
        migrate_relationship(mysql_conn, neo4j_driver, "orders", "Order", "id", "Store", "storeId", "PLACED_AT")
        migrate_relationship(mysql_conn, neo4j_driver, "orders", "Order", "id", "StoreTable", "storeTableId", "AT_TABLE")
        migrate_relationship(mysql_conn, neo4j_driver, "orders", "Order", "id", "Payment", "paymentId", "HAS_PAYMENT")
        migrate_relationship(mysql_conn, neo4j_driver, "order_items", "Order", "orderId", "OrderItem", "id", "CONTAINS")
        migrate_relationship(mysql_conn, neo4j_driver, "order_items", "OrderItem", "menuId", "Menu", "id", "IS_MENU")
        migrate_relationship(mysql_conn, neo4j_driver, "menus", "Menu", "categoryId", "Category", "id", "IN_CATEGORY")
        migrate_relationship(mysql_conn, neo4j_driver, "categories", "Category", "storeId", "Store", "id", "BELONGS_TO")

        logger.info("Migration completed.")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if mysql_conn:
            mysql_conn.close()
        if neo4j_driver:
            neo4j_driver.close()

if __name__ == "__main__":
    main()

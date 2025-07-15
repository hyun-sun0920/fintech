import mysql.connector
import pymysql
from pymysql.cursors import DictCursor
from neo4j import GraphDatabase
import json
from decimal import Decimal
from datetime import datetime
import concurrent.futures
import logging
import sys

# --- DRIVER CONFIGURATION ---
mysql.connector.connect = pymysql.connect

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.FileHandler("migration_final.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- DATABASE & MIGRATION CONFIGURATION ---
MYSQL_CONFIG = {
    'user': 'dev',
    'password': 'pwd',  # Your actual password for the 'localhost' user
    'host': '127.0.0.1',
    'database': 'orders',
    'port': 3306
}

NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'gustjs21@'
}

# --- TUNING PARAMETERS ---
MAX_WORKERS = 5
BATCH_SIZE = 10000
DB_NAME = 'sicpama'


class MySqlToNeo4jMigrator:
    # --- All methods are the same except for run_migration() at the end ---
    def __init__(self, mysql_config, neo4j_config):
        logging.info("Initializing migrator...")
        self.mysql_config = mysql_config
        self.neo4j_driver = GraphDatabase.driver(neo4j_config['uri'],
                                                 auth=(neo4j_config['user'], neo4j_config['password']))
        logging.info("Neo4j Driver established.")

    def close(self):
        logging.info("Closing Neo4j driver.")
        self.neo4j_driver.close()

    def _clean_properties(self, properties):
        cleaned = {}
        for key, value in properties.items():
            if isinstance(value, datetime):
                cleaned[key] = value.isoformat()
            elif isinstance(value, Decimal):
                cleaned[key] = float(value)
            elif isinstance(value, bytes):
                cleaned[key] = value.decode('utf-8', 'ignore')
            elif isinstance(value, dict) or isinstance(value, list):
                cleaned[key] = json.dumps(value)
            elif value is not None:
                cleaned[key] = value
        return cleaned

    def clear_neo4j_database(self):
        logging.warning(f"Clearing all data from the '{DB_NAME}' Neo4j database...")
        with self.neo4j_driver.session(database=DB_NAME) as session:
            session.run("MATCH (n) DETACH DELETE n")
        logging.info(f"Neo4j '{DB_NAME}' database cleared.")

    def create_constraints(self):
        logging.info(f"Creating uniqueness constraints in '{DB_NAME}' database...")
        with self.neo4j_driver.session(database=DB_NAME) as session:
            constraints = [
                ("Category", "id"), ("Country", "id"), ("Coupon", "id"),
                ("CouponUsage", "id"), ("Customer", "id"), ("FoodCourt", "id"),
                ("GroupedText", "id"), ("InventoryItem", "id"),
                ("InventoryTransaction", "id"), ("Locale", "code"),
                ("MenuOptionChoice", "id"), ("MenuOption", "id"), ("Menu", "id"),
                ("OrderItem", "id"), ("Order", "id"),
                ("PaymentOptionEnum", "paymentOptionEnum"), ("Payment", "id"),
                ("Refund", "id"), ("RefundItem", "id"), ("StoreAttribute", "id"),
                ("MetaAdvertInsight", "id"), ("MetaAdvert", "id"),
                ("StoreTable", "id"), ("Store", "id"), ("TranslatedText", "id"),
                ("MenuOptionChoiceToMenuOption", "id"),
                ("MenuOptionToMenu", "id"),
                ("MenuToInventoryItem", "id")
            ]
            for label, key in constraints:
                query = f"CREATE CONSTRAINT {label}_{key}_unique IF NOT EXISTS FOR (n:{label}) REQUIRE n.{key} IS UNIQUE"
                session.run(query)
        logging.info("All constraints created successfully.")

    def migrate_nodes_batched(self, table_name, node_label, primary_key='id'):
        conn = mysql.connector.connect(**self.mysql_config)
        cursor = conn.cursor(DictCursor)
        offset = 0
        total_migrated = 0
        logging.info(f"Starting migration for table '{table_name}'...")

        query = f"SELECT * FROM `{table_name}`"
        try:
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE 'deletedAt'")
            if cursor.fetchone():
                query += " WHERE deletedAt IS NULL"
        except Exception:
            pass

        query_base = query

        while True:
            paginated_query = query_base + f" LIMIT {BATCH_SIZE} OFFSET {offset}"
            cursor.execute(paginated_query)
            rows = cursor.fetchall()
            if not rows:
                break

            cleaned_rows = [self._clean_properties(row) for row in rows]
            cypher_query = f"""
            UNWIND $rows AS row
            CREATE (n:{node_label})
            SET n = row
            """
            with self.neo4j_driver.session(database=DB_NAME) as session:
                session.run(cypher_query, rows=cleaned_rows)

            total_migrated += len(rows)
            logging.debug(f"Migrated batch of {len(rows)} nodes for ':{node_label}'. Total: {total_migrated}")
            offset += BATCH_SIZE

        logging.info(f"Finished migration for '{table_name}'. Migrated a total of {total_migrated} nodes.")
        cursor.close()
        conn.close()
        return f"Completed {table_name}"

    def establish_relationship_native(self, relationship_name, apoc_query):
        logging.info(f"Starting native relationship build for ':{relationship_name}' using APOC...")
        try:
            with self.neo4j_driver.session(database=DB_NAME) as session:
                result = session.execute_write(lambda tx: tx.run(apoc_query).data())
                logging.info(f"APOC job for ':{relationship_name}' completed. Details: {result}")
        except Exception:
            logging.exception(
                f"An error occurred during the APOC build for ':{relationship_name}'. Make sure the APOC plugin is installed.")

    # <--- THE ONLY METHOD WITH CHANGES --->
    def run_migration(self):
        """Executes the full migration process using a thread pool."""
        self.clear_neo4j_database()
        self.create_constraints()

        node_tasks = [
            ('stores', 'Store'), ('customers', 'Customer'), ('orders', 'Order'),
            ('order_items', 'OrderItem'), ('payments', 'Payment'), ('refunds', 'Refund'),
            ('refund_items', 'RefundItem'), ('categories', 'Category'), ('menus', 'Menu'),
            ('menu_options', 'MenuOption'), ('menu_option_choices', 'MenuOptionChoice'),
            ('coupons', 'Coupon'), ('coupon_usages', 'CouponUsage'),
            ('store_tables', 'StoreTable'), ('store_attributes', 'StoreAttribute'),
            ('food_courts', 'FoodCourt'), ('inventory_items', 'InventoryItem'),
            ('inventory_transactions', 'InventoryTransaction'), ('countries', 'Country'),
            ('locales', 'Locale', 'code'), ('grouped_texts', 'GroupedText'),
            ('translated_texts', 'TranslatedText'), ('payment_option_enums', 'PaymentOptionEnum', 'paymentOptionEnum'),
            ('store_meta_adverts', 'MetaAdvert'), ('store_meta_advert_insights', 'MetaAdvertInsight'),
            ('menu_option_to_menus', 'MenuOptionToMenu'),
            ('menu_option_choice_to_menu_options', 'MenuOptionChoiceToMenuOption'),
            ('menu_to_inventory_items', 'MenuToInventoryItem'),
        ]

        logging.info("--- Starting Node Migration in Parallel ---")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_task = {executor.submit(self.migrate_nodes_batched, *task): task[0] for task in node_tasks}
            for future in concurrent.futures.as_completed(future_to_task):
                table = future_to_task[future]
                try:
                    result = future.result()
                    logging.info(f"SUCCESS: {result}")
                except Exception:
                    logging.exception(f"ERROR: Migration for table '{table}' generated an exception.")

        logging.info("--- All Node Migrations Complete. Starting NATIVE Relationship Migration ---")

        # NOTE: All the first queries now end with a RETURN clause to fix the syntax error.
        relationship_queries = {
            "ORDER_PLACED_BY_CUSTOMER": "CALL apoc.periodic.iterate('MATCH (n:Order) WHERE n.customerId IS NOT NULL RETURN n', 'MATCH (c:Customer {id: n.customerId}) MERGE (c)-[:PLACED]->(n)', {batchSize:10000})",
            "ORDER_AT_STORE": "CALL apoc.periodic.iterate('MATCH (n:Order) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:PLACED_AT]->(s)', {batchSize:10000})",
            "ORDER_AT_TABLE": "CALL apoc.periodic.iterate('MATCH (n:Order) WHERE n.storeTableId IS NOT NULL RETURN n', 'MATCH (t:StoreTable {id: n.storeTableId}) MERGE (n)-[:AT_TABLE]->(t)', {batchSize:10000})",
            "ORDER_HAS_PAYMENT": "CALL apoc.periodic.iterate('MATCH (n:Order) WHERE n.paymentId IS NOT NULL RETURN n', 'MATCH (p:Payment {id: n.paymentId}) MERGE (n)-[:HAS_PAYMENT]->(p)', {batchSize:10000})",
            "ORDER_USES_PAYMENT_OPTION": "CALL apoc.periodic.iterate('MATCH (n:Order) WHERE n.paymentOptionEnum IS NOT NULL RETURN n', 'MATCH (pe:PaymentOptionEnum {paymentOptionEnum: n.paymentOptionEnum}) MERGE (n)-[:USES_OPTION]->(pe)', {batchSize:10000})",
            "ORDER_CONTAINS_ITEM": "CALL apoc.periodic.iterate('MATCH (n:OrderItem) WHERE n.orderId IS NOT NULL RETURN n', 'MATCH (o:Order {id: n.orderId}) MERGE (o)-[:CONTAINS]->(n)', {batchSize:10000})",
            "ITEM_IS_MENU": "CALL apoc.periodic.iterate('MATCH (n:OrderItem) WHERE n.menuId IS NOT NULL RETURN n', 'MATCH (m:Menu {id: n.menuId}) MERGE (n)-[:IS_MENU]->(m)', {batchSize:10000})",
            "PAYMENT_BY_CUSTOMER": "CALL apoc.periodic.iterate('MATCH (n:Payment) WHERE n.customerId IS NOT NULL RETURN n', 'MATCH (c:Customer {id: n.customerId}) MERGE (n)-[:PAID_BY]->(c)', {batchSize:10000})",
            "PAYMENT_AT_STORE": "CALL apoc.periodic.iterate('MATCH (n:Payment) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:PROCESSED_AT]->(s)', {batchSize:10000})",
            "REFUND_FOR_ORDER": "CALL apoc.periodic.iterate('MATCH (n:Refund) WHERE n.orderId IS NOT NULL RETURN n', 'MATCH (o:Order {id: n.orderId}) MERGE (n)-[:REFUNDS_ORDER]->(o)', {batchSize:10000})",
            "REFUND_FOR_PAYMENT": "CALL apoc.periodic.iterate('MATCH (n:Refund) WHERE n.paymentId IS NOT NULL RETURN n', 'MATCH (p:Payment {id: n.paymentId}) MERGE (n)-[:ISSUED_FOR]->(p)', {batchSize:10000})",
            "REFUND_AT_STORE": "CALL apoc.periodic.iterate('MATCH (n:Refund) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:PROCESSED_AT]->(s)', {batchSize:10000})",
            "REFUND_ITEM_PART_OF_REFUND": "CALL apoc.periodic.iterate('MATCH (n:RefundItem) WHERE n.refundId IS NOT NULL RETURN n', 'MATCH (r:Refund {id: n.refundId}) MERGE (n)-[:PART_OF_REFUND]->(r)', {batchSize:10000})",
            "REFUND_ITEM_REFERENCES_ORDER_ITEM": "CALL apoc.periodic.iterate('MATCH (n:RefundItem) WHERE n.orderItemId IS NOT NULL RETURN n', 'MATCH (oi:OrderItem {id: n.orderItemId}) MERGE (n)-[:REFUNDS]->(oi)', {batchSize:10000})",
            "MENU_IN_CATEGORY": "CALL apoc.periodic.iterate('MATCH (n:Menu) WHERE n.categoryId IS NOT NULL RETURN n', 'MATCH (c:Category {id: n.categoryId}) MERGE (n)-[:IN_CATEGORY]->(c)', {batchSize:10000})",
            "CATEGORY_IN_STORE": "CALL apoc.periodic.iterate('MATCH (n:Category) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:BELONGS_TO]->(s)', {batchSize:10000})",
            "MENU_HAS_OPTION": "CALL apoc.periodic.iterate('MATCH (j:MenuOptionToMenu) RETURN j', 'MATCH (m:Menu {id: j.menuId}) MATCH (mo:MenuOption {id: j.menuOptionId}) MERGE (m)-[:HAS_OPTION]->(mo)', {batchSize:10000})",
            "OPTION_HAS_CHOICE": "CALL apoc.periodic.iterate('MATCH (j:MenuOptionChoiceToMenuOption) RETURN j', 'MATCH (mo:MenuOption {id: j.menuOptionId}) MATCH (moc:MenuOptionChoice {id: j.menuOptionChoiceId}) MERGE (mo)-[:HAS_CHOICE]->(moc)', {batchSize:10000})",
            "OPTION_BELONGS_TO_STORE": "CALL apoc.periodic.iterate('MATCH (n:MenuOption) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:BELONGS_TO]->(s)', {batchSize:10000})",
            "CHOICE_BELONGS_TO_STORE": "CALL apoc.periodic.iterate('MATCH (n:MenuOptionChoice) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:BELONGS_TO]->(s)', {batchSize:10000})",
            "MENU_REQUIRES_INVENTORY": "CALL apoc.periodic.iterate('MATCH (j:MenuToInventoryItem) RETURN j', 'MATCH (m:Menu {id: j.menuId}) MATCH (i:InventoryItem {id: j.inventoryItemId}) MERGE (m)-[:REQUIRES]->(i)', {batchSize:10000})",
            "INVENTORY_ITEM_IN_STORE": "CALL apoc.periodic.iterate('MATCH (n:InventoryItem) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:IN_STORE]->(s)', {batchSize:10000})",
            "TRANSACTION_FOR_INVENTORY": "CALL apoc.periodic.iterate('MATCH (n:InventoryTransaction) WHERE n.inventoryItemId IS NOT NULL RETURN n', 'MATCH (i:InventoryItem {id: n.inventoryItemId}) MERGE (n)-[:APPLIES_TO]->(i)', {batchSizse:10000})",
            "STORE_IN_FOOD_COURT": "CALL apoc.periodic.iterate('MATCH (n:Store) WHERE n.foodCourtId IS NOT NULL RETURN n', 'MATCH (fc:FoodCourt {id: n.foodCourtId}) MERGE (n)-[:LOCATED_IN]->(fc)', {batchSize:10000})",
            "STORE_HAS_ATTRIBUTE": "CALL apoc.periodic.iterate('MATCH (n:StoreAttribute) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:ATTRIBUTE_OF]->(s)', {batchSize:10000})",
            "ADVERT_FOR_STORE": "CALL apoc.periodic.iterate('MATCH (n:MetaAdvert) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:ADVERTISES_FOR]->(s)', {batchSize:10000})",
            "INSIGHT_FOR_ADVERT": "CALL apoc.periodic.iterate('MATCH (n:MetaAdvertInsight) WHERE n.storeMetaAdvertId IS NOT NULL RETURN n', 'MATCH (ad:MetaAdvert {id: n.storeMetaAdvertId}) MERGE (n)-[:INSIGHT_FOR]->(ad)', {batchSize:10000})",
            "COUPON_FOR_STORE": "CALL apoc.periodic.iterate('MATCH (n:Coupon) WHERE n.storeId IS NOT NULL RETURN n', 'MATCH (s:Store {id: n.storeId}) MERGE (n)-[:VALID_AT]->(s)', {batchSize:10000})",
            "USAGE_OF_COUPON": "CALL apoc.periodic.iterate('MATCH (n:CouponUsage) WHERE n.couponId IS NOT NULL RETURN n', 'MATCH (c:Coupon {id: n.couponId}) MERGE (n)-[:USES]->(c)', {batchSize:10000})",
            "USAGE_BY_CUSTOMER": "CALL apoc.periodic.iterate('MATCH (n:CouponUsage) WHERE n.customerId IS NOT NULL RETURN n', 'MATCH (c:Customer {id: n.customerId}) MERGE (n)-[:USED_BY]->(c)', {batchSize:10000})",
            "USAGE_ON_ORDER": "CALL apoc.periodic.iterate('MATCH (n:CouponUsage) WHERE n.orderId IS NOT NULL RETURN n', 'MATCH (o:Order {id: n.orderId}) MERGE (n)-[:APPLIED_TO]->(o)', {batchSize:10000})",
            "GROUPED_TEXT_HAS_ORIGINAL_LOCALE": "CALL apoc.periodic.iterate('MATCH (n:GroupedText) WHERE n.originalLocaleCode IS NOT NULL RETURN n', 'MATCH (l:Locale {code: n.originalLocaleCode}) MERGE (n)-[:ORIGINALLY_IN]->(l)', {batchSize:10000})",
            "TRANSLATION_OF_GROUPED_TEXT": "CALL apoc.periodic.iterate('MATCH (n:TranslatedText) WHERE n.groupedTextId IS NOT NULL RETURN n', 'MATCH (gt:GroupedText {id: n.groupedTextId}) MERGE (n)-[:TRANSLATION_OF]->(gt)', {batchSize:10000})",
            "TRANSLATION_IN_LOCALE": "CALL apoc.periodic.iterate('MATCH (n:TranslatedText) WHERE n.localeCode IS NOT NULL RETURN n', 'MATCH (l:Locale {code: n.localeCode}) MERGE (n)-[:IN_LOCALE]->(l)', {batchSize:10000})",
            "CATEGORY_HAS_GROUPED_TEXT": "CALL apoc.periodic.iterate('MATCH (n:Category) WHERE n.groupedTextId IS NOT NULL RETURN n', 'MATCH (gt:GroupedText {id: n.groupedTextId}) MERGE (n)-[:HAS_TEXT]->(gt)', {batchSize:10000})",
            "MENU_HAS_GROUPED_TEXT": "CALL apoc.periodic.iterate('MATCH (n:Menu) WHERE n.groupedTextId IS NOT NULL RETURN n', 'MATCH (gt:GroupedText {id: n.groupedTextId}) MERGE (n)-[:HAS_TEXT]->(gt)', {batchSize:10000})",
            "MENU_OPTION_HAS_GROUPED_TEXT": "CALL apoc.periodic.iterate('MATCH (n:MenuOption) WHERE n.groupedTextId IS NOT NULL RETURN n', 'MATCH (gt:GroupedText {id: n.groupedTextId}) MERGE (n)-[:HAS_TEXT]->(gt)', {batchSize:10000})",
            "MENU_OPTION_CHOICE_HAS_GROUPED_TEXT": "CALL apoc.periodic.iterate('MATCH (n:MenuOptionChoice) WHERE n.groupedTextId IS NOT NULL RETURN n', 'MATCH (gt:GroupedText {id: n.groupedTextId}) MERGE (n)-[:HAS_TEXT]->(gt)', {batchSize:10000})",
        }

        for rel_name, query in relationship_queries.items():
            self.establish_relationship_native(rel_name, query)

        logging.info("--- Migration process completed successfully! ---")


if __name__ == '__main__':
    migrator = None
    try:
        migrator = MySqlToNeo4jMigrator(MYSQL_CONFIG, NEO4J_CONFIG)
        migrator.run_migration()
    except Exception:
        logging.exception("A critical error occurred in the main script execution.")
    finally:
        if migrator:
            migrator.close()
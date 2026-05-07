import os
from dotenv import load_dotenv

import psycopg2
from neo4j import GraphDatabase

# Load environment variables
load_dotenv("configs/.env")

# PostgreSQL credentials
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Neo4j credentials
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print("\n--- TESTING POSTGRESQL CONNECTION ---")

try:
    pg_conn = psycopg2.connect(
        host="localhost",
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    print("✅ PostgreSQL connected successfully!")

    pg_conn.close()

except Exception as e:
    print("❌ PostgreSQL connection failed")
    print(e)

print("\n--- TESTING NEO4J CONNECTION ---")

try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    driver.verify_connectivity()

    print("✅ Neo4j connected successfully!")

    driver.close()

except Exception as e:
    print("❌ Neo4j connection failed")
    print(e)
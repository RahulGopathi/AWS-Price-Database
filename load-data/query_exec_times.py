from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decouple import config
import time
from tabulate import tabulate

# Replace with your database URL
DATABASE_URL = f"mysql+mysqlconnector://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}/{config('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a list to store query results
query_results = []


def measure_query_execution_time(query_description, query, parameters=None):
    session = SessionLocal()
    try:
        start_time = time.time()
        result = (
            session.execute(query, parameters) if parameters else session.execute(query)
        )
        end_time = time.time()
        execution_time = end_time - start_time
        rows = result.fetchall()
        num_rows = len(rows)
        query_results.append(
            (query_description, round(execution_time * 1000, 4), num_rows)
        )
        return rows  # Return rows instead of result
    finally:
        session.close()


# Query 1: Know all product families
query_1 = text("SELECT * FROM product_family")
result_1 = measure_query_execution_time("Know all product families", query_1)

# Query 2: Know all the services under a product family
query_2 = text("SELECT DISTINCT service_code FROM product")
result_2 = measure_query_execution_time(
    "Know all the services under a product family", query_2
)

# Query 3: Know all the services available in a region
query_3 = text("SELECT DISTINCT service_code FROM product WHERE region_code = :region")
result_3 = measure_query_execution_time(
    "Know all the services available in a region", query_3, {"region": "us-east-1"}
)

# Query 4: Know all the products of a particular service (e.g., Amazon S3)
query_4 = text(
    "SELECT p.id, p.product_family_id, p.sku, p.location, p.region_code FROM product p WHERE service_code = :service_code"
)
result_4 = measure_query_execution_time(
    "Know all the products of a particular service",
    query_4,
    {"service_code": "AmazonS3"},
)

# Query 5: Know the price in different regions of a particular service
query_5 = text(
    """
    SELECT
    p.id AS id,
    p.sku AS sku,
    p.location AS location,
    p.region_code AS region_code,
    pr.pricePerUnit AS price,
    pr.unit AS unit
    FROM
        product p
    JOIN
        price pr ON p.id = pr.product_id
    WHERE
        p.service_code = :service_code
"""
)
result_5 = measure_query_execution_time(
    "Know the price in different regions of a particular service",
    query_5,
    {"service_code": "AmazonS3"},
)

# Query 6: Know all the products and their prices with a particular product attribute value
query_6 = text(
    """
    SELECT p.id, p.product_family_id, p.sku, p.location, p.region_code, pr.pricePerUnit, pr.unit
    FROM product AS p
    JOIN
        price pr ON p.id = pr.product_id
    WHERE p.service_code = :service_code
    AND JSON_EXTRACT(product_attributes, CONCAT('$.', :attribute_name)) = :attribute_value
"""
)
result_6 = measure_query_execution_time(
    "Know all the products and their prices with a particular product attribute value",
    query_6,
    {
        "attribute_name": "memory",
        "service_code": "AmazonRDS",
        "attribute_value": "1024 GiB",
    },
)

# Print the results as a table
table = tabulate(
    query_results,
    headers=["Query Description", "Execution Time (ms)", "No of Rows returned"],
    tablefmt="grid",
)
print(table)

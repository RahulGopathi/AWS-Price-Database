import json
import requests
import mysql.connector
import sys
from decouple import config

# Check if a JSON file name was provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <json_file_name>")
    sys.exit(1)

json_file_name = sys.argv[1]

# Load the JSON file
try:
    with open(json_file_name, 'r') as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    print(f"Error: File '{json_file_name}' not found.")
    sys.exit(1)

# Define a list of offer names to process
offer_names_to_process = config('OFFER_NAMES_TO_PROCESS', cast=lambda v: [s.strip() for s in v.split(',')])


# Function to create the database and tables
def create_database_and_tables(cursor):
    # Create the 'aws_database' database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS aws_database")
    cursor.execute("USE aws_database")

    # Create the 'product_family' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_family (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """)

    # Create the 'product' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_family_id INT,
            FOREIGN KEY (product_family_id) REFERENCES product_family(id),
            sku VARCHAR(255),
            service_code VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            region_code VARCHAR(255),
            product_attributes JSON
        )
    """)

    # Create the 'price' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price (
            product_id INT,
            FOREIGN KEY (product_id) REFERENCES product(id),
            pricePerUnit DECIMAL(10, 6),
            unit VARCHAR(255),
            description TEXT
        )
    """)


# Function to process an offer
def process_offer(offer_name, offer_details, cursor):
    print(f"Processing offer '{offer_name}'...")

    current_version_url = offer_details['currentVersionUrl']

    # Download the JSON data from the currentVersionUrl
    print(f"Downloading '{offer_name}' JSON data...")
    response = requests.get('https://pricing.us-east-1.amazonaws.com' + current_version_url)
    offer_data = response.json()
    print(f"Loaded '{offer_name}' JSON data.")

    # Initialize variables to track the product family ID and name
    product_family_ids = {}

    # Create the Unknown product family if it doesn't exist
    cursor.execute("INSERT INTO product_family (name) VALUES (%s)", ('Unknown',))
    unknown_product_family_id = cursor.lastrowid
    product_family_ids['Unknown'] = unknown_product_family_id

    print("Inserting products and prices...")
    # Iterate over the products in the offer data
    for product_sku, product_details in offer_data.get('products', {}).items():
        # Create the product family if doesn't exist and use the ID if it does
        product_family_name = product_details.get('productFamily', '')
        if not product_family_name:
            product_family_name = 'Unknown'
        product_family_id = product_family_ids.get(product_family_name)

        if not product_family_id and product_family_name != '' and product_family_name != 'Unknown':
            # If it doesn't exist, create a new product family
            cursor.execute("INSERT INTO product_family (name) VALUES (%s)", (product_family_name,))
            product_family_id = cursor.lastrowid
            product_family_ids[product_family_name] = product_family_id

        # Insert data into the 'product' table
        cursor.execute("""
            INSERT INTO product (product_family_id, sku, service_code, location, region_code, product_attributes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            product_family_id,
            product_details.get('sku', ''),
            product_details.get('attributes', {}).get('servicecode', ''),
            product_details.get('attributes', {}).get('location', product_details.get('attributes', {}).get('fromLocation', '')),
            product_details.get('attributes', {}).get('regionCode', product_details.get('attributes', {}).get('fromRegionCode', '')),
            json.dumps(product_details.get('attributes', {})),  # Entire product_details as JSON
        ))

        last_added_product_id = cursor.lastrowid

        # Insert data into the 'price' table
        term_details = offer_data.get('terms', {}).get('OnDemand', {}).get(product_sku, {})
        price_dimensions = term_details.get(list(term_details.keys())[0], {}).get('priceDimensions', {})
        price_info = price_dimensions.get(list(price_dimensions.keys())[0], {})
        cursor.execute("""
            INSERT INTO price (product_id, pricePerUnit, unit, description)
            VALUES (%s, %s, %s, %s)
        """, (
            last_added_product_id,  # Last inserted product_id
            price_info.get('pricePerUnit', {}).get('USD', 0.0),
            price_info.get('unit', ''),
            price_info.get('description', ''),
        ))

    print(f"Offer '{offer_name}' processed.")


# Define MySQL database connection parameters
db_config = {
    'host': config('DB_HOST'),
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
}

# Create a MySQL database connection
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    print("MySQL connection established.")
    print("Creating database and tables...")
    create_database_and_tables(cursor)
    print("Database and tables created.")

    print("Processing offers...")
    # Iterate over the offers in the JSON data
    if offer_names_to_process == ['*']:
        for offer_name, offer_details in data['offers'].items():
            process_offer(offer_name, offer_details, cursor)
    else:
        for offer_name in offer_names_to_process:
            if offer_name in data['offers']:
                process_offer(offer_name, data['offers'][offer_name], cursor)
            else:
                print(f"Offer '{offer_name}' not found in JSON data.")

    # Commit changes and close the database connection
    connection.commit()

except mysql.connector.Error as error:
    print(f"Error: {error}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")

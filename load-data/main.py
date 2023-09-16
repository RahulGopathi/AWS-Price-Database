import json
import mysql.connector
import sys
from decouple import config
from create_database import create_database_and_tables
from process_offer import process_offer

# Check if a JSON file name was provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <json_file_name>")
    sys.exit(1)

json_file_name = sys.argv[1]

# Load the JSON file
try:
    with open(json_file_name, "r") as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    print(f"Error: File '{json_file_name}' not found.")
    sys.exit(1)

# Define a list of offer names to process
offer_names_to_process = config(
    "OFFER_NAMES_TO_PROCESS", cast=lambda v: [s.strip() for s in v.split(",")]
)


# Define MySQL database connection parameters
db_config = {
    "host": config("DB_HOST"),
    "user": config("DB_USER"),
    "password": config("DB_PASSWORD"),
}

# Create a MySQL database connection
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # collect all the average query times for all offers
    avg_query_times = []

    print("MySQL connection established.")
    print("Creating database and tables...")
    create_database_and_tables(cursor)
    print("Database and tables created.")

    print("Processing offers...")
    # Iterate over the offers in the JSON data
    if offer_names_to_process == ["*"]:
        for offer_name, offer_details in data["offers"].items():
            avg_query_times.append(process_offer(offer_name, offer_details, cursor))
    else:
        for offer_name in offer_names_to_process:
            if offer_name in data["offers"]:
                avg_query_times.append(
                    process_offer(offer_name, data["offers"][offer_name], cursor)
                )
            else:
                print(f"Offer '{offer_name}' not found in JSON data.")

    # Commit changes and close the database connection
    connection.commit()

    print("Successfully processed all offers.")
    print(
        f"Average query execution time for all the offers: {round(sum(avg_query_times) / len(avg_query_times), 2)} ms."
    )

except mysql.connector.Error as error:
    print(f"Error: {error}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")

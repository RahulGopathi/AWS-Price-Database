import requests
import json
import time


# Function to process an offer
def process_offer(offer_name, offer_details, cursor):
    print(f"Processing offer '{offer_name}'...")

    current_version_url = offer_details["currentVersionUrl"]

    # Download the JSON data from the currentVersionUrl
    print(f"Downloading '{offer_name}' JSON data...")
    response = requests.get(
        "https://pricing.us-east-1.amazonaws.com" + current_version_url
    )
    offer_data = response.json()
    print(f"Loaded '{offer_name}' JSON data.")

    # Initialize variables to track the product family ID and name
    product_family_ids = {}

    # Start measuring time
    start_time = time.time()

    # Start measuring no.of queries executed
    query_count = 0

    # Create the Unknown product family if it doesn't exist
    cursor.execute("INSERT INTO product_family (name) VALUES (%s)", ("Unknown",))
    unknown_product_family_id = cursor.lastrowid
    product_family_ids["Unknown"] = unknown_product_family_id
    query_count += 1

    print("Inserting products and prices...")
    # Iterate over the products in the offer data
    for product_sku, product_details in offer_data.get("products", {}).items():
        # Create the product family if doesn't exist and use the ID if it does
        product_family_name = product_details.get("productFamily", "")
        if not product_family_name:
            product_family_name = "Unknown"
        product_family_id = product_family_ids.get(product_family_name)

        if (
            not product_family_id
            and product_family_name != ""
            and product_family_name != "Unknown"
        ):
            # If it doesn't exist, create a new product family
            cursor.execute(
                "INSERT INTO product_family (name) VALUES (%s)", (product_family_name,)
            )
            product_family_id = cursor.lastrowid
            product_family_ids[product_family_name] = product_family_id
            query_count += 1

        # Insert data into the 'product' table
        cursor.execute(
            """
            INSERT INTO product (product_family_id, sku, service_code, location, region_code, product_attributes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                product_family_id,
                product_details.get("sku", ""),
                product_details.get("attributes", {}).get("servicecode", ""),
                product_details.get("attributes", {}).get(
                    "location",
                    product_details.get("attributes", {}).get("fromLocation", ""),
                ),
                product_details.get("attributes", {}).get(
                    "regionCode",
                    product_details.get("attributes", {}).get("fromRegionCode", ""),
                ),
                json.dumps(
                    product_details.get("attributes", {})
                ),  # Entire product_details as JSON
            ),
        )

        last_added_product_id = cursor.lastrowid
        query_count += 1

        # Insert data into the 'price' table
        term_details = (
            offer_data.get("terms", {}).get("OnDemand", {}).get(product_sku, {})
        )
        price_dimensions = term_details.get(list(term_details.keys())[0], {}).get(
            "priceDimensions", {}
        )
        price_info = price_dimensions.get(list(price_dimensions.keys())[0], {})
        cursor.execute(
            """
            INSERT INTO price (product_id, pricePerUnit, unit, description)
            VALUES (%s, %s, %s, %s)
        """,
            (
                last_added_product_id,  # Last inserted product_id
                price_info.get("pricePerUnit", {}).get("USD", 0.0),
                price_info.get("unit", ""),
                price_info.get("description", ""),
            ),
        )
        query_count += 1

    # Stop measuring time
    end_time = time.time()

    # Print the time taken to process the offer
    avg_query_time = (end_time - start_time) * 1000 / query_count
    print(
        f"Average query execution time for the offer '{offer_name}': {round(avg_query_time, 2)} ms."
    )

    print(f"Offer '{offer_name}' processed.")

    return avg_query_time

# Function to create the database and tables
def create_database_and_tables(cursor):
    # Create the 'aws_database' database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS aws_database")
    cursor.execute("USE aws_database")

    # Create the 'product_family' table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_family (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """
    )

    # Create the 'product' table
    cursor.execute(
        """
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
    """
    )

    # Create region_code indexe on the 'product' table
    cursor.execute(
        """
        CREATE INDEX idx_region ON product (region_code)
    """
    )

    # Create service_code index on the 'product' table
    cursor.execute(
        """
        CREATE INDEX idx_service ON product (service_code)
    """
    )

    # Create location index on the 'product' table
    cursor.execute(
        """
        CREATE INDEX idx_location ON product (location)
    """
    )

    # Create product_attributes index on the 'product' table
    cursor.execute(
        """
        CREATE INDEX idx_product_attributes ON product ((CAST(product_attributes->>'$.operation' AS CHAR(255))));
    """
    )

    # Create the 'price' table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS price (
            product_id INT,
            FOREIGN KEY (product_id) REFERENCES product(id),
            pricePerUnit DECIMAL(10, 6),
            unit VARCHAR(255),
            description TEXT
        )
    """
    )

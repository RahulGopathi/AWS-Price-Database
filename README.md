# AWS-Price-Database
Fast API with MySQL database created from AWS Bulk price API

## **Objective**

To create a MySQL database that stores metadata,
pricing, and types of all AWS services across all regions. Additionally, we
will expose an API that can accept various service attributes as input and
return specific product details and their pricing.

## **Database Schema**

Since AWS contains many services across regions, it is important to decide the schema based on the queries users tend to hit on.

### Possible queries

- Know all product families
- Know all the services under a product family
- Know all the services available in a region
- Know all the products of a particular service (e.g., Amazon S3)
- Know the price in different regions of a particular service
- Know all the products and their prices with a particular product attribute value under a service

Here is the schema that I have used to create the database:

- `product_family`
    - `id`
    - `name`
- `product`
    - `id`
    - `sku`
    - FOREIGN KEY `product_family.id`
    - `service_code` - Indexed
    - `location` - Indexed
    - `region_code` - Indexed
    - `product_attributes` - Indexed a particular attribute(e.g., memory in RDS)
- `price`
    - FOREIGN KEY `product.id`
    - `pricePerUnit`
    - `unit`
    - `description`

To achieve Maximum Query Execution time of 50ms, Several Indexes have been added as mentioned above.

## **Creating the Database**
Here are the steps to Creating the Database and loading the data in it.
- Clone the repository
    ```
    git clone https://github.com/RahulGopathi/AWS-Price-Database.git
    ```
- Create the virtual environment
    ```
    python -m venv env
    ```
- Installing the Dependencies
    ```
    pip install -r requirements.txt
    ```
- Activate the virtual environment
    ```
    source env/bin/activate
    ```
- Create the `.env` file and add the following variables
    ```
    cp .env.example .env
    ```
    > Change the variables accordingly in your `.env` file
- Create and Load the Database
    ```
    cd load-data/
    python main.py index.json
    ```
    > Note: Here the offer index file should be provided so that it will automatically download the offer files and load the data into the database. Offer index file can be found [here](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json)
- Run the FastAPI
    ```
    cd ../
    uvicorn main:app --reload
    ```
    > Note: The API will be running on `http://localhost:8000` and the docs can be found at `http://localhost:8000/docs`. You can find the details of all the endpoints in the docs. That's it! You are good to go.

## **Evaluating the Performance**
To see how the schema performs, I have created the `query_exec_time.py` file which will run all the queries mentioned above and prints the execution time of each query.

You can run the file by using the following command:
```
cd load-data/
python query_exec_time.py
```
> Note: The above command will run all the queries and prints the execution time of each query. You can also run each query individually by commenting out the other queries.

Here is the output of the above command:
```
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
| Query Description                                                                |   Execution Time (ms) |   No of Rows returned |
+==================================================================================+=======================+=======================+
| Know all product families                                                        |               16.4297 |                    18 |
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
| Know all the services under a product family                                     |                0.7792 |                     2 |
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
| Know all the services available in a region                                      |                5.945  |                     2 |
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
| Know all the products of a particular service                                    |               21.7781 |                  5691 |
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
| Know the price in different regions of a particular service                      |               36.1409 |                  5691 |
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
| Know all the products and their prices with a particular product attribute value |              113.66   |                   647 |
+----------------------------------------------------------------------------------+-----------------------+-----------------------+
```
> Note: The above results are obtained on a 8GB RAM, 2.3 GHz Dual-Core Intel Core i5 8th gen processor. This may vary depending on the system configuration.

## **Working Demo**
Here is the working demo of the database and the API. You can find the video [here](https://drive.google.com/file/d/17CUAJaXwI6bIBJVY3Z8-vwLEXDBos9jd/view).

## **Future Scope**
- The database can be further optimized by doing more analysis on the queries that are being hit on the database and adding more indexes accordingly.
- Displaying the results in a more user-friendly way by removing the unnecessary columns may improve the performance.
- Since, all the offer files are being downloaded and loaded into the RAM, it is currently impossible to load the data of all the services. So, we can load the data of only the services that are being used by the users. This can be solved by downloading the offer files into the disk and loading the data into the database by reading the offer files from the disk. We can also implement multi-threading to speed up the process of loading the data into the database through which multiple offer files can be loaded into the database at the same time.
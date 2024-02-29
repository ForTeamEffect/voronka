import os

from dotenv import load_dotenv

load_dotenv()

# postgres
pg_user = os.getenv('PG_USER')
pg_password = os.getenv('PG_PASSWORD')
pg_address = os.getenv('PG_ADDRESS')
pg_port = os.getenv('PG_PORT')
pg_server_name = os.getenv('PG_SERVER_NAME')

# telegram
api_id_1 = os.getenv('API_ID_1')
api_hash_1 = os.getenv('API_HASH_1')
phone_number_1 = os.getenv('PHONE_NUMBER_1')
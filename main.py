import connexion
from connexion.resolver import RestyResolver

from app.config import CONFIG
from app.logger import logger
from dotenv import load_dotenv

load_dotenv()

from app.config import CONFIG
import os
import ibm_boto3
from ibm_botocore.client import Config
import pymysql as MySQLdb

cos = ibm_boto3.resource('s3',
    ibm_api_key_id=CONFIG['cos']['apiKey'],
    ibm_service_instance_id=CONFIG['cos']['instanceCRN'],
    config=Config(signature_version="oauth"),
    endpoint_url=CONFIG['cos']['endpoint']
)
cos_client = ibm_boto3.client('s3',
    ibm_api_key_id=CONFIG['cos']['apiKey'],
    ibm_service_instance_id=CONFIG['cos']['instanceCRN'],
    config=Config(signature_version="oauth"),
    endpoint_url=CONFIG['cos']['endpoint']
)

bucket = os.getenv('BUCKET')

conn = MySQLdb.Connection(
    host=CONFIG['sql']['host'],
    user=CONFIG['sql']['user'],
    passwd=CONFIG['sql']['password'],
    port=CONFIG['sql']['port'],
    db=CONFIG['sql']['db']
)

def start_service():
    connex_app = connexion.App(__name__, specification_dir='./')
    connex_app.add_api('swagger.yaml',  strict_validation=False, resolver=RestyResolver('api'))
    logger.info(f'Service starting to listen on port {CONFIG["PORT"]}')

    # get handle to Flask app
    # app = connex_app.app

    if CONFIG['ENV'] != 'local':
        from waitress import serve
        serve(connex_app, host="0.0.0.0", port=CONFIG['PORT'])
    else:
        connex_app.run(port=CONFIG['PORT'])


if __name__ == '__main__':
    start_service()

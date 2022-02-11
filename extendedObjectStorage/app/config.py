import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    'NODE_ENV': os.environ.get('NODE_ENV') or 'local',
    'PORT': os.environ.get('PORT') or 8094,
    'processId': os.getpid(),
    'serviceName': os.environ.get('SERVICE_NAME') or 'serviceName',
    'logs': {
        'enableDebug': os.environ.get('LOG_DEBUG') == 'true'
    },
    'sql': {
        'host': os.environ.get('SQL_HOST'),
        'user': os.environ.get('SQL_USER'),
        'password': os.environ.get('SQL_PASSWORD'),
        'port': int(os.environ.get('SQL_PORT')),
        'db': os.environ.get('SQL_DB'),
    },
    'cos': {
        'endpoint': os.environ.get('COS_ENDPOINT'),
        'apiKey': os.environ.get('COS_API_KEY_ID'),
        'instanceCRN': os.environ.get('COS_INSTANCE_CRN'),
        'bucket': os.environ.get('BUCKET'),
    }
}
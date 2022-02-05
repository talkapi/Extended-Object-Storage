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
    }
}
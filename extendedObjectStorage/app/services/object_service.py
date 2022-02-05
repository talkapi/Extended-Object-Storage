from app.logger import logger
import requests


async def get_object_service():
    logger.info('[get_object_service] starting request')
    x = requests.get('https://w3schools.com')
    return {'object': x.status_code}

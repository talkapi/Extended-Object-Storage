import connexion
from app.config import CONFIG
from app.logger import logger


def start_service():
    connex_app = connexion.App(__name__, specification_dir='./')
    connex_app.add_api('swagger.yaml')
    logger.info(f'Service starting to listen on port {CONFIG["PORT"]}')

    # get handle to Flask app
    # app = connex_app.app

    if CONFIG['NODE_ENV'] != 'local':
        from waitress import serve
        serve(connex_app, host="0.0.0.0", port=CONFIG['PORT'])
    else:
        connex_app.run(port=CONFIG['PORT'])


if __name__ == '__main__':
    start_service()

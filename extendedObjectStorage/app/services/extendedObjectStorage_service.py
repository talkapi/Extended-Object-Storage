from app.logger import logger
from app.config import CONFIG
import os
import uuid
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import pymysql as MySQLdb
import re

cos = ibm_boto3.resource('s3',
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


class ExtendedObjectStorage:
    def create_object(self, obj_name, obj_path, file):
        # Generate bucket filename
        pattern = '\.([a-zA-Z]{3})$'
        match = re.search(pattern, obj_name)
        ext = match.group(1)
        print(ext)
        if ext:
            bucket_file_name = f'{str(uuid.uuid1())}.{ext}'
        else:
            return {'success': False, 'reason': 'Ilegal file', 'status': 400}
        
        # Get directory ID from DB
        cursor = conn.cursor()
        sql = '''SELECT id FROM Directories WHERE directory = %s'''
        dir = (obj_path, )
        cursor.execute(sql, dir)
        result = cursor.fetchone()
        if result:
            dir_id = result[0]
        else:
            logger.warning(f'Path {obj_path} not found')
            return {'success': False, 'reason': 'Path not found', 'status': 404}

        # Insert to DB
        sql = '''INSERT INTO Objects (id, directory_id, object_key) VALUES (%s, %s, %s)'''
        val = (bucket_file_name, dir_id, obj_name)

        try:
            cursor.execute(sql, val)
            conn.commit() #TODO: This commit should be done only after uploading the file into the storage.
        except MySQLdb.Error as err:
            logger.error(f'Error inserting file {obj_name} record to database. Error: {err}.')
            return {'success': False, 'reason': 'Object already exists', 'status': 409}

        # Store incoming file to s3 bucket
        try:
            cos.Object(bucket, bucket_file_name).put(
                Body=file
            )
            logger.info(f'File {bucket_file_name} has been successfully uploaded to s3 bucket {bucket})')
        except ClientError as be:
            logger.error('Error uploading file {bucket_file_name} to bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}
        except Exception as e:
            logger.error('Error uploading file {bucket_file_name} to bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

        return {'success': True, 'status': 200}

    def get_object(self, obj):
        pass

    def delete_object(self, obj):
        pass
    
    def create_directory(self, dir_path):
        # Get directory ID from DB
        try:
            cursor = conn.cursor()
            sql = '''SELECT id FROM Directories WHERE directory = %s'''
            dir = (dir_path,)
            cursor.execute(sql, dir)
            result = cursor.fetchone()
            if result:
                return {'success': False, 'reason': 'Dir is already exist', 'status': 409}

            # Insert to DB
            sql = '''INSERT INTO Directories (directory) VALUES (%s)'''
            val = (dir_path)

            cursor.execute(sql, val)
            conn.commit()
            return {'success': True, 'status': 200}
        except Exception as err:
            logger.error(f'Error creating dir record into the database. Error: {err}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

    def delete_directory(self, dir_path):
        pass

    def list_directory(self, dir_path):
        # Get directory ID from DB
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Directories WHERE directory LIKE %s"
            dir = (dir_path+'%')
            cursor.execute(sql, dir)
            results = cursor.fetchall()
            if results is None:
                return {'success': False, 'reason': 'No elements', 'status': 404}

            filtered_results = []
            for tuple_result in results:
                if tuple_result[1] == dir_path:
                    dir_id = tuple_result[0]
                    sql = "SELECT * FROM Objects WHERE directory_id=%s"
                    cursor.execute(sql, (dir_id, ))
                    objects_results = cursor.fetchall()
                    if objects_results is not None:
                        filtered_results.extend(list(map(lambda object_tuple: object_tuple[2],objects_results)))
                if f'{dir_path}/' in tuple_result[1]:
                    filtered_results.append(tuple_result[1])

            return {'success': True, 'status': 200, 'response': filtered_results}
        except Exception as err:
            logger.error(f'Error: {err}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

    def rename_directory(self, dir_path, new_dir_path):
        pass

    def rename_object(self, obj, new_name):
        pass
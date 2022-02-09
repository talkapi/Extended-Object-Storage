from app.logger import logger
import os
import uuid
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import MySQLdb

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=os.getenv('COS_API_KEY_ID'),
    ibm_service_instance_id=os.getenv('COS_INSTANCE_CRN'),
    config=Config(signature_version="oauth"),
    endpoint_url=os.getenv('COS_ENDPOINT')
)
bucket = os.getenv('BUCKET')

conn = MySQLdb.Connection(
    host=os.getenv('HOST'),
    user=os.getenv('USER'),
    passwd=os.getenv('PASSWORD'),
    port=os.getenv('PORT'),
    db=os.getenv('DB')
)

class ExtendedObjectStorage:
    def create_object(self, obj_name, obj_path, file):
        # Generate bucket filename
        bucket_file_name = str(uuid.uuid1())

        # Get directory ID from DB
        cursor = conn.cursor()
        sql= '''SELECT id from Directories where directory = %s'''
        dir = (obj_path, )
        cursor.execute(sql,dir)
        result = cursor.fetchone()
        if result:
            dir_id = result[0]
        else:
            logger.warning(f'Path {obj_path} not found')
            return {'success': False, 'reason': 'Path not found'}

        # Insert to DB
        sql = '''INSERT INTO Objects (id, directory_id, object_key) VALUES (%s, %s, %s)'''
        val = (bucket_file_name, dir_id, obj_name)

        try:
            cursor.execute(sql, val)
            conn.commit()
        except MySQLdb.Error as err:
            logger.error(f'Error inserting file {obj_name} record to database. Error: {err}.')
            return {'success': False, 'reason': 'Object already exists'}

        # Store incoming file to s3 bucket
        try:
            cos.Object(bucket, bucket_file_name).put(
                Body=file
            )
            logger.info(f'File {bucket_file_name} has been successfully uploaded to s3 bucket {bucket})')
        except ClientError as be:
            logger.error('Error uploading file {bucket_file_name} to bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error'}
        except Exception as e:
            logger.error('Error uploading file {bucket_file_name} to bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error'}

        return {'success': True}


    def get_object(self, obj):
        pass

    def delete_object(self, obj):
        pass
    
    def create_directory(self, dir_name, dir_path):
        pass

    def delete_directory(self, dir):
        pass

    def list_directory(self, dir):
        pass

    def rename_directory(self, dir, new_name):
        pass

    def rename_object(self, obj, new_name):
        pass
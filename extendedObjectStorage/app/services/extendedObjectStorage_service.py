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
            logger.error(f'Error uploading file {bucket_file_name} to bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}
        except Exception as e:
            logger.error(f'Error uploading file {bucket_file_name} to bucket {bucket}. Error: {e}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

        return {'success': True, 'status': 200}

    def get_object(self, obj_name, obj_path):
        # Get object from DB
        cursor = conn.cursor()
        sql = '''SELECT Objects.id from Objects, Directories where Directories.id = Objects.directory_id and Directories.directory = %s and Objects.object_key = %s'''
        obj = (obj_path, obj_name, )
        cursor.execute(sql, obj)
        result = cursor.fetchone()
        if result:
            obj_id = result[0]
        else:
            logger.warning(f'Object {obj_path}{obj_name} not found')
            return {'success': False, 'reason': 'Object not found', 'status': 404}

        # Get object from s3 bucket
        try:
            file = cos.Object(bucket, obj_id).get()
            file_content = file["Body"].read()
        except ClientError as be:
            logger.error(f'Error getting file {obj_id} from bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}
        except Exception as e:
            logger.error(f'Error getting file {obj_id} to bucket {bucket}. Error: {e}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}
        
        return {'success': True, 'object': file_content.decode(), 'contentType': file["ContentType"], 'status': 200}

    def delete_object(self, obj_name, obj_path):
         # Get object from DB
        cursor = conn.cursor()
        sql = '''SELECT Objects.id from Objects, Directories where Directories.id = Objects.directory_id and Directories.directory = %s and Objects.object_key = %s'''
        obj = (obj_path, obj_name, )
        cursor.execute(sql, obj)
        result = cursor.fetchone()
        if result:
            obj_id = result[0]
        else:
            logger.warning(f'Object {obj_path}{obj_name} not found')
            return {'success': False, 'reason': 'Object not found', 'status': 404}

        # Delete object from s3
        try:
            cos.Object(bucket, obj_id).delete()
        except ClientError as be:
            logger.error(f'Error deleting file {obj_id} from bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}
        except Exception as e:
            logger.error(f'Error deleting file {obj_id} from bucket {bucket}. Error: {e}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

        # remove object from DB
        cursor = conn.cursor()
        sql = '''DELETE from Objects where id = %s'''
        obj = (obj_id, )
        cursor.execute(sql, obj)
        conn.commit()

        return {'success': True, 'status': 204}

    
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
        try:
            # Get all directories and sub directories
            cursor = conn.cursor()
            sql = "SELECT id FROM Directories WHERE directory LIKE %s"
            dir = (dir_path+'%')
            cursor.execute(sql, dir)
            results = cursor.fetchall()
            if results is None:
                return {'success': False, 'reason': 'No elements', 'status': 404}

            # Get all the objects that are in the directory
            dir_ids = [item for r in results for item in r]
            sql = f"SELECT id FROM Objects WHERE directory_id in {tuple(dir_ids)}"
            cursor.execute(sql)
            results = cursor.fetchall()

        except Exception as err:
            logger.error(f'Error: {err}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

        # Delete files from bucket
        try:
            obj_ids = [item for r in results for item in r]
            obj_list = []
            for id in obj_ids:
                obj_list.append({"Key": id })
            delete_request = {
                "Objects": obj_list
            }

            cos_client.delete_objects(
                Bucket=bucket,
                Delete=delete_request
            )

            logger.info(f'Directory items has been successfully deleted from s3 bucket {bucket})')
        except ClientError as be:
            logger.error(f'Error deleting directory files from s3 bucket {bucket}. Error: {be}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}
        except Exception as e:
            logger.error(f'Error deleting directory files from s3 bucket {bucket}. Error: {e}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}

        # Remove all objects and folders from DB
        try:
            sql = f"DELETE FROM Directories WHERE id in {tuple(dir_ids)}"
            cursor.execute(sql)
            sql = f"DELETE FROM Objects WHERE id in {tuple(obj_ids)}"
            cursor.execute(sql)
            conn.commit()

        except Exception as err:
            logger.error(f'Error: {err}.')
            return {'success': False, 'reason': 'Internal error', 'status': 500}


        return {'success': True, 'status': 200}
            

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
        if dir_path == new_dir_path:
            return {'success': False, 'reason': 'Bad request', 'status': 400}
        # Get object from DB
        cursor = conn.cursor()
        sql = '''SELECT id from Directories where directory = %s'''
        obj = (dir_path, )
        cursor.execute(sql, obj)
        result = cursor.fetchone()
        if result:
            dir_id = result[0]
        else:
            logger.warning(f'Directory {dir_path} not found')
            return {'success': False, 'reason': 'Directory not found', 'status': 404}
        
        # Update object on DB
        sql = '''update Directories set directory = %s where id = %s'''
        obj = (new_dir_path ,dir_id, )
        cursor.execute(sql, obj)
        conn.commit()

        return {'success': True, 'status': 200}


    def rename_object(self, obj_name, obj_path, new_name):
        if obj_name == new_name:
            return {'success': False, 'reason': 'Bad request', 'status': 400}

        # Get object from DB
        cursor = conn.cursor()
        sql = '''SELECT Objects.id from Objects, Directories where Directories.id = Objects.directory_id and Directories.directory = %s and Objects.object_key = %s'''
        obj = (obj_path, obj_name, )
        cursor.execute(sql, obj)
        result = cursor.fetchone()
        if result:
            obj_id = result[0]
        else:
            logger.warning(f'Object {obj_path}{obj_name} not found')
            return {'success': False, 'reason': 'Object not found', 'status': 404}

        # Update object on DB
        sql = '''update Objects set object_key = %s where id = %s'''
        obj = (new_name ,obj_id, )
        cursor.execute(sql, obj)
        conn.commit()

        return {'success': True, 'status': 200}

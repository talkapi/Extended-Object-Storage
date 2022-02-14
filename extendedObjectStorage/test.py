import os
import ibm_boto3
import uuid
from ibm_botocore.client import Config, ClientError

from dotenv import load_dotenv
load_dotenv()

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=os.getenv('COS_API_KEY_ID'),
    ibm_service_instance_id=os.getenv('COS_INSTANCE_CRN'),
    config=Config(signature_version="oauth"),
    endpoint_url=os.getenv('COS_ENDPOINT')
)

def create_text_file(bucket_name, item_name, file_text):
    print("Creating new item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).put(
            Body=file_text
        )
        print("Item: {0} created!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create text file: {0}".format(e))

with open('testfile.txt', 'r') as f:
    data = f.read()

bucket_file_name = str(uuid.uuid1())

# create_text_file(os.getenv('BUCKET'), bucket_file_name, data)

def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()
        print("File Contents: {0}".format(file["Body"].read()))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))

get_item(os.getenv('BUCKET'),'bede3826-8dba-11ec-a36a-acde48001122.txt')
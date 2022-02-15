import os
import ibm_boto3
import uuid
from ibm_botocore.client import Config, ClientError

from dotenv import load_dotenv
load_dotenv()

cos = ibm_boto3.client("s3",
    ibm_api_key_id=os.getenv('COS_API_KEY_ID'),
    ibm_service_instance_id=os.getenv('COS_INSTANCE_CRN'),
    config=Config(signature_version="oauth"),
    endpoint_url=os.getenv('COS_ENDPOINT')
)


delete_request = {
    "Objects": [
        { "Key": "04498b56-89ae-11ec-a1be-acde48001122" },
        { "Key": "1f8d9d10-8b77-11ec-b8be-acbc32c21c31" }
    ]
}
cos.delete_objects(
    Bucket=os.getenv('BUCKET'),
    Delete=delete_request
)
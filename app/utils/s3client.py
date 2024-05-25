import boto3
import logging
from botocore.exceptions import ClientError
from app.config.settings import settings


class S3Client:
    def __init__(self, region=None):
        self._aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        self._aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        self._aws_bucket_name = settings.AWS_BUCKET_NAME
        self._aws_bucket_region = settings.AWS_BUCKET_REGION

        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._aws_bucket_region
        )
        
    def upload_file(self, file_path, destination="attach/"):
        file_name = file_path.split('/')[-1]  
        destination = destination + file_name
        print(f"Uploading {file_path} to {self._aws_bucket_name}/{destination}")
        try:
            self._client.upload_file(file_path, self._aws_bucket_name, destination)
            print(f"File uploaded to {self._aws_bucket_name}/{destination}")
            return destination
        
        except ClientError as e:
            logging.error(e)
            return False
    
    def create_presigned_url(self, object_name, expiration=3600):
        try:
            response = self._client.generate_presigned_url('get_object',
                Params={
                    'Bucket': self._aws_bucket_name,
                    'Key': object_name},
                    ExpiresIn=expiration
                )
        except ClientError as e:
            logging.error(e)
            return None
        return response

    def close(self):
        self._client.close()
        
import boto3
from botocore.exceptions import ClientError
from app.config.settings import settings


class S3Client:
    def __init__(
            self,
            aws_s3_access_key_id: str = settings.AWS_S3_ACCESS_KEY_ID,
            aws_s3_secret_access_key: str = settings.AWS_S3_SECRET_ACCESS_KEY,
            aws_s3_bucket_name: str = settings.AWS_S3_BUCKET_NAME,
            aws_s3_bucket_region: str = settings.AWS_S3_BUCKET_REGION
    ):
        self.aws_s3_access_key_id = aws_s3_access_key_id
        self.aws_s3_secret_access_key = aws_s3_secret_access_key
        self.aws_s3_bucket_name = aws_s3_bucket_name
        self.aws_s3_bucket_region = aws_s3_bucket_region

        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_s3_access_key_id,
            aws_secret_access_key=self.aws_s3_secret_access_key,
            region_name=self.aws_s3_bucket_region
        )
        
    def upload_file(self, path_from, path_to):
        try:
            if not self.client:
                raise ClientError("S3 client not initialized")
            if not path_from or not path_to:
                raise ClientError("Invalid file path or destination")
            self.client.upload_file(path_from, self.aws_s3_bucket_name, path_to)
            return path_to
        
        except ClientError as e:
            str(e)
            return False

    def delete_file(self, object_name):
        try:
            if not self.client:
                raise Exception("S3 client not initialized")
            if not object_name:
                raise Exception("Invalid object name")
            result = self.client.delete_object(Bucket=self.aws_s3_bucket_name, Key=object_name)
            return result
        except Exception as e:
            str(e)
            return False

    def create_presigned_url(self, object_name, expiration=3600):
        try:
            response = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.aws_s3_bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return response

        except Exception as e:
            print(e)
            return None

    def close(self):
        if self.client:
            self.client.close()
        
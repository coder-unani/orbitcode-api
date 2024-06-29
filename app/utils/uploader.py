from abc import ABC, abstractmethod
from io import BytesIO

import boto3
import requests
from PIL import Image
from app.config.settings import settings


class ImageUploader(ABC):
    @abstractmethod
    def upload_from_file(self, file_path, s3_path):
        pass

    @abstractmethod
    def upload_from_url(self, image_url, s3_path):
        pass

    @abstractmethod
    def close(self):
        pass


class S3ImageUploader(ImageUploader):
    def __init__(
        self,
        uploader=None,
        region=settings.AWS_S3_BUCKET_REGION,
        bucket=settings.AWS_S3_BUCKET_NAME,
        access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
    ):
        # S3 Client 생성
        if uploader is None:
            self.uploader = boto3.client(
                "s3",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region,
            )
        else:
            self.uploader = uploader
        # S3 Bucket 설정
        self.bucket = bucket

    # 파일에서 이미지 생성 및 S3 업로드
    def upload_from_file(self, file, s3_path, resize_width=None):
        try:
            print(s3_path)
            # 파일 오픈
            with Image.open(file) as image:
                image_format = image.format
                image_width, image_height = image.size
                # 이미지 리사이즈
                if resize_width:
                    # 이미지 리사이즈
                    if image_width > resize_width:
                        image = self.resize_image(image, resize_width)
                    # 리사이즈된 이미지 정보 가져오기
                    image_width = image.width
                    image_height = image.height

                # 리사이즈된 이미지를 BytesIO 형태로 저장
                with BytesIO() as buffer:
                    # 리사이즈된 이미지 저장
                    image.save(buffer, format=image_format)
                    # 버퍼 처음 위치로 재설정
                    buffer.seek(0)
                    # S3에 이미지 업로드
                    self.upload(buffer, s3_path)
                    # 버퍼의 끝이로 이동
                    buffer.seek(0, 2)
                    # 이미지 사이즈 가져오기
                    image_size = buffer.tell()

                # 이미지 파일명, 확장자, 사이즈 리턴
                return {
                    "url": s3_path,
                    "extension": image_format,
                    "width": image_width,
                    "height": image_height,
                    "size": image_size,
                }
        except Exception as e:
            print(f"Failed to process the image: {e}")
            return None

    # 이미지 URL에서 이미지 다운로드 후 S3 업로드
    def upload_from_url(self, image_url, s3_path):
        try:
            # 이미지URL에서 다운로드
            response = requests.get(image_url)
            response.raise_for_status()
            response = requests.get(image_url)
            # Ensure we handle HTTP errors
            # 이미지 데이터 가져오기
            with BytesIO(response.content) as image_data:
                # 이미지 사이즈, 확장자 가져오기
                with Image.open(image_data) as image:
                    image_format = image.format
                    image_width, image_height = image.size
                # Reset the buffer's current position to the beginning
                image_size = len(response.content)
                image_data.seek(0)
                # S3에 이미지 업로드
                self.upload(image_data, s3_path)
                # 이미지 확장자, 사이즈 리턴
                return {
                    "url": s3_path,
                    "extension": image_format,
                    "width": image_width,
                    "height": image_height,
                    "size": image_size,
                }
        except Exception as e:
            print(f"Failed to process the image: {e}")
            return None

    # 이미지 S3 업로드
    def upload(self, image, s3_path):
        try:
            self.uploader.upload_fileobj(image, self.bucket, s3_path)
            print(f"Image uploaded to {self.bucket}/{s3_path}")
        except Exception as e:
            print(f"Failed to upload the image to S3: {e}")
            raise e

    # 이미지 리사이즈
    @classmethod
    def resize_image(cls, image, size):
        aspect_ratio = image.height / image.width
        if image.width >= image.height:  # 가로 이미지
            width = size
            height = int(size * aspect_ratio)
        else:  # 세로 이미지
            height = size
            width = int(size / aspect_ratio)

        return image.resize((width, height), Image.Resampling.LANCZOS)

    # S3 클라이언트 종료
    def close(self):
        self.uploader.close()

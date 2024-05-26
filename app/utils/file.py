import os
import uuid
from urllib.request import urlretrieve

from app.config.settings import settings
from app.utils.s3client import S3Client


class File:
    @classmethod
    def read(cls, path):
        try:
            if cls.is_file(path):
                with open(path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(e)
            return None

    @classmethod
    def store(cls, file_path, file_name, file):
        store_file_name = cls.make_unique_filename(file_name)
        store_file_path = os.path.join(file_path, store_file_name)
        try:
            with open(store_file_path, 'wb') as f:
                f.write(file)
            return store_file_path
        except Exception as e:
            print(e)
            return False

    @classmethod
    def store_from_url(cls, url, path):
        filename = cls.make_unique_filename(url)
        path = os.path.join(path, filename)
        try:
            urlretrieve(url, path)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def delete(cls, path):
        try:
            if cls.is_file(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            print(e)
            return False

    @classmethod
    def move(cls, path, new_path):
        try:
            if cls.is_file(path):
                os.rename(path, new_path)
                return True
            return False
        except Exception as e:
            print(e)
            return False

    @classmethod
    def copy(cls, path, new_path):
        try:
            if cls.is_file(path):
                with open(path, 'rb') as f:
                    with open(new_path, 'wb') as nf:
                        nf.write(f.read())
                return True
            return False
        except Exception as e:
            print(e)
            return False

    @classmethod
    def update_to_s3(cls, path, s3_path):
        # Upload the file to s3
        file_name = cls.get_filename_from_path(path)
        s3 = None
        try:
            if cls.is_file(path):
                s3 = S3Client()
                upload_object = s3.upload_file(path, s3_path + file_name)
                s3.close()
                return upload_object
            return False
        except Exception as e:
            print(e)
            return False
        finally:
            if s3:
                s3.close()

    @classmethod
    def delete_from_s3(cls, s3_path):
        # Delete the file from s3
        try:
            s3 = S3Client()
            s3.delete_file(s3_path)
            s3.close()
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_filename_from_path(cls, path):
        # Get the filename from the path
        try:
            if cls.is_file(path):
                return os.path.basename(path)
            return None
        except Exception as e:
            print(e)
            return None

    @classmethod
    def get_extension(cls, path):
        # Get the file extension
        try:
            if cls.is_file(path):
                return os.path.splitext(path)[1]
            return None
        except Exception as e:
            print(e)
            return None

    @classmethod
    def get_size(cls, path):
        try:
            if cls.is_file(path):
                return os.path.getsize(path)
            return None
        except Exception as e:
            print(e)
            return None

    @classmethod
    def is_file(cls, path):
        return os.path.isfile(path)

    @classmethod
    def make_unique_filename(cls, filename):
        # Make a unique filename
        try:
            name, ext = os.path.splitext(filename)
            return f"{str(uuid.uuid4())}{ext}"
        except Exception as e:
            print(e)
            return None

import random
import string
from datetime import datetime


class S3Service:
    def __init__(
        self,
        s3_client_factory,
        s3_endpoint: str,
        s3_bucket: str,
    ):
        self.s3_client_factory = s3_client_factory
        self.s3_endpoint = s3_endpoint
        self.s3_bucket = s3_bucket

    @staticmethod
    def _generate_unique_filename(extension="html"):
        """Генерация уникального имени файла на
        основе времени и случайных символов."""
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        random_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        return f"file_{current_time}_{random_suffix}.{extension}"

    async def upload_file(self, file):
        file_name = self._generate_unique_filename()
        async with self.s3_client_factory() as s3_client:
            await s3_client.upload_fileobj(
                file,
                Bucket=self.s3_bucket,
                Key=file_name,
                ExtraArgs={"ACL": "public-read"},
            )
        file_url = f"{self.s3_endpoint}/{self.s3_bucket}/{file_name}"
        return file_url

import boto3


class S3Helper:
    def __init__(self, endpoint_url: str, region: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            config=boto3.session.Config(signature_version="s3v4"),
            region_name=region,
            endpoint_url=endpoint_url,
        )

    def upload_file(self, file_path: str, file_name: str, body: bytes):
        response = self.s3_client.put_object(
            Bucket=self.bucket_name, Key=f"{file_path}/{file_name}", Body=body
        )
        return response

    def download_file(self, file_path: str, file_name: str):
        response = self.s3_client.get_object(
            Bucket=self.bucket_name, Key=f"{file_path}/{file_name}"
        )
        return response["Body"].read()

    def delete_file(self, file_path: str, file_name: str):
        response = self.s3_client.delete_object(
            Bucket=self.bucket_name, Key=f"{file_path}/{file_name}"
        )
        return response

import os
import boto3
from pathlib import Path


def _to_s3(res_path: Path, s3_bucket: str, s3_url: str) -> None:
    """
    Sends the finished dataset to remote s3-storage

    Arguments:
    res_path: Path - path to res data
    s3_bucket: str - s3 bucket name
    s3_url: str - storage url
    """
    session = boto3.session.Session()

    s3 = session.client(
        service_name="s3",
        aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
        endpoint_url=s3_url,
    )

    s3.upload_file(
        Path.joinpath(res_path, "data.csv"), s3_bucket, "GeneticsDataset.csv"
    )

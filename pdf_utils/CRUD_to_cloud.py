import boto3

from PSITExamCellBackend.settings import *


def save_to_aws(io_buffer, filename, session_name, bucket=BUCKET_NAME):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='ap-south-2'
    )

    try:
        io_buffer.seek(0)
        s3_client.put_object(Body=io_buffer, Bucket=bucket, Key=f'PSIT/{session_name}/{filename}.pdf')
    except Exception as e:
        print(e)
        raise f"Error:{str(e)}"


def delete_from_aws(filename, session_name, bucket=BUCKET_NAME):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='ap-south-2'
    )

    try:
        s3_client.delete_object(Bucket=bucket, Key=f'PSIT/{session_name}/{filename}.pdf')
    except Exception as e:
        print(e)
        raise f"Error:{str(e)}"

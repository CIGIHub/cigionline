from botocore.exceptions import ClientError
from storages.backends.s3boto3 import S3ManifestStaticStorage


class StaticFilesS3Storage(S3ManifestStaticStorage):
    """
    django-storages 1.12.3+ re-raises non-404 errors from exists(), but our
    IAM policy does not grant s3:GetObject (HeadObject) on the static path.
    This restores the pre-1.12.3 behaviour of treating 403 as "file does not
    exist", allowing collectstatic to run without that permission.
    """

    def exists(self, name):
        try:
            return super().exists(name)
        except ClientError as e:
            if e.response['Error']['Code'] in ('403', 'Forbidden'):
                return False
            raise

import boto3
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import DocumentUpload
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.http import StreamingHttpResponse
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from .models import DocumentUpload


class DocumentZipAPIView(APIView):
    def get(self, request, *args, **kwargs):
        API_PASSWORD = settings.DOCUMENT_UPLOAD_PASSWORD

        # Get the password from query parameters
        password = request.query_params.get('password')
        if not password or password != API_PASSWORD:
            return Response({"error": "Invalid or missing password."}, status=403)

        # Fetch all DocumentUpload objects
        documents = DocumentUpload.objects.all()
        if not documents.exists():
            return Response({"error": "No documents found."}, status=404)

        # Create a streaming response
        def zip_generator():
            buffer = BytesIO()
            with ZipFile(buffer, "w", ZIP_DEFLATED) as zip_file:
                s3_client = boto3.client("s3")
                for doc_upload in documents:
                    document = doc_upload.document
                    email = doc_upload.email
                    try:
                        # Fetch the file from S3
                        file_key = document.file.name
                        s3_bucket = settings.AWS_STORAGE_BUCKET_NAME
                        response = s3_client.get_object(Bucket=s3_bucket, Key=file_key)
                        file_content = response["Body"].read()

                        # Write the file to the zip
                        file_name = f"{email} - {file_key.split('/')[-1]}"
                        zip_file.writestr(file_name, file_content)
                    except (NoCredentialsError, PartialCredentialsError, Exception) as e:
                        continue  # Skip if file cannot be retrieved
            buffer.seek(0)
            yield buffer.read()

        # Return streaming response
        response = StreamingHttpResponse(
            zip_generator(), content_type="application/zip"
        )
        response["Content-Disposition"] = "attachment; filename=all_documents.zip"
        return response

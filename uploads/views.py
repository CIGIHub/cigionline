from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
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

        # Create a zip file in memory
        buffer = BytesIO()
        with ZipFile(buffer, 'w', ZIP_DEFLATED) as zip_file:
            for doc_upload in documents:
                document = doc_upload.document
                email = doc_upload.email

                # Get file path and read the file
                file_path = document.file.path
                if not default_storage.exists(file_path):
                    continue

                with default_storage.open(file_path, 'rb') as f:
                    file_content = f.read()

                # Define the file name in the zip
                file_name = f"{email} - {document.file.name.split('/')[-1]}"
                zip_file.writestr(file_name, file_content)

        # Set the response headers for file download
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="all_documents.zip"'
        return response

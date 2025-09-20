"""
EcoleHub Stage 3 - MinIO File Storage Service
For product images, education resources, and school documents
"""

import os
from typing import Optional, BinaryIO, Dict, Any
from minio import Minio
from minio.error import S3Error
import uuid
from urllib.parse import urljoin
import magic
import logging

class MinIOStorageService:
    """
    MinIO service for EcoleHub file storage
    Handles product images, educational resources, and school documents
    """
    
    def __init__(self):
        endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "ecolehub_minio")
        secret_key = os.getenv("MINIO_SECRET_KEY", "minio_secure_password_ndi")
        
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # True for production with HTTPS
        )
        
        # EcoleHub buckets
        self.buckets = {
            "products": "ecolehub-products",      # Shop product images
            "education": "ecolehub-education",    # Educational resources
            "school": "ecolehub-school",          # School official documents
            "user-uploads": "ecolehub-uploads"    # Parent uploads
        }
        
        # Avoid network calls when running tests
        if os.getenv("TESTING") != "1":
            self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Create buckets if they don't exist."""
        for bucket_type, bucket_name in self.buckets.items():
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    logging.info(f"✅ Created bucket: {bucket_name}")
                    
                    # Set public read policy for product images
                    if bucket_type == "products":
                        self._set_public_read_policy(bucket_name)
                        
            except S3Error as e:
                logging.error(f"❌ Error creating bucket {bucket_name}: {e}")
    
    def _set_public_read_policy(self, bucket_name: str):
        """Set public read policy for product images."""
        policy = f'''{{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Effect": "Allow",
                    "Principal": {{"AWS": ["*"]}},
                    "Action": ["s3:GetObject"],
                    "Resource": ["arn:aws:s3:::{bucket_name}/*"]
                }}
            ]
        }}'''
        
        try:
            self.client.set_bucket_policy(bucket_name, policy)
        except S3Error as e:
            logging.warning(f"⚠️ Could not set public policy for {bucket_name}: {e}")
    
    def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        bucket_type: str = "user-uploads",
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to MinIO storage
        
        Args:
            file_data: File binary data
            filename: Original filename
            bucket_type: Type of bucket (products, education, school, user-uploads)
            content_type: MIME type (auto-detected if None)
        """
        try:
            bucket_name = self.buckets.get(bucket_type, self.buckets["user-uploads"])
            
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Auto-detect content type if not provided
            if not content_type:
                file_data.seek(0)
                content_type = magic.from_buffer(file_data.read(1024), mime=True)
                file_data.seek(0)
            
            # Validate file type for school context
            allowed_types = {
                "products": ["image/jpeg", "image/png", "image/webp"],
                "education": ["application/pdf", "image/jpeg", "image/png", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
                "school": ["application/pdf", "image/jpeg", "image/png"],
                "user-uploads": ["image/jpeg", "image/png", "application/pdf"]
            }
            
            if content_type not in allowed_types.get(bucket_type, allowed_types["user-uploads"]):
                return {
                    "success": False,
                    "error": f"Type de fichier non autorisé: {content_type}",
                    "allowed_types": allowed_types.get(bucket_type)
                }
            
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Back to start
            
            # Size limits (in bytes)
            max_sizes = {
                "products": 5 * 1024 * 1024,    # 5MB for product images
                "education": 50 * 1024 * 1024,   # 50MB for educational resources
                "school": 20 * 1024 * 1024,      # 20MB for school documents
                "user-uploads": 10 * 1024 * 1024  # 10MB for user uploads
            }
            
            if file_size > max_sizes.get(bucket_type, max_sizes["user-uploads"]):
                return {
                    "success": False,
                    "error": f"Fichier trop volumineux ({file_size} bytes)",
                    "max_size": max_sizes.get(bucket_type)
                }
            
            # Upload to MinIO
            result = self.client.put_object(
                bucket_name,
                unique_filename,
                file_data,
                length=file_size,
                content_type=content_type
            )
            
            # Generate public URL
            file_url = f"http://{self.client._base_url.netloc}/{bucket_name}/{unique_filename}"
            
            return {
                "success": True,
                "file_url": file_url,
                "filename": unique_filename,
                "original_name": filename,
                "size": file_size,
                "content_type": content_type,
                "bucket": bucket_name,
                "etag": result.etag
            }
            
        except S3Error as e:
            logging.error(f"❌ MinIO upload error: {e}")
            return {
                "success": False,
                "error": f"Erreur upload: {str(e)}"
            }
        except Exception as e:
            logging.error(f"❌ Upload service error: {e}")
            return {
                "success": False,
                "error": "Erreur système upload"
            }
    
    def delete_file(self, file_url: str) -> Dict[str, Any]:
        """Delete file from MinIO storage."""
        try:
            # Extract bucket and filename from URL
            url_parts = file_url.split('/')
            bucket_name = url_parts[-2]
            filename = url_parts[-1]
            
            self.client.remove_object(bucket_name, filename)
            
            return {
                "success": True,
                "message": "Fichier supprimé"
            }
            
        except S3Error as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_url(self, bucket_type: str, filename: str, expires_hours: int = 24) -> Optional[str]:
        """
        Get presigned URL for private files
        For educational resources with restricted access
        """
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                return None
            
            from datetime import timedelta
            
            url = self.client.presigned_get_object(
                bucket_name,
                filename,
                expires=timedelta(hours=expires_hours)
            )
            
            return url
            
        except S3Error:
            return None
    
    def list_files(self, bucket_type: str, prefix: str = "") -> list:
        """List files in a bucket."""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                return []
            
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            
            files = []
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat(),
                    "etag": obj.etag
                })
            
            return files
            
        except S3Error:
            return []

# Global MinIO service instance
minio_service = MinIOStorageService()

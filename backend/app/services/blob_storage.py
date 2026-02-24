from azure.storage.blob.aio import BlobServiceClient, BlobClient
from app.config import settings
from typing import Optional, BinaryIO
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AzureBlobStorageService:
    """Service for managing Azure Blob Storage operations"""
    
    def __init__(self):
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.container_name = settings.BLOB_CONTAINER_NAME
        self.client: Optional[BlobServiceClient] = None
    
    async def initialize(self):
        """Initialize Blob Storage client"""
        try:
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.account_name};"
                f"AccountKey={self.account_key};"
                f"EndpointSuffix=core.windows.net"
            )
            self.client = BlobServiceClient.from_connection_string(
                connection_string
            )
            logger.info(f"Blob Storage initialized: {self.account_name}/{self.container_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Blob Storage: {e}")
            raise
    
    async def close(self):
        """Close Blob Storage client"""
        if self.client:
            await self.client.close()
    
    async def upload_paper(
        self,
        blob_name: str,
        paper_content: dict,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload a question paper to blob storage
        
        Args:
            blob_name: Name for the blob (e.g., "papers/paper_123.json")
            paper_content: Paper content as dictionary
            metadata: Optional metadata for the blob
            
        Returns:
            Blob URL
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Convert content to JSON
            content = json.dumps(paper_content, indent=2)
            
            async with self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            ) as blob_client:
                await blob_client.upload_blob(
                    content,
                    overwrite=True,
                    raw_response_hook=None
                )
                
                # Set metadata if provided
                if metadata:
                    await blob_client.set_blob_metadata(metadata)
            
            # Get blob URL
            blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
            logger.info(f"Paper uploaded: {blob_name}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Failed to upload paper: {e}")
            raise
    
    async def download_paper(self, blob_name: str) -> dict:
        """
        Download a question paper from blob storage
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            Paper content as dictionary
        """
        try:
            if not self.client:
                await self.initialize()
            
            async with self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            ) as blob_client:
                download_stream = await blob_client.download_blob()
                content = await download_stream.readall()
                return json.loads(content.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Failed to download paper: {e}")
            raise
    
    async def delete_paper(self, blob_name: str) -> bool:
        """
        Delete a question paper from blob storage
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            True if deletion successful
        """
        try:
            if not self.client:
                await self.initialize()
            
            async with self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            ) as blob_client:
                await blob_client.delete_blob()
                logger.info(f"Paper deleted: {blob_name}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to delete paper: {e}")
            raise
    
    async def list_papers(self, prefix: str = "") -> list:
        """
        List all papers (blobs) in storage
        
        Args:
            prefix: Optional prefix filter
            
        Returns:
            List of blob names
        """
        try:
            if not self.client:
                await self.initialize()
            
            blobs = []
            async with self.client.get_container_client(
                self.container_name
            ) as container_client:
                async for blob in container_client.list_blobs(name_starts_with=prefix):
                    blobs.append(blob.name)
            
            return blobs
            
        except Exception as e:
            logger.error(f"Failed to list papers: {e}")
            raise
    
    async def get_sas_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Generate a SAS URL for secure access to blob
        
        Args:
            blob_name: Name of the blob
            expiry_hours: Hours until URL expiry
            
        Returns:
            SAS URL for the blob
        """
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            sas_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            logger.info(f"SAS URL generated for: {blob_name}")
            return sas_url
            
        except Exception as e:
            logger.error(f"Failed to generate SAS URL: {e}")
            raise


# Singleton instance
_blob_storage_instance: Optional[AzureBlobStorageService] = None


async def get_blob_storage_service() -> AzureBlobStorageService:
    """Get or create Blob Storage service instance"""
    global _blob_storage_instance
    if _blob_storage_instance is None:
        _blob_storage_instance = AzureBlobStorageService()
        await _blob_storage_instance.initialize()
    return _blob_storage_instance

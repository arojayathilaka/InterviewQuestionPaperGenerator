from azure.cosmos.aio import CosmosClient, ContainerProxy
from app.config import settings
from typing import Optional, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AzureCosmosDBService:
    """Service for managing Azure Cosmos DB operations"""
    
    def __init__(self):
        self.connection_string = settings.COSMOS_DB_CONNECTION_STRING
        self.database_name = settings.COSMOS_DB_DATABASE_NAME
        self.container_name = settings.COSMOS_DB_CONTAINER_NAME
        self.client: Optional[CosmosClient] = None
        self.container: Optional[ContainerProxy] = None
    
    async def initialize(self):
        """Initialize Cosmos DB client and container"""
        try:
            self.client = CosmosClient.from_connection_string(
                self.connection_string
            )
            database = self.client.get_database_client(self.database_name)
            self.container = database.get_container_client(self.container_name)
            logger.info(f"Cosmos DB initialized: {self.database_name}/{self.container_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            raise
    
    async def close(self):
        """Close Cosmos DB client"""
        if self.client:
            await self.client.close()
    
    async def create_user(self, user_id: str, user_data: dict) -> dict:
        """
        Create or update a user profile
        
        Args:
            user_id: Unique user identifier
            user_data: User profile data
            
        Returns:
            Created/updated user document
        """
        try:
            if not self.container:
                await self.initialize()
            
            user_data["id"] = user_id
            user_data["created_at"] = user_data.get("created_at", datetime.utcnow().isoformat())
            user_data["papers_generated"] = user_data.get("papers_generated", 0)
            
            response = await self.container.upsert_item(user_data)
            logger.info(f"User created/updated: {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """
        Retrieve a user profile
        
        Args:
            user_id: User identifier
            
        Returns:
            User data or None if not found
        """
        try:
            if not self.container:
                await self.initialize()
            
            response = await self.container.read_item(user_id, partition_key=user_id)
            logger.info(f"User retrieved: {user_id}")
            return response
            
        except Exception as e:
            logger.warning(f"User not found: {user_id}")
            return None
    
    async def get_item(self, item_id: str, partition_key_value: str) -> Optional[dict]:
        """
        Retrieve an item by ID with explicit partition key
        
        Args:
            item_id: Document ID
            partition_key_value: Partition key value
            
        Returns:
            Item data or None if not found
        """
        try:
            if not self.container:
                await self.initialize()
            
            response = await self.container.read_item(item_id, partition_key=partition_key_value)
            logger.info(f"Item retrieved: {item_id}")
            return response
            
        except Exception as e:
            logger.warning(f"Item not found: {item_id}")
            return None
    
    async def get_by_id(self, item_id: str) -> Optional[dict]:
        """
        Retrieve an item by ID using query (works across partitions)
        
        Args:
            item_id: Document ID
            
        Returns:
            Item data or None if not found
        """
        try:
            if not self.container:
                await self.initialize()
            
            query = "SELECT * FROM c WHERE c.id = @id"
            items = []
            async for item in self.container.query_items(
                query=query,
                parameters=[{"name": "@id", "value": item_id}]
            ):
                items.append(item)
            
            if items:
                logger.info(f"Item retrieved by query: {item_id}")
                return items[0]
            
            logger.warning(f"Item not found by query: {item_id}")
            return None
            
        except Exception as e:
            logger.warning(f"Item query failed: {item_id} - {e}")
            return None
    
    async def search_users(self, query: str, parameters: list) -> List[dict]:
        """
        Search users with SQL query
        
        Args:
            query: SQL query string
            parameters: Query parameters
            
        Returns:
            List of matching users
        """
        try:
            if not self.container:
                await self.initialize()
            
            items = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters
            ):
                items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"User search failed: {e}")
            raise
    
    async def update_item_field(self, item_id: str, field_name: str, field_value: any) -> bool:
        """
        Update a single field in an item using query
        
        Args:
            item_id: Document ID
            field_name: Field to update
            field_value: New field value
            
        Returns:
            True if successful
        """
        try:
            if not self.container:
                await self.initialize()
            
            # Get the item first
            item = await self.get_by_id(item_id)
            if not item:
                logger.warning(f"Item not found for update: {item_id}")
                return False
            
            # Update the field
            item[field_name] = field_value
            item["updated_at"] = datetime.utcnow().isoformat()
            
            # Upsert the item back
            await self.container.upsert_item(item)
            logger.info(f"Item {item_id} field '{field_name}' updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update item field: {e}")
            return False
    
    async def store_paper_metadata(self, paper_id: str, metadata: dict) -> dict:
        """
        Store paper generation metadata
        
        Args:
            paper_id: Unique paper identifier
            metadata: Paper metadata
            
        Returns:
            Stored metadata document
        """
        try:
            if not self.container:
                await self.initialize()
            
            metadata["id"] = paper_id
            metadata["created_at"] = metadata.get("created_at", datetime.utcnow().isoformat())
            
            response = await self.container.upsert_item(metadata)
            logger.info(f"Paper metadata stored: {paper_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to store paper metadata: {e}")
            raise


# Singleton instance
_cosmos_db_instance: Optional[AzureCosmosDBService] = None


async def get_cosmos_db_service() -> AzureCosmosDBService:
    """Get or create Cosmos DB service instance"""
    global _cosmos_db_instance
    if _cosmos_db_instance is None:
        _cosmos_db_instance = AzureCosmosDBService()
        await _cosmos_db_instance.initialize()
    return _cosmos_db_instance

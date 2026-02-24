from azure.servicebus.aio import ServiceBusClient
from app.config import settings
from typing import Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class AzureServiceBusService:
    """Service for managing Azure Service Bus queue operations"""
    
    def __init__(self):
        self.connection_string = settings.AZURE_SERVICE_BUS_CONNECTION_STRING
        self.queue_name = settings.SERVICE_BUS_QUEUE_NAME
        self.client: Optional[ServiceBusClient] = None
    
    async def initialize(self):
        """Initialize the Service Bus client"""
        try:
            self.client = ServiceBusClient.from_connection_string(
                self.connection_string
            )
            logger.info(f"Service Bus client initialized for queue: {self.queue_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Service Bus client: {e}")
            raise
    
    async def close(self):
        """Close the Service Bus client"""
        if self.client:
            await self.client.close()
    
    async def send_message(
        self,
        message_body: dict,
        message_id: str,
        properties: Optional[dict] = None
    ) -> bool:
        """
        Send a message to the queue
        
        Args:
            message_body: The message content as dictionary
            message_id: Unique message identifier
            properties: Optional message properties
            
        Returns:
            True if message sent successfully
        """
        try:
            if not self.client:
                await self.initialize()
            
            async with self.client.get_queue_sender(self.queue_name) as sender:
                from azure.servicebus import ServiceBusMessage
                
                # Prepare application properties
                app_props = properties if properties else {}
                
                message = ServiceBusMessage(
                    body=json.dumps(message_body),
                    message_id=message_id,
                    content_type="application/json",
                    application_properties=app_props
                )
                
                await sender.send_messages(message)
                logger.info(f"Message sent to queue: {message_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def receive_messages(self, max_messages: int = 10) -> list:
        """
        Receive messages from the queue
        
        Args:
            max_messages: Maximum number of messages to receive
            
        Returns:
            List of received messages
        """
        try:
            if not self.client:
                await self.initialize()
            
            messages = []
            async with self.client.get_queue_receiver(
                self.queue_name,
                max_wait_time=5
            ) as receiver:
                batch = await receiver.receive_messages(max_messages=max_messages)
                for message in batch:
                    messages.append({
                        "id": message.message_id,
                        "body": json.loads(str(message)),
                        "message": message
                    })
            
            logger.info(f"Received {len(messages)} messages from queue")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to receive messages: {e}")
            raise
    
    async def delete_message(self, message: Any) -> bool:
        """
        Delete a message from the queue
        
        Args:
            message: The message object to delete
            
        Returns:
            True if message deleted successfully
        """
        try:
            async with self.client.get_queue_receiver(self.queue_name) as receiver:
                await receiver.complete_message(message)
                logger.info(f"Message deleted from queue")
                return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise


# Singleton instance
_service_bus_instance: Optional[AzureServiceBusService] = None


async def get_service_bus_service() -> AzureServiceBusService:
    """Get or create Service Bus service instance"""
    global _service_bus_instance
    if _service_bus_instance is None:
        _service_bus_instance = AzureServiceBusService()
        await _service_bus_instance.initialize()
    return _service_bus_instance

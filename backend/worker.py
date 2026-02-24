"""
Background worker for processing paper generation tasks from Service Bus
Run this in a separate terminal/process alongside the FastAPI server
"""

import asyncio
import json
import logging
from app.config import settings
from app.services import get_service_bus_service, get_cosmos_db_service
from app.services.orchestration import get_orchestration_service
from app.utils import get_logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
)
logger = get_logger(__name__)


async def process_message(message, orchestration_service, cosmos_db_service):
    """Process a single paper generation message"""
    paper_id = message.message_id
    message_body = json.loads(str(message))
    try:
        logger.info(f"Processing paper generation: {paper_id}")
        # Update status to "processing"
        await cosmos_db_service.update_item_field(
            item_id=paper_id,
            field_name="status",
            field_value="processing"
        )
        logger.info(f"[{paper_id}] Status updated to processing")
        request_dict = message_body.get("request", {})
        # Execute the paper generation workflow
        logger.info(f"[{paper_id}] Starting orchestration workflow")
        success = await orchestration_service.execute_paper_generation(
            paper_id=paper_id,
            request_dict=request_dict
        )
        if success:
            logger.info(f"[{paper_id}] Paper generation workflow completed successfully")
        else:
            logger.warning(f"[{paper_id}] Paper generation workflow returned False")
        logger.info(f"[{paper_id}] Message processed successfully - removing from queue")
        
    except asyncio.TimeoutError as e:
        logger.error(f"[{paper_id}] Timeout during processing: {e}")
        try:
            await cosmos_db_service.update_item_field(
                item_id=paper_id,
                field_name="status",
                field_value="failed"
            )
        except Exception as update_err:
            logger.error(f"[{paper_id}] Failed to update status to failed: {update_err}")
        raise
    except Exception as e:
        logger.error(f"[{paper_id}] Failed to process message: {e}", exc_info=True)
        try:
            await cosmos_db_service.update_item_field(
                item_id=paper_id,
                field_name="status",
                field_value="failed"
            )
        except Exception as update_err:
            logger.error(f"[{paper_id}] Failed to update status to failed: {update_err}")
        raise
    finally:
        # Guarantee status update to 'completed' if not failed, and log errors
        try:
            # Only set to completed if not already failed
            item = await cosmos_db_service.get_by_id(paper_id)
            if item and item.get("status") not in ["failed", "completed"]:
                await cosmos_db_service.update_item_field(
                    item_id=paper_id,
                    field_name="status",
                    field_value="completed"
                )
        except Exception as final_update_err:
            logger.error(f"[GUARANTEE] Failed to set status to 'completed' for {paper_id}: {final_update_err}")
        await message.complete()


async def run_worker():
    """Run the worker loop"""
    logger.info("Starting paper generation worker...")
    
    try:
        # Initialize services
        service_bus = await get_service_bus_service()
        cosmos_db = await get_cosmos_db_service()
        orchestration = await get_orchestration_service()
        
        await service_bus.initialize()
        await cosmos_db.initialize()
        
        logger.info(f"Worker listening to queue: {settings.SERVICE_BUS_QUEUE_NAME}")
        
        # Process messages indefinitely
        while True:
            try:
                async with service_bus.client.get_queue_receiver(
                    settings.SERVICE_BUS_QUEUE_NAME,
                    max_wait_time=30  # Wait max 30 seconds for a message
                ) as receiver:
                    async for message in receiver:
                        await process_message(message, orchestration, cosmos_db)
                        
            except asyncio.TimeoutError:
                logger.debug("No messages received, continuing...")
                continue
            except Exception as e:
                logger.error(f"Error in message receive loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                continue
    
    except Exception as e:
        logger.error(f"Worker initialization failed: {e}")
        raise
    finally:
        await service_bus.close()
        await cosmos_db.close()
        logger.info("Worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        exit(1)

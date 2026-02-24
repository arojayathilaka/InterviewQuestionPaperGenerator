from fastapi import APIRouter, HTTPException, Depends, status
import logging

from app.services import get_cosmos_db_service
from app.models.schemas import UserProfile
from app.utils import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register")
async def register_user(
    user_data: dict,
    cosmos_db_service=Depends(get_cosmos_db_service)
):
    """
    Register a new user
    
    Args:
        user_data: User profile data
        cosmos_db_service: Cosmos DB service
        
    Returns:
        Created user profile
    """
    try:
        # Validate required fields
        if "user_id" not in user_data or not user_data["user_id"]:
            raise ValidationError("user_id is required")
        if "email" not in user_data or not user_data["email"]:
            raise ValidationError("email is required")
        if "name" not in user_data or not user_data["name"]:
            raise ValidationError("name is required")
        
        logger.info(f"Registering user: {user_data['user_id']}")
        
        # Create user in Cosmos DB
        created_user = await cosmos_db_service.create_user(
            user_data["user_id"],
            user_data
        )
        
        return {
            "status": "success",
            "user_id": created_user["id"],
            "email": created_user["email"],
            "name": created_user["name"],
            "created_at": created_user.get("created_at"),
        }
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/{user_id}")
async def get_user_profile(
    user_id: str,
    cosmos_db_service=Depends(get_cosmos_db_service)
):
    """
    Get user profile
    
    Args:
        user_id: User ID
        cosmos_db_service: Cosmos DB service
        
    Returns:
        User profile
    """
    try:
        user = await cosmos_db_service.get_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": "USER_NOT_FOUND", "message": f"User {user_id} not found"}
            )
        
        return {
            "user_id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "created_at": user.get("created_at"),
            "papers_generated": user.get("papers_generated", 0),
            "preferences": user.get("preferences"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )

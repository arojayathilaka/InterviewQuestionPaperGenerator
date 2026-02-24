import uuid
from datetime import datetime
from typing import Optional


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    unique_id = str(uuid.uuid4()).replace("-", "")[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_paper_id() -> str:
    """Generate a unique paper ID"""
    return generate_id("paper")


def generate_user_id() -> str:
    """Generate a unique user ID"""
    return generate_id("user")


def generate_request_id() -> str:
    """Generate a unique request ID"""
    return generate_id("req")


def get_current_timestamp() -> str:
    """Get current UTC timestamp"""
    return datetime.utcnow().isoformat()


def calculate_difficulty_distribution(
    num_questions: int,
    target_level: str = "mixed"
) -> dict:
    """
    Calculate difficulty distribution based on target level
    
    Args:
        num_questions: Total number of questions
        target_level: Target difficulty level (easy, medium, hard, mixed)
        
    Returns:
        Dictionary with difficulty distribution counts
    """
    distributions = {
        "easy": {"easy": 0.4, "medium": 0.4, "hard": 0.2},
        "medium": {"easy": 0.2, "medium": 0.6, "hard": 0.2},
        "hard": {"easy": 0.1, "medium": 0.3, "hard": 0.6},
        "mixed": {"easy": 0.33, "medium": 0.34, "hard": 0.33},
    }
    
    percentages = distributions.get(target_level, distributions["mixed"])
    
    result = {}
    for difficulty, percentage in percentages.items():
        count = int(num_questions * percentage)
        result[difficulty] = count
    
    # Adjust for rounding errors
    total = sum(result.values())
    if total < num_questions:
        result["medium"] += num_questions - total
    elif total > num_questions:
        result["medium"] -= total - num_questions
    
    return result

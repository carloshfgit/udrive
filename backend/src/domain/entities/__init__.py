"""
Domain Entities

Entidades puras de domínio sem dependências externas.
"""

from .availability import Availability
from .instructor_profile import InstructorProfile
from .location import Location
from .refresh_token import RefreshToken
from .scheduling import Scheduling
from .scheduling_status import SchedulingStatus
from .student_profile import LearningStage, StudentProfile
from .user import User
from .user_type import UserType

__all__ = [
    "User",
    "UserType",
    "RefreshToken",
    "Location",
    "InstructorProfile",
    "StudentProfile",
    "LearningStage",
    "Scheduling",
    "SchedulingStatus",
    "Availability",
]


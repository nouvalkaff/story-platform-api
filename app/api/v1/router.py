from fastapi import APIRouter

from .auth import router as auth_router
from .stories import router as story_router
from .user import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(story_router)

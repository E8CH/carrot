from fastapi import APIRouter

from app.features.admin.router import router as admin_router
from app.features.chats.router import router as chats_router
from app.features.posts.router import router as posts_router
from app.features.reviews.router import router as reviews_router
from app.features.users.router import router as auth_router
from app.features.users.router import users_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(chats_router, prefix="/chats", tags=["chats"])
router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
router.include_router(admin_router, prefix="/admin", tags=["admin"])

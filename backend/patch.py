from app.api.v1.router import api_router
from test_500 import router
api_router.include_router(router)

from fastapi import APIRouter
router = APIRouter()
@router.get("/test-500")
def test_500():
    raise Exception("Test 500")

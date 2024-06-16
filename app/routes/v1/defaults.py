from fastapi import APIRouter, Depends
from app.database.schema.default import ResData
from app.security.verifier import verify_access_token
from app.network.response import json_response


router = APIRouter()


@router.get("/token", tags=["OAUTH2.0"], response_model=ResData)
async def token(access_token: str = Depends(verify_access_token)):
    if not access_token:
        return json_response(400, "ACCESS_TOKEN_REQUIRE")
    return json_response(200, "ACCESS_TOKEN_VERIFY", {"access_token": access_token})

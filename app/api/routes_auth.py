from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_auth_usecases, get_current_user_id, get_db_session
from app.core.errors import ConflictError, UnauthorizedError, NotFoundError
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCases

router = APIRouter(tags=["authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_usecases: AuthUseCases = Depends(get_auth_usecases),
    db: AsyncSession = Depends(get_db_session)
) -> UserPublic:
    try:
        user = await auth_usecases.register(email=request.email, password=request.password)
        await db.commit()
        return user
    except ConflictError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_usecases: AuthUseCases = Depends(get_auth_usecases),
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    try:
        token = await auth_usecases.login(email=form_data.username, password=form_data.password)
        return TokenResponse(access_token=token, token_type="bearer")
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserPublic)
async def get_current_user_profile(
    user_id: int = Depends(get_current_user_id),
    auth_usecases: AuthUseCases = Depends(get_auth_usecases),
    db: AsyncSession = Depends(get_db_session)
) -> UserPublic:
    try:
        return await auth_usecases.get_profile(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

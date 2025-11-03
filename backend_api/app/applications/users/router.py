import uuid

from fastapi import APIRouter, Depends, status, HTTPException, Request, BackgroundTasks, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession

from applications.users.crud import create_user_in_db, get_user_by_email, activate_user_account
from applications.users.shemas import BaseUserInfo, RegisterUserFields, NewComment, UserSchema, UserUpdateProfile
from database.session_dependencies import get_async_session
from services.rabbit.constants import SupportedQueues
from services.rabbit.rabbitmq_service import rabbitmq_broker
from applications.users.models import User
from applications.auth.auth_handler import AuthHandler
from applications.auth.security import get_current_user

router_users = APIRouter()


@router_users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
        request: Request,
        new_user: RegisterUserFields,
        background_task: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session),
) -> BaseUserInfo:
    user = await get_user_by_email(new_user.email, session)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Already exists')

    created_user = await create_user_in_db(new_user.email, new_user.name, new_user.password, session)
    background_task.add_task(
        rabbitmq_broker.send_message,
        message={
            "name": created_user.name,
            "email": created_user.email,
            'redirect_url': str(request.url_for('verify_user', user_uuid=created_user.uuid_data))
        },
        queue_name=SupportedQueues.USER_REGISTRATION
    )

    return created_user


@router_users.get('/verify/{user_uuid}')
async def verify_user(user_uuid: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    await activate_user_account(user_uuid, session)
    return {"Status": "activated"}


@router_users.patch("/users/add_comment")
async def add_comment_to_user(comment: dict = Body(...), user: User = Depends(get_current_user),
                              session: AsyncSession = Depends(get_async_session)):
    user.comments.append({
        "restaurant_id": comment["restaurant_id"],
        "text": comment["text"],
        "author_name": comment["author_name"]
    })
    session.add(user)
    await session.commit()
    return {"status": "ok", "comments": user.comments}


@router_users.get("/me", response_model=UserSchema)
async def get_my_info(
        current_user: User = Depends(get_current_user),
):
    return current_user



@router_users.patch("/settings_upgrade_profile")
async def upgrade_users_profile(
    user_data: UserUpdateProfile,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):

    updated = False


    if user_data.name is not None:
        if not user_data.name.strip():
            raise HTTPException(status_code=400, detail="Ім'я не може бути порожнім.")
        current_user.name = user_data.name
        updated = True

    if user_data.profile_description is not None:
        current_user.profile_description = user_data.profile_description
        updated = True

    if user_data.email is not None:
        current_user.email = user_data.email
        updated = True


    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Немає даних для оновлення."
        )

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return {
        "status": "200",
        "updated_user": {
            "name": current_user.name,
            "description": current_user.profile_description,
            "email": current_user.email,
        }
    }





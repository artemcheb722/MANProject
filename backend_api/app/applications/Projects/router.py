from typing import Annotated
from fastapi import APIRouter, Depends, status, Body, UploadFile, HTTPException, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from services.s3.s3 import s3_storage
from applications.Projects.models_restaurants import Project
from database.session_dependencies import get_async_session
import uuid
from sqlalchemy import Text, and_, delete
from sqlalchemy.orm import joinedload
from applications.Projects.crud import create_project_in_db, get_project_data, create_comment, \
     get_project_data, get_project_by_pk
from applications.Projects.schemas import ProjectSchema, SearchParamsSchema, CommentResponse, CommentCreate
from applications.users.models import User
from sqlalchemy import select
from applications.Projects.models_restaurants import ProjectComments
from applications.auth.security import get_current_user

router_projects = APIRouter()


@router_projects.post("/create",
                      # dependencies=[Depends(admin_required)]
                      )
async def create_project(
        main_image: UploadFile,
        images: list[UploadFile] = None,
        name: str = Form(..., max_length=50),
        category: str = Form(..., max_length=150),
        description: str = Form(...),
        technologies: str = Form(...),
        detailed_description: str = Form(...),
        user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
) -> ProjectSchema:
    project_uuid = uuid.uuid4()
    main_image = await s3_storage.upload_product_image(main_image, restaurant_uuid=project_uuid)
    images = images or []
    images_urls = []
    for image in images:
        url = await s3_storage.upload_product_image(image, restaurant_uuid=project_uuid)
        images_urls.append(url)

    created_project = await  create_project_in_db(user_id=user.id, project_uuid=project_uuid, project_name=name, category=category,
                                                  description=description, technologies=technologies,
                                                  detailed_description=detailed_description,
                                                  main_image=main_image, images=images_urls,
                                                  session=session)

    return created_project


@router_projects.get('/by_category')
async def get_projects_by_category(category: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(Project).where(Project.category == category)
    )
    projects = result.scalars().all()
    return {
        "items": projects,
        "total": len(projects),
    }

## Get projects by primary key to upload in catalog
@router_projects.get('/{pk}')
async def get_project(
        pk: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await get_project_by_pk(pk, session)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "user_id": project.user_id,
        "id": project.id,
        "project_name": project.project_name,
        "category": project.category,
        "description": project.description,
        "technologies": project.technologies,
        "detailed_description": project.detailed_description,
        "main_image": project.main_image,
        "created_at": project.created_at,
        "images": project.images,
        "author": {
            "id": project.user.id,
            "name": project.user.name,
            "email": project.user.email,
            "followers": project.user.followers,
            "profile_description": project.user.profile_description,
            "subscriptions": project.user.subscriptions,
            "user_avatar": project.user.user_avatar
        }
    }


## Get projects by search
@router_projects.get('/')
async def get_projects(params: Annotated[SearchParamsSchema, Depends()],
                       session: AsyncSession = Depends(get_async_session)):
    result = await get_project_data(params, session)
    return result


@router_projects.post('/create_comments', response_model=CommentResponse)
async def post_comments(
        feedback: CommentCreate,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    project = await get_project_by_pk(feedback.project_id, session)
    if not project:
        raise HTTPException(status_code=404, detail="Ресторан не знайдено")

    comment = await create_comment(
        user_id=user.id,
        project_id=feedback.project_id,
        feedback=feedback.text,
        session=session
    )

    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        project_id=comment.project_id,
        text=comment.feedback,
        user_name=user.name,
        created_at=comment.created_at
    )


@router_projects.get("/comments/{project_id}")
async def get_comments_for_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(ProjectComments, User.name)
        .join(User, User.id == ProjectComments.user_id)
        .where(ProjectComments.project_id == project_id)
    )
    result = await session.execute(stmt)
    feedbacks_with_users = result.all()

    return [
        {
            "status": 200,
            "text": comment.feedback,
            "author": name,
            "created_at": comment.created_at
        }
        for comment, name in feedbacks_with_users
    ]

# @router_restaurants.post("/favourite/{restaurant_id}")
# async def add_to_favourite(
#     restaurant_id: int,
#     user: User = Depends(get_current_user),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     fav = FavouriteRestaurants(user_id=user.id, restaurant_id=restaurant_id)
#     session.add(fav)
#     await session.commit()
#     return {"detail": "Added to favourites"}
#
# @router_restaurants.delete("/favourit/{restaurant_id}")
# async def remove_from_favourite(
#     restaurant_id: int,
#     user: User = Depends(get_current_user),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     stmt = delete(FavouriteRestaurants).where(
#         and_(
#             FavouriteRestaurants.user_id == user.id,
#             FavouriteRestaurants.restaurant_id == restaurant_id
#         )
#     )
#     await session.execute(stmt)
#     await session.commit()
#     return {"detail": "Removed from favourites"}
#
#
#
# @router_restaurants.get("/restaurants/favourite/check/{restaurant_id}")
# async def check_if_favourite(
#     restaurant_id: int,
#     session: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user)
# ):
#     stmt = select(FavouriteRestaurants).where(
#         FavouriteRestaurants.restaurant_id == restaurant_id,
#         FavouriteRestaurants.user_id == current_user.id
#     )
#     result = await session.execute(stmt)
#     favourite = result.scalar_one_or_none()
#
#     if favourite:
#         return {"is_favourite": True}
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Ресторан не у списку улюблених"
#     )

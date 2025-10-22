from typing import Annotated
from fastapi import APIRouter, Depends, status, Body, UploadFile, HTTPException, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from services.s3.s3 import s3_storage
from applications.Projects.models_restaurants import Project
from database.session_dependencies import get_async_session
import uuid
from sqlalchemy import Text, and_, delete
from applications.Projects.crud import create_project_in_db, get_project_data, get_project_by_pk, create_comment, \
    get_project_by_pk, get_project_data
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
        session: AsyncSession = Depends(get_async_session)
) -> ProjectSchema:
    project_uuid = uuid.uuid4()
    main_image = await s3_storage.upload_product_image(main_image, restaurant_uuid=project_uuid)
    images = images or []
    images_urls = []
    for image in images:
        url = await s3_storage.upload_product_image(image, restaurant_uuid=project_uuid)
        images_urls.append(url)

    created_project = await  create_project_in_db(project_uuid=project_uuid, project_name=name, category=category,
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


@router_projects.get('/{pk}')
async def get_product(pk: int, session: AsyncSession = Depends(get_async_session), ) -> ProjectSchema:
    product = await get_project_by_pk(pk, session)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with pk #{pk} not found")
    return product


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
    restaurant = await get_project_by_pk(feedback.restaurant_id, session)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Ресторан не знайдено")

    comment = await create_comment(
        user_id=user.id,
        restaurant_id=feedback.restaurant_id,
        feedback=feedback.text,
        session=session
    )

    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        restaurant_id=comment.restaurant_id,
        text=comment.feedback,
        user_name=user.name,
        created_comment=comment.created_at
    )


@router_projects.get("/comments/{restaurant_id}")
async def get_comments_for_restaurant(
        restaurant_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(ProjectComments, User.name)
        .join(User, User.id == ProjectComments.user_id)
        .where(ProjectComments.restaurant_id == restaurant_id)
    )
    result = await session.execute(stmt)
    feedbacks_with_users = result.all()

    return [
        {
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

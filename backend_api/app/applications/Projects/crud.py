from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, select, func, or_, and_
import math

from applications.Projects.schemas import SearchParamsSchema, SortEnum, SortByEnum, CommentCreate

from applications.Projects.models_restaurants import Project, ProjectComments


async def create_project_in_db(project_uuid, project_name, category, description, technologies, detailed_description, main_image, images, session) -> Project:
    new_project = Project(
        uuid_data=project_uuid,
        project_name=project_name.strip(),
        category=category.strip(),
        description=description.strip(),
        technologies=technologies.strip(),
        detailed_description=detailed_description,
        main_image=main_image,
        images=images,
    )
    session.add(new_project)
    await session.commit()
    return new_project


async def get_project_data(params: SearchParamsSchema, session: AsyncSession):
    query = select(Project)
    count_query = select(func.count()).select_from(Project)

    order_direction = asc if params.order_direction == SortEnum.ASC else desc
    if params.q:
        search_fields = [Project.project_name, Project.description]
        if params.use_sharp_q_filter:
            cleaned_query = params.q.strip().lower()
            search_condition = [func.lower(search_field) == cleaned_query for search_field in search_fields]
            query = query.filter(or_(*search_condition))
            count_query = count_query.filter(or_(*search_condition))
        else:
            words = [word for word in params.q.strip().split() if len(word) > 1]
            search_condition = or_(
                and_(*(search_field.icontains(word) for word in words)) for search_field in search_fields
            )
            query = query.filter(search_condition)
            count_query = count_query.filter(search_condition)

    result = await session.execute(query)
    result_count = await session.execute(count_query)
    total = result_count.scalar()

    return {
        "items": result.scalars().all(),
        "total": total,
        'page': params.page,
        'limit': params.limit,
        'pages': math.ceil(total / params.limit)
    }

async def get_project_by_pk(pk: int, session: AsyncSession) -> Project | None:
    query = select(Project).filter(Project.id == pk)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_comment(user_id: int, project_id: int, feedback: str, session: AsyncSession) -> ProjectComments:
    created_comment = ProjectComments(
        user_id=user_id,
        project_id=project_id,
        feedback=feedback
    )

    session.add(created_comment)
    await session.commit()
    return created_comment
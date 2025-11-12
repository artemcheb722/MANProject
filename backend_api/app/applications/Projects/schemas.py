from pydantic import BaseModel, Field
from enum import StrEnum
from datetime import datetime
from applications.Projects.models_restaurants import Project
from pydantic import BaseModel, Field
from typing import Annotated, Optional



class ProjectSchema(BaseModel):
    id: int
    name: str =  Field(alias="project_name")
    category: str
    description: str
    technologies: str
    detailed_description: str
    main_image: str
    created_at: datetime
    images: list[str]
    user_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class CommentCreate(BaseModel):
    project_id: int
    text: str = Field(alias="feedback")


class CommentResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    text: str
    created_at: datetime
    user_name: str

    class Config:
        from_attributes = True


class SortEnum(StrEnum):
    ASC = 'asc'
    DESC = 'desc'


class SortByEnum(StrEnum):
    ID = 'id'
    PRICE = 'price'


class SearchParamsSchema(BaseModel):
    q: Annotated[Optional[str], Field(default=None)] = None
    page: Annotated[int, Field(default=1, ge=1)]
    limit: Annotated[int, Field(default=10, ge=1, le=50)]
    order_direction: SortEnum = SortEnum.DESC
    sort_by: SortByEnum = SortByEnum.ID
    use_sharp_q_filter: bool = Field(default=False, description='used to search exact q')

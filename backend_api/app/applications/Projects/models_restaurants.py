import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base_models import Base


class ModelCommonMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())


class Project(ModelCommonMixin, Base):
    __tablename__ = "projects"

    uuid_data: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    project_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[str] = mapped_column(Text, nullable=True)
    main_image: Mapped[str] = mapped_column(nullable=True)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=True)
    detailed_description: Mapped[str] = mapped_column(Text, nullable=True)
    Additional_information: Mapped[str] = mapped_column(Text, nullable=True)
    user = relationship("User", back_populates="projects", lazy="selectin")
    count_of_likes: Mapped[int] = mapped_column(default=0, nullable=True)
    comments_relation = relationship(
        "ProjectComments",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"Project {self.project_name} - {self.id}"


class ProjectComments(ModelCommonMixin, Base):
    __tablename__ = "project_comments"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    feedback: Mapped[str] = mapped_column(Text, nullable=True)

    project = relationship("Project", back_populates="comments_relation")


class UserProject(ModelCommonMixin, Base):
    __tablename__ = "user_projects"

    uuid_data: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    project_name: Mapped[str] = mapped_column(String(300), index=True)
    category: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    technologies: Mapped[str] = mapped_column(Text, nullable=True)
    project_photo: Mapped[str] = mapped_column(nullable=True)

    # user = relationship("User", back_populates="projects")



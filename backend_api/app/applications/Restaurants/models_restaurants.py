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

class Restaurants(ModelCommonMixin, Base):
    __tablename__ = "Restaurants"

    uuid_data: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    city: Mapped[str] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    menu: Mapped[str] = mapped_column(Text, nullable=False)
    main_image: Mapped[str] = mapped_column(nullable=False)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    detailed_description: Mapped[str] = mapped_column(Text, nullable=True)
    comments_relation = relationship(
        "RestaurantComments",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f'Restaurant {self.name} - {self.id}'

class RestaurantComments(ModelCommonMixin, Base):
    __tablename__ = "restaurant_comments"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("Restaurants.id"))
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    restaurant = relationship("Restaurants", back_populates="comments_relation")



class FavouriteRestaurants(ModelCommonMixin, Base):
    __tablename__ = "favourite_restaurants"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("Restaurants.id"))



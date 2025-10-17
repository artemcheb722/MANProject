from enum import StrEnum
from typing import Callable, Self

from services.rabbit.handlers import register_user, user_added_product_to_cart


class SupportedQueues(StrEnum):
    USER_REGISTRATION = 'user_registration'
    USER_ADDED_PRODUCT_TO_CART = 'user_added_product_to_cart'

    @classmethod
    def get_queues(cls) -> list[str]:
        return list(cls)

    @classmethod
    def get_handler(cls, queue_name: Self) -> Callable:
        handlers_map = {
            cls.USER_REGISTRATION: register_user,
            cls.USER_ADDED_PRODUCT_TO_CART: user_added_product_to_cart
        }
        return handlers_map[queue_name]
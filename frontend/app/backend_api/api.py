

import httpx
from settings import settings
from fastapi import Request


async def login_user(user_email: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f'{settings.BACKEND_API}/auth/login',
            data={"username": user_email, 'password': password}

        )
        print(response.json())
        return response.json()


async def register_user(user_email: str, password: str, name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f'{settings.BACKEND_API}/users/create',
            json={"name": name, 'password': password, "email": user_email},
            headers={'Content-Type': 'application/json'}

        )
        return response.json()


async def get_user_info(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/auth/get_my_info',
            headers={"Authorization": f'Bearer {access_token}'}

        )
        user_data = response.json()
        return user_data


async def get_current_user_with_token(request: Request) -> dict:
    access_token = request.cookies.get('access_token')
    if not access_token:
        return {}
    user = await get_user_info(access_token)
    user['access_token'] = access_token
    return user


async def get_restaurants(q: str = ""):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/restaurants/',
            params={"q": q}

        )
        return response.json()

async def get_restaurant(pk: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/restaurants/{pk}',
        )
        return response.json()

async def get_restaurant_by_city(city: str = ""):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/restaurants/by_city',
            params={"city": city}

        )
        return response.json()


async def send_comment(access_token: str, restaurant_id: int, text: str, author_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url=f'{settings.BACKEND_API}/users/users/add_comment',
            json={
                "restaurant_id": restaurant_id,
                "text": text,
                "author_name": author_name
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()

## current func to create comment
async def create_comment(restaurant_id: int, feedback: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f'{settings.BACKEND_API}/restaurants/create_comments',
            json={
                'restaurant_id': restaurant_id,
                'feedback': feedback
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        return response.json()



async def get_all_comments(restaurant_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f"{settings.BACKEND_API}/restaurants/comments/{restaurant_id}"
        )
        return response.json()


async def add_to_favourite(restaurant_id: int, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"{settings.BACKEND_API}/restaurants/favourite/{restaurant_id}",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        return response.json()

async def remove_from_favourite(restaurant_id: int, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            url=f"{settings.BACKEND_API}/restaurants/favourite/{restaurant_id}",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        return response.json()

async def check_if_favourite(restaurant_id: int, token: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f"{settings.BACKEND_API}/restaurants/favourite/check/{restaurant_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200
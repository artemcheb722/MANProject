

import httpx
from settings import settings
from fastapi import Request, UploadFile


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


async def get_projects(q: str = ""):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/projects/',
            params={"q": q}

        )
        return response.json()

async def get_project(pk: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/projects/{pk}',
        )
        return response.json()

async def get_project_by_category(category: str = ""):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/projects/by_category',
            params={"category": category}

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
async def create_comment(project_id: int, feedback: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f'{settings.BACKEND_API}/projects/create_comments',
            json={
                'project_id': project_id,
                'feedback': feedback
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        return response.json()



async def get_all_comments(project_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f"{settings.BACKEND_API}/projects/comments/{project_id}"
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


async def get_users_info_for_account(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=f'{settings.BACKEND_API}/users/me',
            headers={"Authorization": f'Bearer {access_token}'}

        )
        user_info = response.json()
        return user_info

## TO ADD WITHOUT AVA
async def edit_users_profile(access_token: str, profile_description: str, name: str, email: str, user_avatar: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url=f'{settings.BACKEND_API}/users/settings_upgrade_profile',
            json={
                'access_token': access_token,
                'profile_description': profile_description,
                'name': name,
                'email': email,
                'user_avatar': user_avatar
            },
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        new_description = response.json()
        return new_description

## TO ADD WITH AVA
async def edit_users_profile_with_avatar(access_token: str, profile_description: str, name: str, email: str,
                                         user_avatar: UploadFile, token: str):
    async with httpx.AsyncClient() as client:

        data = {
            'access_token': access_token or "",
            'profile_description': profile_description or "",
            'name': name or "",
            'email': email or "",
        }

        file_content = await user_avatar.read()
        files = {
            'user_avatar': (user_avatar.filename, file_content, user_avatar.content_type)
        }

        response = await client.patch(
            url=f'{settings.BACKEND_API}/users/settings_upgrade_profile',
            data=data,
            files=files,
            headers={
                'Authorization': f'Bearer {access_token}',
            },
            timeout=30.0
        )
        return response.json()
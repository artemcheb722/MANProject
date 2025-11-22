from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from backend_api.api import get_current_user_with_token, login_user, get_projects, get_project, get_user_info, \
    get_project_by_category, get_users_info_for_account, edit_users_profile, edit_users_profile_with_avatar, \
    create_projects, get_user_by_pk

import humanize
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi import HTTPException, UploadFile, File
from backend_api.api import register_user, send_comment, get_all_comments, create_comment, add_to_favourite, \
    remove_from_favourite, check_if_favourite

router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.get('/')
@router.post('/')
async def index(request: Request,
                category: str = Form(''),
                query: str = Form(''),
                user: dict = Depends(get_current_user_with_token)):
    if category:
        projects_response = await get_project_by_category(category=category)
    else:
        projects_response = await get_projects(query)

    projects = projects_response['items']
    show_not_found = query and not projects

    context = {
        'request': request,
        'restaurants': projects,
        'selected_category': category,
        'query': query,
        'show_not_found': show_not_found
    }

    if user.get('name'):
        context['user'] = user

    return templates.TemplateResponse('index.html', context=context)


@router.post('/favourite_restaurants')
async def favourite_restaurants():
    return templates.TemplateResponse('favourite_restaurants.html')


def naturaltime(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return humanize.naturaltime(datetime.utcnow() - value)


templates.env.filters["naturaltime"] = naturaltime


@router.get("/project/{project_id}")
async def restaurant_detail(
        request: Request,
        project_id: int,

):
    project = await  get_project(project_id)
    comments = await get_all_comments(project_id)

    return templates.TemplateResponse("restaurant_detail.html", {
        "request": request,
        "project": project,
        "comments": comments,
    })


@router.post("/project/{project_id}/add_comment")
async def add_comment(
        request: Request,
        project_id: int,
        comment_text: str = Form(...),
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    await create_comment(
        project_id=project_id,
        feedback=comment_text,
        token=token
    )

    return RedirectResponse(
        url=request.url_for("restaurant_detail", project_id=project_id),
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/restaurants/favourite/{restaurant_id}/add")
async def add_to_favourite_route(
        request: Request,
        restaurant_id: int,
):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    await add_to_favourite(restaurant_id=restaurant_id, token=token)

    return RedirectResponse(
        url=request.url_for("restaurant_detail", restaurant_id=restaurant_id),
        status_code=303
    )


@router.get("/project/{restaurant_id}")
async def get_all_comments_for_project(
        request: Request,
        project_id: int,

):
    project = await  get_project(project_id)
    comments = await get_all_comments(project_id)

    return templates.TemplateResponse("restaurant_detail.html", {
        "request": request,
        "project": project,
        "comments": comments,
    })


@router.post("/restaurants/favourite/{restaurant_id}/remove")
async def remove_from_favourite(
        request: Request,
        restaurant_id: int,
):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    await remove_from_favourite(restaurant_id=restaurant_id, token=token)

    return RedirectResponse(
        url=request.url_for("restaurant_detail", restaurant_id=restaurant_id),
        status_code=303
    )


@router.get('/restaurants/{project_id}')
async def restaurant_detail(
        request: Request,
        project_id: int,
        user: dict = Depends(get_current_user_with_token)
):
    project = await get_project(project_id)



    context = {
        'request': request,
        'project': project,
        'user': user if user.get("name") else None,
        'is_favourite': False,
    }

    token = user.get("token")
    if token:
        try:
            context["is_favourite"] = await check_if_favourite(project_id, token)
        except Exception as e:
            print(f"[ERROR is_favourite]: {e}")
            context["is_favourite"] = False

    return templates.TemplateResponse('restaurant_detail.html', context=context)


@router.get('/login')
@router.post('/login')
async def login(request: Request, user: dict = Depends(get_current_user_with_token), user_email: str = Form(''),
                password: str = Form('')):
    context = {'request': request}
    print(user, 55555555555555555555555)
    redirect_url = request.url_for("index")
    if user.get('name'):
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    if request.method == "GET":
        response = templates.TemplateResponse('login.html', context=context)
        response.delete_cookie('access_token')
        return response

    user_tokens = await login_user(user_email, password)
    access_token = user_tokens.get('access_token')
    if not access_token:
        errors = ['Incorrect login or password']
        context['errors'] = errors
        return templates.TemplateResponse('login.html', context=context)

    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60 * 5)
    return response


@router.get('/logout')
async def logout(request: Request):
    redirect_url = request.url_for("login")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('access_token')
    return response


@router.get('/register')
@router.post('/register')
async def register(
        request: Request,
        user: dict = Depends(get_current_user_with_token),
        user_email: str = Form(''),
        password: str = Form(''),
        user_name: str = Form(''),
):
    context = {'request': request, "entered_email": user_email, 'entered_name': user_name}
    redirect_url = request.url_for("index")
    if user.get('name'):
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    if request.method == "GET":
        response = templates.TemplateResponse('register.html', context=context)
        response.delete_cookie('access_token')
        return response

    created_user = await register_user(user_email=user_email, password=password, name=user_name)
    if created_user.get('email'):
        user_tokens = await login_user(user_email, password)
        access_token = user_tokens.get('access_token')
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60 * 5)
        return response

    context['errors'] = [created_user['detail']]
    response = templates.TemplateResponse('register.html', context=context)
    return response


@router.get("/main_page", response_class=HTMLResponse)
async def get_main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


@router.get("/user_info", response_class=HTMLResponse)
async def get_users_data(request: Request):
    access_token = request.cookies.get("access_token")

    if not access_token:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Потрібна авторизація!"}
        )

    try:
        user_info = await get_users_info_for_account(access_token)
        user_info["projects_count"] = len(user_info.get("projects", []))
        user_info["following"] = user_info.get("subscriptions", 0)

        return templates.TemplateResponse(
            "user_profile.html",
            {
                "request": request,
                "user": user_info
            }
        )

    except Exception as e:
        print(f"Error in get_users_data: {e}")
        return templates.TemplateResponse(
            "user_profile.html",
            {
                "request": request,
                "user": {
                    "name": user_info.name,
                    "email": "",
                    "projects": [],
                    "profile_description": "Користувач ще не додав опису",
                    "user_avatar": None,
                    "projects_count": 0,
                    "followers": 0,
                    "following": 0
                }
            }
        )


@router.get("/user/{user_id}", response_class=HTMLResponse)
async def get_user_profile_by_id(request: Request, user_id: int):
    try:
        user_info = await get_user_by_pk(user_id)

        user_info["projects_count"] = len(user_info.get("projects", []))
        user_info["following"] = user_info.get("subscriptions", 0)

        return templates.TemplateResponse(
            "user_profile.html",
            {
                "request": request,
                "user": user_info
            }
        )

    except Exception as e:
        print(f"Error in get_user_profile_by_id: {e}")
        return templates.TemplateResponse(
            "user_profile.html",
            {
                "request": request,
                "user": {
                    "name": "Користувач не знайдений",
                    "email": "",
                    "projects": [],
                    "profile_description": "Цей користувач не існує",
                    "user_avatar": None,
                    "projects_count": 0,
                    "followers": 0,
                    "following": 0
                }
            }
        )


@router.get("/Upgrade_profile_page", response_class=HTMLResponse)
async def settings_page(request: Request, user: dict = Depends(get_current_user_with_token)):
    return templates.TemplateResponse(
        "user_profile_settings.html",
        {
            "request": request,
            "user": user,
            "users_upgrade": None
        }
    )


@router.post("/settings_upgrade_profile")
async def Edit_users_profile(
        request: Request,
        user: dict = Depends(get_current_user_with_token),
        name: str = Form(None),
        profile_description: str = Form(None),
        email: str = Form(None),
        user_avatar: UploadFile = File(None)):
    if user_avatar and user_avatar.filename:
        Upgraded_profile = await edit_users_profile_with_avatar(
            name=name,
            profile_description=profile_description,
            email=email,
            user_avatar=user_avatar,
            access_token=user.get("access_token"),
            token=user.get("token")
        )
    else:

        Upgraded_profile = await edit_users_profile(
            name=name,
            profile_description=profile_description,
            email=email,
            user_avatar=None,
            access_token=user.get("access_token"),
            token=user.get("token")
        )

    return templates.TemplateResponse(
        "user_profile_settings.html",
        {
            "request": request,
            "users_upgrade": Upgraded_profile,
            "user": user
        }
    )


@router.post("/create_project")
async def create_project_endpoint(
        request: Request,
        name: str = Form(...),
        category: str = Form(...),
        description: str = Form(...),
        technologies: str = Form(...),
        detailed_description: str = Form(...),
        main_image: UploadFile = File(...),
        images: list[UploadFile] = File(None)
):
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        new_project = await create_projects(
            access_token=access_token,
            name=name,
            category=category,
            description=description,
            technologies=technologies,
            detailed_description=detailed_description,
            main_image=main_image,
            images=images or []
        )

        user_data = await get_current_user_with_token(access_token)
        return templates.TemplateResponse(
            "user_profile.html",
            {
                "request": request,
                "new_project": new_project,
                "author_profile_url": user_data
            }
        )

    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            {
                "request": request,
                "error_message": "Помилка при створенні проєкту"
            }
        )

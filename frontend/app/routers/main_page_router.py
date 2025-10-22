from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import  RedirectResponse

from backend_api.api import get_current_user_with_token, login_user, get_projects, get_project, get_user_info, get_project_by_category
import humanize
from datetime import datetime
from fastapi import HTTPException
from backend_api.api import register_user, send_comment, get_all_comments, create_comment, add_to_favourite, remove_from_favourite, check_if_favourite

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




@router.post("/restaurants/{restaurant_id}/add_comment")
async def add_comment(
    request: Request,
    restaurant_id: int,
    comment_text: str = Form(...),
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    await create_comment(
        restaurant_id=restaurant_id,
        feedback=comment_text,
        token=token
    )

    return RedirectResponse(
        url=request.url_for("restaurant_detail", restaurant_id=restaurant_id),
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






@router.get("/projects/{project_id}")
async def project_detail(
    request: Request,
    project_id: int,
    user: dict = Depends(get_current_user_with_token)
):
    # Получаем сам проект из БД или API
    project = await get_project(project_id)
    if not project:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Проект не знайдено"}
        )

    # Получаем комментарии
    comments = project.get("comments", [])

    # Формируем контекст
    context = {
        "request": request,
        "project": project,
        "comments": comments,
        "user": user if user and user.get("name") else None,
        "is_favourite": False,
    }

    # Проверяем, в избранном ли проект
    token = user.get("token") if user else None
    if token:
        try:
            context["is_favourite"] = await check_if_favourite(project_id, token)
        except Exception as e:
            print(f"[ERROR is_favourite]: {e}")
            context["is_favourite"] = False

    # Возвращаем шаблон
    return templates.TemplateResponse("restaurant_detail.html", context)

@router.get('/login')
@router.post('/login')
async def login(request: Request, user: dict=Depends(get_current_user_with_token), user_email: str = Form(''), password: str = Form('')):
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
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60*5)
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


from django.shortcuts import render
from smauth.lib import fb_user_handler
from smauth.lib.decorations import requires_login, requires_admin
from django.conf import settings
from django.contrib import auth
from .models import Users
import requests

# Create your views here.
fb_auth = settings.FIREBASE_CLIENT_AUTH


def index(request):
    return render(request, 'index.html')


def sign_up(request):
    email = request.POST.get('email')
    password = request.POST.get('pass')
    try:
        fb_user_handler.create_fb_user_with_email_and_password(
            email=email,
            password=password
        )
    except Exception as e:
        print('Error: {}'.format(e))
        message = "계정 생성에 실패했습니다. 다시 시도해주세요. ;("
        return render(request, 'sign_up.html', {'message': message})
    message = '회원가입이 완료되었습니다. 로그인해주세요!'
    return render(request, 'index.html', {'message': message})


def sign_up_post(request):
    return render(request, 'sign_up.html')


def logout(request):
    auth.logout(request)
    return render(request, 'index.html')


def sign_in(request):
    email = request.POST.get('email')
    password = request.POST.get('pass')
    try:
        user = fb_auth.sign_in_with_email_and_password(email, password)
    except Exception as e:
        print('Error: {}'.format(e))
        message = '아이디나 비밀번호가 일치하지않습니다.'
        return render(request, 'index.html', {'message': message})
    session_id = user.get('idToken')
    request.session['uid'] = str(session_id)
    return render(request, 'index.html')


def api_test(request):
    query_text = request.GET.get('query_text')
    if not query_text:
        message = 'Input Data가 없습니다! :('
        return render(request, 'index.html', {'message': message})

    id_token = request.session.get('uid')
    if id_token is None:
        id_token = ''

    try:
        res = requests.get(
            url=settings.API_URL + 'smbotText/?query_text=' + query_text,
            headers={
                'authorization': 'JWT ' + id_token
            }
        )
        message = str(res.json())
    except Exception as e:
        print('Error: {}'.format(e))
        message = 'API 서버에 알 수 없는 오류가 발생했습니다. 다시 시도해주세요... ;('
    return render(request, 'index.html', {'message': message, 'token_info': id_token})


@requires_login
def create_claim(request):
    id_token = request.session.get('uid')
    uid = fb_auth.get_account_info(id_token).get('users')[0].get('localId')
    user = fb_user_handler.get_fb_user_from_uid(uid)
    if fb_user_handler.fb_user_claim_update(user, settings.API_APP_NAME, True):
        message = 'API 서비스 이용 권한을 생성했습니다. 다시 로그인 해주세요.'
        auth.logout(request)
    else:
        message = '이미 부여된 권한입니다.'
    return render(request, 'index.html', {'message': message})


@requires_login
def delete_claim(request):
    id_token = request.session.get('uid')
    uid = fb_auth.get_account_info(id_token).get('users')[0].get('localId')
    user = fb_user_handler.get_fb_user_from_uid(uid)
    if fb_user_handler.fb_user_claim_update(user, settings.API_APP_NAME, False):
        message = 'API 서비스 이용 권한을 제거했습니다. 다시 로그인 해주세요.'
        auth.logout(request)
    else:
        message = '존재하지않는 권한입니다.'
    return render(request, 'index.html', {'message': message})


@requires_admin
def admin_dashboard(request):
    key = Users.objects.all()
    context = {'users': key}
    return render(request, 'dashboard.html', context)


@requires_admin
def auth_db_synchronization(request):
    fb_user_handler.fb_and_mydb_all_sync()
    key = Users.objects.all()
    message = '동기화가 완료되었습니다.'
    context = {
        'users': key,
        'message': message
    }
    return render(request, 'dashboard.html', context)


@requires_admin
def user_update(request):
    uid = request.POST.get('uid')
    email = request.POST.get('email')
    password = request.POST.get('pass')
    display_name = request.POST.get('name')
    try:
        fb_user_handler.fb_user_update(
            uid=uid,
            email=email,
            password=password,
            display_name=display_name
        )
        message = '해당 사용자 정보를 수정했습니다.'
    except Exception as e:
        message = '사용자 정보 변경 중 오류 발생: ' + str(e)
    key = Users.objects.all()
    context = {
        'users': key,
        'message': message
    }
    return render(request, 'dashboard.html', context)


@requires_admin
def user_update_post(request):
    uid = request.GET.get('uid')
    if uid is None:
        key = Users.objects.all()
        message = '잘못된 접근입니다.'
        context = {
            'users': key,
            'message': message
        }
        return render(request, 'dashboard.html', context)
    context = {'uid': uid}
    return render(request, 'user_update.html', context)


@requires_admin
def user_delete(request):
    try:
        fb_user_handler.fb_user_delete(request.GET.get('uid'))
        message = '해당 사용자를 삭제했습니다.'
    except Exception as e:
        message = '사용자 삭제 중 오류 발생: ' + str(e)
    key = Users.objects.all()
    context = {
        'users': key,
        'message': message
    }
    return render(request, 'dashboard.html', context)

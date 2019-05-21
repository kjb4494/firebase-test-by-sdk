from django.shortcuts import render
from smauth.lib import pyrebase_auth
from config import config
from django.conf import settings
from django.contrib import auth
from firebase_admin import auth as fb_admin_auth
import requests

# Create your views here.
firebase = pyrebase_auth.initialize_app(config)
fb_auth = firebase.auth()


def index(request):
    return render(request, 'index.html')


def sign_up(request):
    email = request.POST.get('email')
    password = request.POST.get('pass')
    try:
        user = fb_auth.create_user_with_email_and_password(email, password)
        print('sign up user: {}'.format(user))
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
    id_token = request.session.get('uid')
    if id_token is None:
        message = '해당 서비스는 로그인이 필요합니다!'
        return render(request, 'index.html', {'message': message})

    app_name = settings.API_APP_NAME
    user = fb_admin_auth.get_user(fb_auth.get_account_info(id_token).get('users')[0].get('localId'))
    claims_of_user = user.custom_claims

    if claims_of_user is None:
        message = 'API 서비스를 이용할 권한이 없습니다.'
        return render(request, 'index.html', {'message': message})

    if claims_of_user.get(app_name) is None:
        message = 'API 서비스를 이용할 권한이 없습니다'
        return render(request, 'index.html', {'message': message})

    try:
        res = requests.get(
            url=settings.API_URL,
            headers={
                'authorization': 'JWT ' + id_token
            }
        )
        message = str(res.json())
    except Exception as e:
        print('Error: {}'.format(e))
        message = 'API 서버에 알 수 없는 오류가 발생했습니다. 다시 시도해주세요... ;('
    return render(request, 'index.html', {'message': message})


def create_claim(request):
    id_token = request.session.get('uid')
    if id_token is None:
        message = '해당 서비스는 로그인이 필요합니다!'
        return render(request, 'index.html', {'message': message})

    user = fb_admin_auth.get_user(fb_auth.get_account_info(id_token).get('users')[0].get('localId'))
    app_name = settings.API_APP_NAME

    try:
        claims_of_user = user.custom_claims
        if claims_of_user.get(app_name):
            message = '이미 부여된 권한입니다.'
            return render(request, 'index.html', {'message': message})
    except:
        pass

    uid = user.uid
    claim = {
        'smbot': True
    }

    fb_admin_auth.set_custom_user_claims(uid, claim)
    message = 'API 서비스 이용 권한을 생성했습니다. 다시 로그인 해주세요.'
    auth.logout(request)
    return render(request, 'index.html', {'message': message})

from django.shortcuts import render
from smauth.lib import user_claim_update
from smauth.lib.decorations import requires_login, requires_admin
from django.conf import settings
from django.contrib import auth
from firebase_admin import auth as fb_admin_auth
from datetime import datetime
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
        id_token = ''

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
    return render(request, 'index.html', {'message': message, 'token_info': id_token})


@requires_login
def create_claim(request):
    id_token = request.session.get('uid')
    user = fb_admin_auth.get_user(fb_auth.get_account_info(id_token).get('users')[0].get('localId'))
    app_name = settings.API_APP_NAME

    try:
        claims_of_user = user.custom_claims
        if claims_of_user.get(app_name):
            message = '이미 부여된 권한입니다.'
            return render(request, 'index.html', {'message': message})
    except:
        pass

    user_claim_update.claim_update(user, app_name, True)
    message = 'API 서비스 이용 권한을 생성했습니다. 다시 로그인 해주세요.'
    auth.logout(request)
    return render(request, 'index.html', {'message': message})


@requires_login
def delete_claim(request):
    id_token = request.session.get('uid')
    user = fb_admin_auth.get_user(fb_auth.get_account_info(id_token).get('users')[0].get('localId'))
    app_name = settings.API_APP_NAME

    try:
        claims_of_user = user.custom_claims
        if claims_of_user.get(app_name):
            user_claim_update.claim_update(user, app_name, False)
            message = 'API 서비스 이용 권한을 제거했습니다. 다시 로그인 해주세요.'
            auth.logout(request)
            return render(request, 'index.html', {'message': message})
    except:
        pass
    message = '존재하지않는 권한입니다.'
    return render(request, 'index.html', {'message': message})


@requires_admin
def admin_dashboard(request):
    key = Users.objects.all()
    context = {'users': key}
    return render(request, 'dashboard.html', context)


@requires_admin
def auth_db_synchronization(request):
    for user in fb_admin_auth.list_users().iterate_all():
        str_claims = ''

        # 문자열로 부여된 권한을 표기
        claims = user.custom_claims
        if claims is not None:
            for claim, claim_exist in claims.items():
                if claim_exist:
                    str_claims += claim + ', '
            if len(str_claims) != 0:
                str_claims = str_claims[:-2]

        user_db = Users(
            uid=user.uid,
            email=user.email,
            email_verified=user.email_verified,
            password_hash=user.password_hash,
            password_salt=user.password_salt,
            phone_number=user.phone_number,
            photo_url=user.photo_url,
            provider_id=user.provider_id,
            display_name=user.display_name,
            disabled=user.disabled,
            claims=str_claims,
            last_sign_in_timestamp=datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp/1000),
            tokens_valid_after_timestamp=datetime.fromtimestamp(user.tokens_valid_after_timestamp/1000),
            creation_timestamp=datetime.fromtimestamp(user.user_metadata.creation_timestamp/1000)
        )
        user_db.save()
    key = Users.objects.all()
    context = {'users': key}
    return render(request, 'dashboard.html', context)

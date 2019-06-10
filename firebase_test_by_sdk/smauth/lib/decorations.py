from django.shortcuts import render
from firebase_admin.auth import get_user, verify_id_token
from django.contrib import auth
from requests.exceptions import HTTPError
import json


def requires_login(func):
    def wrapper(*args, **kwargs):
        if args[0].session.get('uid') is None:
            message = '해당 서비스는 로그인이 필요합니다!'
            return render(args[0], 'index.html', {'message': message})
        try:
            order = func(*args, **kwargs)
            return order
        except HTTPError as e:
            err = json.loads(e.strerror)
            if err['error']['message'] == 'TOKEN_EXPIRED':
                auth.logout(args[0])
                message = '세션 기간이 만료되었습니다. 다시 로그인해주세요.'
                return render(args[0], 'index.html', {'message': message})
            else:
                message = '알 수 없는 네트워크 에러입니다.'
                print(err)
                return render(args[0], 'index.html', {'message': message})
    return wrapper


def requires_admin(func):
    def wrapper(*args, **kwargs):
        id_token = args[0].session.get('uid')
        if id_token is None:
            message = '해당 서비스는 관리자 권한이 필요합니다!'
            return render(args[0], 'index.html', {'message': message})
        user = get_user(verify_id_token(id_token)['uid'])
        admin_claim = user.custom_claims.get('admin')
        if admin_claim is None:
            message = '해당 서비스는 관리자 권한이 필요합니다!'
            return render(args[0], 'index.html', {'message': message})
        if admin_claim is False:
            message = '해당 서비스는 관리자 권한이 필요합니다!'
            return render(args[0], 'index.html', {'message': message})
        order = func(*args, **kwargs)
        return order

    return wrapper

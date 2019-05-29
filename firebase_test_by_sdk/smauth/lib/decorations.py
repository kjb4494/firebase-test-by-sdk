from django.shortcuts import render
from django.conf import settings
from firebase_admin.auth import get_user


auth = settings.FIREBASE_CLIENT_AUTH


def requires_login(func):
    def wrapper(*args, **kwargs):
        if args[0].session.get('uid') is None:
            message = '해당 서비스는 로그인이 필요합니다!'
            return render(args[0], 'index.html', {'message': message})
        order = func(*args, **kwargs)
        return order

    return wrapper


def requires_admin(func):
    def wrapper(*args, **kwargs):
        id_token = args[0].session.get('uid')
        if id_token is None:
            message = '해당 서비스는 관리자 권한이 필요합니다!'
            return render(args[0], 'index.html', {'message': message})
        user = get_user(auth.get_account_info(id_token).get('users')[0].get('localId'))
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

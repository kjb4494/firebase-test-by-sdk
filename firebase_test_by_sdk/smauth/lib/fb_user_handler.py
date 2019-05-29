from firebase_admin import auth
from smauth.models import Users
from datetime import datetime


def fb_and_mydb_all_sync():
    for user in auth.list_users().iterate_all():
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
            last_sign_in_timestamp=datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000),
            tokens_valid_after_timestamp=datetime.fromtimestamp(user.tokens_valid_after_timestamp / 1000),
            creation_timestamp=datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000)
        )
        user_db.save()


def fb_user_delete(uid):
    auth.delete_user(uid)
    instance = Users.objects.get(uid=uid)
    instance.delete()


def fb_user_update(uid, email, password, display_name):
    auth.update_user(
        uid=uid,
        email=email,
        password=password,
        display_name=display_name
    )
    fb_and_mydb_all_sync()

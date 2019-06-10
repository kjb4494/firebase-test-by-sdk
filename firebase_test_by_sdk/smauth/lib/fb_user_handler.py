from firebase_admin import auth
from smauth.models import Users, Tokens
from smauth.lib import pyrebase
from datetime import datetime, timedelta
from config import config as fb_config

firebase = pyrebase.initialize_app(fb_config)
fb_db = firebase.database()


def _set_fb_user_default_claims(user):
    default_cliams = {
        'smbot': False,
        'admin': False
    }
    auth.set_custom_user_claims(user.uid, default_cliams)


def _get_to_string_fb_user_claims(user):
    str_claims = ''
    for claim, claim_exist in user.custom_claims.items():
        if claim_exist:
            str_claims += claim + ', '
    if len(str_claims) != 0:
        str_claims = str_claims[:-2]
    return str_claims


def _get_datetime_from_fb_timestamp(fb_timestamp):
    fb_timestamp_datetime = fb_timestamp
    if fb_timestamp is not None:
        fb_timestamp_datetime = datetime.fromtimestamp(fb_timestamp / 1000)
    return fb_timestamp_datetime


def _get_fb_timestamp_from_datetime(date_time):
    return int(date_time.timestamp() * 1000)


def get_fb_user_from_uid(uid):
    return auth.get_user(uid)


def fb_and_mydb_all_sync():
    for user in auth.list_users().iterate_all():
        fb_and_mydb_user_sync(user)


def fb_and_mydb_user_sync(user):
    claims_string = _get_to_string_fb_user_claims(user)
    user_db = Users(
        uid=user.uid,
        email=user.email,
        email_verified=user.email_verified,
        phone_number=user.phone_number,
        photo_url=user.photo_url,
        provider_id=user.provider_id,
        display_name=user.display_name,
        disabled=user.disabled,
        claims=claims_string,
        last_sign_in_timestamp=_get_datetime_from_fb_timestamp(user.user_metadata.last_sign_in_timestamp),
        tokens_valid_after_timestamp=_get_datetime_from_fb_timestamp(user.tokens_valid_after_timestamp),
        creation_timestamp=_get_datetime_from_fb_timestamp(user.user_metadata.creation_timestamp)
    )
    user_db.save()


def create_fb_user_with_email_and_password(email, password):
    auth.create_user(
        email=email,
        password=password
    )
    user = auth.get_user_by_email(email)
    _set_fb_user_default_claims(user)


def fb_user_update(uid, email, password, display_name):
    auth.update_user(
        uid=uid,
        email=email,
        password=password,
        display_name=display_name
    )
    fb_and_mydb_user_sync(auth.get_user(uid))


def fb_user_delete(uid):
    auth.delete_user(uid)
    instance = Users.objects.get(uid=uid)
    instance.delete()


def fb_user_claim_update(user, key, value):
    uid = user.uid
    claims = user.custom_claims
    if claims[key] == value:
        return False
    claims[key] = value
    auth.set_custom_user_claims(uid, claims)
    return True


def set_user_meta_data(uid, **kwargs):
    now = _get_fb_timestamp_from_datetime(datetime.now())
    data = {}
    for key, value in kwargs.items():
        data.update({
            key: value
        })
    data.update({
        'creation_timestamp': now
    })
    if kwargs.get('expiresIn') is not None:
        data.update({
            'expire': now + int(kwargs.get('expiresIn')) * 1000
        })
    fb_db.child('meta_data').child(uid).set(data)


def get_all_users_meta_data():
    return fb_db.child('meta_data').get().val()


def fb_and_mydb_token_sync_for_token_info_of_user(uid):
    token = fb_db.child('meta_data').child(uid).get().val()
    if token is None:
        return False
    token_db = Tokens(
        uid=uid,
        id_token=token.get('idToken'),
        refresh_token=token.get('refreshToken'),
        creation_timestamp=_get_datetime_from_fb_timestamp(token.get('creation_timestamp')),
        expire=_get_datetime_from_fb_timestamp(token.get('expire')),
        expire_in=token.get('expiresIn'),
        kind=token.get('kind')
    )
    token_db.save()
    return True


def revoke_refresh_token(uid):
    auth.revoke_refresh_tokens(uid)

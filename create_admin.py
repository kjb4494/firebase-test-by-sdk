
from firebase_admin import auth, initialize_app, credentials
from smauth.lib.user_claim_update import claim_update

cred = credentials.Certificate('firebase-adminsdk.json')
default_app = initialize_app(cred)


if __name__ == '__main__':
    uid = 'VYy6ejX4uQbiAEsOvURCKhVSI9E3'
    claim_update(auth.get_user(uid), 'admin', True)

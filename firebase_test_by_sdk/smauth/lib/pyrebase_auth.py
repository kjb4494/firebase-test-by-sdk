from requests.exceptions import HTTPError
from Crypto.PublicKey import RSA
import python_jwt as jwt
import requests
import datetime
import json


class Auth:
    """ Authentication Service """

    def __init__(self, api_key, requests, credentials):
        self.api_key = api_key
        self.requests = requests
        self.credentials = credentials

    def sign_in_with_email_and_password(self, email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()

    def create_custom_token(self, uid, additional_claims=None):
        service_account_email = self.credentials.service_account_email
        private_key = RSA.importKey(self.credentials._private_key_pkcs8_pem)
        payload = {
            "iss": service_account_email,
            "sub": service_account_email,
            "aud": "https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit",
            "uid": uid
        }
        if additional_claims:
            payload["claims"] = additional_claims
        exp = datetime.timedelta(minutes=60)
        return jwt.generate_jwt(payload, private_key, "RS256", exp)

    def sign_in_with_custom_token(self, token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"returnSecureToken": True, "token": token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()

    def refresh(self, refresh_token):
        request_ref = "https://securetoken.googleapis.com/v1/token?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"grantType": "refresh_token", "refreshToken": refresh_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        request_object_json = request_object.json()
        # handle weirdly formatted response
        user = {
            "userId": request_object_json["user_id"],
            "idToken": request_object_json["id_token"],
            "refreshToken": request_object_json["refresh_token"]
        }
        return user

    def get_account_info(self, id_token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()

    def send_email_verification(self, id_token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()

    def send_password_reset_email(self, email):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()

    def verify_password_reset_code(self, reset_code, new_password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/resetPassword?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"oobCode": reset_code, "newPassword": new_password})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()

    def create_user_with_email_and_password(self, email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={0}".format(
            self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()


def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        # raise detailed error message
        # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
        raise HTTPError(e, request_object.text)

from firebase_admin import auth


def claim_update(user, claim, value):
    uid = user.uid
    claims = user.custom_claims

    if claims is None:
        claims = {
            claim: value
        }
        auth.set_custom_user_claims(uid, claims)
        return

    if claims.get(claim) is None:
        claims.update({
            claim: value
        })
        auth.set_custom_user_claims(uid, claims)
        return

    claims[claim] = value
    auth.set_custom_user_claims(uid, claims)

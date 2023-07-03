from mozilla_django_oidc import auth


class OIDCAuthenticationBackend(auth.OIDCAuthenticationBackend):
    def create_user(self, claims):
        email = claims.get("email")
        user = self.UserModel.objects.create_user(email=email)

        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.save()

        return user

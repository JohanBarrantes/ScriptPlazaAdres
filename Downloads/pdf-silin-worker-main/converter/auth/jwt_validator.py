"""
AccessJWTValidator is used as middleware to
intercept requests and validate access token jwt
"""
import jwt
from typing import Any, Dict, Union

from django.conf import settings

from rest_framework import authentication, exceptions

from constants import (
    AuthorizationStr, InvalidBearerToken, Bearer,
    InvalidAuthenticationSchema, MissingToken, HS256,
    RS256, AlgJWTHeader, UnexpectedSigningMethod,
    EmptyString, VerifyAud, InvalidTokenSignature,
    ExpiredToken
)


class AccessJWTValidator(authentication.BaseAuthentication):

    # https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication
    # don't change input or return parameters
    # return (user,auth) accessible as request.user and request.auth
    def authenticate(self, request):
        token = self._get_bearer_token_from_request(request)
        claims = self._validate_token(token)
        claims['token'] = token
        return None, claims

    def _get_bearer_token_from_request(self, request) -> Union[str, None]:
        header = request.headers.get(AuthorizationStr, None)
        if header is None:
            raise exceptions.AuthenticationFailed(MissingToken)
        header_array = header.split()
        if len(header_array) != 2:
            raise exceptions.AuthenticationFailed(
                InvalidBearerToken
            )
        if header_array[0] != Bearer:
            raise exceptions.AuthenticationFailed(InvalidAuthenticationSchema)
        return header_array[1]

    def _validate_token(self, token: str) -> Dict[str, Any]:
        supported_algorithms = [HS256, RS256]
        header = jwt.get_unverified_header(token)
        algorithm = header.get(AlgJWTHeader, None)
        if algorithm not in supported_algorithms:
            raise exceptions.AuthenticationFailed(UnexpectedSigningMethod)

        key = EmptyString
        if algorithm == HS256:
            key = settings.ACCESS_SECRET
        elif algorithm == RS256:
            key = settings.PUBLIC_RSA

        try:
            return jwt.decode(token, key, algorithms=supported_algorithms, options={VerifyAud: False})
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed(InvalidTokenSignature)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(ExpiredToken)
        except (jwt.DecodeError, jwt.InvalidTokenError) as e:
            raise exceptions.AuthenticationFailed(f'invalid token: {e}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                f"unexpected error while decoding token: {e}"
            )

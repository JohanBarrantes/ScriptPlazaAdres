import requests

from constants import (
    ApplicationIdStr, ApplicationSecretStr, GrantTypeStr,
    ClientCredentialsStr, TokenStr, ClientCredentialsFlowManagerNullToken
)

from converter.exceptions import ClientCredentialsFlowError


class ClientCredentialsFlowManager:
    def __init__(
        self,
        url: str,
        app_id: str,
        app_secret: str
    ):
        self.url = url
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = None

    def refreshToken(self):
        try:
            response = requests.post(
                "{}/oauth/token".format(self.url),
                params={
                    ApplicationIdStr: self.app_id,
                    ApplicationSecretStr: self.app_secret,
                    GrantTypeStr: ClientCredentialsStr
                }
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ClientCredentialsFlowError(f"ClientCredentialsFlowManager.refreshToken failed: {e}")

        if response.status_code == 200:
            self.token = response.json().get(TokenStr, None)
            if self.token is None:
                raise ClientCredentialsFlowError(
                    ClientCredentialsFlowManagerNullToken
                )
            return

        raise ClientCredentialsFlowError(
            "ClientCredentialsFlowManager.refreshToken failed with status code: {}".format(response.status_code)
        )

    def getToken(self) -> str:
        return self.token

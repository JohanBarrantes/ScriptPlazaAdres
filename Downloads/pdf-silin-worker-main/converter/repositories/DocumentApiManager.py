import requests
import backoff
import uuid

from typing import Union

from converter.repositories.ClientCredentialsFlowManager import ClientCredentialsFlowManager
from converter.exceptions import DocumentApiError


from constants import (
    fileMetadata, taxDocumentTypeId,
    fileContent, sendSNSStr, documentIDStr,
    AuthorizationHeader,
    relatedSourceId as relatedSourceIdStr, templateStr,
    destinationsStr
)


class DocumentApiManager:
    def __init__(
        self,
        url: str,
        clientCredentialsApi: ClientCredentialsFlowManager = None
    ):
        """
        if clientCredentialsApi is different from None then all requests to
        docs-management-api will use a token generated from client credentials flow
        in auth2-silin-api (unless manually passing some token to the registerDocument method).

        if clientCredentialsApi is different from None, when 401 response happens,
        token will be refresh using m2m (machine to machine) credentials
        """
        self.url = url
        self.clientCredentialsApi = clientCredentialsApi
        self.token = None

    def registerDocument(
            self, file_metadata: str, template_name: str, tax_document_type_id: int = None,
            related_source_id: uuid.UUID = None, file_content: dict = None,
            send_SNS: bool = True, destinations: list = None, token: str = None) -> Union[str, None]:
        """
        registerDocument returns (document_id, status_code)
        If token is None, the token will then be created from ClientCredentialsFlowManager
        """
        @backoff.on_exception(
            backoff.expo,
            requests.exceptions.RequestException,
            max_tries=5,
            giveup=self._refreshToken
        )
        def _registerDocument(
                file_metadata: str, template_name: str, tax_document_type_id: int = None,
                related_source_id: uuid.UUID = None, file_content: dict = None,
                send_SNS: bool = True, destinations: list = None, token: str = None) -> Union[str, None]:
            if token is None and self.token is None:
                response = requests.Response()
                response.status_code = 401
                raise requests.exceptions.RequestException(response=response)
            token = token if token is not None else self.token
            params = {}
            params[fileMetadata] = file_metadata
            params[sendSNSStr] = send_SNS
            params[templateStr] = {
                templateStr: template_name
            }

            if tax_document_type_id is not None:
                params[taxDocumentTypeId] = int(tax_document_type_id)
            if related_source_id is not None:
                params[relatedSourceIdStr] = str(related_source_id)
            if file_content is not None:
                params[fileContent] = file_content
            if destinations is not None:
                params[destinationsStr] = destinations

            response = requests.post(
                "{}/docs".format(self.url),
                json=params,
                headers={
                    AuthorizationHeader: "Bearer {}".format(token)
                }
            )
            response.raise_for_status()

            if response.status_code == 201:
                return response.json().get(documentIDStr, None)

            raise requests.exceptions.RequestException(
                (
                    "DocumentApiManager.registerDocument failed with status code {} and message {}"
                    .format(response.status_code, response.text)
                ),
                response=response
            )

        try:
            return _registerDocument(
                file_metadata,
                template_name,
                tax_document_type_id,
                related_source_id,
                file_content,
                send_SNS,
                destinations,
                token
            )
        except requests.exceptions.RequestException as e:
            raise DocumentApiError("DocumentApiManager.registerDocument failed: {}".format(e.response.text))
        except Exception as e:
            raise DocumentApiError("DocumentApiManager.registerDocument failed: {}".format(e))

    def _refreshToken(self, e: requests.exceptions.RequestException) -> bool:
        """
        _refreshToken is used as giveup function for backoff library.
        give up if failed to retrieve token using client credentials flow or
        if passed token is expired
        """
        if e.response.status_code == 401:
            if self.clientCredentialsApi is not None:
                try:
                    self.clientCredentialsApi.refreshToken()
                    self.token = self.clientCredentialsApi.getToken()
                    return False
                except Exception:
                    return False
            return True
        return False

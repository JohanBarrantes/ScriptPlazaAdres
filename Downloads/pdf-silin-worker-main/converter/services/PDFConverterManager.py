import logging
from time import time
from shutil import rmtree, copy
from os import makedirs, system
from os.path import exists
from uuid import uuid1
from unidecode import unidecode
from shlex import quote

from constants import (
    EmptyString, relatedSourceId as relatedSourceIdStr
)

from converter.repositories.aws.S3Manager import S3Manager
from converter.services.TemplateManager import TemplateManager
from converter.repositories.DocumentApiManager import DocumentApiManager
from converter.exceptions import TemplateManagerError, DocumentApiError, PDFConverterManagerError

from constants import (
    S3Folder, Id as IdStr,
    temporal, pdfToBase64 as pdfToBase64Str,
    S3Destination as S3DestinationStr, fileType as fileTypeStr, bucketName as bucketNameStr,
    PDF, content as contentStr, loggerConfig, UTF8,
    NameStr
)

logging.basicConfig(format=loggerConfig)


class PDFConverterManager:
    def __init__(
        self,
        s3Manager: S3Manager,
        bucketName: str,
        downloadFolder: str,
        convertedFolder: str,
        barcodesFolder: str,
        documentApi: DocumentApiManager = None,
    ):
        self.s3Manager = s3Manager
        self.documentApi = documentApi
        self.bucketName = bucketName
        self.downloadFolder = downloadFolder
        self.convertedFolder = convertedFolder
        self.barcodesFolder = barcodesFolder

    def process(
            self, templateName: str, contents=[],
            uploadS3: bool = True, s3Folder: str = S3Folder, convertBase64: bool = False,
            registerDocument: bool = True, token: str = None,
            sendSNS: bool = True, tax_document_type_id: int = None, destinations: list = None) -> list:
        """
        process expects a list of dicts in the contents param.
        Each of these dicts follows the format:
            {
                "name": "", (optional)
                "related_source_id": UUID, (optional)
                "content": {
                    ....
                }
            }
        process returns a list of dicts following the format:
            {
                "id": "convertedFileID",
                "name": "convertedFileName",
                "pdf_to_base64": "pdfBase64",
                "S3Destination": "s3Destination",
                "file_type": "pdf",
                "bucket_name": "self.bucketName",
            }
        Parameter token is the needed access jwt to communicate with docs-management-api and
        register the document. If token is None, pdf-worker will create his own token using
        client credentials flow
        """
        try:
            if len(contents) == 1:
                templateNameID = contents[0].get(NameStr, str(uuid1()))
            else:
                templateNameID = str(uuid1())

            templateNameID = unidecode(templateNameID)

            results = []
            filePathsToRemove = []

            templateFilepath = self._downloadTemplate(templateName, templateNameID)
            filePathsToRemove.append(templateFilepath)

            templateManager = TemplateManager(templateFilepath, self.barcodesFolder)

            for content in contents:
                self._processContent(
                    templateManager,
                    templateName,
                    results,
                    filePathsToRemove,
                    content,
                    uploadS3,
                    s3Folder,
                    convertBase64,
                    registerDocument,
                    token,
                    tax_document_type_id,
                    sendSNS,
                    destinations
                )
            return results
        except Exception as e:
            import traceback
            logging.log(
                logging.ERROR,
                f"PdfConverterManager.process with errors: {str(traceback.format_exc())}",
            )
            raise e
        finally:
            self.clearFiles(filePathsToRemove)

    def convertFileToPDF(
            self, docxFilepath: str, pdfFilepath: str,
            fileID: str = None):

        docx_path_quoted = quote(docxFilepath)
        pdf_path_quoted = quote(pdfFilepath)

        cmd = f"unoconvert --convert-to pdf {docx_path_quoted} {pdf_path_quoted}"
        try:
            system(cmd)
        except Exception as e:
            raise PDFConverterManagerError(
                f"PDFConverterManager.convertFileToPDF ({fileID}) Error trying to convert the file: {e}"
            )

    def clearFiles(self, paths):
        from os import remove
        for path in paths:
            try:
                remove(path)
            except Exception:
                pass

    def cleanDownloadFolder(self, initTime: float) -> float:
        """
        delete temporal files from download folder each hour
        """
        try:
            timeInterval = time() - initTime
            if (timeInterval / 3600) > 1:
                rmtree(f"{self.downloadFolder}{temporal}")
                return time()
        except Exception:
            pass

    def pdfToBase64(self, file):
        from base64 import b64encode
        with open(file, "rb") as file:
            return str(b64encode(file.read()), UTF8)

    def _processContent(
            self, templateManager: TemplateManager, templateName: str,
            results=[], filePathsToRemove=[], content: dict = {},
            uploadS3: bool = True, s3Folder: str = S3Folder,
            convertBase64: bool = False, registerDocument: bool = True, token: str = None,
            tax_document_type_id: int = None, send_SNS: bool = True,
            destinations: list = None):
        try:
            document_id = None
            convertedFileName = unidecode(content.get(NameStr, str(uuid1())))
            s3Destination = EmptyString
            pdfBase64 = EmptyString

            docxFilepath = f"{self.convertedFolder}{convertedFileName}.docx"
            self._generateDocxDocument(templateManager, docxFilepath, convertedFileName, content)
            filePathsToRemove.append(docxFilepath)

            pdfFilepath = f"{self.convertedFolder}{convertedFileName}.pdf"
            self.convertFileToPDF(docxFilepath, pdfFilepath, convertedFileName)
            filePathsToRemove.extend(templateManager.getBarcodesPaths())
            filePathsToRemove.append(pdfFilepath)

            if uploadS3:
                s3Destination = f"{s3Folder}{convertedFileName}.pdf"
                self.s3Manager.uploadS3File(
                    pdfFilepath,
                    self.bucketName,
                    s3Destination
                )

            if convertBase64:
                pdfBase64 = self.pdfToBase64(pdfFilepath)
        
            if registerDocument:
                document_id = self.documentApi.registerDocument(
                    token=token,
                    template_name=templateName,
                    file_metadata=s3Destination,
                    tax_document_type_id=tax_document_type_id,
                    related_source_id=content.get(relatedSourceIdStr, None),
                    file_content=content.get(contentStr, None),
                    send_SNS=send_SNS,
                    destinations=destinations
                )
                if document_id is None:
                    raise DocumentApiError(
                        f"id was not generated for document {s3Destination}"
                    )
        except Exception as e:
            raise e
        finally:
            results.append({
                IdStr: document_id if document_id is not None else convertedFileName,
                NameStr: convertedFileName,
                pdfToBase64Str: pdfBase64,
                S3DestinationStr: s3Destination,
                fileTypeStr: PDF,
                bucketNameStr: self.bucketName,
            })

    def _downloadTemplate(self, templateName: str, templateNameId: str) -> str:
        originalTemplateFilePath = f"{self.downloadFolder}{temporal}/{templateName}"
        templateFilepath = f"{self.downloadFolder}{templateNameId}.docx"
        if not exists(originalTemplateFilePath):
            originalTemplatePath = originalTemplateFilePath.split("/")
            originalTemplatePath = "/".join(originalTemplatePath[:-1])
            makedirs(originalTemplatePath, exist_ok=True)
            self.s3Manager.downloadS3File(
                self.bucketName, templateName, originalTemplateFilePath
            )
        templateFilepath = copy(originalTemplateFilePath, templateFilepath)
        return templateFilepath

    def _generateDocxDocument(
            self, templateManager: TemplateManager, path: str,
            fileID: str, file: dict):
        try:
            templateManager.generateDocument(
                file.get(contentStr, {}), path
            )
        except Exception as e:
            raise TemplateManagerError(
                f"templateManager.generateDocument ({fileID}): generateDocument: {e}"
            )

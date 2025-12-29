# Package constants.

# Empty strings
EmptyString = ""
EmptyStringDiff = ''
DotString = "."

# Data types
DataTypeStr = "DataType"
Binary = "Binary"
BinaryValue = "BinaryValue"
String = "String"
StringValue = "StringValue"

# Extensions
PDF = "pdf"

# Encoding
UTF8 = "utf-8"

# boolean
trueStr = "True"
falseStr = "False"

# Params
Id = "id"
NameStr = "name"
Document = "document"
DocumentType = "document_type"
fileMetadata = "file_metadata"
sendSNSStr = "send_SNS"
taxDocumentTypeId = "tax_document_type_id"
relatedSourceId = "related_source_id"
fileContent = "file_content"
pdfToBase64 = "pdf_to_base64"
S3Destination = "S3Destination"
fileType = "file_type"
bucketName = "bucket_name"
content = "content"
contentsStr = "contents"
destinationsStr = "destinations"
templateName = "template_name"
contextStr = "context"
templateStr = "template"
queueNameStr = "queue_name"
subFolderStr = "subfolder"
traceParentStr = "Traceparent"
contributorStr = "contributor"
documentNumberStr = "document_number"
governmentEntityStr = "government_entity"
pathStr = "path"
filenameStr = "filename"
contextDataStr = "context_data"
filesStr = "files"
registerDocumentStr = "register_document"
documentIDStr = "document_id"
TokenStr = "token"

# Headers
AuthorizationHeader = "Authorization"

# Status
StatusCodeStr = "status_code"

# Folders
S3Folder = "/pdf"
temporal = "temporal"

# AWS SQS errors
SQSGetClientError = "SQSManager.getClient: Could not get SQS Client"
SQSSendMessageInvalidContent = "SQSManager.sendSqsMessage: Invalid Message Contents"
SQSSendMessageUnsupportedOperation = "SQSManager.sendSqsMessage: Unsupported Operation"
SQSReceiveMessageOverLimit = "SQSManager.receiveSqsMessage: Over Limit"
SQSDeleteMessageInvalidFormat = "SQSManager.deleteSqsMessage: Invalid Format"
SQSDeleteMessageInvalidReceiptHandle = "SQSManager.deleteSqsMessage: Receipt Handle Is Invalid"

# AWS SQS Attributes
QueueUrl = "QueueUrl"
responseMetadata = "ResponseMetadata"
httpStatusCode = "HTTPStatusCode"
messagesStr = "Messages"
messageIdStr = "MessageId"
processedStr = "processed"
attributesStr = "attributes"
receiptHandleStr = "ReceiptHandle"
MessageattributesStr = "MessageAttributes"
bodyStr = "body"
bodyUppercaseStr = "Body"

# S3 errors
S3GetClientError = "S3Manager.getClient: Could not get S3 Client"
S3GetResourceError = "S3Manager.getResource: Could not get S3 Resource"

# DocumentAPI errors
DocumentApiRegisterError = "DocumentApiManager.registerDocument failed"

# Redis errors
RedisGetClientError = "RedisManager.getClient: Could not get Redis Client"

# Logger config
loggerConfig = "[%(process)s] %(processName)s: %(message)s"

# SQS worker
SQSWorkerName = "SQSWorkerManager"

# Timestamps
DDMMYY = "%d%m%Y"

# Notifications
temporalFilesRemovedStr = "Temporal files has been removed."

# Exceptions errors
DocumentApiErrorStr = "docs-management-api unavailable"
ClientCredentialsFlowErrorStr = "auth2-silin-api unavailable"
PDFConverterManagerErrorStr = "pdf conversion error"
TemplateManagerErrorStr = "template error"
DocumentApiNullToken = "Could not retrieve token. Must pass token or instantiate clientCredentialsApi in parent class"

# Parse errors
InvalidBooleanStr = "invalid boolean"

# Client credentials flow
ApplicationIdStr = "application_id"
ApplicationSecretStr = "application_secret"
GrantTypeStr = "grant_type"
ClientCredentialsStr = "client_credentials"
ClientCredentialsFlowManagerNullToken = "ClientCredentialsFlowManager.refreshToken got None Token"

# JWT
AuthorizationStr = "authorization"
InvalidBearerToken = "invalid bearer token syntax"
Bearer = "Bearer"
InvalidAuthenticationSchema = "invalid authentication schema"
MissingToken = "missing token"
HS256 = "HS256"
RS256 = "RS256"
AlgJWTHeader = "alg"
UnexpectedSigningMethod = "unexpected signing method"
ExpiredToken = "expired token"

# Pyjwt options
VerifyAud = "verify_aud"
InvalidTokenSignature = "invalid token signature"

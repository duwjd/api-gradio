from api.modules.schema import BaseConfigModel


class ReqUploadS3PresignedUrl(BaseConfigModel):
    mimeType: str
    s3Path: str


class ResUploadS3PresignedUrl(BaseConfigModel):
    uploadUrl: str
    headers: dict


class ReqDownloadS3PresignedUrl(BaseConfigModel):
    s3Path: str


class ResDownloadS3PresignedUrl(BaseConfigModel):
    presignedUrl: str | None

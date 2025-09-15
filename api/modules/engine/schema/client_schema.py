from typing import Optional, List
from PIL import Image
from pydantic import ConfigDict, Field

from api.modules.schema import BaseConfigModel


class ReqClientDocumentParser(BaseConfigModel):
    user_id: int
    project_id: int
    analysis_code: str
    env: str
    document_s3_key: str
    upload_s3_key: str
    pages: list
    api_endpoint: str


class ResClientDocumentParser(BaseConfigModel):
    images: List[str]
    extracted_images: List[str]


class ReqClientMaskImage(BaseConfigModel):
    user_id: int
    project_id: int
    analysis_code: str
    env: str
    document_s3_key: str
    upload_s3_key: str
    upload_folder: Optional[str] = ""
    api_endpoint: str


class ResClientMaskImage(BaseConfigModel):
    mask_image: str


class ReqClientInsertAnythingImage(BaseConfigModel):
    user_id: int
    project_id: int
    analysis_code: str
    env: str
    upload_s3_key: str
    upload_folder: Optional[str] = ""
    source_image_path: str
    source_mask_path: str
    reference_image_path: str
    reference_mask_path: str
    api_endpoint: str


class ResClientInsertAnythingImage(BaseConfigModel):
    image: str


class ReqClientRelight(BaseConfigModel):
    user_id: int
    project_id: int
    analysis_code: str
    env: str
    upload_s3_key: str
    upload_folder: Optional[str] = ""
    source_image_path: str
    target_image_path: str
    num_sampling_step: int = Field(default=1)
    api_endpoint: str


class ResClientRelight(BaseConfigModel):
    image: str


class ReqClientFramePack(BaseConfigModel):
    user_id: int
    project_id: int
    analysis_code: str
    env: str
    document_s3_key: str
    upload_s3_key: str
    upload_folder: Optional[str] = ""
    prompt: str = Field(
        default="""A stationary car with the camera slowly rotating around it from a 180 to 270-degree arc, capturing different angles and details of the car's exterior. The environment remains consistent with the original scene. The camera movement is smooth and cinematic, focusing on presenting the car's design in a clear and visually appealing way."""
    )

    api_endpoint: str


class ResClientFramePack(BaseConfigModel):
    video: str


class ModelInputSchema(BaseConfigModel):
    frames_per_second: int = Field(default=16, ge=1, le=60, alias="framesPerSecond")
    guidance_scale: float = Field(default=1.0, ge=1.0, le=10, alias="guidanceScale")
    image: Optional[Image.Image] = Field(default=None)
    max_area: int = Field(
        default=720 * 1280,
        alias="maxArea",  # 480 * 832 for 480p, 720 * 1280 for 720p
    )
    negative_prompt: str = Field(
        default=(
            "Bright tones, overexposed, static,"
            " blurred details, subtitles, style, works, paintings,"
            " images, static, overall gray, worst quality, low quality,"
            " JPEG compression residue, ugly, incomplete, extra fingers,"
            " poorly drawn hands, poorly drawn faces, deformed, disfigured,"
            " misshapen limbs, fused fingers, still picture, messy background,"
            " three legs, many people in the background, walking backwards, shaking"
        ),
        alias="negativePrompt",
    )
    num_inference_steps: int = Field(default=8, ge=8, le=50, alias="numInferenceSteps")
    prompt: str = Field(
        default=(
            "A sleek modern car driving slowly and smoothly forward, "
            "with a cinematic presentation style. The camera follows "
            "the car at a steady pace, showcasing its elegant design "
            "and motion. The car moves at a moderate speed"
        ),
        alias="prompt",
    )
    seed: int = Field(default=0, ge=0, le=2**32 - 1, alias="seed")
    shift: int = Field(default=8.0, ge=1.0, le=10.0, alias="shift")  # not used
    total_second_length: int = Field(default=5, ge=1, le=10, alias="totalSecondLength")
    # Configuration that allows PIL image object
    model_config = ConfigDict(
        extra="forbid",  # 모든 모델에서 추가 필드 금지
        arbitrary_types_allowed=True,  # 임의의 타입 허용
    )


class ReqClientWan(BaseConfigModel):
    userId: int
    projectId: int
    analysisCode: str
    env: str
    documentS3Key: str
    orderNo: Optional[int] = None
    uploadS3Key: str
    modelInput: ModelInputSchema = Field(default_factory=lambda: ModelInputSchema())


class ResClientWan(BaseConfigModel):
    video: str


class ReqClientLtx(BaseConfigModel):
    user_id: int
    project_id: int
    analysis_code: str
    env: str
    document_s3_key: str
    upload_s3_key: str
    upload_folder: Optional[str] = ""
    prompt: str = Field(
        default="""A stationary car with the camera slowly rotating around it from a 180 to 270-degree arc, capturing different angles and details of the car's exterior. The environment remains consistent with the original scene. The camera movement is smooth and cinematic, focusing on presenting the car's design in a clear and visually appealing way."""
    )

    api_endpoint: str


class ResClientLtx(BaseConfigModel):
    video: str


class ResponseError(BaseConfigModel):
    error: str

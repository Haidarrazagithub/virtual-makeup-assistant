from fastapi import HTTPException, UploadFile

from app.core.settings import settings


class ImageValidator:
    """
    Validates uploaded image files.
    """

    @staticmethod
    async def validate(image: UploadFile) -> None:
        """
        Validate uploaded image.

        Raises:
            HTTPException: If validation fails.
        """

        # Validate content type
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image format."
            )

        # Read uploaded bytes
        file_bytes = await image.read()

        # Empty file
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # Maximum file size
        if len(file_bytes) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Image exceeds maximum allowed size."
            )

        # Reset pointer for next service
        await image.seek(0)

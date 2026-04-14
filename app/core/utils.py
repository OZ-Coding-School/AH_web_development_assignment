import os
import re
from typing import Optional

from fastapi import HTTPException, status

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def validate_image_extension(filename: Optional[str]) -> str:
    """
    Check if the file extension is allowed.
    Returns the extension if valid, otherwise raises HTTPException.
    """
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="파일명이 비어있습니다.")

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않는 파일 형식입니다. (허용되는 형식: {', '.join(ALLOWED_IMAGE_EXTENSIONS)})",
        )

    return ext


def validate_chart_number(chart_number: str) -> None:
    """
    Check if the chart number format is valid (YYYYMMDD-XXXX).
    YYYYMMDD: 8 digits for date
    XXXX: 4 digits for sequence number
    """
    pattern = r"^\d{8}-\d{4}$"
    if not re.match(pattern, chart_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 차트 번호 형식입니다. (예: 20260101-9231)",
        )

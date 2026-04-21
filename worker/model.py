from typing import Any, Optional, Self

import torch
from torchvision import transforms  # type: ignore
from PIL import Image
import torch.nn as nn
from torch.nn import functional as F
import logging

# 로거 설정
logger = logging.getLogger(__name__)

MODEL_PATHS = {"pneumonia_model_v1": "worker/models/pneumonia_model.pth"}


class SimpleCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(nn.Flatten(), nn.Linear(32 * 32 * 32, 2))

    def forward(self, x):
        return self.fc(self.conv(x))


class PneumoniaPredictModel:
    def __init__(self, model_name: str) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = MODEL_PATHS.get(model_name, "worker/models/pneumonia_model.pth")
        self.model: Optional[nn.Module] = None
        self.transform = transforms.Compose(
            [transforms.Grayscale(), transforms.Resize((128, 128)), transforms.ToTensor()]
        )

    def load(self) -> Self:
        logger.info(f"Loading pneumonia prediction model on {self.device}...")
        self.model = SimpleCNN().to(self.device)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.eval()
        logger.info("Pneumonia prediction model loaded successfully.")
        return self

    def predict(self, img_path: str) -> dict[str, Any]:
        # 모델이 로드되어 있지 않으면 런타임 에러 발생
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # 이미지 가져오기 및 변환
        try:
            image = Image.open(img_path).convert("L")
            image = self.transform(image).unsqueeze(0).to(self.device)
        except Exception as e:
            logger.error(f"Invalid image: {e}")
            raise

        # 모델 inference
        with torch.no_grad():
            output = self.model(image)
            probs = F.softmax(output, dim=1)
            pred = probs.argmax(dim=1).item()
            confidence = probs.max().item()

        # 추론 결과 리턴
        return {"label": "Pneumonia" if pred == 1 else "Normal", "confidence": confidence}

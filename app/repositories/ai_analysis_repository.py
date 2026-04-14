from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.ai_analysis_results import AIAnalysis


class AIAnalysisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, ai_analysis: AIAnalysis) -> AIAnalysis:
        self.db.add(ai_analysis)
        await self.db.commit()
        await self.db.refresh(ai_analysis)
        return ai_analysis

    async def get_by_record_id_and_model(self, record_id: int, ai_model: str) -> Optional[AIAnalysis]:
        result = await self.db.execute(
            select(AIAnalysis).where(AIAnalysis.record_id == record_id, AIAnalysis.ai_model == ai_model)
        )
        return result.scalars().first()

    async def get_list_by_record_id(self, record_id: int) -> Sequence[AIAnalysis]:
        result = await self.db.execute(
            select(AIAnalysis).where(AIAnalysis.record_id == record_id).order_by(AIAnalysis.created_at.desc())
        )
        return result.scalars().all()

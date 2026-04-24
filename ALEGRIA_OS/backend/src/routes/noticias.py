from fastapi import APIRouter, Query
from src.services.news_service import service as news_service

router = APIRouter(tags=["noticias"])

@router.get("/dashboard")
async def get_news_dashboard(category: str = Query("general")):
    """
    Retorna datos de noticias y clima en tiempo real.
    """
    return await news_service.get_dashboard_data(category)

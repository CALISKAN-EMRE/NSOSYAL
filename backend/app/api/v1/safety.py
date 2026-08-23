from fastapi import APIRouter, Request
from app.models.safety import SafetyAnalysisRequest, SafetyAnalysisResponse

router = APIRouter(prefix="/safety", tags=["Safety & Moderation"])


@router.post("/analyze", response_model=SafetyAnalysisResponse)
def analyze_safety(request: Request, payload: SafetyAnalysisRequest):
    safety_service = request.app.state.safety_service
    adapter = request.app.state.data_adapter
    existing_posts = adapter.get_posts(limit=100) if adapter else []
    return safety_service.analyze_text(request=payload, existing_posts=existing_posts)

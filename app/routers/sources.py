from fastapi import APIRouter

from app.schemas import SourceStatusOut
from app.services.source_status import get_all

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get(
    "/status",
    response_model=list[SourceStatusOut],
    summary="Status das fontes de dados",
    description=(
        "Retorna o estado atual de cada fonte de dados integrada: "
        "se a última coleta foi bem-sucedida, quando ocorreu e qual erro foi retornado caso tenha falhado. "
        "Permite identificar quais fontes estão operacionais e quais apresentaram falha no último ciclo."
    ),
)
def sources_status():
    return [
        SourceStatusOut(
            source=s.source,
            is_healthy=s.is_healthy,
            last_attempt=s.last_attempt,
            last_success=s.last_success,
            last_error=s.last_error,
        )
        for s in get_all()
    ]

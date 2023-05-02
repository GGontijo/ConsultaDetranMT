from fastapi import APIRouter, status
from models.response_models import *
from repositories.veiculo_consulta import VeiculoConsulta

detran_router = APIRouter()

@detran_router.get("/consulta", responses={200: {"model": VeiculoConsultaSuccess}, 422: {"model": VeiculoConsultaError}})
def consultar(placa: str, renavam: int) -> str:
    consulta = VeiculoConsulta()
    response = consulta.consulta_detran(placa, renavam)
    if not response.success:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    
    return response
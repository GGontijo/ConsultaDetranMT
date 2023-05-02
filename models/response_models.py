from pydantic import BaseModel

class VeiculoConsultaSuccess(BaseModel):
    
    Multa_Autuacao_Pendente: str | None
    dados_veiculos: str | None
    dados_multas_aberto: str | None
    dados_autuacoes_aberto: str | None
    dados_historico_multas: str | None
    dados_multas_conveniadas: str | None
    dados_recursos: str | None
    dados_recall: str | None
    dados_impedimentos: str | None
    success: bool | None

class VeiculoConsultaError(BaseModel):
    resultado: str | None
    detalhes: str | None
    status_code: int | None
    success: bool | None

# Consulta Detran MT

Consulta automatizada de dados de veículos no portal do Detran.

## Dependências

Para rodar esse projeto, você vai precisar das seguintes bibliotecas para Python:

`Selenium` -> Usado para acessar a página do Detran e coletar o HTML.

`FastAPI` -> Usado para a estruturação da FastAPI.

`Uvicorn` -> Usado para rodar o servidor da API.

`Pydantic` -> Usado para auxiliar nos modelos bases.

`BeautifulSoup` -> Usado para instanciar um objeto HTML manipulável.

`lxml` -> Usado para desacoplar os frames da estruturação principal e encontrar o frame por XPath

#### Para instalar todas as Dependências:

```
  pip install -r requirements.txt
```
## Documentação da API

#### Consultar veículo

```http
  GET /consulta
```

| Parâmetro   | Tipo       | Descrição                           |
| :---------- | :--------- | :---------------------------------- |
| `placa` | `string` | **Obrigatório**. Placa do Veículo |
| `renavam` | `string` | **Obrigatório**. Renavam do Veículo |

#### Response: Sucesso (200)

```
  {
  "Multa_Autuacao_Pendente": "bool",
  "dados_veiculos": "string",
  "dados_multas_aberto": "string",
  "dados_autuacoes_aberto": "string",
  "dados_historico_multas": "string",
  "dados_multas_conveniadas": "string",
  "dados_recursos": "string",
  "dados_recall": "string",
  "dados_impedimentos": "string",
  "success": "bool"
  }
```

#### Response: Veículo Não Encontrado (422)

```
  {
  "resultado": "string",
  "detalhes": "string",
  "status_code": "int",
  "success": "bool"
  }
```
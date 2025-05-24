# Sistema de Gerenciamento de Boletos

Sistema web desenvolvido com FastAPI (backend) e React (frontend) para gerenciamento de boletos, permitindo importação em lote e controle de acesso por usuário.

## Funcionalidades

- Autenticação e autorização de usuários
- Importação de boletos via CSV
- Visualização e download de boletos em PDF
- Filtros por empresa, status e data
- Observações e histórico por boleto
- Painel administrativo
- Controle de acesso baseado em roles (admin/user)

## Tecnologias Utilizadas

- Backend:
  - FastAPI
  - SQLAlchemy
  - PostgreSQL
  - Pydantic
  - Python 3.8+

- Frontend:
  - React
  - Material-UI
  - Axios
  - React Query

## Configuração do Ambiente

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_REPOSITORIO]
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Crie um arquivo `.env` na raiz do projeto
- Copie o conteúdo de `.env.example` e ajuste as variáveis

5. Execute as migrações do banco de dados:
```bash
python app/scripts/migrate_add_empresa_observacao.py
```

6. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

## Estrutura do Projeto

```
app/
├── api/            # Rotas e endpoints
├── core/           # Configurações centrais
├── crud/          # Operações de banco de dados
├── models/        # Modelos SQLAlchemy
├── schemas/       # Schemas Pydantic
├── scripts/       # Scripts de utilidade
└── tests/         # Testes
```

## Documentação da API

Após iniciar o servidor, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 
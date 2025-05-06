# planeja-pdf-ai-backend

Esse é o backend da implementação do assistente de inteligência artificial utilizado no projeto planeja-pdf.
O projeto utiliza como base a API do Gemini para a conversação.

Para instalar o projeto, siga os comandos abaixo:

* Instale o uv
[https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
* Instale o Docker (preferencialmente Docker Desktop, que já inclui o docker-compose) [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

Crie o ambiente virtual  
`
uv venv .venv
`

Ative o ambiente  

``` shell
source .venv/bin/activate # Linux/MacOS
# ou
.\venv\Scripts\activate # Windows
```

Instale as dependências
``` shell
uv pip install -r requirements.txt
```

Configure as credenciais no .env (chave da API do Gemini, usuário, senha e URL do banco)
``` shell
GEMINI_API_KEY={sua_chave_aqui}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/planeja-pdf-ai-backend
POSTGRES_USER={usuario_do_banco}
POSTGRES_PASSWORD={senha_do_banco}
```

Rode o container do banco PostgreSQL, na pasta raiz do repositório
``` shell
docker-compose up -d
```

Rode as migrações do Alembic

``` shell
alembic upgrade head
```

Para rodar o projeto localmente, utilize:

``` shell
fastapi dev app/main.py
```

Também é necessário colar uma chave com as credenciais utilzadas no banco de dados, seguindo esse formato aqui:

```
DATABASE_URL=postgresql://${username}:${password}@localhost:5432/planeja-pdf-ai-backend
```

Substitua **$username** e **$password** pelo usuário e senha do banco que você definiu no .env






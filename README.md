# planeja-pdf-ai-backend

Para instalar o projeto, siga os comandos abaixo:

* Instale o uv
[https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

Crie o ambiente virtual  
`
uv venv .venv
`

Ative o ambiente  

```
source .venv/bin/activate # Linux/MacOS
# ou
.\venv\Scripts\activate # Windows
```

Instale as dependências
```
uv pip install -r requirements.txt
```

Para rodar o projeto localmente, utilize:

```
fastapi dev main.py
```

Cole a chave da API do Gemini no .env

```
GEMINI_API_KEY={your_key_here}

```





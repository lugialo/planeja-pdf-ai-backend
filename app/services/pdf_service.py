from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import timedelta

# Configura o ambiente do Jinja2 para carregar templates da pasta 'app/templates'
env = Environment(loader=FileSystemLoader('app/templates/'))
template = env.get_template("budget_template.html")

def generate_budget_pdf(budget, customer, settings):
    """
    Gera um PDF de orçamento a partir de um template HTML e dados do banco.
    """
    # Prepara um dicionário com todos os dados para o template
    template_data = {
        "budget": budget,
        "customer": customer,
        "settings": settings,
        "timedelta": timedelta # Passa a função timedelta para o template
    }

    # Renderiza o template HTML com os dados
    html_out = template.render(template_data)

    # Converte o HTML renderizado para PDF em memória
    pdf_bytes = HTML(string=html_out).write_pdf()

    return pdf_bytes
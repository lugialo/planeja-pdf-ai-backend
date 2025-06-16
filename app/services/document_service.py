from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from docxtpl import DocxTemplate
from datetime import timedelta
import io
import pathlib 

SERVICE_DIR = pathlib.Path(__file__).resolve().parent

APP_DIR = SERVICE_DIR.parent

TEMPLATE_DIR = APP_DIR / "templates"


env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
pdf_template = env.get_template("budget_template.html")

def generate_budget_pdf(budget_data):
    """Gera um PDF de orçamento a partir dos dados processados."""
    html_out = pdf_template.render(budget_data)
    return HTML(string=html_out).write_pdf()


docx_template_path = TEMPLATE_DIR / "budget_template.docx"


def generate_budget_docx(budget_data):
    """Gera um DOCX de orçamento a partir dos dados processados."""
    # Carrega o template usando o caminho absoluto
    docx_template = DocxTemplate(docx_template_path)
    
    # Renderiza o template .docx com o contexto
    docx_template.render(budget_data)
    
    # Salva o documento em um buffer de bytes em memória
    file_stream = io.BytesIO()
    docx_template.save(file_stream)
    file_stream.seek(0)
    
    return file_stream.read()
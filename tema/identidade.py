"""
Dados institucionais e paleta do tema UFF (escuro).

Edite este arquivo para trocar textos, integrantes ou links.
Cores e estilos visuais ficam em assets/css/tema_uff.css e .streamlit/config.toml.
"""

# --------------------------------------------------
# Paleta (referência: "Manual de Aplicação do Logo da UFF")
# --------------------------------------------------
AZUL_UFF       = "#004f9f"   # Azul-UFF oficial: faixas do cabeçalho e do rodapé
AZUL_UFF_VIVO  = "#1a6cc4"   # derivado, mais claro: botões e controles sobre fundo escuro
AZUL_UFF_TEXTO = "#8fbdf0"   # derivado, para textos/links em azul sobre fundo escuro

# --------------------------------------------------
# Instituição
# --------------------------------------------------
UNIVERSIDADE = "Universidade Federal Fluminense"
UNIDADE      = "Escola de Engenharia"
ENDERECO     = "Reitoria da UFF – Rua Miguel de Frias, 9, Icaraí. Niterói – RJ – CEP 24220-900"

# --------------------------------------------------
# Trabalho
# --------------------------------------------------
TIPO_TRABALHO     = "Trabalho de Extensão"
DISCIPLINA        = "Instalações Elétricas"
CODIGO_DISCIPLINA = "TEE00198"
PERIODO           = "2026.2"
INTEGRANTES = [
    "Luiz Furlanetti",
    "João Victor C. Magalhães",
    "Tyrone Hentzy Stellet",
]

# --------------------------------------------------
# Links (rodapé de https://www.uff.br/)
# --------------------------------------------------
URL_UFF      = "https://www.uff.br/"
URL_EXTENSAO = "https://www.uff.br/extensao/o-que-e-a-extensao/"

REDES_SOCIAIS = [
    ("Instagram", "https://instagram.com/uffoficial"),
    ("Facebook",  "https://www.facebook.com/UFFOficial/"),
    ("X",         "https://x.com/uff_br"),
    ("LinkedIn",  "https://www.linkedin.com/school/30752/"),
    ("YouTube",   "https://www.youtube.com/@UFFoficial"),
    ("Telegram",  "https://t.me/uff_oficial"),
]

# --------------------------------------------------
# Tooltip do mapa (pydeck)
# --------------------------------------------------
ESTILO_TOOLTIP_MAPA = {
    "backgroundColor": AZUL_UFF,
    "color": "#ffffff",
    "fontFamily": "Barlow, Arial, sans-serif",
    "fontSize": "13px",
    "lineHeight": "1.45",
    "padding": "8px 12px",
    "borderRadius": "6px",
    "border": "1px solid rgba(255, 255, 255, 0.25)",
    "boxShadow": "0 6px 18px rgba(0, 0, 0, 0.5)",
}

"""
Componentes visuais do tema UFF: CSS, logos, cabeçalho e rodapé.

- Estilos: assets/css/tema_uff.css
- Logos:   assets/img/ (veja assets/img/LEIA-ME.md)
- Textos:  tema/identidade.py
"""
from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import streamlit as st

from tema import identidade as idt

_RAIZ = Path(__file__).resolve().parent.parent
_ARQUIVO_CSS = _RAIZ / "assets" / "css" / "tema_uff.css"
_PASTA_IMG = _RAIZ / "assets" / "img"

_EXTENSOES = (".svg", ".png", ".webp", ".jpg", ".jpeg")
_MIME = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

# Ícone oficial publicado no portal da UFF: usado só se não houver logo em assets/img/
_LOGO_UFF_PORTAL = "https://www.uff.br/wp-content/uploads/2024/06/cropped-favicon-270x270.png"


# --------------------------------------------------
# Logos
# --------------------------------------------------
def _procurar_imagem(nome_base: str) -> Path | None:
    for ext in _EXTENSOES:
        caminho = _PASTA_IMG / f"{nome_base}{ext}"
        if caminho.is_file():
            return caminho
    return None


_ARQ_LOGO_UFF = _procurar_imagem("logo_uff")
_ARQ_LOGO_ESCOLA = _procurar_imagem("logo_escola_engenharia")
_ARQ_ICONE_UFF = _procurar_imagem("icone_uff")  # símbolo quadrado: aba do navegador

# Aceito por st.set_page_config(page_icon=...) e st.logo(...)
LOGO_UFF: str = str(_ARQ_LOGO_UFF) if _ARQ_LOGO_UFF else _LOGO_UFF_PORTAL
ICONE_UFF: str = str(_ARQ_ICONE_UFF) if _ARQ_ICONE_UFF else _LOGO_UFF_PORTAL

# Versões brancas (negativo da marca) para a barra lateral escura
_ARQ_LOGO_UFF_BRANCO = _procurar_imagem("logo_uff_branco")
_ARQ_ICONE_UFF_BRANCO = _procurar_imagem("icone_uff_branco")
_LOGO_LATERAL = str(_ARQ_LOGO_UFF_BRANCO) if _ARQ_LOGO_UFF_BRANCO else LOGO_UFF
_ICONE_LATERAL = str(_ARQ_ICONE_UFF_BRANCO) if _ARQ_ICONE_UFF_BRANCO else ICONE_UFF


def _src_img(caminho: Path | None, reserva: str | None = None) -> str | None:
    """data URI do arquivo local (para usar dentro de <img>) ou a URL reserva."""
    if caminho is None:
        return reserva
    mime = _MIME.get(caminho.suffix.lower(), "image/png")
    dados = base64.b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{dados}"


# --------------------------------------------------
# Helpers de HTML
# --------------------------------------------------
def _link(texto: str, url: str, rotulo: str | None = None, classe: str = "") -> str:
    attr_classe = f' class="{classe}"' if classe else ""
    attr_rotulo = f' aria-label="{escape(rotulo)}"' if rotulo else ""
    return (
        f'<a{attr_classe} href="{escape(url)}" target="_blank" '
        f'rel="noopener noreferrer"{attr_rotulo}>{escape(texto)}</a>'
    )


def _img(src: str, alt: str) -> str:
    return f'<img src="{escape(src)}" alt="{escape(alt)}">'


# --------------------------------------------------
# API pública
# --------------------------------------------------
def aplicar_tema() -> None:
    """Carrega o CSS do tema e coloca o logo da UFF no canto superior esquerdo."""
    css = _ARQUIVO_CSS.read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")
    st.logo(_LOGO_LATERAL, link=idt.URL_UFF, size="large", icon_image=_ICONE_LATERAL)


def cabecalho(titulo: str, subtitulo: str) -> None:
    """Faixa Azul-UFF com logos, identificação da disciplina e título do app."""
    # UFF em placa branca (azul sobre branco, como no manual da marca);
    # Escola de Engenharia direto sobre a faixa azul (o logo tem detalhes brancos).
    marca_uff = (
        f'<a class="uff-marcas" href="{idt.URL_UFF}" target="_blank" rel="noopener noreferrer" '
        f'title="{escape(idt.UNIVERSIDADE)}">'
        f'{_img(_src_img(_ARQ_LOGO_UFF, _LOGO_UFF_PORTAL), f"Logotipo da {idt.UNIVERSIDADE}")}</a>'
    )
    src_escola = _src_img(_ARQ_LOGO_ESCOLA)
    marca_escola = (
        f'<span class="uff-marca-escola">{_img(src_escola, f"Logotipo da {idt.UNIDADE} da UFF")}</span>'
        if src_escola else ""
    )

    selos = [
        (idt.TIPO_TRABALHO, "uff-selo uff-selo--destaque"),
        (f"{idt.CODIGO_DISCIPLINA} · {idt.DISCIPLINA}", "uff-selo"),
        (f"Período {idt.PERIODO}", "uff-selo"),
    ]
    html_selos = "".join(f'<span class="{c}">{escape(t)}</span>' for t, c in selos)

    st.html(
        '<header class="uff-cabecalho">'
        f'<div class="uff-cabecalho__marcas">{marca_uff}{marca_escola}</div>'
        '<div class="uff-cabecalho__textos">'
        f'<div class="uff-cabecalho__instituicao">{escape(idt.UNIVERSIDADE)}'
        f'<span aria-hidden="true"> · </span>{escape(idt.UNIDADE)}</div>'
        f'<h1 class="uff-cabecalho__titulo">{escape(titulo)}</h1>'
        f'<div class="uff-cabecalho__subtitulo">{escape(subtitulo)}</div>'
        f'<div class="uff-selos">{html_selos}</div>'
        "</div>"
        "</header>"
    )


def rodape() -> None:
    """Rodapé institucional: UFF, dados do trabalho, equipe e redes oficiais."""
    integrantes = "".join(f"<li>{escape(n)}</li>" for n in idt.INTEGRANTES)
    redes = "".join(
        _link(nome, url, f"{nome} da UFF (abre em nova aba)", "uff-rodape__rede")
        for nome, url in idt.REDES_SOCIAIS
    )

    st.html(
        '<footer class="uff-rodape">'
        '<div class="uff-rodape__grade">'
        # Coluna 1: instituição
        '<section class="uff-rodape__coluna">'
        f'<div class="uff-rodape__nome">{escape(idt.UNIVERSIDADE)}</div>'
        f'<div class="uff-rodape__unidade">{escape(idt.UNIDADE)}</div>'
        f'<div class="uff-rodape__endereco">{escape(idt.ENDERECO)}</div>'
        "</section>"
        # Coluna 2: trabalho e equipe
        '<section class="uff-rodape__coluna">'
        f'<h2 class="uff-rodape__titulo">{escape(idt.TIPO_TRABALHO)}</h2>'
        f'<div class="uff-rodape__linha">{escape(idt.CODIGO_DISCIPLINA)} · '
        f"{escape(idt.DISCIPLINA)}</div>"
        f'<div class="uff-rodape__periodo">Período {escape(idt.PERIODO)}</div>'
        f'<ul class="uff-rodape__equipe" aria-label="Integrantes do grupo">{integrantes}</ul>'
        "</section>"
        # Coluna 3: redes
        '<nav class="uff-rodape__coluna" aria-label="Redes sociais da UFF">'
        '<h2 class="uff-rodape__titulo">UFF nas redes</h2>'
        f'<div class="uff-rodape__redes">{redes}</div>'
        "</nav>"
        "</div>"
        '<div class="uff-rodape__base">'
        '<div class="uff-rodape__links">'
        f"{_link('uff.br', idt.URL_UFF, 'Portal da UFF (abre em nova aba)')}"
        f"{_link('Extensão na UFF', idt.URL_EXTENSAO, 'Extensão na UFF (abre em nova aba)')}"
        "</div>"
        '<div class="uff-rodape__fonte">Dados: ABNT NBR 5419-2:2026, Anexo F · Malha municipal IBGE</div>'
        "</div>"
        "</footer>"
    )

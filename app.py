# Pesquisa de índice de Ng por cidade — SPDA
# Versão para GitHub / Streamlit Community Cloud (caminhos relativos ao repositório)
import streamlit as st
import pandas as pd
import pydeck as pdk
import geopandas as gpd
from pathlib import Path
from typing import Any, cast
import io
import unicodedata

st.set_page_config(layout="wide", page_title="Mapa Ng", page_icon=":material/thunderstorm:")

# Estilo opcional: se existir um style.py local (ex.: identidade visual UFF), aplica.
try:
    from style import apply_sidebar_style  # type: ignore
    apply_sidebar_style()
except ImportError:
    pass

# --------------------------------------------------
# Constantes (tudo relativo à pasta do app)
# --------------------------------------------------
BASE_DIR      = Path(__file__).parent
DATA_DIR      = BASE_DIR / "data"
CACHE_PARQUET = DATA_DIR / "ng_municipios_cache_2026.parquet"
ARQUIVO_CSV   = DATA_DIR / "ng_municipios.csv"
ARQUIVO_SHP   = DATA_DIR / "BR_Municipios_2024.shp"   # só usado localmente para regerar o cache

LABELS_NG = ["Muito baixo (mínimo local)", "Baixo", "Médio", "Alto", "Muito alto (máximo local)"]
CORES_NG = {
    "Muito baixo (mínimo local)":  [20,   55,  125, 160],
    "Baixo":                       [70,  115,  175, 170],
    "Médio":                       [140, 165,  140, 180],
    "Alto":                        [220, 200,   70, 190],
    "Muito alto (máximo local)":   [255, 235,    0, 200],
}

# --------------------------------------------------
# Carregamento de dados
# --------------------------------------------------
def _chave(nome: str) -> str:
    """Normaliza nome de município para o cruzamento CSV × IBGE
    (ignora acentos, maiúsculas, apóstrofo reto/tipográfico e hífen)."""
    s = unicodedata.normalize("NFKD", str(nome).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\u2019", "").replace("'", "").replace("-", " ")
    return " ".join(s.split())

@st.cache_data(show_spinner="Carregando dados de Ng (2026)…")
def carregar_gdf() -> gpd.GeoDataFrame:
    if CACHE_PARQUET.exists():
        return gpd.read_parquet(CACHE_PARQUET)

    if not (ARQUIVO_CSV.exists() and ARQUIVO_SHP.exists()):
        st.error(
            "Cache de dados não encontrado. Coloque `ng_municipios_cache_2026.parquet` "
            "na pasta `data/` do repositório."
        )
        st.stop()

    # — leitura do CSV (Dados 2026) —
    df_ng = pd.read_csv(ARQUIVO_CSV)
    df_ng["UF"] = df_ng["UF"].str.strip()
    df_ng["chave"] = df_ng["Municipio"].map(_chave)

    # — shapefile dos municípios brasileiros —
    mun = gpd.read_file(ARQUIVO_SHP, columns=["NM_MUN", "NM_UF", "SIGLA_UF", "geometry"])
    mun = mun.to_crs("EPSG:4326")

    mun_simpl = mun.copy()
    mun_simpl["geometry"] = mun_simpl["geometry"].simplify(0.01, preserve_topology=True)
    mun_simpl["chave"] = mun_simpl["NM_MUN"].map(_chave)

    gdf = mun_simpl.merge(
        df_ng,
        left_on=["chave", "SIGLA_UF"],
        right_on=["chave", "UF"],
        how="inner",
    )

    gdf.rename(columns={"NM_MUN": "Cidade", "NG": "Dens_km2_ano"}, inplace=True)
    gdf.drop(columns=["chave", "Municipio", "UF"], errors="ignore", inplace=True)

    try:
        gdf.to_parquet(CACHE_PARQUET, index=False)
    except Exception:
        pass

    return gdf

# --------------------------------------------------
# Classificação Dinâmica de Ng (quantis)
# --------------------------------------------------
def classificar_ng_dinamico(series: pd.Series) -> pd.Series:
    if series.nunique() <= 1:
        return pd.Series(LABELS_NG[0], index=series.index)
    try:
        return pd.qcut(series, q=5, labels=LABELS_NG, duplicates="drop")
    except Exception:
        return pd.cut(series, bins=5, labels=LABELS_NG, include_lowest=True)

def cor_por_classe(classe_series: pd.Series) -> pd.Series:
    return classe_series.astype(str).map(CORES_NG).apply(
        lambda x: x if isinstance(x, list) else [120, 120, 120, 140]
    )

def raio_proporcional(series: pd.Series) -> pd.Series:
    vmin, vmax = series.min(), series.max()
    if vmax > vmin:
        return ((series - vmin) / (vmax - vmin)) * 30_000 + 8_000
    return pd.Series(15_000, index=series.index)

# --------------------------------------------------
# Legenda na sidebar
# --------------------------------------------------
def render_legenda(labels_visiveis: list[str]) -> None:
    st.sidebar.markdown(
        "### Legenda – Ng Dinâmica",
        help=(
            "O índice Ng é a densidade média anual de descargas atmosféricas "
            "(raios) nuvem-solo por km² por ano. As cores se adaptam dinamicamente "
            "com base nos limites mínimo e máximo da região filtrada."
        ),
    )
    for label in labels_visiveis:
        cor = CORES_NG.get(label)
        if not cor:
            continue
        rgba = f"rgba({cor[0]},{cor[1]},{cor[2]},{cor[3]/255:.2f})"
        st.sidebar.markdown(
            f"""<div style="display:flex;align-items:center;margin-bottom:4px;">
                  <div style="width:16px;height:16px;background:{rgba};
                              margin-right:8px;border-radius:3px;"></div>
                  <span>{label}</span>
               </div>""",
            unsafe_allow_html=True,
        )

# --------------------------------------------------
# Estatísticas resumidas
# --------------------------------------------------
def render_estatisticas(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pontos exibidos",  f"{len(df):,}".replace(",", "."))
    col2.metric("Ng mínimo",        f"{df['Dens_km2_ano'].min():.2f}")
    col3.metric("Ng máximo",        f"{df['Dens_km2_ano'].max():.2f}")
    col4.metric("Ng médio",         f"{df['Dens_km2_ano'].mean():.2f}")

# --------------------------------------------------
# Construção das layers PyDeck
# --------------------------------------------------
def build_deck(df_mapa: gpd.GeoDataFrame, zoom: float) -> pdk.Deck:
    if not df_mapa.empty:
        bounds = df_mapa.total_bounds
        lon_c = (bounds[0] + bounds[2]) / 2
        lat_c = (bounds[1] + bounds[3]) / 2
    else:
        lat_c, lon_c = -15.78, -47.92

    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        df_mapa,
        opacity=0.7,
        stroked=True,
        filled=True,
        extruded=False,
        get_fill_color="cor",
        get_line_color=[200, 200, 200, 150],
        line_width_min_pixels=0.3,
        pickable=True,
    )

    view = pdk.ViewState(latitude=lat_c, longitude=lon_c, zoom=zoom, pitch=0)

    return pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip=cast(Any, {"text": "Cidade: {Cidade}\nUF: {SIGLA_UF}\nNg: {Dens_km2_ano}\nClasse: {Ng_classe}"}),
    )

# ==================================================
# APP PRINCIPAL
# ==================================================
st.title("Mapa Ng")
st.caption("Densidade de descargas atmosféricas (raios/km²/ano) · ABNT NBR 5419-2:2026")

gdf = carregar_gdf()

# --------------------------------------------------
# Sidebar – filtros
# --------------------------------------------------
with st.sidebar:
    st.header("Filtros")

    ufs = sorted(gdf["SIGLA_UF"].dropna().unique())
    uf_sel = st.selectbox("Estado (UF)", options=["Todos"] + ufs)

    gdf_uf = gdf if uf_sel == "Todos" else gdf[gdf["SIGLA_UF"] == uf_sel]
    cidades = sorted(gdf_uf["Cidade"].dropna().unique())
    cidade_sel = st.selectbox("Cidade", options=["Todas"] + cidades)

    df_limites = gdf_uf[gdf_uf["Cidade"] == cidade_sel] if cidade_sel != "Todas" else gdf_uf

    ng_dinamico_min = float(df_limites["Dens_km2_ano"].min())
    ng_dinamico_max = float(df_limites["Dens_km2_ano"].max())

    if ng_dinamico_min == ng_dinamico_max:
        ng_dinamico_min = max(0.0, ng_dinamico_min - 0.1)
        ng_dinamico_max = ng_dinamico_max + 0.1

    ng_range = st.slider(
        "Faixa de Ng (raios/km²/ano)",
        min_value=ng_dinamico_min,
        max_value=ng_dinamico_max,
        value=(ng_dinamico_min, ng_dinamico_max),
        step=0.1,
        format="%.1f",
    )

    st.divider()
    render_legenda(LABELS_NG)

# --------------------------------------------------
# Aplicação dos filtros no mapa
# --------------------------------------------------
df_mapa = gdf.copy()

if uf_sel != "Todos":
    df_mapa = df_mapa[df_mapa["SIGLA_UF"] == uf_sel]

if cidade_sel != "Todas":
    df_mapa = df_mapa[df_mapa["Cidade"] == cidade_sel]

df_mapa = df_mapa[df_mapa["Dens_km2_ano"].between(ng_range[0], ng_range[1])].copy()

if df_mapa.empty:
    st.warning("Nenhum ponto encontrado com os filtros selecionados.")
    st.stop()

# --------------------------------------------------
# Enriquecimento visual dinâmico (após filtros)
# --------------------------------------------------
df_mapa["Ng_classe"] = classificar_ng_dinamico(df_mapa["Dens_km2_ano"])
df_mapa["cor"]       = cor_por_classe(df_mapa["Ng_classe"])
df_mapa["raio"]      = raio_proporcional(df_mapa["Dens_km2_ano"])

render_estatisticas(df_mapa)

if cidade_sel != "Todas":
    zoom = 10.0
elif uf_sel != "Todos":
    zoom = 5.5
else:
    zoom = 3.5

st.pydeck_chart(build_deck(df_mapa, zoom), height=800, width="stretch")

# --------------------------------------------------
# Tabela de dados (expansível)
# --------------------------------------------------
with st.expander(":material/table_chart: Ver dados tabulares"):
    cols_tabela = ["Cidade", "SIGLA_UF", "Dens_km2_ano", "Ng_classe"]
    cols_tabela = [c for c in cols_tabela if c in df_mapa.columns]
    tabela = (
        pd.DataFrame(df_mapa[cols_tabela])
        .rename(columns={"Dens_km2_ano": "Ng (raios/km²/ano)", "Ng_classe": "Classe", "SIGLA_UF": "UF"})
        .sort_values("Ng (raios/km²/ano)", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(tabela, width="stretch", height=320)

    # Exporta só a tabela (geometria e cor não vão para o Excel)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        tabela.assign(Classe=tabela["Classe"].astype(str)).to_excel(w, index=False, sheet_name="Ng")
    st.download_button(
        "Tabela NG (Excel)",
        data=buf.getvalue(),
        file_name="Tabela NG (Excel).xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

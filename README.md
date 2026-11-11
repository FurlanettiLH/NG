# Mapa Ng

Mapa interativo da densidade de descargas atmosféricas **Ng** (raios/km²/ano) por município,
conforme a Tabela F.1 do Anexo F da ABNT NBR 5419-2:2026.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dados

- `data/ng_municipios_cache_2026.parquet`: municípios com geometria simplificada e Ng (é o que o app lê).
- `data/ng_municipios.csv`: valores de Ng por município (Município, UF, NG), com os nomes compatibilizados com a malha do IBGE.

Para regerar o cache, coloque o shapefile `BR_Municipios_2024` do IBGE (.shp, .shx, .dbf, .prj, .cpg)
em `data/`, apague o parquet e rode o app. O shapefile não vai para o repositório (está no `.gitignore`).

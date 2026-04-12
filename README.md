# Evaluación de Calidad del Sistema de Etiquetado Alimentario 🍎🔬

## Estructura del Proyecto

```text
foodfacts/
├── notebooks/          # Notebooks .ipynb (Preprocesado y Análisis)
│   ├── 01_data_preprocessing.ipynb  # Limpieza y preparación inicial
│   ├── 02_h01.ipynb                 # Análisis de la Hipótesis 1
│   ├── 03_h02.ipynb                 # Análisis de la Hipótesis 2
│   ├── 04_h03.ipynb                 # Análisis de la Hipótesis 3
│   └── 05_h04.ipynb                 # Análisis de la Hipótesis 4
├── data/               # Directorio principal de datos
│   ├── raw/            # Datos originales (FAO, OpenFoodFacts)
│   ├── processed/      # Datos procesados (foods_cleaned_2026.csv)
│   └── txt/            # Textos extraídos para procesamiento con Regex
├── images/             # Gráficos y visualizaciones generadas
│   ├── 01_h01/                      # Gráficos de la Hipótesis 1
│   ├── 02_h02/                      # Gráficos de la Hipótesis 2
│   ├── 03_h03/                      # Gráficos de la Hipótesis 3
│   └── 04_h04/                      # Gráficos de la Hipótesis 4
└── README.md           # Documentación del proyecto
```

# Hipótesis planteadas

### H1 (Nutri-Score vs. NOVA): El algoritmo Nutri-Score reduce la calidad de un alimento a sus macronutrientes permitiendo que productos ultraprocesados obtengan buenas calificaciones.

### H2 (Efecto Halo 'Bio'): El etiquetado “BIO” hace pensar al consumidor que el producto es mas saludable, pero no necesariamente es más nutritivo o menos procesado.

### H3 (Marcas de distribuidor vs. Grandes corporaciones): Las marcas blancas ofrecen perfiles nutricionales más equilibrados y menor carga de aditivos que las grandes corporaciones.

### H4 (Mercado Cárnico vs. Plant-based): En países de alta cultura ganadera, la oferta vegetal presenta mayor procesamiento tecnológico y menor densidad proteica para mimetizar la experiencia cárnica.




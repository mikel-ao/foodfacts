# Evaluación de la Calidad del Sistema Alimentario mediante Ciencia de Datos Aplicada

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
│   ├── raw/            # Datos originales (FAO, OpenFoodFacts original)
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

### Hipótesis 1 (NutriScore): El sistema NutriScore no refleja adecuadamente la calidad nutricional real de los productos, ya que se basa principalmente en los ingredientes y nutrientes declarados, pero no considera el grado de procesamiento de los alimentos.

### Hipótesis 2 (Etiquetado ‘Bio’): Los productos con etiqueta “Bio” no presentan un perfil nutricional significativamente mejor (en valores de grasa, azúcar o sal) que sus equivalentes convencionales.

### Hipótesis 3 (Marcas blancas vs multinacionales): En general, las marcas blancas ofrecen productos con un perfil nutricional más equilibrado que las grandes multinacionales dentro de las mismas categorías alimentarias.

### Hipótesis 4 (Producción cárnica vs calidad vegetal): En países con alta producción de proteína animal, las alternativas vegetales tienden a ser más procesadas para imitar texturas y sabores cárnicos, lo que reduce su calidad nutricional.



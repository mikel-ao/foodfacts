# Evaluación de la Calidad del Sistema Alimentario mediante Ciencia de Datos Aplicada

## Estructura del Proyecto

```text
foodfacts/
├── notebooks/          # Notebooks .ipynb (Preprocesado y Análisis)
├── data/               # Directorio principal de datos
│   ├── raw/            # Datos originales (FAO, OpenFoodFacts original)
│   ├── processed/      # Datos procesados (foods_cleaned_2026.csv)
│   └── txt/            # Textos extraídos para procesamiento con Regex
├── images/             # Gráficos y visualizaciones generadas
└── README.md           # Documentación del proyecto
```

# Hipótesis planteadas

### Hipótesis 1 (NutriScore): El sistema NutriScore no refleja adecuadamente la calidad nutricional real de los productos, ya que se basa principalmente en los ingredientes y nutrientes declarados pero no considera el grado de procesamiento de los alimentos.

### Hipótesis 2 (Etiquetado ‘Bio’/Orgánico): Los productos con etiqueta “Bio” u “Orgánica” no presentan un perfil nutricional significativamente mejor (en valores de grasa, azúcar o sal) que sus equivalentes convencionales.

### Hipótesis 3 (Marcas blancas vs multinacionales): En general, las marcas blancas ofrecen productos con un perfil nutricional más equilibrado que las grandes multinacionales dentro de las mismas categorías alimentarias.

### Hipótesis 4 (Producción cárnica vs calidad vegetal): En países con alta producción de proteína animal, las alternativas vegetales tienden a ser más procesadas para imitar texturas y sabores cárnicos, lo que reduce su calidad nutricional.



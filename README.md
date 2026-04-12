# Evaluación de Calidad del Sistema de Etiquetado Alimentario 🍎🔬

Este proyecto realiza una auditoría multidimensional del sistema alimentario actual, integrando dimensiones nutricionales (Nutri-Score), industriales (NOVA), ambientales (Eco-Score) y de mercado (Marcas de distribuidor vs. Grandes corporaciones). El objetivo es desentrañar la "paradoja de la información" que enfrenta el consumidor europeo en 2026.

# 📌 Resumen del Proyecto

A través del análisis de ~10.000 productos extraídos de Open Food Facts y datos de producción de la FAO, este trabajo utiliza técnicas de Data Science para validar si los sellos de calidad actuales reflejan la realidad biológica de los alimentos o si son vulnerables al marketing nutricional.

# 🚀 Tecnologías y Herramientas

* Lenguaje: Python 3.11+
  
* Análisis de Datos: Pandas, NumPy.
  
* Limpieza Avanzada: ReGex (para normalización multilingüe de >2.000 variantes de países y marcas).
  
* Visualización: Seaborn, Matplotlib (Enfoque en mapas de calor y diagramas de barras para una visualización sencilla).
  
* Modelado: Regresión Lineal Múltiple (Interpretación de coeficientes $\beta$ para ingeniería inversa del Nutri-Score).

# 💡 Hipótesis de Investigación

* H1 (Nutri-Score vs. NOVA): El algoritmo Nutri-Score reduce la calidad de un alimento a sus macronutrientes permitiendo que productos ultraprocesados obtengan buenas calificaciones.

* H2 (Efecto Halo 'Bio'): El etiquetado “BIO” hace pensar al consumidor que el producto es mas saludable, pero no necesariamente es más nutritivo o menos procesado.

* H3 (Marcas de distribuidor vs. Grandes corporaciones): Las marcas blancas ofrecen perfiles nutricionales más equilibrados y menor carga de aditivos que las grandes corporaciones.

* H4 (Mercado Cárnico vs. Plant-based): En países de alta cultura ganadera, la oferta vegetal presenta mayor procesamiento tecnológico y menor densidad proteica para mimetizar la experiencia cárnica.

# 📊 Hallazgos Clave 

* Fallo Lógico: El 23.3% de los productos ultraprocesados logran un Nutri-Score A o B.

* La Rebelión de la Marca Blanca: Los productos de marca blanca contienen un 62% menos de azúcar y casi el cuádruple de fibra que las grandes multinacionales.

* Limpieza 'Bio': El sello Bio reduce a menos de la mitad la carga de aditivos químicos (0.95 vs 1.96 de media).

* Erosión Nutricional: En España, los análogos cárnicos tienen una mediana de 3 aditivos, frente a los 0 aditivos que se observan en mercados más maduros como Reino Unido.

# 📂 Estructura del Proyecto

```text
foodfacts/
├── notebooks/          # Pipeline completo de los datos
│   ├── 01_data_preprocessing.ipynb  # ReGex, unificación taxonómica y limpieza
│   ├── 02_h01.ipynb                 # Hackeando el Nutri-Score
│   ├── 03_h02.ipynb                 # Auditoría del segmento Bio
│   ├── 04_h03.ipynb                 # Comparativa Marcas Blancas vs. Grandes Corporaciones
│   └── 05_h04.ipynb                 # Análisis de análogos cárnicos por países
├── data/               # Datasets (FAO & OpenFoodFacts)
│   ├── raw/            # Datos originales
│   ├── processed/      # Dataset final normalizado (foods_cleaned_2026.csv)
│   └── txt/            # Textos extraídos para procesamiento con Regex
├── images/             # Visualizaciones exportadas
└── README.md           # Documentación
```






# Evaluación de Calidad del Sistema de Etiquetado Alimentario 🍎🔬

Este proyecto realiza una auditoría multidimensional del sistema alimentario actual, integrando dimensiones nutricionales, industriales, ambientales y de mercado. El objetivo es desentrañar la "paradoja de la información" que enfrenta el consumidor europeo en 2026.

# 📌 Resumen del Proyecto

A través del análisis de ~10.000 productos extraídos de Open Food Facts y datos de producción de la FAO, este trabajo utiliza técnicas de Data Science para validar si los sellos de calidad actuales reflejan la realidad biológica de los alimentos o si son vulnerables al marketing nutricional.

# 💾 Tecnologías y Herramientas

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

* Fallo lógico: El 23% de los productos ultraprocesados logran un Nutri-Score A o B.
![Figura 1](outputs/plots/1.1_heatmap.png)

* Algoritmo manipulable: El Nutri-Score es susceptible de ser "hackeado" mediante ajustes técnicos en la formulación para mejorar artificialmente la nota sin elevar necesariamente la calidad nutricional real.
![Figura 2](outputs/plots/1.2_regresion.png)

* Limpieza 'Bio': El sello Bio reduce a menos de la mitad la carga de aditivos químicos en la mayoría de categorías.
![Figura 3](outputs/plots/2_3_heatmap_aditivos.png)

* La Rebelión de la marca blanca: Los productos de marca blanca contienen un 62% menos de azúcar y casi el cuádruple de fibra que los productos de grandes corporaciones.
![Figura 4](outputs/plots/3_2_perfil_nutricional.png)

* Marcas blancas más limpias: El 57% del catálogo de las marcas blancas contiene cero aditivos vs. el 43% del catálogo de grandes corporaciones.
* ![Figura 5](outputs/plots/3_3_aditivos_marcas.png)

* Erosión nutricional: En España, los análogos cárnicos tienen una mediana de 3 aditivos, frente a los 0 aditivos que se observan en mercados más maduros como Reino Unido.
* ![Figura 6](outputs/plots/4_1_cultura_procesado.png)

* Calidad vs. Experiencia sensorial: En el mercado de los análogos cárnicos se observan dos vertientes: propuestas que priorizan la densidad nutricional, frente a las que centran sus esfuerzos en mimetizar la experiencia sensorial de la carne animal, sacrificando el valor nutricional del producto final.
* ![Figura 7](outputs/plots/4_2_cultura_proteina.png)

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
├── README.md           # Documentación
└── requirements.txt    # Lista de librerías
```
# 🚀 Perspectivas Futuras

El proyecto propone la evolución hacia un Nutri-Score 2.0 que utilice Inteligencia Artificial para penalizar automáticamente la complejidad química y el ultraprocesamiento. Se busca visibilizar el grado de procesamiento industrial para evitar el "maquillaje" nutricional y democratizar la salud alimentaria en Europa.

# ✍️ Autor
Mikel Añibarro Ortega | Data Science Bootcamp The Bridge (Bilbao)





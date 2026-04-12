import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

# Diccionario Maestro
TRADUCCION_CAT = {
     "beverage": "Bebidas y Refrescos",
    "dairy_eggs": "Lácteos",
    "meat_fish": "Carnes y Pescados",
    "fats_sauces": "Grasas y Salsas",
    "snacks_sweets": "Snacks y Dulces",
    "plant_based": "Frutas y Verduras",
    "plant_based_protein": "Análogos Cárnicos Vegetales",
    "plant_based_milks": "Análogos Lácteos Vegetales",
    "bread_and_grains": "Pan y Cereales",
    "ready_to_eat": "Platos Preparados",
    "breakfast_cereals": "Cereales Desayuno",
    "seeds_nuts": "Frutos Secos y Cremas"
}


# PALETA UNIFICADA DE NUTRIENTES
# Mantenemos el orden y colores de la regresión para todo el proyecto
PALETA_NUTRIENTES = {
    'CALORÍAS': "#e74c3c",    # Rojo
    'GRASAS SAT.': "#f39c12", # Naranja
    'AZÚCAR': "#f1c40f",      # Amarillo
    'FIBRA': "#3498db",       # Azul
    'PROTEÍNA': "#2ecc71",    # Verde
    'SAL': "#9b59b6"          # Morado
}

# Configuración estética de Seaborn
sns.set_style("white")

# ==========================================
# FUNCIONES DE LA HIPÓTESIS 01
# ==========================================

def plot_heatmap_nova_nutriscore(df, save_path=None):
    """1. Heatmap: Cruce de NOVA vs Nutri-Score (La Paradoja)"""
    df_paradox = df[
        (df['nutriscore_grade'].isin(['a', 'b', 'c', 'd', 'e'])) & 
        (df['nova_group'] > 0)
    ].copy()

    cross_tab = pd.crosstab(
        df_paradox['nova_group'], 
        df_paradox['nutriscore_grade'], 
        normalize='index'
    ) * 100
    cross_tab = cross_tab.reindex(columns=['a', 'b', 'c', 'd', 'e'])

    plt.figure(figsize=(15, 9))
    ax = sns.heatmap(
        cross_tab, 
        annot=True, 
        annot_kws={"size": 16, "weight": "bold"}, 
        cmap="YlGnBu", 
        fmt=".1f", 
        cbar_kws={'label': 'Porcentaje por Grupo NOVA (%)'}
    )

    plt.title("Distribución de NOVA por Grado Nutri-Score", fontsize=22, fontweight='bold', pad=20)
    plt.ylabel("Grupo NOVA", fontsize=18)
    plt.xlabel("Grado Nutri-Score", fontsize=18)
    plt.xticks(fontsize=15, fontweight='bold')
    plt.yticks(fontsize=15, fontweight='bold')

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_nutriscore_regression(df, save_path=None):
    """2. Ingeniería Inversa: Impacto de nutrientes en la nota por categoría."""
    df_reg = df[df['nutriscore_grade'].isin(['a', 'b', 'c', 'd', 'e'])].copy()
    df_reg['nutri_numeric'] = df_reg['nutriscore_grade'].map({'a': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1})

    nutrientes = ['energy-kcal_100g', 'saturated-fat_100g', 'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g']
    results = []

    for cat in df_reg['category_unified'].unique():
        cat_data = df_reg[df_reg['category_unified'] == cat].dropna(subset=nutrientes + ['nutri_numeric'])
        if len(cat_data) > 20:
            X_scaled = StandardScaler().fit_transform(cat_data[nutrientes])
            model = LinearRegression().fit(X_scaled, cat_data['nutri_numeric'])
            cat_name = TRADUCCION_CAT.get(cat, cat).upper()
            
            for i, nutri in enumerate(nutrientes):
                # Generamos el nombre tal cual está en la PALETA_NUTRIENTES
                label = nutri.replace('-kcal_100g', '').replace('_100g', '').replace('saturated-fat', 'Grasas Sat.').replace('sugars', 'Azúcar').replace('fiber', 'Fibra').replace('proteins', 'Proteína').replace('salt', 'Sal').replace('energy', 'Calorías').upper()
                results.append({'category': cat_name, 'nutrient': label, 'coefficient': model.coef_[i]})

    df_res = pd.DataFrame(results)
    plt.figure(figsize=(20, 18))

    # Usamos la paleta global filtrando solo los que aparecen en este DF
    sns.barplot(data=df_res, x='coefficient', y='category', hue='nutrient', 
                palette=PALETA_NUTRIENTES, edgecolor='black', linewidth=0.8)
    
    plt.axvline(0, color='black', linestyle='-', linewidth=2.5)
    plt.title("Ingeniería Inversa del Nutri-Score por Categoría", fontsize=32, pad=75, fontweight='bold')
    plt.xlabel("Impacto en la Nota (Coeficiente)", fontsize=22, fontweight='bold', labelpad=20)
    plt.xticks(fontsize=18); plt.yticks(fontsize=18, fontweight='bold')
    
    plt.legend(title="COMPONENTE", title_fontsize=18, fontsize=16, loc='lower center', bbox_to_anchor=(1, 0.8), frameon=True, shadow=True)
    plt.text(0.3, -0.9, "⬆️ FAVORECE", color='#1e8449', fontweight='bold', ha='center', fontsize=20, bbox=dict(facecolor='white', alpha=0.8))
    plt.text(-0.3, -0.9, "⬇️ PENALIZA", color='#a93226', fontweight='bold', ha='center', fontsize=20, bbox=dict(facecolor='white', alpha=0.8))

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_paradox_comparison(df, save_path=None):
    """3. Comparativa Crítica: Aceite de Oliva vs Cereales (Colores sincronizados)."""
    aceites = df[df['product_name'].str.contains('olive oil|aceite de oliva|huile d\'olive', case=False, na=False)].copy()
    aceites['group_label'] = 'ACEITE DE OLIVA (C/D)'
    cereales = df[df['category_unified'] == 'breakfast_cereals'].copy()
    cereales['group_label'] = 'CEREALES DESAYUNO (A/B)'

    df_comp = pd.concat([aceites, cereales])
    
    # Mapeo a nombres en MAYÚSCULAS para coincidir con la paleta global
    nutri_map = {
        'sugars_100g': 'AZÚCAR', 
        'saturated-fat_100g': 'GRASAS SAT.', 
        'fiber_100g': 'FIBRA', 
        'proteins_100g': 'PROTEÍNA'
    }

    df_medians = df_comp.groupby('group_label')[list(nutri_map.keys())].median().reset_index()
    df_melted = df_medians.melt(id_vars='group_label', var_name='Nutriente', value_name='g_100g')
    df_melted['Nutriente'] = df_melted['Nutriente'].map(nutri_map)

    plt.figure(figsize=(16, 10))

    # Usamos la misma PALETA_NUTRIENTES definida arriba
    ax = sns.barplot(data=df_melted, x='group_label', y='g_100g', hue='Nutriente', 
                    palette=PALETA_NUTRIENTES, edgecolor='black', linewidth=1.5)

    plt.title("Paradoja del Algoritmo: Aceite de Oliva vs. Cereales", fontsize=30, fontweight='bold', pad=75)
    plt.ylabel("Gramos por 100g (Mediana)", fontsize=20, fontweight='bold', labelpad=20)
    plt.xticks(fontsize=20, fontweight='bold'); plt.yticks(fontsize=18)
    
    plt.legend(title="COMPONENTE", title_fontsize=16, fontsize=16, loc='lower center', 
               bbox_to_anchor=(0.5, 0.9), ncol=4, frameon=True, shadow=True)

    for p in ax.patches:
        h = p.get_height()
        if not pd.isna(h) and h > 0.05:
            ax.annotate(f'{h:.2f}g', (p.get_x() + p.get_width()/2., h), ha='center', va='bottom', 
                        xytext=(0, 12), textcoords='offset points', fontsize=18, fontweight='bold', color='#2c3e50')

    plt.ylim(0, df_melted['g_100g'].max() * 1.3)
    sns.despine()
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()
    
# PIPELINE MAESTRO DE LA H01 (INCLUYE LAS 3 FIGURAS CLAVE)
    
def pipeline_figuras_h01(df, output_dir=None):
    """Pipeline Maestro simplificado"""
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plot_heatmap_nova_nutriscore(df, save_path=(os.path.join(output_dir, "1_heatmap.png") if output_dir else None))
    plot_nutriscore_regression(df, save_path=(os.path.join(output_dir, "2_regresion.png") if output_dir else None))
    plot_paradox_comparison(df, save_path=(os.path.join(output_dir, "3_aceite_vs_cereales.png") if output_dir else None))
    
    print("✅ Análisis H01 completado.")
    
# ==========================================
# FUNCIONES DE LA HIPÓTESIS 02
# ==========================================
def plot_bio_presence_by_category(df, save_path=None):
    """1. Barplot: Porcentaje de productos Bio frente a Convencionales por categoría."""
    df_plot = df.copy()
    df_plot["category_es"] = df_plot["category_unified"].map(TRADUCCION_CAT).fillna(df_plot["category_unified"])

    # Tabla cruzada con porcentajes
    cross_tab = pd.crosstab(df_plot["category_es"], df_plot["is_bio"], normalize="index") * 100
    cross_tab = cross_tab.sort_values(by=True, ascending=False)

    plot_df = cross_tab.reset_index().melt(id_vars="category_es", var_name="tipo_bio", value_name="porcentaje")
    plot_df["tipo_label"] = plot_df["tipo_bio"].map({True: "Bio", False: "Convencional"})

    plt.figure(figsize=(16, 10))
    ax = sns.barplot(
        data=plot_df, y="category_es", x="porcentaje", hue="tipo_label",
        palette={"Bio": "#2ecc71", "Convencional": "#95a5a6"}, edgecolor="black"
    )

    plt.title("Presencia del Segmento Bio por Categoría", fontsize=28, fontweight="bold", pad=65)
    plt.xlabel("Porcentaje (%)", fontsize=20, fontweight="bold"); plt.ylabel("")
    plt.xticks(fontsize=18); plt.yticks(fontsize=16, fontweight="bold")

    plt.legend(title="Tipo", fontsize=16, loc='lower center', bbox_to_anchor=(1, 0.9), ncol=2)

    for p in ax.patches:
        width = p.get_width()
        if 0 < width < 45: # Solo anotamos si la barra es pequeña para no saturar
            ax.annotate(f'{width:.1f}%', (width, p.get_y() + p.get_height() / 2.),
                        ha='left', va='center', xytext=(8, 0), textcoords='offset points',
                        fontsize=14, fontweight='bold', color='#1b5e20')

    sns.despine()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()


def plot_bio_quality_indicators(df, save_path=None):
    """2. Subplots: Comparativa Bio vs Convencional en Eco-Score, Nutri-Score y NOVA."""
    
    def _get_melted_data(data, col_name, order_list):
        sub = data[data[col_name].isin(order_list)].copy()
        sub['Tipo'] = sub['is_bio'].map({True: 'Bio', False: 'Convencional'})
        pct = pd.crosstab(sub['Tipo'], sub[col_name], normalize='index') * 100
        return pct.reindex(columns=order_list).fillna(0).reset_index().melt(
            id_vars='Tipo', value_name='pct', var_name='grade'
        )

    # Aumentamos el tamaño de la figura para acomodar fuentes grandes
    fig, axes = plt.subplots(1, 3, figsize=(28, 12)) 
    
    configs = [
        ('ecoscore_grade', ['a', 'b', 'c', 'd', 'e'], "ECO-SCORE", {"Convencional": "#B0BEC5", "Bio": "#2E7D32"}),
        ('nutriscore_grade', ['a', 'b', 'c', 'd', 'e'], "NUTRI-SCORE", {"Convencional": "#B0BEC5", "Bio": "#4CAF50"}),
        ('nova_group', [1, 2, 3, 4], "NOVA", {"Convencional": "#B0BEC5", "Bio": "#FF9800"})
    ]

    for i, (col, order, title, palette) in enumerate(configs):
        melted = _get_melted_data(df, col, order)
        sns.barplot(ax=axes[i], data=melted, x='grade', y='pct', hue='Tipo', palette=palette, edgecolor='black')
        
        # --- AUMENTO DE FUENTES ---
        axes[i].set_title(title, fontsize=32, fontweight='bold', pad=30)
        axes[i].set_ylabel("% de Productos" if i == 0 else "", fontsize=24, fontweight='bold', labelpad=15)
        axes[i].set_xlabel("Grado / Grupo", fontsize=24, fontweight='bold', labelpad=15)
        axes[i].tick_params(labelsize=22) # Tamaño de los números en los ejes
        axes[i].set_ylim(0, 85)           # Damos margen superior para la leyenda
        
        # --- LEYENDA MEJORADA ---
        # La ponemos dentro del gráfico (loc='upper center') para que no toque el título superior
        axes[i].legend(title="", fontsize=20, loc='upper center', frameon=True, shadow=True)

    # Título Principal (Suptitle) con más aire
    plt.suptitle("Impacto del Sello Bio en los Indicadores de Calidad", 
                 fontsize=42, fontweight='bold', y=1.02)
    
    # tight_layout ajusta automáticamente los espacios entre los subplots
    plt.tight_layout()
    
    if save_path: 
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()


def plot_bio_additives_heatmap(df, save_path=None):
    """3. Heatmap: Media de aditivos por categoría y sello Bio."""
    df_heat = df.copy()
    # Calcular medias por categoría y sello
    stats = df_heat.groupby(['category_unified', 'is_bio'])['additive_count'].mean().unstack()
    # Traducir índices (filas) y columnas
    stats.index = [TRADUCCION_CAT.get(c, c) for c in stats.index]
    stats.columns = ['Convencional', 'Bio']
    
    # Transponer para que el diseño coincida con tu original
    stats_t = stats.T
    stats_t.index = ['Conv.', 'Bio']

    plt.figure(figsize=(18, 7))
    sns.heatmap(stats_t, annot=True, fmt='.1f', cmap='RdYlGn_r', cbar=False,
                annot_kws={"size": 20, "weight": "bold"}, linewidths=1.5)

    plt.title('Carga de Aditivos por Categoría y Sello', fontsize=28, fontweight='bold', pad=45)
    plt.xticks(rotation=30, ha='right', fontsize=14, fontweight='bold')
    plt.yticks(rotation=0, fontsize=20, fontweight='bold')
    
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def pipeline_figuras_h02(df, output_dir=None):
    """Ejecuta los 3 análisis de la Hipótesis 02 (Segmento Bio)."""
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("📊 Iniciando Análisis del Segmento Bio (H02)...")
    
    plot_bio_presence_by_category(df, save_path=(os.path.join(output_dir, "2_1_presencia_bio.png") if output_dir else None))
    plot_bio_quality_indicators(df, save_path=(os.path.join(output_dir, "2_2_indicadores_calidad.png") if output_dir else None))
    plot_bio_additives_heatmap(df, save_path=(os.path.join(output_dir, "2_3_heatmap_aditivos.png") if output_dir else None))
    
    print("✅ Análisis H02 completado.")

# ==========================================
# CONFIGURACIÓN GLOBAL H03
# ==========================================

MARCAS_BLANCAS = [
    'hacendado', 'mercadona', 'deliplus', 'compy', 'bosque verde', 'entrepinares', 
    'lidl', 'alesto', 'milbona', 'fin carré', 'sondey', 'freshona', 'crownfield', 
    'carrefour', 'u bio', 'paturages', 'nos regions ont du talent', 'bio village', 
    'marque repère', 'aldi', 'harvest morn', 'village bakery', 'tesco', 'auchan', 'intermarche'
]

GRANDES_MULTINACIONALES = [
    'nestle', 'nescafe', 'unilever', 'hellmann', 'knorr', 'mondelez', 'lu', 'milka', 
    'danone', 'activia', 'ferrero', 'nutella', 'pepsico', 'lays', 'coca-cola', 
    'kellogg', 'pringles', 'heinz', 'mars', 'dr. oetker'
]

def _clasificar_grupo_marca(brand_str):
    """Función interna para clasificar marcas."""
    brand_str = str(brand_str).lower()
    if any(mb in brand_str for mb in MARCAS_BLANCAS):
        return 'Marcas Blancas'
    if any(multi in brand_str for multi in GRANDES_MULTINACIONALES):
        return 'Grandes Multinacionales'
    return 'Otras'

def _agrupar_aditivos_label(count):
    """Función interna para categorizar el número de aditivos."""
    if count == 0: return '0 Aditivos'
    if count == 1: return '1 Aditivo'
    if count == 2: return '2 Aditivos'
    if count == 3: return '3 Aditivos'
    if count == 4: return '4 Aditivos'
    if count >= 5: return '5 o más'
    return f'{int(count)} Aditivos'

# ==========================================
# FUNCIONES DE LA HIPÓTESIS 03
# ==========================================

def plot_brand_nutriscore_dist(df, save_path=None):
    """1. Comparativa de distribución de Nutri-Score por tipo de fabricante."""
    df_plot = df.copy()
    df_plot['grupo'] = df_plot['brands'].apply(_clasificar_grupo_marca)
    
    df_plot = df_plot[
        df_plot['nutriscore_grade'].isin(['a', 'b', 'c', 'd', 'e']) & 
        df_plot['grupo'].isin(['Marcas Blancas', 'Grandes Multinacionales'])
    ]

    dist = df_plot.groupby(['grupo', 'nutriscore_grade']).size().unstack(fill_value=0)
    pct = dist.div(dist.sum(axis=1), axis=0) * 100
    pct = pct[['a', 'b', 'c', 'd', 'e']]

    plt.figure(figsize=(18, 8))
    colors_ns = ['#038141', '#85BB2F', '#FECB02', '#EE8100', '#E63E11']
    ax = pct.plot(kind='barh', stacked=True, color=colors_ns, ax=plt.gca(), edgecolor='white', width=0.7, legend = False)

    for p in ax.patches:
        width = p.get_width()
        if width > 5:
            ax.annotate(f'{width:.1f}%', (p.get_x() + width/2, p.get_y() + p.get_height()/2),
                        ha='center', va='center', fontsize=14, fontweight='bold', color='white')

    plt.title("Calidad Nutricional: Marcas Blancas vs. Grandes Multinacionales", fontsize=28, fontweight='bold', pad=40)
    plt.xlabel("Porcentaje del Catálogo (%)", fontsize=18, fontweight='bold')
    plt.yticks(fontsize=20, fontweight='bold')
       
    sns.despine(left=True)
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_brand_nutritional_profile(df, save_path=None):
    """2. Perfil Nutricional (Medianas): Marcas Blancas vs Multinacionales."""
    df_plot = df.copy()
    df_plot['grupo'] = df_plot['brands'].apply(_clasificar_grupo_marca)
    df_plot = df_plot[df_plot['grupo'].isin(['Marcas Blancas', 'Grandes Multinacionales'])]

    nutri_dict = {'sugars_100g': 'Azúcares', 'saturated-fat_100g': 'Grasas Sat.', 'salt_100g': 'Sal', 'proteins_100g': 'Proteínas', 'fiber_100g': 'Fibra'}
    df_melt = df_plot.melt(id_vars='grupo', value_vars=list(nutri_dict.keys()), var_name='Nutriente', value_name='valor')
    df_melt['Nutriente'] = df_melt['Nutriente'].map(nutri_dict)

    plt.figure(figsize=(18, 10))
    paleta = {"Marcas Blancas":"#1976D2" , "Grandes Multinacionales": "#B0BEC5"}

    ax = sns.barplot(data=df_melt, x='Nutriente', y='valor', hue='grupo', palette=paleta, 
                     edgecolor='black', linewidth=1.5, estimator='median', errorbar=None)

    plt.title("Perfil Nutricional: Marcas Blancas vs. Multinacionales", fontsize=30, fontweight='bold', pad=80)
    plt.ylabel("Mediana ($g/100g$)", fontsize=20, fontweight='bold')
    plt.ylim(0, 12)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=True, shadow=True, fontsize=18)

    for p in ax.patches:
        h = p.get_height()
        if h > 0.01:
            ax.annotate(f'{h:.2f}g', (p.get_x() + p.get_width()/2., h), ha='center', va='bottom', 
                        xytext=(0, 10), textcoords='offset points', fontsize=16, fontweight='bold')
    
    sns.despine()
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_brand_additives_dist(df, save_path=None):
    """3. Comparativa de carga de aditivos por tipo de fabricante."""
    df_plot = df.copy()
    df_plot['grupo'] = df_plot['brands'].apply(_clasificar_grupo_marca)
    df_plot = df_plot[df_plot['grupo'].isin(['Marcas Blancas', 'Grandes Multinacionales'])]
    df_plot['additive_cat'] = df_plot['additive_count'].apply(_agrupar_aditivos_label)

    cat_order = ['0 Aditivos', '1 Aditivo', '2 Aditivos', '3 Aditivos', '4 Aditivos', '5 o más']
    counts = df_plot.groupby(['grupo', 'additive_cat']).size().unstack(fill_value=0)
    pct_dist = counts.reindex(columns=cat_order, fill_value=0).div(counts.sum(axis=1), axis=0) * 100

    plt.figure(figsize=(16, 6))
    colors = sns.color_palette("YlOrRd", n_colors=len(cat_order))
    ax = pct_dist.plot(kind='barh', stacked=True, color=colors, ax=plt.gca(), width=0.6, edgecolor='white', legend=False)

    ax.set_yticklabels([]) 
    for i, grupo in enumerate(pct_dist.index):
        ax.text(0, i + 0.35, grupo.upper(), fontsize=18, fontweight='bold', ha='left', va='center')

    for i, (grupo, row_pct) in enumerate(pct_dist.iterrows()):
        cum_width = 0
        for j, cat in enumerate(cat_order):
            width = row_pct[cat]
            if width > 3.5:
                text_color = "white" if j >= 4 else "#2c3e50"
                ax.text(cum_width + width/2, i, f'{width:.1f}%', ha='center', va='center', color=text_color, fontweight='bold', fontsize=13)
            cum_width += width

    plt.title("Presencia de Aditivos por Tipo de Fabricante", fontsize=24, fontweight='bold', pad=60)
    plt.legend(labels=cat_order, bbox_to_anchor=(0.5, 1.0), loc='lower center', ncol=3, frameon=True, shadow=True)
    
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_brand_bio_presence(df, save_path=None):
    """4. Donut Charts: Penetración de productos BIO por grupo."""
    df_plot = df.copy()
    df_plot['grupo'] = df_plot['brands'].apply(_clasificar_grupo_marca)
    df_plot = df_plot[df_plot['grupo'].isin(['Marcas Blancas', 'Grandes Multinacionales'])]

    fig, axes = plt.subplots(1, 2, figsize=(18, 9))
    grupos = ['Marcas Blancas', 'Grandes Multinacionales']
    colors_donut = ['#2E7D32', '#CFD8DC']

    for i, grupo in enumerate(grupos):
        datos = df_plot[df_plot['grupo'] == grupo]['is_bio'].value_counts()
        sizes = [datos.get(True, 0), datos.get(False, 0)]
        
        wedges, texts, autotexts = axes[i].pie(sizes, labels=['BIO', 'NO BIO'], autopct='%1.1f%%', 
                                              startangle=140, colors=colors_donut, pctdistance=0.82, 
                                              explode=(0.1, 0), wedgeprops={'edgecolor': 'white', 'linewidth': 3})
        
        centre_circle = plt.Circle((0,0), 0.65, fc='white', edgecolor='black', linewidth=1)
        axes[i].add_artist(centre_circle)
        axes[i].set_title(f'{grupo.upper()}', fontsize=22, fontweight='bold', pad=20)
        for autotext in autotexts:
            autotext.set_fontsize(16); autotext.set_fontweight('bold')

    plt.suptitle('Presencia de Productos BIO: Marcas Blancas vs. Multinacionales', fontsize=30, fontweight='bold', y=1.05)
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_brand_ecoscore_dist(df, save_path=None):
    """5. Distribución de Eco-Score por grupo de fabricante."""
    df_plot = df.copy()
    df_plot['grupo'] = df_plot['brands'].apply(_clasificar_grupo_marca)
    eco_order = ['a', 'b', 'c', 'd', 'e']
    
    df_eco = df_plot[df_plot['ecoscore_grade'].str.lower().isin(eco_order) & 
                     df_plot['grupo'].isin(['Marcas Blancas', 'Grandes Multinacionales'])]

    eco_dist = df_eco.groupby(['grupo', 'ecoscore_grade']).size().unstack(fill_value=0)
    eco_pct = eco_dist.reindex(columns=eco_order, fill_value=0).div(eco_dist.sum(axis=1), axis=0) * 100

    plt.figure(figsize=(18, 6))
    colors_eco = ['#1E8F4E', '#2ECC71', '#FFC90E', '#EF7D18', '#E63323']
    ax = eco_pct.plot(kind='barh', stacked=True, color=colors_eco, ax=plt.gca(), width=0.8, edgecolor='white', legend=False)

    for i, (grupo, row_pct) in enumerate(eco_pct.iterrows()):
        cum_width = 0
        for j, grade in enumerate(eco_order):
            width = row_pct[grade]
            if width > 3.5:
                text_color = "white" if j in [0, 4] else "#2c3e50"
                ax.text(cum_width + width/2, i, f'{width:.1f}%', ha='center', va='center', color=text_color, fontweight='bold', fontsize=17)
            cum_width += width

    plt.title("Sostenibilidad (Eco-Score): Marcas Blancas vs. Grandes Multinacionales", fontsize=28, fontweight='bold', pad=25)
    plt.yticks(fontsize=22, fontweight='bold')
    sns.despine(left=True)
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()


def pipeline_figuras_h03(df, output_dir=None):
    """Ejecuta todos los análisis de la Hipótesis 03 (Marcas)."""
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("📊 Iniciando Comparativa de Fabricantes (H03)...")
    
    plot_brand_nutriscore_dist(df, save_path=(os.path.join(output_dir, "3_1_nutriscore_marcas.png") if output_dir else None))
    plot_brand_nutritional_profile(df, save_path=(os.path.join(output_dir, "3_2_perfil_nutricional.png") if output_dir else None))
    plot_brand_additives_dist(df, save_path=(os.path.join(output_dir, "3_3_aditivos_marcas.png") if output_dir else None))
    plot_brand_bio_presence(df, save_path=(os.path.join(output_dir, "3_4_presencia_bio.png") if output_dir else None))
    plot_brand_ecoscore_dist(df, save_path=(os.path.join(output_dir, "3_5_ecoscore_marcas.png") if output_dir else None))
    
    print("✅ Análisis H03 completado.")
    
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# CONFIGURACIÓN GLOBAL H04
# ==========================================
ORDEN_PAISES = ['Spain', 'Germany', 'France', 'United Kingdom']
CAT_INTERES = ['meat_fish', 'plant_based_protein']

# ==========================================
# FUNCIONES DE LA HIPÓTESIS 04
# ==========================================

def plot_market_penetration_additives(df, fao_meat, save_path=None):
    """1. Análisis Estratégico: Producción vs. Penetración vs. Aditivos (Mediana)."""
    # 2. Procesamiento de OpenFoodFacts
    mask = (df['main_country'].isin(ORDEN_PAISES)) & (df['category_unified'].isin(CAT_INTERES))
    subset = df[mask].copy()

    # Agregación: CALCULANDO LA MEDIANA DE ADITIVOS (Solo para PB)
    stats = subset.groupby(['main_country', 'category_unified']).agg(
        conteo=('code', 'count'),
        additives_mediana=('additive_count', 'median')
    ).unstack(fill_value=0)

    # Aplanamos MultiIndex y calculamos % de penetración
    stats.columns = [f"{c[1]}_{c[0]}" for c in stats.columns]
    stats['total_proteina'] = stats['meat_fish_conteo'] + stats['plant_based_protein_conteo']
    stats['pct_analogos'] = (stats['plant_based_protein_conteo'] / stats['total_proteina']) * 100

    # 3. Integración con FAO
    fao_clean = fao_meat[fao_meat['Item'] == 'Meat, Total'][['Area', 'Value']].copy()
    df_mkt = pd.merge(stats.reset_index(), fao_clean, left_on='main_country', right_on='Area')

    # Reordenamiento explícito
    df_mkt['main_country'] = pd.Categorical(df_mkt['main_country'], categories=ORDEN_PAISES, ordered=True)
    df_mkt = df_mkt.sort_values('main_country')

    # 4. Visualización de Triple Eje
    fig, ax1 = plt.subplots(figsize=(16, 9))
    sns.set_style("white")

    x = np.arange(len(df_mkt))
    width = 0.35

    # EJE 1: Producción FAO (Barras Rojas)
    color_fao = '#B71C1C' 
    ax1.bar(x - width/2, df_mkt['Value'], width, label='Prod. Carne FAO (Mt)', color=color_fao, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Producción Ganadera (Mt)', fontsize=16, fontweight='bold', color=color_fao)
    ax1.tick_params(axis='y', labelcolor=color_fao, labelsize=14)

    # EJE 2: Cuota de Análogos (Barras Verdes)
    ax2 = ax1.twinx()
    color_pb = '#2E7D32' 
    ax2.bar(x + width/2, df_mkt['pct_analogos'], width, label='% Cuota Análogos', color=color_pb, alpha=0.8, edgecolor='black')
    ax2.set_ylabel('% Cuota Análogos (Market Share)', fontsize=16, fontweight='bold', color=color_pb)
    ax2.tick_params(axis='y', labelcolor=color_pb, labelsize=14)
    ax2.set_ylim(0, 100)

    # EJE 3: Complejidad Química (Línea Azul - MEDIANA)
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 80)) 
    color_add = "#000000"

    ax3.plot(df_mkt['main_country'].astype(str), df_mkt['plant_based_protein_additives_mediana'], 
             color=color_add, marker='s', markersize=12, linewidth=4, label='Mediana Aditivos (PB)')

    ax3.set_ylabel('Nº de Aditivos (Mediana)', fontsize=16, fontweight='bold', color=color_add)
    max_y = df_mkt['plant_based_protein_additives_mediana'].max()
    ax3.set_ylim(0, max_y + 2) 
    ax3.tick_params(axis='y', labelcolor=color_add, labelsize=14)

    # Estética y Títulos
    plt.title('Cultura Cárnica vs. Carga de Aditivos', fontsize=28, fontweight='bold', pad=45)

    ax1.set_xticks(x)
    ax1.set_xticklabels(ORDEN_PAISES, fontsize=18, fontweight='bold')

    # Leyenda unificada
    all_h, all_l = [], []
    for ax in [ax1, ax2, ax3]:
        h, l = ax.get_legend_handles_labels()
        all_h.extend(h)
        all_l.extend(l)
    ax1.legend(all_h, all_l, loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol=3, fontsize=14, frameon=True, shadow=True)

    sns.despine(right=False)
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

def plot_meat_culture_vs_protein(df, fao_meat, save_path=None):
    """2. Comparativa: Cultura Cárnica (FAO) vs. Densidad Proteica Vegetal (PB)."""
    # 1. Preparación de datos de Proteína (MEDIANA)
    df_pb_prot = df[
        (df['main_country'].isin(ORDEN_PAISES)) & 
        (df['category_unified'] == 'plant_based_protein')
    ].groupby('main_country')['proteins_100g'].median().reset_index()

    # 2. Preparación de datos FAO
    fao_total = fao_meat[fao_meat['Item'] == 'Meat, Total'][['Area', 'Value']].copy()

    # 3. Combinar y Ordenar
    df_comp = pd.merge(df_pb_prot, fao_total, left_on='main_country', right_on='Area')
    df_comp['main_country'] = pd.Categorical(df_comp['main_country'], categories=ORDEN_PAISES, ordered=True)
    df_comp = df_comp.sort_values('main_country')

    # 4. Visualización de Doble Eje
    fig, ax1 = plt.subplots(figsize=(16, 9))
    sns.set_style("white")

    x = np.arange(len(df_comp))
    width = 0.35

    # EJE 1: Producción Cárnica (Barras Rojas)
    color_fao = '#B71C1C'
    bar1 = ax1.bar(x - width/2, df_comp['Value'], width, label='Producción Carne FAO (Mt)', 
                   color=color_fao, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Producción Ganadera (Mt)', fontsize=18, fontweight='bold', color=color_fao)
    ax1.tick_params(axis='y', labelcolor=color_fao, labelsize=14)

    # EJE 2: Densidad Proteica Vegetal (Barras Verdes - MEDIANA)
    ax2 = ax1.twinx()
    color_pb = '#2E7D32'
    bar2 = ax2.bar(x + width/2, df_comp['proteins_100g'], width, label='Proteína Análogos (g/100g)', 
                   color=color_pb, alpha=0.8, edgecolor='black')
    ax2.set_ylabel('Calidad Vegetal: Proteínas (Mediana g/100g)', fontsize=18, fontweight='bold', color=color_pb)
    ax2.tick_params(axis='y', labelcolor=color_pb, labelsize=14)
    ax2.set_ylim(0, df_comp['proteins_100g'].max() * 1.2)

    # Estética y Etiquetas
    plt.title("Cultura Cárnica vs. Potencial Proteico Vegetal", fontsize=28, fontweight='bold', pad=40)
    ax1.set_xticks(x)
    ax1.set_xticklabels(ORDEN_PAISES, fontsize=18, fontweight='bold')

    # Anotaciones
    for i, rect in enumerate(bar2):
        height = rect.get_height()
        ax2.annotate(f'{height:.1f}g', 
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=13, fontweight='bold', color=color_pb)

    # Leyenda
    lines = [bar1, bar2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fontsize=14, frameon=True, shadow=True)

    sns.despine(right=False)
    plt.tight_layout()
    if save_path: plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

# ==========================================
# PIPELINE H04
# ==========================================

def pipeline_figuras_h04(df, fao_meat, output_dir=None):
    """Ejecuta los análisis estratégicos de la Hipótesis 04."""
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("📊 Iniciando Análisis Estratégico Internacional (H04)...")
    
    plot_market_penetration_additives(df, fao_meat, 
                                     save_path=(os.path.join(output_dir, "4_1_cultura_procesado.png") if output_dir else None))
    
    plot_meat_culture_vs_protein(df, fao_meat, 
                                 save_path=(os.path.join(output_dir, "4_2_cultura_proteina.png") if output_dir else None))
    
    print("✅ Análisis H04 completado.")
import pandas as pd
import re
import unicodedata

def filtrar_paises(df, columna='countries'):
    
    """
    Filtra y normaliza la distribución geográfica del dataset.
    Se ha utilizado una lista exhaustiva de variantes lingüísticas y códigos ISO para alimentar 
    el diccionario de unificación, permitiendo el cálculo de la variable 'main_country' 
    para segmentar el análisis por mercados clave.
    """
    
    # 1. Definimos los patrones de búsqueda (Regex), producidos a partir del archivo de texto lista_paises_crudos.txt
    patrones = {
        'Spain': r'Spain|España|Espagne|Espanha|ES|en:es',
        'France': r'France|Francia|França|FR|en:fr',
        'Germany': r'Germany|Alemania|Allemagne|Deutschland|DE|en:de',
        'United Kingdom': r'United Kingdom|UK|Reino Unido|Royaume-Uni|GB|en:gb|Great Britain',
        'Maghreb': r'Morocco|Maroc|Marruecos|Algeria|Algérie|Tunisia|Tunisie|MA|DZ|TN|en:ma|المغرب',
        'Italy': r'Italy|Italia|Italie|IT|en:it',
        'Benelux': r'Belgium|Belgique|België|Netherlands|Nederland|Pays-Bas|BE|NL',
        'Alpine (CH/AT)': r'Switzerland|Suisse|Schweiz|Austria|Österreich|CH|AT',
        'Nordics': r'Norway|Sweden|Sverige|Denmark|Danmark|Finland|Suomi|NO|SE|DK|FI',
        'Eastern Europe': r'Poland|Polska|Romania|România|Bulgaria|Czech|Hungary|PL|RO',
        'Americas': r'United States|USA|EEUU|Argentina|Mexico|México|Canada|US|MX|AR|CA',
        'Ireland': r'Ireland|Irlanda|en:ie|IE',
        'Portugal': r'Portugal|Portugália|en:pt|PT'
    }

    patron_global = '|'.join(patrones.values())
    
    # Filtramos el DataFrame original
    df_result = df[df[columna].str.contains(patron_global, case=False, na=False)].copy()

    # 2. Lógica de etiquetado priorizada
    def etiquetar_pais(row):
        val = str(row).lower()
        if any(term in val for term in ['spain', 'españa', 'espagne', 'es:']): return 'Spain'
        if any(term in val for term in ['france', 'frança', 'fr:']): return 'France'
        if any(term in val for term in ['germany', 'alemania', 'deutschland', 'de:']): return 'Germany'
        if any(term in val for term in ['united kingdom', 'uk', 'gb:', 'en:gb']): return 'United Kingdom'
        if any(term in val for term in ['morocco', 'maroc', 'marruecos', 'algeria', 'tunisia', 'ma:', 'المغرب']): return 'Maghreb'
        if any(term in val for term in ['switzerland', 'suisse', 'schweiz', 'austria', 'österreich', 'ch:', 'at:']): return 'Alpine (CH/AT)'
        if any(term in val for term in ['sweden', 'denmark', 'finland', 'norway', 'norge']): return 'Nordics'
        if any(term in val for term in ['belgium', 'belgique', 'netherlands', 'holland']): return 'Benelux'
        if any(term in val for term in ['poland', 'romania', 'bulgaria', 'hungary', 'czech']): return 'Eastern Europe'
        if any(term in val for term in ['ireland', 'ie:']): return 'Ireland'
        if any(term in val for term in ['italy', 'italia', 'it:']): return 'Italy'
        if any(term in val for term in ['usa', 'united states', 'mexico', 'argentina', 'canada']): return 'Americas'
        if any(term in val for term in ['portugal', 'pt:']): return 'Portugal'
        return 'Other / Global'

    df_result['main_country'] = df_result[columna].apply(etiquetar_pais)
    
    # LOG
    print(f"Log: Filtro de países aplicado. Registros resultantes: {len(df_result)}")
    
    return df_result

def unificacion_categorias(food_countries, columna='categories'):
    
    """
    Realiza una unificación taxonómica de las categorías de productos de Open Food Facts.
    
    Esta función aborda la complejidad de un dataset multilingüe y ruidoso mediante un sistema
    de clasificación jerárquico por "embudo" (funneling). Utiliza una lógica de prioridad
    donde el orden de los pasos es crítico para evitar falsos positivos.

    Lógica de Clasificación:
    ------------------------
    1. Limpieza de Ruido (Paso 0): Elimina etiquetas genéricas multilingües (ej: 'plant-based') 
       que suelen causar que productos sólidos se clasifiquen erróneamente como bebidas.
    
    2. Prioridad de Exclusión: 
       - Primero identifica proteínas animales, pero con un "veto" estricto: si el producto 
         menciona términos veganos o es una salsa/caldo, no se etiqueta como carne.
       - Segundo, rescata alternativas vegetales procesadas (Tofu, Heura, etc.) para que no
         se pierdan en categorías genéricas de vegetales.
    
    3. Manejo de Ambigüedades:
       - Los frutos secos y cremas se clasifican antes que los cereales para asegurar que 
         mantequillas de cacahuete (grasas) no se confundan con panes.
       - Las bebidas (Paso 10) actúan como último filtro y cuentan con un 'veto de sólidos'
         reforzado para garantizar que solo líquidos reales queden en esta categoría.

    Parámetros:
    -----------
    food_countries : pandas.DataFrame
        El DataFrame original que contiene las columnas 'product_name' y la columna de categorías.
    columna : str, opcional (defecto='categories')
        Nombre de la columna que contiene las etiquetas de categorías originales.

    Retorna:
    --------
    pandas.DataFrame
        DataFrame con la nueva columna 'category_unified' que contiene una de las 11 
        categorías normalizadas (meat_fish, plant_based_alternatives, dairy_eggs, 
        fats_sauces, cereals_bread, ready_to_eat, snacks_sweets, plant_based, 
        beverage, u 'Otros').
    """
    
    def clasificar(row):
        cat_raw = str(row[columna]).lower() if pd.notna(row[columna]) else ""
        nom_raw = str(row['product_name']).lower() if pd.notna(row['product_name']) else ""
        txt = (nom_raw + " " + cat_raw)

        # --- PASO 0: LIMPIEZA DE RUIDO ---
        ruido = [
            'plant-based foods and beverages', 'aliments et boissons à base de végétaux',
            'alimentos y bebidas de origen vegetal', 'alimentos e bebidas à base de plantas',
            'beverages and beverages preparations', 'boissons et préparations de boissons',
            'bebidas de origen vegetal', 'plant-based beverages', 'en:beverages'
        ]
        for r in ruido:
            txt = txt.replace(r, ' ')

        # --- PASO 1: PROTEÍNA ANIMAL (Carne/Pescado real) ---
        if any(p in txt for p in ['meat', 'viand', 'carn', 'pollo', 'chicken', 'poulet', 'fish', 'poisson', 'pescad', 'atún', 'thon', 'tuna', 'sardin', 'makreel', 'vis', 'maquereau', 'merluza', 'bacalao', 'ham', 'jambon', 'jamón', 'kebab']):
            # Veto: si es vegetal, condimento o salsa, NO es carne animal
            if not any(x in txt for x in ['vegan', 'vegetar', 'plant-based', 'falafel', 'tofu', 'veggie', 'beyond', 'fond ', 'bouillon', 'caldo', 'gravy', 'sauce', 'salsa', 'bologn']):
                return 'meat_fish'

        # --- PASO 2: ALTERNATIVAS VEGETALES (Sustitutos Procesados) ---
        if any(p in txt for p in ['soja', 'soya', 'soja nature', 'soja ungesüßt', 'soiabeverage', 'soyamilch', 'lait soja', 'steak', 'burger', 'sausage', 'salchicha', 'saucisse', 'nugget', 'boulette', 'falafel', 'pakora', 'beyond', 'impossible', 'veggie','tofu', 'tempeh', 'seitan', 'heura', 'soy-based', 'oat drink', 'alpro', 'milk substitute', 'bebida de soja', 'lait végétal', 'leche vegetal', 'vegan burger', 'haché végétal', 'vuna', 'meat-substitute', 'soja cuisine', 'röstis']):
            return 'plant_based_alternatives'

        # --- PASO 3: LÁCTEOS Y HUEVOS (Animal) ---
        if any(p in txt for p in ['oeuf', 'œuf', 'egg' ,'cheese', 'fromag', 'queso', 'yogurt', 'yaourt', 'milk', 'lait', 'lech', 'egg', 'oeuf', 'huev', 'dairy', 'kefir', 'pudding', 'creme', 'crème', 'nata']):
            if not any(x in txt for x in ['vegan', 'soja', 'oat', 'avena', 'alpro', 'vegetal', 'plant-based']): 
                return 'dairy_eggs'

        # --- PASO 4: FRUTOS SECOS Y CREMAS (Grasas) ---
        if any(p in txt for p in ['seeds', 'nuts', 'cacahuète', 'purée de cacahuète', 'purée cacahuète', 'pâte à tartiner', 'nut', 'noix', 'nuez', 'almond', 'amand', 'almendr', 'cashew', 'anacard', 'walnut', 'avellan', 'cacahuet', 'peanut', 'maní', 'pistach', 'seed', 'grain', 'semill', 'pindakaas', 'beurre de cacahuète', 'crema de cacahuete']):
            return 'seeds_nuts' 

        # --- PASO 5: CEREALES, PAN Y PASTA ---
        if any(p in txt for p in ['muesli', 'granola', 'flake', 'oat', 'avena', 'avoine', 'porridge', 'bread', 'pain', 'pan', 'mie', 'weetabix', 'pasta', 'pâte', 'riz', 'rice', 'arroz', 'couscous', 'fusilli', 'spaghetti']):
            return 'cereals_bread'

        # --- PASO 6: GRASAS, SALSAS Y CALDOS ---
        if any(p in txt for p in ['olej', 'casolare', 'rzepakowy', 'oil', 'huil', 'aceit', 'butter', 'beurr', 'mantequill', 'mayonnais', 'mustard', 'moutard', 'salsa', 'sauce', 'ketchup', 'pesto', 'spread', 'margarine', 'bouillon', 'caldo', 'levure', 'yeast', 'gravy', 'fond de veau', 'bologn']):
            return 'fats_sauces'

        # --- PASO 7: PLATOS PREPARADOS ---
        if any(p in txt for p in ['pizza', 'lasagna', 'sandwich', 'ready meal', 'preparado', 'mccain', 'frite', 'fries', 'hummus', 'sushi', 'choucroute']):
            return 'ready_to_eat'

        # --- PASO 8: DULCES Y SNACKS ---
        if any(p in txt for p in ['nocciolata', 'nutella', 'mermelada', 'confiture' ,'chocolat', 'candy', 'biscuit', 'gallet', 'confitur', 'jam', 'mermelad', 'chips', 'snack', 'bonbon', 'ice cream', 'helado', 'dessert', 'flan', 'pruneau']):
            return 'snacks_sweets'

        # --- PASO 9: VEGETALES Y FRUTAS ---
        if any(p in txt for p in ['beans', 'haricots', 'lentejas', 'lentilles', 'pois', 'tomato', 'tomat', 'vegetable', 'légume', 'verdur', 'fruit', 'fruta', 'legumbr', 'puree', 'purée', 'gazpacho', 'plant-based', 'avocado', 'aguacate', 'brocoli']):
            return 'plant_based'

        # --- PASO 10: BEBIDAS (Con veto reforzado de sólidos) ---
        if any(p in txt for p in ['water', 'eau', 'agua', 'juice', 'jus', 'zumo', 'soda', 'cola', 'coke', 'fanta', 'pepsi', 'coffee', 'café', 'tea', 'thé', 'té', 'drink', 'beverag', 'boisson', 'bebid', 'protein drink']):
            # Si el producto tiene cualquier rastro de comida sólida, NO es bebida
            veto_solidos = ['purée', 'puree', 'soja nature', 'ferment', 'soy-based', 'krispies', 'flakes', 'gazpacho', 'steak', 'burger', 'sausage', 'falafel', 'pakora', 'choucroute', 'puree', 'purée', 'fusilli', 'nugget', 'boulette', 'porridge', 'muesli', 'muesli', 'crispy']
            if not any(v in txt for v in veto_solidos):
                return 'beverage'

        return 'Otros'

    food_countries['category_unified'] = food_countries.apply(clasificar, axis=1)
    return food_countries


# Aumentamos la granuralidad de la categoria 'cereales/panes', separando esta en 'cerales/granos' y 'cereales_desayuno'
# Igualmente separamos la categoria 'alternativas_vegetales' en 'alternativas_lacteas_vegetales' y 'alternativas_carne_vegetales'

def refinar_categorias(df):
    
    """
    Realiza una segmentación granular de segundo nivel sobre las categorías unificadas.
    
    ESTRATEGIA DE DISEÑO:
    --------------------
    Esta función se aplica tras una clasificación inicial general. El objetivo de separar 
    el proceso en dos fases (Unificación -> Refinamiento) es evitar una complejidad excesiva 
    y errores de solapamiento en una sola pasada. 
    
    Al ejecutar este refinamiento a posteriori, garantizamos que solo los productos 
    ya identificados como "Cereales/Pan" o "Alternativas Vegetales" sean evaluados bajo 
    filtros más estrictos, mejorando la precisión científica del dataset final.

    Sub-segmentaciones realizadas:
    ------------------------------
    1. Cereales (cereals_bread): 
       - Separa 'breakfast_cereals' (ultraprocesados, mueslis, granolas) de 'bread_and_grains' 
         (productos base como pan, pasta o arroz). Esto es vital para un análisis de 
         Nutri-Score honesto, dado que los cereales de desayuno suelen tener perfiles 
         mucho más altos en azúcares.
    
    2. Alternativas Vegetales (plant_based_alternatives):
       - Divide entre 'plant_based_milks' (bebidas vegetales) y 'plant_based_protein' 
         (sustitutos de carne como tofu/hamburguesas y derivados fermentados). 
       - Aplica una lógica de exclusión cruzada para asegurar que productos sólidos 
         (steaks, burgers) no se clasifiquen como líquidos incluso si la etiqueta 
         menciona ingredientes base como "leche de soja".

    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame que ya ha pasado por la función 'unificacion_categorias'.

    Retorna:
    --------
    pandas.DataFrame
        Dataset refinado con categorías granulares listas para análisis estadístico.
    """
    
    # Creamos una copia para no alterar el original por accidente
    df_refined = df.copy()

    def granular(row):
        cat_actual = row['category_unified']
        cat_raw = str(row['categories']).lower() if pd.notna(row['categories']) else ""
        nom_raw = str(row['product_name']).lower() if pd.notna(row['product_name']) else ""
        txt = nom_raw + " " + cat_raw

        # 1. SEPARACIÓN DE CEREALES (Diferenciando Desayuno de Pan/Base)
        if cat_actual == 'cereals_bread':
            # Palabras clave de cereales de desayuno (procesados/dulces)
            keywords_breakfast = ['muesli', 'granola', 'flakes', 'pétales', 'crunchy', 'cruesli', 
                                  'honey', 'chocapic', 'cheerios', 'all bran', 'fitness', 'corn pops', 'weetabix', 'bisks', 'wheats']
            if any(k in txt for k in keywords_breakfast):
                return 'breakfast_cereals'
            else:
                return 'bread_and_grains' # Pan, arroz, pasta, harinas

        # 2. SEPARACIÓN DE ALTERNATIVAS VEGETALES (Proteína vs Leches)
        if cat_actual == 'plant_based_alternatives':
            # Palabras clave de bebidas/leches vegetales
            keywords_milks = ['drink', 'boisson', 'bebid', 'milk substitute', 'lait', 'leche', 'alpro', 'sojasun']
            
            # REGLA 3 + EXCLUSIÓN DE YOGURES:
            # Si contiene palabras de bebida PERO NO es yogur NI es carne vegetal (steak, burger, etc.)
            exclusiones_leche = ['yogurt', 'yaourt', 'pudding', 'ferment', 'saucisse', 'burger', 'steak', 'haché']
            
            if any(k in txt for k in keywords_milks) and not any(x in txt for x in exclusiones_leche):
                return 'plant_based_milks'
            else:
                return 'plant_based_protein' # Tofu, Heura, Hamburguesas, Yogures veg, Salchichas

        # Si no entra en los refinamientos, mantiene la categoría anterior
        return cat_actual

    df_refined['category_unified'] = df_refined.apply(granular, axis=1)
    
    # LOG
    print(f"Log: Refinamiento granular finalizado.")
    
    return df_refined

def normalizar(texto):
    
    """
MOTOR DE NORMALIZACIÓN Y CLASIFICACIÓN DE CORPORACIONES (Mapping Jerárquico)

Objetivo: 
Resolver la fragmentación de marcas en OpenFoodFacts, agrupando miles de variantes 
(ej: 'Nestlé', 'Nescafé', 'Maggi') bajo su entidad matriz (ej: 'Nestlé') para 
permitir un análisis de mercado por grupos corporativos.

Metodología en 3 etapas:
1. Normalización Fonética y Tipográfica: 
   La función 'normalizar' utiliza el estándar Unicode (NFD) para eliminar acentos, 
   cedillas y caracteres especiales. Transforma 'Nestlé' en 'nestle', asegurando 
   que errores de escritura en el dataset no afecten al agrupamiento.

2. Diccionario de Mapeo Multilevel:
   Estructura de datos exhaustiva que clasifica marcas por sectores estratégicos:
   - Grandes Multinacionales (Big Food).
   - Marcas de Distribuidor (Retailers/MDD): Hacendado, Lidl, Carrefour, etc.
   - Grupos Especializados (Lácteos, Bio, Bebidas).

3. Algoritmo de Búsqueda Optimizado (Motor de Búsqueda):
   - Prioridad por Longitud: Se ordenan las marcas de mayor a menor longitud para 
     evitar falsos positivos (ej: no confundir 'Mars' con 'Marshmallow').
   - Regex con 'Word Boundaries' (\b): Garantiza que se encuentre la marca exacta 
     y no una cadena de texto dentro de otra palabra.
   - Memoización (Memo): Sistema de caché para acelerar el procesamiento, calculando 
     solo una vez cada variante única de marca.
"""
    
    if pd.isna(texto): return ""
    # Transforma 'Nestlé' en 'Nestle' y pasa a minúsculas
    texto = unicode_str = unicodedata.normalize('NFD', str(texto))
    return "".join([c for c in unicode_str if unicodedata.category(c) != 'Mn']).lower().strip()

mapping = {
    # ======================
    # GRANDES MULTINACIONALES
    # ======================
    'Nestlé': [
        'nestle', 'nescafe', 'nescafé', 'nesquik', 'maggi', 'chocapic',
        'garden gourmet', 'le chocolat', 'lion', 'kitkat', 'after eight',
        'cookie crisp', 'golden grahams', 'herta', 'la laitiere', 'la laitière',
        'la laitiere, la laitière', 'mousline', 'vittel', 'perrier', 'badoit',
        'solis', 'buino', 'ricore', 'dolce gusto', 'cailler', 'ovomaltine',
        'ovo maltine', 'cappuccino, gold cappuccino, nescafé'
    ],

    'Unilever': [
        'unilever', 'marmite', 'hellmann', "hellman's", 'hellmanns',
        'knorr', 'knoor', 'amora', 'maizena', 'ben & jerry', 'ben & jerry\'s',
        'maille', 'frigo', 'ligeresa', 'calve', 'calvé', 'flora', 'planta fin',
        'flora proactiv', "fruit d'or", "fruit d'or proactiv, pro activ, proactiv, proactiv expert",
        "fruit d'or,becel", "fruit d'or proactiv,proactiv,proactiv expert,pro activ",
        'lipton', 'benedicta', 'bénédicta', 'skip', 'dove',
        'pukka', 'fruittare', 'the vegetarian butcher', 'magnum', 'magnum', 'miko', 'graze'
    ],

    'Mondelez': [
        'mondelez', 'lu', 'lu ', ' lu', 'lu,', 'lu.', 'milka', 'oreo',
        'toblerone', 'tuc', 'belvita', 'cadbury', 'philadelphia',
        'cote d’or', "cote d'or", "côte d'or", 'granola', 'heudebert',
        'pelletier', 'mikado', 'fontaneda', 'principe', 'príncipe', 'barny',
        'oscar mayer', 'belin', 'royal', 'daunat', 'jacob', 'mcvitie', 'nippon'
    ],

    'Danone': [
        'danone', 'activia', 'evian', 'volvic', 'alpro', 'hipro',
        'savane', 'font vella', 'lanjarón', 'les 2 vaches', 'oatly',
        'la salvetat', 'salvetat', 'vrai', 'charles & alice', 'michel & augustin',
        'michel et augustin', 'siggi', 'nyakas', 'danao'
    ],

    'Ferrero': [
        'ferrero', 'nutella', 'kinder', 'rocher', 'tic tac', 'tictac',
        'raffaello', 'mon cheri', 'mon chéri', 'mon chéri', "MON CHÉRI"
    ],

    'PepsiCo': [
        'pepsico', 'pepsi', 'lays', "lay's", 'lay&#039;s', 'doritos', 'cheetos',
        'alvalle', 'quaker', 'gatorade', 'tropicana', 'cruesli', 'matutano',
        'benenuts', 'sun bites', 'sun bites', 'walkers', 'AQUAFINA'
    ],

    'Coca-Cola': [
        'coca-cola', 'coca cola', 'coke', 'fanta', 'sprite', 'fuze tea',
        'aquarius', 'minute maid', 'pulco', 'honest', 'innocent', 'powerade',
        'monster energy', 'nestea', 'adez', 'cappy', 'smartwater',
        'the coca cola company'
    ],

    'Kellogg': [
        'kellogg', "kellog's", 'special k', 'all-bran', 'frosties',
        'smacks', 'tresor', 'cheerios', 'cheerios multigrain', 'pringles', 'Pringles', 'PRINGLES'
    ],

    'General Mills': [
        'general mills', 'nature valley', 'old el paso', 'haagen-dazs',
        'häagen-dazs', 'jus rol', 'pillsbury', 'green giant', 'gigante verde', 'yoplait', 'yop', 'petit filous'
    ],

    'Kraft Heinz': [
        'heinz', 'kraft', 'orlando', 'hp sauce', 'lea & perrins'
    ],

    'Mars Wrigley': [
        'mars', 'm&m', "m&m's", 'snickers', 'twix', 'orbit', 'skittles',
        'maltesers', 'celebrations', 'reese', 'whiskas', 'pedigree',
        'ebly', "ben's original", 'suzi wan'
    ],

    'Dr. Oetker': [
        'dr. oetker', 'dr oetker', 'alsa', 'ancel', 'condi', 'muesli crunchy',
        'muesli crunchy'
    ],

    'Deoleo / Aceites': [
        'deoleo', 'carapelli', 'bertolli', 'carbonell', 'koipe', 'hula'
    ],

    'Valeo Foods': [
        'valeo foods', 'balconi', 'kettle', 'kettle chips', 'rowan hill'
    ],

    'Princes Group': [
        'princes', 'napolina', 'juver'
    ],

    'Ecotone / Wessanen': [
        'ecotone', 'wessanen', 'bjorg', 'alter eco',
        'allos', 'clipper', 'tanoshi', 'zonnatura', 'whole earth', 'isitar'
    ],

    'Upfield': [
        'becel', "fruit d'or", 'proactiv', 'pro activ',
        "fruit d'or proactiv,proactiv,proactiv expert,pro activ",
        "fruit d'or,becel", "fruit d'or proactiv, pro activ, proactiv, proactiv expert",
        "fruit d'or proactiv,proactiv,proactiv expert, pro activ"
    ],

    # ======================
    # MARCAS DE DISTRIBUIDOR / RETAILERS
    # ======================

    'Hacendado / Mercadona': [
        'hacendado', 'mercadona', 'deliplus', 'compy', 'bosque verde',
        'entrepinares', 'facendado', 'FACENDADO'
    ],

    'Lidl': [
        'lidl', 'alesto', 'milbona', 'fin carré', 'fin carre', 'sondey',
        'freshona', 'crownfield', 'vemondo', 'vermondo', 'baresa',
        'j.d. gross', 'bellarom', 'combino', 'italiamo', 'snack day',
        'envia', 'nixe', 'maribel', 'saguaro', 'trattoria', 'gelatelli',
        'toque du chef', 'duc de coeur', 'deluxe', "vitad'or",
        "vita d'or", 'belbake', 'primadonna', 'solesita', 'tastino',
        'harvest basket', 'maître jean pierre', 'maitre jean pierre',
        'mister choc', 'favourina', 'favorina', 'rivercote', 'solevita'
    ],

    'Carrefour / Système U / Intermarché': [
        'carrefour', 'reflets de france', 'eco +', 'eco+',
        'nos regions ont du talent', 'nos régions ont du talent',
        'nos regions ont du talent', 'nos régions ont du talent',
        'u bio', 'magasins u', 'u ', 'u,', 'u', 'paturages', 'pâturages',
        'páturages', 'paturages, sélection des mousquetaires',
        'sélection des mousquetaires', 'les mousquetaires',
        'nos regions ont du talent', 'nos régions ont du talent',
        'itineraires des saveurs', 'itinéraire des saveurs',
        'itinéraire des saveurs, les mousquetaires',
        'itineraires de nos regions',
        'saveurs de nos regions', 'saveurs de nos régions',
        'saveurs de nos régions', 'saveurs de nos regions'
    ],

    'Leclerc': [
        'e.leclerc', 'bio village', 'marque repère', 'marque repere',
        'saveurs de nos régions', 'saveurs de nos regions'
    ],
    
    'Aldi': [
        'aldi', 'harvest morn', 'savour bakes', 'specially selected', 
        'the foodie market', 'village bakery', 'bramwells', 'brooklea', 'four seasons', 'valencia'
    ],

    'Retail Internacional (Otros)': [
        'tesco', 'sainsbury', 'waitrose', 'marks & spencer', 'marks and spencer',
        'm&s', 'auchan', 'migros', 'coop', 'picard', 'costco',
        'asda', 'morrisons', 'système u', 'dia', 'el corte inglés',
        'mcennedy', 'stockwell', 'monoprix', 'woolworths food',
        'co op', 'the co-operative loved by us',
        'kirkland', 'kirkland signature', "member's mark"
    ],
    
    'Intermarche': [
        'intermarche', 'intermarché', 'chabrior', "bouton d'or"
    ],

    # ======================
    # GRANDES GRUPOS LÁCTEOS / QUESOS
    # ======================

    'Lactalis / Bel': [
        'lactalis', 'président', 'president', 'galbani', 'lactel', 'puleva',
        'lauki', 'société', 'société', 'bridelice', 'bridelight',
        'kiri', 'babybel', 'la vache qui rit', 'boursin', 'leerdammer',
        'candia', 'milsa', 'pilos', 'grand fermage', 'le petit basque',
        'la laitìère', 'la laitière', 'la laitiere', 'nurishh'
    ],

    'Savencia': [
        'savencia', 'st moret', 'saint moret', 'tartare', 'caprice des dieux',
        'saint agur', 'elle & vire', 'elle&vire', 'cœur de lion', 'chavroux',
        'bordeau chesnel', 'le rustique', 'fromarsac', 'rians'
    ],

    'FrieslandCampina': [
        'frieslandcampina', 'milko', 'longley farm'  
    ],

    'Arla': [
        'arla', 'castello', 'lurpak' 
    ],

    # ======================
    # OTROS GRANDES GRUPOS EUROPEOS
    # ======================

    'Barilla / Pasta': [
        'barilla', 'wasa', 'mulino bianco', 'harry', 'harrys',
        'de cecco', 'rummo', 'panzani', 'giovanni rana', 'rana',
        'misura', 'garofalo', 'jacquet', 'gran cereale', 'gran cereale'
    ],

    'Associated British Foods (ABF)': [
        'jordans', 'dorset cereals', 'twinings', 'ryvita', 'patak',
        'primark', 'allinson', 'kingsmill', 'silver spoon'
    ],

    'Ebro Foods / Mutti': [
        'ebro foods', 'brillante', 'sos', 'lustucru', 'taureau ailé',
        'tilda', 'mutti', 'liebig'
    ],
    
    'GB Foods': [
        'star', 'gallina blanca', 'avecrem', 'yatekomo'

    ],

    'Grandes Grupos Europeos': [
        'fleury michon', 'fleurs michon', 'bonne maman', 'andros',
        'gerblé', 'gerble', 'bonduelle', 'brioche pasquier', 'pasquier',
        'st michel', 'saint michel', 'la boulangère', 'la boulangere',
        'sodebo', 'tipiak', 'gullon', 'gullón', 'cuetara', 'cuétara',
        'mccain', 'mc cain', 'findus', 'bimbo', 'haribo', 'ricola',
        'st hubert', 'paysan breton', 'lotus', 'weetabix', 'pascual',
        'don simón', 'don simon', 'elpozo', 'campofrío', 'campofrio',
        'marie', 'petit navire', 'saupiquet', 'connetable', 'connétable',
        'poulain', 'lucien georgelin', 'pierre martinet', "d'aucy",
        'soignon', 'lesieur', 'quorn', 'entremont', 'william saurin',
        'jaouda', 'chergui', 'aicha', 'cassegrain', 'brets', "bret's",
        'warburtons', 'vico', 'seeberger', 'puget', 'primevère',
        'brossard', 'le gaulois', 'lutti', 'lune de miel', 'francine',
        'le ster', 'coraya', 'storck', 'hovis', 'tramier', 'yeo valley',
        'filippo berio', 'kikkoman', 'saclà', 'lindt', 'sprüngli',
        'bahlsen', 'bahlsen,leibniz', 'leibniz', 'Lotus Bakeries', 
        'lotus', 'nakd', 'bear', 'biscoff'

    ],

    # ======================
    # BIO / SALUD (GRUPOS GRANDES)
    # ======================

    'Léa Nature / Bio Salud': [
        'jardin bio', 'jardin bio étic', 'lea nature', 'léa nature',
        'karelea', 'bisson', 'evernat', 'ethiquable', 'éthiquable',
        'cereal bio', 'céréal bio', 'sojasun', 'taifun', 'soy',
        'happyvore', 'ecomil', 'eco mil', 'alnatura', 'huel',
        'deliciously ella', 'violife', 'pure via', 'dmbio', 'bio u',
        'isola bio', 'schar', 'kallo', 'bio & me', 'nairns', 'proper', 'crosta & mollica'
    ],

    # ======================
    # BEBIDAS / ALCOHOL
    # ======================

    'Bebidas no alcohólicas (otros grupos)': [
        'red bull', 'redbull', 'schweppes', 'orangina', 'teisseire',
        'cristaline', 'joker', 'pago', 'solan de cabras', 'bezoya',
        'san benedetto', 'oasis', 'robinsons', 'vita coco', 'champomy',
        'mogu mogu', 'mogu mogu (sappé)', 'thanon', 'campo largo',
        'hawai', 'HAWAI', 'champomy'
    ],

    'Cerveceras / Alcohol': [
        'estrella damm', 'estrella galicia', 'heineken', 'peroni',
        'budweiser', 'mahou', '1664', 'leffe', 'grimbergen',
        'tourtel', 'tourtel twist', 'tourtel twist citron',
        'tourtel twist framboise', 'tourtel twist pêche'
    ],

    # ======================
    # Especialistas / Líderes de Categoría
    # ======================

    'CHO Group (Terra Delyssa)': [
        'terra delyssa', 'terra delyssa estate', 'TERRA DELYSSA'
    ],

    'Ekibio / Le Pain des Fleurs (Léa Compagnie Biodiversité)': [
        'ekibio, le pain des fleurs', 'ekibio,le pain des fleurs',
        'le pain des fleurs', 'le pain des fleurs, ekibio',
        'ekibio', 'le moulin du pivert', 'le moulin du pivert', 'priméal'
    ],

    'La Fournée Dorée (grupo familiar francés)': [
        'la fournée dorée', 'la fournee doree', 'la fournée dorée',
        'la fournée dorée', 'la fournee doree'
    ],

    'Heura Foods': [
        'heura'
    ],

    'Samyang': [
        'samyang', 'buldak,samyang', 'buldak'
    ],

    'Lee Kum Kee': [
        'lee kum kee'
    ],

    'Ayam': [
        'ayam'
    ],

    'Artiach (Grupo Bimbo)': [
        'artiach'
    ],

    'Birds Eye / Nomad Foods': [
        'birds eye'
    ],

    'Mission (Gruma)': [
        'mission', 'gruma,mission wrap'
    ],

    'Mizkan': [
        'mizkan'
    ],

    'Mentos / Perfetti Van Melle': [
        'mentos', 'mentos,perfetti'
    ],

    'Tabasco / McIlhenny': [
        'tabasco', 'mcIlhenny company, tabasco', 'avery island la, mcihenny company, tabasco'
    ],

    'Rügenwalder Mühle': [
        'rügenwalder mühle'
    ],

    'Ritter Sport': [
        'ritter sport', 'RITTER SPORT'
    ],

    'Idilia Foods': [
        'valor', 'VALOR', 'nocilla', 'cola cao', 'colacao', 'colacaoidilia foods'
    ],
    
    'Anouar Invest': [
        'excelo', 'jibal', 'badaouia'
    ]
    
}

def clasificar_marcas(df, columna_brands, diccionario):
    # APLANAR Y NORMALIZAR EL DICCIONARIO
    flat_mapping = []
    for corp, marcas in diccionario.items():
        for m in marcas:
            # Guardamos la marca del diccionario ya normalizada
            flat_mapping.append((normalizar(m), corp))
    
    # Ordenar por longitud para máxima precisión
    flat_mapping.sort(key=lambda x: len(x[0]), reverse=True)

    memo = {}

    def motor_busqueda(texto_original):
        if pd.isna(texto_original) or texto_original == "": return 'Desconocido'
        
        # Normalizamos la marca que viene del dataset
        texto_norm = normalizar(texto_original)
        
        if texto_norm in memo: return memo[texto_norm]

        # Búsqueda optimizada
        for marca_hija_norm, corp_padre in flat_mapping:
            if marca_hija_norm in texto_norm:
                if re.search(rf'\b{re.escape(marca_hija_norm)}\b', texto_norm):
                    memo[texto_norm] = corp_padre
                    return corp_padre
                
        memo[texto_norm] = 'Otras / Local'
        return 'Otras / Local'

    # Ejecución sobre valores únicos
    marcas_unicas = df[columna_brands].unique()
    mapa_final = {marca: motor_busqueda(marca) for marca in marcas_unicas}
    
    df['corporation'] = df[columna_brands].map(mapa_final)
    
    cobertura = (df['corporation'] != 'Otras / Local').mean() * 100
    print(f"Log: Clasificación de marcas completada. Cobertura: {cobertura:.2f}%")
    
    return df

def clasificar_bio(df, columna='labels'):
    """
    Identifica productos orgánicos/bio mediante la búsqueda de sellos y variantes 
    lingüísticas en la columna de etiquetas.
    
    Parámetros:
    -----------
    df : pandas.DataFrame
        Dataset de entrada.
    columna : str, opcional (defecto='labels')
        Columna donde buscar los sellos bio.

    Retorna:
    --------
    pandas.DataFrame : Dataset con la nueva columna booleana 'is_bio'.
    """
    
    # 1. Definimos el patrón de búsqueda (Regex)
    # Lo mantenemos dentro para que la función sea autónoma
    bio_pattern = (
        r'(?i)\b(?:'
        r'bio|eco|organic|organico|biologique|biologico|biologisch|ekologisk|ekologiczny|ökologisch|öko|'
        r'biomilch|bio-organic|bio-européen|bio-équitable|bio-dynamie|'
        r'agriculture biologique|ab agriculture biologique|nature et progrès|biopartenaire|'
        r'bioland|naturland|demeter|eg-öko-verordnung|eu-öko-verordnung|'
        r'ecológico|ecologico|biológico|biologico ue|orgânico|organico eu|'
        r'eu organic|usda organic|certified organic|aco certified organic|soil association organic|'
        r'organic food federation|canada organic|'
        r'[a-z]{2}-bio-\d+|[a-z]{2}-öko-\d+|[a-z]{2}-org-\d+|[a-z]{2}-eko-\d+|'
        r'at-bio-301|at-bio-901|be-bio-01|be-bio-02|ch-bio-004|ch-bio-006|cz-bio-001|'
        r'de-öko-\d+|es-eco-\d+|fr-bio-\d+|it-bio-\d+|nl-bio-01|pl-eko-\d+|pt-bio-\d+|'
        r'био|биологично|biological'
        r')\b'
    )

    # 2. Creamos la columna booleana
    # Usamos .copy() para evitar avisos de SettingWithCopy
    df = df.copy()
    df['is_bio'] = df[columna].str.contains(bio_pattern, case=False, na=False)

    # 3. Métricas rápidas (Log de consola)
    porcentaje_bio = (df['is_bio'].mean() * 100).round(2)
    print(f"Log: Clasificación Bio completada. Cobertura: {porcentaje_bio}%")
    
    return df

"""
Creamos un diccionario para crear una función que genere columnas booleanas
que indican la presencia o ausencia de ingredientes clave en cada producto, y un contador aproximado
de aditivos (multiidioma).
"""

def extraer_ingredientes_clave(df, columna='ingredients_text'):
    df_ing = df.copy()

    # Diccionario maestro con Regex tamizado (Multilingüe)
    dicc_ingredientes = {
        # GRASAS Y ACEITES
        'has_palm_oil': r'palm(?:a|e|iste|fat|fett|öl)|aceite.*palma|huile.*palme',
        'has_olive_oil': r'oliv(?:a|e|enöl)|azeite.*oliva|huile.*olive',
        'has_sunflower_oil': r'girasol|sunflower|tournesol|sonnenblumen',
        'has_rapeseed_oil': r'colza|rapeseed|canola|rapsöl|nabina',
        'has_coconut_oil': r'coco(?:nut|tier|s)?|koko(?:s|söl|sfett)',

        # CEREALES
        'has_wheat': r'trig(?:o|u)|wheat|blé|weizen|frumento',
        'has_oat': r'aven(?:a|e)|oat|avoine|hafer',
        'has_corn': r'ma(?:íz|iz|is|ize)|corn|korns?|granoturco',
        'has_rye': r'centeno|rye|seigle|roggen|segale',
        'has_barley': r'cebad(?:a)|barley|orge|gerst(?:e|en)',
        'has_rice': r'arroz|rice|riz|reiss?|riso',

        # AZÚCARES
        'has_added_sugar': r'sugar|sucre|zucchero|azúcar|zucker|açúcar|dextros(?:e|a)|fructos(?:e|a)|glucos(?:e|a)',
        'has_syrup': r'syrup|sirop|sciroppo|jarabe|xarope|sirup',

        # OTROS
        'has_soy': r'soja|soy(?:bean)?|soya',
        'has_nuts': r'hazelnut|noisette|avellan|mandeln?|almond|amand|anacard|cashew|walnut|noix'
    }
    
    for col_name, pattern in dicc_ingredientes.items():
        # Creamos una columna booleana para cada ingrediente del diccionario
        df_ing[col_name] = df_ing[columna].str.contains(pattern, case=False, na=False)

    # Contador de aditivos MULTIIDIOMA (EN/FR/NL/AR)
    def contar_aditivos_multilenguaje(text):
        if pd.isna(text):
            return 0

        text_upper = str(text).upper()

        # E-numbers (universal)
        e_nums = len(re.findall(r'E\d{3,4}', text_upper))

        # Keywords MULTIIDIOMA
        keywords_multi = {
            # Conservantes
            'BENZOATO', 'BENZOATE', 'ACIDE BENZOÏQUE', 'BENZOËZUURZOUT', 'بنزوات',
            'SORBATO', 'SORBATE', 'SORBATE DE POTASSIUM', 'SORBAT', 'سوربات',
            'SULFITO', 'SULFITE', 'SULFITE DE SODIUM', 'SULFIET', 'سلفيت',

            # Antioxidantes
            'ASCORB', 'VITAMINE C', 'ACIDE ASCORBIQUE', 'ASCORBIJZURE',
            'GALATO', 'GALATE', 'BHT', 'BHA',

            # Emulsionantes
            'LECITIN', 'LÉCITINE', 'LECITHINE', 'XANTAN', 'XANTHANE',
            'GUAR', 'GOMME DE GUAR', 'CARRAG', 'CARRAGHÉNANE',

            # Edulcorantes artificiales
            'ASPARTAM', 'ACÉSULFAME', 'ACESULFAAMKALI', 'SACCHARINE'
            
            # EMULSIFICANTES (las más frecuentes - 40%+ de las líneas)
            'EMULSIF', 'EMULSI', 'EMULGENT', 'EMULGAT', 'EMULGE', 'EMULSION',
            'EMULSIFIANT', 'EMULSIFIANTS', 'EMULSIFICANT', 'EMULSIFICANTS',
            'EMULGENTE', 'EMULGENTES', 'EMULGATOR', 'EMULGATORES',
            'EMULSIFIK', 'EMULGÁLÓSZER', 'EMULGEÁLÓSZEREK', 'EMULGÁLÓSZEREK',
    
            # LECITINAS (muy específicas y frecuentes)
            'LECITIN', 'LECITHIN', 'LECITINE', 'LECITYN', 'LECITINA', 
            'LÉCITINE', 'LECITHINE', 'LECYTIN', 'LECYTYNA',
            
            # PRESERVANTES/CONSERVANTES
            'PRESERV', 'PRESERVAT', 'PRESERVATIVE', 'PRESERVANTES',
            'CONSERV', 'CONSERVANT', 'CONSERVANTE', 'CONSERVANTES',
            'CONSERVING', 'CONSERVATIF', 'CONSERVATIFS',
            
            # COLORANTES
            'COLOUR', 'COLOR', 'COLORANT', 'COLORANTE', 'COLORANTS', 'COLORING',
            'COLORANTS', 'COLORANTE', 'COLOURING', 'COLORIFICIAL',
            
            # EDULCORANTES
            'SWEETEN', 'SWEETENER', 'SWEETENERS',
            'ÉDULCOR', 'EDULCOR', 'EDULCORANT', 'EDULCORANTE', 'ÉDULCORANTS',
            
            # ESTABILIZANTES (muy frecuentes)
            'STABILIS', 'STABILIZ', 'STABILISANT', 'STABILISANTS',
            'STABILISER', 'STABILISERS', 'STABILIZER', 'STABILIZERS',
            
            # ESPESANTES/GELIFICANTES
            'THICKEN', 'THICKENER', 'THICKENERS',
            'GELIFIANT', 'GELIFIANTS', 'GELIFICANT', 'GELIFICANTS',
            'GELLING', 'GELING', 'GOMME', 'GOMAS',
            
            # ANTIOXIDANTES (además de los tuyos)
            'ANTIOX', 'ANTIOXYD', 'ANTIOXIDANT', 'ANTIOXIDANTS',
            'ANTIOXYDANT', 'ANTIOXYDANTS',
            
            # ACIDIFICANTES
            'ACIDIFIANT', 'ACIDIFIANTS', 'ACIDIFIER', 'ACIDIFYING',
            'ACIDULANT', 'ACIDULANTS',
            
            # AGENTES DE TRATAMIENTO/TRATAMIENTO
            'AGENT DE TRAITEMENT', 'AGENT TRAITEMENT', 'TRATAMIENTO',
            'PROCESSING AID', 'PROCESSING AGENT',
            
            # LEVADURAS LEVANTADORES
            'RAISING AGENT', 'LEAVENING AGENT', 'LEVANTADOR', 'LEVURE',
            
            # VARIAS FAMILIAS detectadas en el TXT [file:57]
            'FLAVOUR ENHANCER', 'EXHAUSTEUR DE GOUT',
            'MOISTURE RETAINING AGENT', 'AGENT DE RETENCIÓN D\'HUMIDITÉ',
            'ACIDITY REGULATOR', 'RÉGULATEUR D\'ACIDITÉ'
        }
        
        keyword_count = sum(text_upper.count(kw) for kw in keywords_multi)
        
        return e_nums + keyword_count

    # Aplicar contador de aditivos 
    df_ing['additive_count'] = df_ing[columna].apply(contar_aditivos_multilenguaje)
    
    print(f"Log: Extracción de ingredientes y aditivos finalizada.")

    return df_ing

def eliminar_categorias_residuales(df, columna='category_unified'):
    """
    Elimina del dataset los productos que no han podido ser clasificados 
    en las categorías principales (etiquetados como 'Otros').
    """
    # 1. Guardamos el número de filas antes de limpiar
    antes = len(df)
    
    # 2. Creamos el nuevo DataFrame filtrado
    df_filtered = df[df[columna] != 'Otros'].copy()
    
    print(f"Log: Categorías residuales eliminadas. (Descartados: {antes - len(df_filtered)})")
  
    return df_filtered


def imputar_fibra_condicional(df, col_cat='category_unified', col_fibra='fiber_100g'):
    """
    Imputa con 0 la fibra en categorías donde biológicamente no existe 
    y elimina registros con nulos en categorías donde la fibra es esencial.
    """
    df = df.copy()

    # 1. Categorías donde la fibra es biológicamente 0
    cats_cero_biologico = [
        'dairy_eggs', 
        'meat_fish', 
        'beverage', 
        'alcoholic_beverages', 
        'fats_sauces', 
        'supplements_nutrition'
    ]

    # 2. Imputación controlada: Solo a las categorías de la lista
    mask_cero = df[col_cat].isin(cats_cero_biologico)
    df.loc[mask_cero, col_fibra] = df.loc[mask_cero, col_fibra].fillna(0)

    # 3. Eliminación de nulos residuales
    # (Para el resto de categorías, si no hay fibra, descartamos el producto)
    df = df.dropna(subset=[col_fibra])
    
    print(f"Log: Imputación de fibra completada.")

    return df

def optimizar_integridad_dataset(df):
    """
    Realiza la limpieza final de nulos en nutrientes críticos, normaliza 
    columnas de texto y ajusta la estructura para el análisis final.
    """
    df = df.copy()

    # 1. Filtrado por integridad nutricional
    cols_criticas = [
        'energy-kcal_100g', 'proteins_100g', 'fat_100g', 
        'saturated-fat_100g', 'carbohydrates_100g', 
        'sugars_100g', 'salt_100g'
    ]
    # Eliminamos registros que no sirven para cálculos nutricionales
    df = df.dropna(subset=cols_criticas)

    # 2. Imputación de variables de texto y categorías
    mapeo_nulos = {
        'product_name': 'Producto sin nombre',
        'brands': 'Marca desconocida',
        'ingredients_text': 'Ingredientes no informados',
        'labels': 'sin etiquetas',
        'categories': 'no clasificado'
    }
    
    for col, valor in mapeo_nulos.items():
        if col in df.columns:
            df[col] = df[col].fillna(valor)
            if df[col].dtype == 'object':  # Normalización de texto
                df[col] = df[col].str.lower().str.strip()

    # 3. Tratamiento de NOVA (Valor centinela 0)
    if 'nova_group' in df.columns:
        df['nova_group'] = df['nova_group'].fillna(0).astype(int)

    # 4. Limpieza de columnas sobrantes
    if 'quantity' in df.columns:
        df = df.drop(columns=['quantity'])

    # 5. Reset de índice para evitar huecos tras el dropna
    df = df.reset_index(drop=True)

    print(f"Log: Integridad del dataset optimizada. Tamaño final: {len(df)}")

    return df

def pipeline_limpieza_completa(df, mapping_marcas):
    """
    Ejecuta el flujo completo de limpieza en el orden óptimo.
    """
    df_clean = filtrar_paises(df)
    df_clean = unificacion_categorias(df_clean)
    df_clean = refinar_categorias(df_clean)
    df_clean = eliminar_categorias_residuales(df_clean)
    df_clean = clasificar_marcas(df_clean, 'brands', mapping_marcas)
    df_clean = clasificar_bio(df_clean)
    df_clean = extraer_ingredientes_clave(df_clean)
    df_clean = imputar_fibra_condicional(df_clean)
    df_clean = optimizar_integridad_dataset(df_clean)
    
    print("✅ Pipeline finalizado con éxito.")
    
    return df_clean

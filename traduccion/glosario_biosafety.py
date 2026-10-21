"""Etiquetas del modelo de bioseguridad que no existen en la traducción publicada.

Son los nombres de categorías, de perfiles de resultados y de las gráficas. Se
conserva la decoración original (asteriscos y guiones), porque la aplicación la
usa para mostrar la jerarquía del cuestionario. La redacción sigue la que ya
emplea la traducción publicada de Sandia.
"""

# Títulos de módulo y de categoría.
CATEGORIAS = {
    'Facility': 'Centro',
    'Agent': 'Agente',

    '*********Likelihood of Exposure**********':
        '*********Probabilidad de exposición**********',
    '-Potential of Exposure from Laboratory Processes-':
        '-Posible exposición por los procesos del laboratorio-',
    '* Type of Material': '* Tipo de material',
    '* Inhalation Exposure': '* Exposición por inhalación',
    '* Percutaneous Exposure': '* Exposición percutánea',
    '* Decontamination': '* Descontaminación',
    '* Contact Exposure': '* Exposición por contacto',
    '-Potential of Exposure from Animals-': '-Posible exposición por los animales-',
    '* Q-Animals': '* Q-Animales',
    '* General Animals': '* Animales en general',

    '**********Main Category: Mitigations**********':
        '**********Categoría principal: Mitigaciones**********',
    '* Standard Procedures': '* Procedimientos estándar',
    '* Management': '* Gestión',
    '* General Procedures': '* Procedimientos generales',
    '-Animals': '-Animales',
    '-Procedures': '-Procedimientos',
    '* Containment': '* Contención',
    '* PPE': '* EPP',

    '********** Main Category: Consequences **********':
        '********** Categoría principal: Consecuencias **********',
    '-Consequences of Diseases to Humans-':
        '-Consecuencias de la enfermedad para los seres humanos-',
    '-Consequences of Diseases to Animals-':
        '-Consecuencias de la enfermedad para los animales-',
    '-Secondary Consequences-': '-Consecuencias secundarias-',
    '* Mortality': '* Mortalidad',
    '* Morbidity': '* Morbilidad',
    '* Agent Characteristics': '* Características del agente',
    '* Species': '* Especies',
    'Mitigation': 'Mitigación',
    '* Routes': '* Vías',
    '* Transmission': '* Transmisión',
    '* Stability': '* Estabilidad',
    '* Reportability': '* Notificación',
    'Humans': 'Seres humanos',
    'Animals': 'Animales',

    '-Individual likelihood of Infection-': '-Probabilidad de infección individual-',
    '* Ingestion': '* Ingestión',
    '* Inhalation': '* Inhalación',
    '* Percutaneous': '* Percutánea',
    '* Direct Contact': '* Contacto directo',
}

# Perfiles de resultados y operaciones del motor de cálculo. Solo se ven en el
# editor de perfiles y en el reporte; no afectan el cálculo.
RESULTADOS = {
    'Likelihood Inhalation Individual': 'Probabilidad por inhalación (individuo)',
    'Likelihood Percutaneous Individual': 'Probabilidad percutánea (individuo)',
    'Likelihood Contact Individual': 'Probabilidad por contacto (individuo)',
    'Likelihood Ingestion Individual': 'Probabilidad por ingestión (individuo)',
    'Likelihood Inhalation Community': 'Probabilidad por inhalación (comunidad)',
    'Likelihood Percutaneous Community': 'Probabilidad percutánea (comunidad)',
    'Likelihood Contact Community': 'Probabilidad por contacto (comunidad)',
    'Likelihood Ingestion Community': 'Probabilidad por ingestión (comunidad)',
    'Likelihood Inhalation Animal': 'Probabilidad por inhalación (animales)',
    'Likelihood Percutaneous Animal': 'Probabilidad percutánea (animales)',
    'Likelihood Contact Animal': 'Probabilidad por contacto (animales)',
    'Likelihood Ingestion Animal': 'Probabilidad por ingestión (animales)',
    'Likelihood of Secondary Transmission Human':
        'Probabilidad de transmisión secundaria (seres humanos)',
    'Likelihood of Secondary Transmission Animal':
        'Probabilidad de transmisión secundaria (animales)',
    'Consequence of Disease to Humans':
        'Consecuencia de la enfermedad para los seres humanos',
    'Consequence of Disease to Animals':
        'Consecuencia de la enfermedad para los animales',
    'Consequence of Disease to the Community':
        'Consecuencia de la enfermedad para la comunidad',
    'Secondary Consequence of Disease to Humans':
        'Consecuencia secundaria de la enfermedad para los seres humanos',
    'Secondary Consequence of Disease to Animals':
        'Consecuencia secundaria de la enfermedad para los animales',

    'Square Root': 'Raíz cuadrada',
    'Normalization': 'Normalización',
    'Normalize': 'Normalizar',
    'Nomalize': 'Normalizar',
    'Normalization Divide': 'División de normalización',
    'Normalization Op': 'Operación de normalización',
    'Normalization Constant': 'Constante de normalización',
    'Norm Const': 'Const. de norm.',
    '1': '1',
    'Community Disease Multiplier (Add 5%)':
        'Multiplicador de enfermedad en la comunidad (suma 5 %)',
    # RRF (Risk Reduction Factor) se conserva como en la guía del usuario.
    'RRF': 'RRF',
    'Obtain RRF': 'Obtener el RRF',
    'Obtaining the RRF': 'Obtención del RRF',
    'Apply weight to cross-normalized category compination':
        'Aplicar el peso a la combinación de categorías normalizadas de forma cruzada',
}

# Gráficas: título, ejes y leyendas.
GRAFICAS = {
    'Biosafety Risk to Individuals in the Laboratory and to the Community':
        'Riesgo de bioseguridad para las personas del laboratorio y para la comunidad',
    'Biosafety Risk to Animals in the Community':
        'Riesgo de bioseguridad para los animales de la comunidad',
    'Consequence': 'Consecuencia',
    'Likelihood': 'Probabilidad',
    'Inhalation Risk to Individual': 'Riesgo por inhalación para el individuo',
    'Percutaneous Risk to Individual': 'Riesgo percutáneo para el individuo',
    'Contact Risk to Individual': 'Riesgo por contacto para el individuo',
    'Ingestion Risk to Individual': 'Riesgo por ingestión para el individuo',
    'Inhalation Risk to Community': 'Riesgo por inhalación para la comunidad',
    'Percutaneous Risk to Community': 'Riesgo percutáneo para la comunidad',
    'Contact Risk to Community': 'Riesgo por contacto para la comunidad',
    'Ingestion Risk to Community': 'Riesgo por ingestión para la comunidad',
    'Inhalation Risk to Animal Community': 'Riesgo por inhalación para la comunidad animal',
    'Percutaneous Risk to Animal Community': 'Riesgo percutáneo para la comunidad animal',
    'Contact Risk to Animal Community': 'Riesgo por contacto para la comunidad animal',
    'Ingestion Risk to Animal Community': 'Riesgo por ingestión para la comunidad animal',
    'Secondary Transmission Risk': 'Riesgo de transmisión secundaria',
}

ETIQUETAS = {**CATEGORIAS, **RESULTADOS, **GRAFICAS}

import pandas as pd
import re

# Cargar el archivo
df = pd.read_csv('lens-export.csv')

# Limpiar valores nulos en Título y Resumen para evitar errores
df['Título'] = df['Título'].fillna('')
df['Resumen'] = df['Resumen'].fillna('')

def clasificar_articulo(row):
    titulo = str(row['Título']).lower()
    resumen = str(row['Resumen']).lower()
    texto_completo = titulo + " " + resumen
    
    # 1. Filtro de exclusión: Revisiones de literatura (CE-1)
    # Buscamos palabras clave típicas de revisiones en el título o resumen
    review_keywords = ['review', 'survey', 'state of the art', 'state-of-the-art', 'overview', 'bibliometric', 'meta-analysis']
    if any(re.search(rf'\b{kw}\b', titulo) for kw in review_keywords) or any(re.search(rf'\b{kw}\b', resumen) for kw in review_keywords):
        return pd.Series(['🔴 Excluir', 'Es un artículo de revisión o survey, no investigación primaria.'])
        
    # 2. Filtro de inclusión metodológica (CI-3)
    # Buscamos verbos o adjetivos que indiquen aportación o comparación algorítmica
    method_keywords = ['propose', 'proposed', 'novel', 'improved', 'hybrid', 'comparative', 'compare', 'outperform', 'outperforms', 'introduce', 'introduced', 'new algorithm']
    tiene_metodologia = any(re.search(rf'\b{kw}\b', texto_completo) for kw in method_keywords)
    
    # 3. Clasificación final
    if tiene_metodologia:
        return pd.Series(['🟢 Incluir', 'Propone, mejora o compara explícitamente una metodología algorítmica.'])
    else:
        return pd.Series(['🟡 Dudoso', 'Menciona los algoritmos, pero el resumen no aclara si hay una aportación metodológica o solo es aplicación.'])

# Aplicar la función a cada fila creando dos nuevas columnas
df[['Decisión de Cribado', 'Razón']] = df.apply(clasificar_articulo, axis=1)

# Guardar el resultado en un nuevo archivo CSV
output_filename = 'lens_cribado_prisma.csv'
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

# Imprimir el resumen estadístico para mostrarle al usuario
conteo = df['Decisión de Cribado'].value_counts()
print("Resultados del Cribado Automatizado:")
for categoria, cantidad in conteo.items():
    print(f"{categoria}: {cantidad} artículos")
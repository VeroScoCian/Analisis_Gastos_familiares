import pandas as pd
import numpy as np # Importamos numpy para usar np.nan
import matplotlib.pyplot as plt

# Ruta al archivo CSV (Por lo pronto con descarga)

ruta_archivo_csv = 'Orden_Economico.csv'

try:
    # 1. Leer el archivo CSV y limpiar los nombres de las columnas
    df_gastos = pd.read_csv(ruta_archivo_csv)
    df_gastos.columns = df_gastos.columns.str.strip()

    print("--- DataFrame original (primeras filas) ---")
    print(df_gastos.head())
    print("\n--- Información del DataFrame original ---")
    print(df_gastos.info())

    # 2. Reemplazar los valores vacíos con NaN, eliminar filas vacías y crear una copia
    df_gastos_limpio = df_gastos.replace('', np.nan, regex=True).dropna(how='all').copy()

    # 3. Manejar la columna 'Fecha'
    if 'Fecha' in df_gastos_limpio.columns:
        df_gastos_limpio['Fecha'] = pd.to_datetime(df_gastos_limpio['Fecha'], format='%d/%m/%Y', errors='coerce')
        df_gastos_limpio['Fecha'].fillna(method='ffill', inplace=True)
    else:
        print("Advertencia: La columna 'Fecha' no se encontró después de limpiar los nombres de columna.")

    # 4. Limpiar y convertir la columna 'Costo'
    if 'Costo' in df_gastos_limpio.columns:
        df_gastos_limpio['Costo'] = (
            df_gastos_limpio['Costo']
            .astype(str)
            .str.replace('$', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.strip()
        )
        df_gastos_limpio['Costo'] = pd.to_numeric(df_gastos_limpio['Costo'], errors='coerce')

    # 5. Renombrar las columnas
    df_gastos_limpio.rename(columns={
        'Gastos': 'Descripcion_Gasto',
        'Metodo de pago': 'Metodo_Pago'
    }, inplace=True)

    # 6. Eliminar las filas donde 'Costo' es NaN
    df_gastos_limpio.dropna(subset=['Costo'], inplace=True)

    print("\n--- DataFrame LIMPIO y TRANSFORMADO (primeras filas) ---")
    print(df_gastos_limpio.head())
    print("\n--- Información del DataFrame LIMPIO y TRANSFORMADO ---")
    print(df_gastos_limpio.info())

    # --- ANÁLISIS Y VISUALIZACIONES ---

    # VISUALIZACIÓN 1: Gasto por Categoría
    print("\n--- Creando el gráfico de Gastos por Categoría ---")
    gastos_por_categoria = df_gastos_limpio.groupby('Categoría')['Costo'].sum().reset_index()
    gastos_por_categoria = gastos_por_categoria.sort_values(by='Costo', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.bar(gastos_por_categoria['Categoría'], gastos_por_categoria['Costo'], color=['teal', 'coral'])
    plt.title('Gasto Total por Categoría', fontsize=16)
    plt.xlabel('Categoría de Gasto', fontsize=12)
    plt.ylabel('Costo Total ($)', fontsize=12)
    plt.xticks(rotation=45)
    for index, value in enumerate(gastos_por_categoria['Costo']):
        plt.text(index, value + 0.5, f'${value:.2f}', ha='center')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('Gasto_por_categoria.png')
    plt.close()

    # VISUALIZACIÓN 2: Gasto en el Tiempo
    print("\n--- Creando el gráfico de Gastos en el Tiempo ---")
    gastos_por_dia = df_gastos_limpio.groupby('Fecha')['Costo'].sum().reset_index()

    plt.figure(figsize=(10, 6))
    plt.plot(gastos_por_dia['Fecha'], gastos_por_dia['Costo'], marker='o', linestyle='-', color='teal')
    plt.title('Gasto Total por Día', fontsize=16)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Costo Diario ($)', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('Gasto_en_el_tiempo.png')
    plt.close()

except FileNotFoundError:
    print(f"Error: El archivo '{ruta_archivo_csv}' no se encontró.")
except Exception as e:
    print(f"Ocurrió un error: {e}. Por favor, revisa el formato de tus datos en el CSV.")

# --- PASO 11: RESUMEN DE ANÁLISIS ESCRITO ---
print("\n" + "="*50)
print("              RESUMEN DEL ANÁLISIS DE GASTOS")
print("="*50)

# 1. Gasto total del período
gasto_total = df_gastos_limpio['Costo'].sum()
print(f"El gasto total en el período analizado fue: ${gasto_total:.2f}")

# 2. Distribución de gastos por categoría
print("\nDistribución de gastos por categoría:")
gastos_por_categoria = df_gastos_limpio.groupby('Categoría')['Costo'].sum().sort_values(ascending=False)
for categoria, costo in gastos_por_categoria.items():
    porcentaje = (costo / gasto_total) * 100
    print(f"- {categoria:<10}: ${costo:.2f} ({porcentaje:.2f}%)")

# 3. Día de mayor gasto
# Agrupamos por fecha y sumamos los costos, luego encontramos el valor máximo
gasto_por_dia = df_gastos_limpio.groupby('Fecha')['Costo'].sum()
dia_mayor_gasto = gasto_por_dia.idxmax()
monto_mayor_gasto = gasto_por_dia.max()
print(f"\nEl día con mayor gasto fue: {dia_mayor_gasto.strftime('%d/%m/%Y')} con un total de ${monto_mayor_gasto:.2f}")

# 4. Gasto individual más alto
# Encontramos la fila con el costo más alto
gasto_individual_mas_alto = df_gastos_limpio.loc[df_gastos_limpio['Costo'].idxmax()]

# Si 'Descripcion_Gasto' es nulo, usamos 'Desconocido'
descripcion = gasto_individual_mas_alto['Descripcion_Gasto']
if pd.isna(descripcion):
    descripcion = 'Desconocido'

print(f"\nEl gasto individual más alto fue de ${gasto_individual_mas_alto['Costo']:.2f} por '{descripcion}'.")

print("="*50)
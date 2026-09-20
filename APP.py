import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os

# 1. Configuración de la página
st.set_page_config(page_title="Análisis de Tasas Reales", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #0e1117; }
    h1, h2, h3, h4 { color: #0e1117; font-family: 'Helvetica', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("Comparación de Depósitos a Plazo: Banco FoundVision vs. Coop. 29 de Octubre")
st.markdown("**Autores:** Emilio Alejandro Castillo Narvaez - Mateo Delgado | USFQ")
st.markdown("---")

# 2. Procesamiento de Datos
inversion_inicial = 10000
inflacion_esperada = 0.029

plazos = [31, 61, 91, 121, 181, 271, 361]

# Tasas de Banco FoundVision extraídas del nuevo tarifario[cite: 7]
tasas_bfv = [0.0300, 0.0325, 0.0350, 0.0375, 0.0475, 0.0550, 0.0575]

# Tasas de Cooperativa 29 de Octubre extraídas del nuevo tarifario[cite: 7]
tasas_coop29 = [0.0355, 0.0375, 0.0405, 0.0425, 0.0455, 0.0495, 0.0565]

df = pd.DataFrame({'Plazo': plazos, 'Tasa_Anual_BFV': tasas_bfv, 'Tasa_Anual_Coop29': tasas_coop29})
df['Inflacion_Plazo'] = inflacion_esperada * (df['Plazo'] / 365)

# Banco FoundVision
df['Rend_Nominal_BFV'] = df['Tasa_Anual_BFV'] * (df['Plazo'] / 365)
df['Rend_Real_BFV'] = ((1 + df['Rend_Nominal_BFV']) / (1 + df['Inflacion_Plazo'])) - 1
df['Ganancia_Real_USD_BFV'] = inversion_inicial * df['Rend_Real_BFV']

# Cooperativa 29 de Octubre
df['Rend_Nominal_Coop29'] = df['Tasa_Anual_Coop29'] * (df['Plazo'] / 365)
df['Rend_Real_Coop29'] = ((1 + df['Rend_Nominal_Coop29']) / (1 + df['Inflacion_Plazo'])) - 1
df['Ganancia_Real_USD_Coop29'] = inversion_inicial * df['Rend_Real_Coop29']

# 3. Enlaces a Documentos de Respaldo
st.subheader("Documentos de Respaldo y Calificaciones de Riesgo")
st.markdown("Para revisión de fuentes, consulte los siguientes enlaces oficiales:")
col_link1, col_link2 = st.columns(2)
with col_link1:
    st.markdown("- [🔗 Tarifario Banco FoundVision (Septiembre 2026)](#)")
    st.markdown("- [🔗 Calificación de Riesgo - Banco FoundVision](#)")
with col_link2:
    st.markdown("- [🔗 Tarifario Coop. 29 de Octubre (Septiembre 2026)](#)")
    st.markdown("- [🔗 Calificación de Riesgo - Coop. 29 de Octubre](#)")
st.markdown("---")

# 4. Mostrar Tablas en la Web
st.subheader("Cuadros de Rendimiento por Entidad (Inversión: USD 10.000)")

col_tabla1, col_tabla2 = st.columns(2)

with col_tabla1:
    st.markdown("**Banco FoundVision**")
    st.markdown("**Monto mínimo: USD 5.000**")
    df_show_bfv = df[['Plazo', 'Tasa_Anual_BFV', 'Rend_Nominal_BFV', 'Inflacion_Plazo', 'Rend_Real_BFV', 'Ganancia_Real_USD_BFV']].copy()
    st.dataframe(df_show_bfv.style.format({
        'Tasa_Anual_BFV': '{:.2%}', 'Rend_Nominal_BFV': '{:.3%}', 'Inflacion_Plazo': '{:.3%}', 
        'Rend_Real_BFV': '{:.3%}', 'Ganancia_Real_USD_BFV': '${:.2f}'
    }), use_container_width=True, hide_index=True)
    st.markdown("*Fuente: Tarifario de Servicios Financieros Septiembre Banco FoundVision 2026*[cite: 7]")

with col_tabla2:
    st.markdown("**Cooperativa 29 de Octubre**")
    st.markdown("**Monto mínimo: USD 500**")
    df_show_coop = df[['Plazo', 'Tasa_Anual_Coop29', 'Rend_Nominal_Coop29', 'Inflacion_Plazo', 'Rend_Real_Coop29', 'Ganancia_Real_USD_Coop29']].copy()
    st.dataframe(df_show_coop.style.format({
        'Tasa_Anual_Coop29': '{:.2%}', 'Rend_Nominal_Coop29': '{:.3%}', 'Inflacion_Plazo': '{:.3%}', 
        'Rend_Real_Coop29': '{:.3%}', 'Ganancia_Real_USD_Coop29': '${:.2f}'
    }), use_container_width=True, hide_index=True)
    st.markdown("*Fuente: Tarifario de Servicios Financieros Septiembre Coop 29 de Octubre*[cite: 7]")

st.markdown("---")

# 5. Gráficas con Plotly
color_bfv = '#003366' # Azul oscuro para FoundVision[cite: 7]
color_coop = '#CC0000' # Rojo para Coop 29[cite: 7]

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df['Plazo'], y=df['Tasa_Anual_BFV'], mode='lines+markers', name='Banco FoundVision', line=dict(color=color_bfv, width=2)))
fig1.add_trace(go.Scatter(x=df['Plazo'], y=df['Tasa_Anual_Coop29'], mode='lines+markers', name='Coop. 29 de Octubre', line=dict(color=color_coop, width=2)))
fig1.update_layout(title='1. Curva de Tasas Nominales Anuales', template='plotly_white', xaxis_title='Plazo (días)', yaxis_tickformat='.2%')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['Plazo'], y=df['Rend_Real_BFV'], mode='lines+markers', name='Banco FoundVision', line=dict(color=color_bfv, width=2)))
fig2.add_trace(go.Scatter(x=df['Plazo'], y=df['Rend_Real_Coop29'], mode='lines+markers', name='Coop. 29 de Octubre', line=dict(color=color_coop, width=2)))
fig2.update_layout(title='2. Rendimiento Real por Plazo (Ecuación de Fisher)', template='plotly_white', xaxis_title='Plazo (días)', yaxis_tickformat='.3%')

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=df['Plazo'], y=df['Ganancia_Real_USD_BFV'], name='Banco FoundVision', marker_color=color_bfv))
fig3.add_trace(go.Bar(x=df['Plazo'], y=df['Ganancia_Real_USD_Coop29'], name='Coop. 29 de Octubre', marker_color=color_coop))
fig3.update_layout(title='3. Ganancia Real Estimada (USD 10.000)', template='plotly_white', xaxis_title='Plazo (días)', barmode='group')

col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)
st.markdown("---")

# 6. Texto Analítico Consolidado
texto_analisis = """
### Análisis Ejecutivo de Rendimientos

**Comportamiento de las Tasas y Curvas de Rendimiento**
Las curvas de rendimiento de ambas instituciones muestran una pendiente positiva congruente con la teoría de tasas de interés, exigiendo un mayor retorno a mayor plazo. La Cooperativa 29 de Octubre mantiene tasas superiores en el corto y mediano plazo (31 a 181 días). Sin embargo, a partir de los 271 días, el Banco FoundVision invierte la tendencia, alcanzando un pico de 5,75% a 361 días frente al 5,65% de la Cooperativa[cite: 7]. 

**Impacto del Tiempo, Inflación y Liquidez**
El crecimiento de la prima de liquidez logra superar el impacto de la inflación (proyectada en 2,90% anual) en todos los plazos analizados[cite: 7]. A diferencia de escenarios anteriores, ninguna entidad presenta rendimientos reales negativos[cite: 7]. La ganancia real más baja ocurre en el Banco FoundVision a 31 días (0,008% o $0,85), lo que evidencia que los plazos cortos apenas logran mantener el poder adquisitivo[cite: 7]. La verdadera compensación por la pérdida de liquidez se consolida en el horizonte de 271 y 361 días.

**Factores de Riesgo y Sensibilidad Macroeconómica**
Previo a la colocación del capital, es imperativo consultar los documentos de respaldo adjuntos. Se debe contrastar la calificación de riesgo institucional y validar las normativas de la COSEDE aplicables a bancos frente a cooperativas. Si la inflación real observada superara la expectativa del 2,90%, todos los rendimientos reales se contraerían, y los plazos cortos de ambas instituciones (31 y 61 días) podrían incurrir en tasas reales negativas, destruyendo valor para el inversionista.

**Recomendación de Inversión y Conclusión**
Basado estrictamente en la maximización del beneficio económico, la opción óptima es invertir los USD 10.000 a un plazo de 361 días en el Banco FoundVision. Esta alternativa genera la mayor ganancia real del análisis ($274,02)[cite: 7]. Los riesgos principales a asumir son el riesgo de liquidez (inmovilización del capital por un año completo) y el riesgo inflacionario durante el período de maduración del depósito[cite: 3].
"""
st.markdown(texto_analisis)

# 7. Generación del Informe PDF (Corregido y blindado)
def dibujar_tabla_pdf(pdf, titulo, sufijo):
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(w=0, h=8, text=titulo, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", 'B', 9)
    
    headers = ['Plazo (dias)', 'Tasa Anual', 'Rend. Nom.', 'Inflacion', 'Rend. Real', 'Ganancia']
    widths = [22, 25, 27, 25, 27, 30] # Ajustado a 156mm total
    
    for i, (head, w) in enumerate(zip(headers, widths)):
        nx = "LMARGIN" if i == len(headers) - 1 else "RIGHT"
        ny = "NEXT" if i == len(headers) - 1 else "TOP"
        pdf.cell(w=w, h=8, text=head, border=1, align='C', new_x=nx, new_y=ny)
        
    pdf.set_font("helvetica", '', 9)
    for _, row in df.iterrows():
        pdf.cell(w=widths[0], h=8, text=str(int(row['Plazo'])), border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[1], h=8, text=f"{row[f'Tasa_Anual_{sufijo}']:.2%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[2], h=8, text=f"{row[f'Rend_Nominal_{sufijo}']:.3%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[3], h=8, text=f"{row['Inflacion_Plazo']:.3%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[4], h=8, text=f"{row[f'Rend_Real_{sufijo}']:.3%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[5], h=8, text=f"${row[f'Ganancia_Real_USD_{sufijo}']:.2f}", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

def crear_pdf():
    pdf = FPDF()
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(w=0, h=10, text="Informe de Rendimientos Reales - Mercados Financieros", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.cell(w=0, h=8, text="Autores: Emilio Alejandro Castillo Narvaez - Mateo Delgado | USFQ", new_x="LMARGIN", new_y="NEXT", align='C')
    
    # Enlaces en PDF
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("helvetica", 'U', 9)
    pdf.cell(w=0, h=6, text="Ver Tarifario Banco FoundVision", link="https://#", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(w=0, h=6, text="Ver Tarifario Cooperativa 29 de Octubre", link="https://#", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Tablas
    dibujar_tabla_pdf(pdf, "Banco FoundVision", "BFV")
    dibujar_tabla_pdf(pdf, "Cooperativa 29 de Octubre", "Coop29")

    # Gráficas
    with tempfile.TemporaryDirectory() as tmpdir:
        fig1_path = os.path.join(tmpdir, "fig1.png")
        fig2_path = os.path.join(tmpdir, "fig2.png")
        fig3_path = os.path.join(tmpdir, "fig3.png")
        
        # Generar imágenes
        fig1.write_image(fig1_path, width=800, height=400, scale=2)
        fig2.write_image(fig2_path, width=800, height=400, scale=2)
        fig3.write_image(fig3_path, width=800, height=400, scale=2)
        
        pdf.add_page()
        pdf.image(fig1_path, x=15, w=180)
        pdf.ln(2)
        pdf.image(fig2_path, x=15, w=180)
        pdf.add_page()
        pdf.image(fig3_path, x=15, w=180)
    
    pdf.ln(5)
    
    # Texto analítico 
    for linea in texto_analisis.split('\n'):
        # Forzar latin-1 para evitar el error de caracteres anchos invisibles
        linea_limpia = linea.strip().encode('latin-1', 'replace').decode('latin-1')
        if not linea_limpia:
            pdf.ln(3)
            continue
        pdf.set_x(15)
        if linea_limpia.startswith('###'):
            pdf.set_font("helvetica", 'B', 14)
            pdf.cell(w=0, h=10, text=linea_limpia.replace('###', '').strip(), new_x="LMARGIN", new_y="NEXT")
        elif linea_limpia.startswith('**'):
            pdf.set_font("helvetica", 'B', 11)
            pdf.multi_cell(w=180, h=7, text=linea_limpia.replace('**', ''), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("helvetica", '', 10)
            pdf.multi_cell(w=180, h=5, text=linea_limpia, new_x="LMARGIN", new_y="NEXT")
            
    return bytes(pdf.output())

st.markdown("---")
pdf_bytes = crear_pdf()
st.download_button(label="📥 Descargar Informe Ejecutivo en PDF",
                   data=pdf_bytes,
                   file_name="Informe_Ejecutivo_Tasas_Reales.pdf",
                   mime="application/pdf")

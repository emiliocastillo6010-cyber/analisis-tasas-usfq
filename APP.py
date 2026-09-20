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
st.markdown("**Emilio Alejandro Castillo Narvaez - Mateo Delgado**")
st.markdown("---")

# 2. Procesamiento de Datos
inversion_inicial = 10000
inflacion_esperada = 0.029

plazos = [31, 61, 91, 121, 181, 271, 361]

# Tasas de Banco FoundVision extraídas de la tabla
tasas_fv = [0.0300, 0.0325, 0.0350, 0.0375, 0.0475, 0.0550, 0.0575]

# Tasas de Cooperativa 29 de Octubre extraídas de la tabla
tasas_coop29 = [0.0355, 0.0375, 0.0405, 0.0425, 0.0455, 0.0495, 0.0565]

df = pd.DataFrame({'Plazo': plazos, 'Tasa_Anual_FV': tasas_fv, 'Tasa_Anual_Coop29': tasas_coop29})
df['Inflacion_Plazo'] = inflacion_esperada * (df['Plazo'] / 365)

# Cálculos Banco FoundVision
df['Rend_Nominal_FV'] = df['Tasa_Anual_FV'] * (df['Plazo'] / 365)
df['Rend_Real_FV'] = ((1 + df['Rend_Nominal_FV']) / (1 + df['Inflacion_Plazo'])) - 1
df['Ganancia_Real_USD_FV'] = inversion_inicial * df['Rend_Real_FV']

# Cálculos Cooperativa 29 de Octubre
df['Rend_Nominal_Coop29'] = df['Tasa_Anual_Coop29'] * (df['Plazo'] / 365)
df['Rend_Real_Coop29'] = ((1 + df['Rend_Nominal_Coop29']) / (1 + df['Inflacion_Plazo'])) - 1
df['Ganancia_Real_USD_Coop29'] = inversion_inicial * df['Rend_Real_Coop29']

# 3. Mostrar Tablas y Links de Documentos
st.subheader("Cuadros de Rendimiento por Entidad (Inversión: USD 10.000)")

col_tabla1, col_tabla2 = st.columns(2)

with col_tabla1:
    st.markdown("### Banco FoundVision")
    st.markdown("**Calificación de Riesgo:** AA+ | **Monto mínimo:** USD 5.001")
    df_show_fv = df[['Plazo', 'Tasa_Anual_FV', 'Rend_Nominal_FV', 'Inflacion_Plazo', 'Rend_Real_FV', 'Ganancia_Real_USD_FV']].copy()
    st.dataframe(df_show_fv.style.format({
        'Tasa_Anual_FV': '{:.2%}', 'Rend_Nominal_FV': '{:.3%}', 'Inflacion_Plazo': '{:.3%}', 
        'Rend_Real_FV': '{:.3%}', 'Ganancia_Real_USD_FV': '${:.2f}'
    }), use_container_width=True, hide_index=True)
    
    # ESPACIO PARA LINKS BANCO FOUNDVISION
    st.markdown("https://visionfund.ec/docs/transparencia/calificaciondeactivosmarzojunio2026.pdf") 
    st.markdown("https://visionfund.ec/docs/transparencia/tarifario-septiembre.pdf")

with col_tabla2:
    st.markdown("### Cooperativa 29 de Octubre")
    st.markdown("**Calificación de Riesgo:** AA | **Monto mínimo:** USD 500")
    df_show_coop = df[['Plazo', 'Tasa_Anual_Coop29', 'Rend_Nominal_Coop29', 'Inflacion_Plazo', 'Rend_Real_Coop29', 'Ganancia_Real_USD_Coop29']].copy()
    st.dataframe(df_show_coop.style.format({
        'Tasa_Anual_Coop29': '{:.2%}', 'Rend_Nominal_Coop29': '{:.3%}', 'Inflacion_Plazo': '{:.3%}', 
        'Rend_Real_Coop29': '{:.3%}', 'Ganancia_Real_USD_Coop29': '${:.2f}'
    }), use_container_width=True, hide_index=True)
    
    # ESPACIO PARA LINKS COOPERATIVA
    st.markdown("https://www.29deoctubre.fin.ec/Portals/0/Documentos/Transparencia-de-la-Informacion/certificado-calificacion-2.pdf")
    st.markdown("https://www.29deoctubre.fin.ec/Portals/0/Documentos/TASAS_VIGENTES_7_SEPT_2026.pdf")

st.markdown("---")

# 4. Gráficas con Plotly
color_fv = '#003366' # Azul oscuro formal para FoundVision
color_coop = '#B30000' # Rojo institucional para 29 de Octubre

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df['Plazo'], y=df['Tasa_Anual_FV'], mode='lines+markers+text', 
    name='Banco FoundVision', line=dict(color=color_fv, width=2),
    text=[f'{val:.2%}' for val in df['Tasa_Anual_FV']], textposition='top left'
))
fig1.add_trace(go.Scatter(
    x=df['Plazo'], y=df['Tasa_Anual_Coop29'], mode='lines+markers+text', 
    name='Coop. 29 de Octubre', line=dict(color=color_coop, width=2),
    text=[f'{val:.2%}' for val in df['Tasa_Anual_Coop29']], textposition='bottom right'
))
fig1.update_layout(title='1. Curva de Tasas Nominales Anuales', template='plotly_white', xaxis_title='Plazo (días)', yaxis_tickformat='.2%')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df['Plazo'], y=df['Rend_Real_FV'], mode='lines+markers+text', 
    name='Banco FoundVision', line=dict(color=color_fv, width=2),
    text=[f'{val:.2%}' for val in df['Rend_Real_FV']], textposition='top left'
))
fig2.add_trace(go.Scatter(
    x=df['Plazo'], y=df['Rend_Real_Coop29'], mode='lines+markers+text', 
    name='Coop. 29 de Octubre', line=dict(color=color_coop, width=2),
    text=[f'{val:.2%}' for val in df['Rend_Real_Coop29']], textposition='bottom right'
))
fig2.update_layout(title='2. Rendimiento Real por Plazo (Ecuación de Fisher)', template='plotly_white', xaxis_title='Plazo (días)', yaxis_tickformat='.2%')

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=df['Plazo'], y=df['Ganancia_Real_USD_FV'], name='Banco FoundVision', marker_color=color_fv,
    text=[f'${val:.2f}' for val in df['Ganancia_Real_USD_FV']], textposition='outside'
))
fig3.add_trace(go.Bar(
    x=df['Plazo'], y=df['Ganancia_Real_USD_Coop29'], name='Coop. 29 de Octubre', marker_color=color_coop,
    text=[f'${val:.2f}' for val in df['Ganancia_Real_USD_Coop29']], textposition='outside'
))
fig3.update_layout(title='3. Ganancia Real Estimada (USD 10.000)', template='plotly_white', xaxis_title='Plazo (días)', barmode='group')

col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)
st.markdown("---")

# 5. Texto Analítico Actualizado
texto_analisis = """
### Análisis Ejecutivo de Rendimientos

**Comportamiento de las Tasas y Curvas de Rendimiento**
Las curvas de rendimiento para ambas instituciones exhiben un comportamiento creciente normal. Sin embargo, existe un punto de inflexión estructural: la Cooperativa 29 de Octubre ofrece mejores tasas nominales en el corto plazo (hasta 121 días). A partir de los 181 días, Banco FoundVision toma un claro liderazgo en rentabilidad, alcanzando un pico de 5,75% nominal a 361 días frente al 5,65% de la Cooperativa.

**Impacto del Tiempo, Inflación y Liquidez**
El rendimiento real crece progresivamente a medida que aumenta el vencimiento, debido a que la prima de liquidez supera el efecto de la inflación esperada del 2,90%. Aunque los plazos mayores exigen inmovilizar el capital, el salto en la tasa nominal compensa con creces esta pérdida de liquidez, especialmente al romper la barrera de los 181 días en Banco FoundVision, donde la rentabilidad se dispara. 

**Factores de Riesgo, Calificación Institucional y Sensibilidad**
Antes de comprometer el capital, es imperativo evaluar la solidez institucional. Ambas entidades presentan un perfil de alta seguridad, pero con una ventaja comparativa para el banco: la Cooperativa 29 de Octubre cuenta con una calificación de riesgo AA, mientras que Banco FoundVision destaca con una calificación superior de AA+. Adicionalmente, si la inflación experimentara un alza no prevista de un punto porcentual, los rendimientos reales se contraerían, acercando peligrosamente los depósitos de corto plazo (31 a 61 días) a terreno de pérdida de valor adquisitivo.

**Recomendación de Inversión y Conclusión**
Considerando el análisis integral de rendimiento matemático y perfil de riesgo, la opción óptima y definitiva es invertir los USD 10.000 a un plazo de 361 días en Banco FoundVision. Esta decisión no solo asegura la mayor ganancia real estimada del mercado evaluado (tasa de 5,75%), sino que resguarda el capital en una institución con calificación AA+. El principal riesgo asumido es la pérdida de liquidez inmediata durante el periodo de un año.
"""
st.markdown(texto_analisis)

# 6. PDF Generator
def dibujar_tabla_pdf(pdf, titulo, calificacion, sufijo):
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(w=0, h=8, text=titulo, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", 'I', 9)
    pdf.cell(w=0, h=6, text=f"Calificación de Riesgo: {calificacion}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("helvetica", 'B', 9)
    
    headers = ['Plazo (dias)', 'Tasa Anual', 'Rend. Nom.', 'Inflacion', 'Rend. Real', 'Ganancia']
    widths = [25, 25, 25, 25, 25, 30]
    
    for i, (head, w) in enumerate(zip(headers, widths)):
        nx = "LMARGIN" if i == len(headers) - 1 else "RIGHT"
        ny = "NEXT" if i == len(headers) - 1 else "TOP"
        pdf.cell(w=w, h=8, text=head, border=1, align='C', new_x=nx, new_y=ny)
        
    pdf.set_font("helvetica", '', 9)
    for _, row in df.iterrows():
        pdf.cell(w=widths[0], h=8, text=str(int(row['Plazo'])), border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[1], h=8, text=f"{row[f'Tasa_Anual_{sufijo}']:.2%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[2], h=8, text=f"{row[f'Rend_Nominal_{sufijo}']:.2%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[3], h=8, text=f"{row['Inflacion_Plazo']:.2%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[4], h=8, text=f"{row[f'Rend_Real_{sufijo}']:.2%}", border=1, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(w=widths[5], h=8, text=f"${row[f'Ganancia_Real_USD_{sufijo}']:.2f}", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

def crear_pdf():
    pdf = FPDF()
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(w=0, h=10, text="Informe de Rendimientos Reales - Mercados Financieros", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.cell(w=0, h=10, text="Autores: Emilio Alejandro Castillo Narvaez - Mateo Delgado", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    # Tablas
    dibujar_tabla_pdf(pdf, "Banco FoundVision", "AA+", "FV")
    dibujar_tabla_pdf(pdf, "Cooperativa 29 de Octubre", "AA", "Coop29")

    # Links en PDF (Dejar como texto referencial para el formato impreso)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(w=0, h=6, text="Enlaces a Documentación de Respaldo:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", '', 9)
    pdf.cell(w=0, h=6, text="1. Tarifario FoundVision: [Insertar URL del Tarifario]", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(w=0, h=6, text="2. Tarifario Coop 29 Oct: [Insertar URL del Tarifario]", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(w=0, h=6, text="3. Calificadoras de Riesgo: [Insertar URL de Calificaciones]", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Gráficas
    with tempfile.TemporaryDirectory() as tmpdir:
        fig1_path = os.path.join(tmpdir, "fig1.png")
        fig2_path = os.path.join(tmpdir, "fig2.png")
        fig3_path = os.path.join(tmpdir, "fig3.png")
        
        # Guardar en blanco para PDF
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
    
    # Texto Analítico
    for linea in texto_analisis.split('\n'):
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

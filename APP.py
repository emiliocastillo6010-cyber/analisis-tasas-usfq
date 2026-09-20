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

st.title("Comparación de Depósitos a Plazo")
st.markdown("**Emilio Alejandro Castillo Narvaez - Mateo Delgado**")
st.markdown("---")

# 2. Procesamiento de Datos
inversion_inicial = 10000
inflacion_esperada = 0.029

plazos = [31, 61, 91, 121, 181, 271, 361]

# Tasas de Banco Guayaquil extraídas del PDF
tasas_bg = [0.039, 0.040, 0.0405, 0.0405, 0.041, 0.0415,0.0420]

# Tasas de Cooperativa 29 de Octubre extraídas del PDF
tasas_coop29 = [0.0355, 0.0375, 0.0405, 0.0425, 0.0455, 0.0495, 0.0565]

df = pd.DataFrame({'Plazo': plazos, 'Tasa_Anual_BG': tasas_bg, 'Tasa_Anual_Coop29': tasas_coop29})
df['Inflacion_Plazo'] = inflacion_esperada * (df['Plazo'] / 365)

# Banco Guayaquil
df['Rend_Nominal_BG'] = df['Tasa_Anual_BG'] * (df['Plazo'] / 365)
df['Rend_Real_BG'] = ((1 + df['Rend_Nominal_BG']) / (1 + df['Inflacion_Plazo'])) - 1
df['Ganancia_Real_USD_BG'] = inversion_inicial * df['Rend_Real_BG']

# Cooperativa 29 de Octubre
df['Rend_Nominal_Coop29'] = df['Tasa_Anual_Coop29'] * (df['Plazo'] / 365)
df['Rend_Real_Coop29'] = ((1 + df['Rend_Nominal_Coop29']) / (1 + df['Inflacion_Plazo'])) - 1
df['Ganancia_Real_USD_Coop29'] = inversion_inicial * df['Rend_Real_Coop29']

# 3. Mostrar Tablas en la Web
st.subheader("Cuadros de Rendimiento por Entidad (Inversión: USD 10.000)")

col_tabla1, col_tabla2 = st.columns(2)

with col_tabla1:
    st.markdown("**Banco Guayaquil**")
    st.markdown("**Monto minimo: USD 5001**")
    df_show_bg = df[['Plazo', 'Tasa_Anual_BG', 'Rend_Nominal_BG', 'Inflacion_Plazo', 'Rend_Real_BG', 'Ganancia_Real_USD_BG']].copy()
    st.dataframe(df_show_bg.style.format({
        'Tasa_Anual_BG': '{:.2%}', 'Rend_Nominal_BG': '{:.2%}', 'Inflacion_Plazo': '{:.2%}', 
        'Rend_Real_BG': '{:.2%}', 'Ganancia_Real_USD_BG': '${:.2f}'
    }), use_container_width=True, hide_index=True)
    st.markdown("*Fuente: Tarifario de Servicios Financieros Junio 2026*")

with col_tabla2:
    st.markdown("**Cooperativa 29 de Octubre**")
    st.markdown("**Monto minimo: USD 500**")
    df_show_coop = df[['Plazo', 'Tasa_Anual_Coop29', 'Rend_Nominal_Coop29', 'Inflacion_Plazo', 'Rend_Real_Coop29', 'Ganancia_Real_USD_Coop29']].copy()
    st.dataframe(df_show_coop.style.format({
        'Tasa_Anual_Coop29': '{:.2%}', 'Rend_Nominal_Coop29': '{:.2%}', 'Inflacion_Plazo': '{:.2%}', 
        'Rend_Real_Coop29': '{:.2%}', 'Ganancia_Real_USD_Coop29': '${:.2f}'
    }), use_container_width=True, hide_index=True)
    st.markdown("*Fuente:Tasas Vigentes 07 Septiembre 2026*")

st.markdown("---")

# 4. Gráficas con Plotly
color_bg = '#FF00FF'
color_coop = '#6B1D2F'

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df['Plazo'], y=df['Tasa_Anual_BG'], mode='lines+markers', name='Banco Guayaquil', line=dict(color=color_bg, width=2)))
fig1.add_trace(go.Scatter(x=df['Plazo'], y=df['Tasa_Anual_Coop29'], mode='lines+markers', name='Coop. 29 de Octubre', line=dict(color=color_coop, width=2)))
fig1.update_layout(title='1. Curva de Tasas Nominales Anuales', template='plotly_dark', xaxis_title='Plazo (días)', yaxis_tickformat='.2%')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['Plazo'], y=df['Rend_Real_BG'], mode='lines+markers', name='Banco Guayaquil', line=dict(color=color_bg, width=2)))
fig2.add_trace(go.Scatter(x=df['Plazo'], y=df['Rend_Real_Coop29'], mode='lines+markers', name='Coop. 29 de Octubre', line=dict(color=color_coop, width=2)))
fig2.update_layout(title='2. Rendimiento Real por Plazo (Ecuación de Fisher)', template='plotly_dark', xaxis_title='Plazo (días)', yaxis_tickformat='.2%')

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=df['Plazo'], y=df['Ganancia_Real_USD_BG'], name='Banco Guayaquil', marker_color=color_bg))
fig3.add_trace(go.Bar(x=df['Plazo'], y=df['Ganancia_Real_USD_Coop29'], name='Coop. 29 de Octubre', marker_color=color_coop))
fig3.update_layout(title='3. Ganancia Real Estimada (USD 10.000)', template='plotly_dark', xaxis_title='Plazo (días)', barmode='group')

col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)
st.markdown("---")

# 5. Texto Analítico (Formato de Informe Consolidado)
texto_analisis = """
### Análisis Ejecutivo de Rendimientos

**Comportamiento de las Tasas y Curvas de Rendimiento**
Las curvas de rendimiento para ambas instituciones financieras exhiben un comportamiento creciente normal, reflejando la teoría clásica donde los plazos más largos exigen rendimientos superiores para compensar el costo de oportunidad y el riesgo. La Cooperativa 29 de Octubre ofrece la tasa nominal más alta en casi todos los plazos, alcanzando un 5,65% a 360 días. La única excepción ocurre a los 91 días, donde ambas entidades empatan con una tasa del 4,05%. En consecuencia, la Cooperativa presenta sistemáticamente el mayor rendimiento real en cada escenario evaluado posterior a los 91 dias.

**Impacto del Tiempo, Inflación y Liquidez**
A medida que aumenta el vencimiento, el rendimiento real crece de forma progresiva. Esto sucede porque la prima de liquidez compensa y supera el impacto acumulado de la inflación esperada. Aunque los plazos más largos compensan la pérdida de liquidez, esta mejora es marginal en los plazos intermedios; el incentivo real se materializa al llegar a los 360 días. Por el contrario, en el plazo más corto (30 días), Banco Guayaquil ofrece una tasa nominal de 0,00%. Esto genera un rendimiento real negativo, ya que el capital no devenga intereses pero sufre la pérdida de poder adquisitivo provocada por la inflación.

**Factores de Riesgo y Sensibilidad Macroeconómica**
Antes de comprometer el capital, es importante considerar factores ajenos a la tasa, tales como la calificación de riesgo de la institución, las necesidades personales de liquidez a corto plazo y los límites de cobertura del seguro de depósitos (COSEDE). Adicionalmente, el entorno macroeconómico es determinante: si la inflación esperada aumentara en un punto porcentual, los rendimientos reales se contraerían en todos los plazos, empujando a los escenarios de corto plazo con tasas bajas hacia retornos negativos.

**Recomendación de Inversión y Conclusión**
Basado en la investigación y cálculo matemático de la ganancia, la opción óptima es invertir los USD 10.000 a un plazo de 360 días en la Cooperativa 29 de Octubre. Esta decisión captura el punto más alto de la curva de rendimientos sin fraccionar el capital. Los riesgos principales de esta alternativa incluyen el riesgo de liquidez (inmovilización de fondos por un año sin acceso libre) y el riesgo inflacionario, en caso de que la inflación real observada termine superando la expectativa del 2%.
"""
st.markdown(texto_analisis)

# 6. Generación del Informe PDF (Tablas, Gráficas y Texto)
def dibujar_tabla_pdf(pdf, titulo, sufijo):
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(w=0, h=8, text=titulo, new_x="LMARGIN", new_y="NEXT")
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
    pdf.cell(w=0, h=10, text="Autor: Emilio Alejandro Castillo Narvaez | USFQ", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    # Tablas de datos en el PDF
    dibujar_tabla_pdf(pdf, "Banco Guayaquil", "BG")
    dibujar_tabla_pdf(pdf, "Cooperativa 29 de Octubre", "Coop29")

    # Gráficas
    with tempfile.TemporaryDirectory() as tmpdir:
        fig1_path = os.path.join(tmpdir, "fig1.png")
        fig2_path = os.path.join(tmpdir, "fig2.png")
        fig3_path = os.path.join(tmpdir, "fig3.png")
        
        fig1.update_layout(template='plotly_white')
        fig2.update_layout(template='plotly_white')
        fig3.update_layout(template='plotly_white')
        
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
    
    # Texto analítico seguro
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

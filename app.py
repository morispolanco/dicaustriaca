import streamlit as st
import requests
import json
from docx import Document
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Diccionario Económico de la Escuela Austríaca", page_icon="📚", layout="wide")

# Función para crear la columna de información
def crear_columna_info():
    st.markdown("""
    ## Sobre esta aplicación

    Esta aplicación es un Diccionario Económico basado en el pensamiento de la Escuela Austríaca de Economía. Permite a los usuarios obtener definiciones de términos económicos según la interpretación de diversos autores de esta escuela.

    ### Cómo usar la aplicación:

    1. Elija un término económico de la lista predefinida o proponga su propio término.
    2. Seleccione uno o más autores de la Escuela Austríaca de Economía.
    3. Haga clic en "Obtener definición" para generar las definiciones.
    4. Lea las definiciones y fuentes proporcionadas.
    5. Si lo desea, descargue un documento DOCX con toda la información.

    ### Autor y actualización:
    **Moris Polanco**, 26 ag 2024

    ### Cómo citar esta aplicación (formato APA):
    Polanco, M. (2024). *Diccionario Económico de la Escuela Austríaca* [Aplicación web]. https://dicaustriaca.streamlit.app

    ---
    **Nota:** Esta aplicación utiliza inteligencia artificial para generar definiciones basadas en información disponible en línea. Siempre verifique la información con fuentes académicas para un análisis más profundo.
    """)

# Título de la aplicación
st.title("Diccionario Económico de la Escuela Austríaca")

# Crear un diseño de dos columnas
col1, col2 = st.columns([1, 2])

# Columna de información
with col1:
    crear_columna_info()

# Columna principal
with col2:
    # Acceder a las claves de API de los secretos de Streamlit
    TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
    SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

    # Lista de términos económicos
    terminos_economicos = [
        "Acción humana", "Agio", "Apalancamiento", "Armonía de intereses", "Banca libre", "Beneficio económico", 
        "Bienes de capital", "Bienes de consumo", "Bimetalismo", "Capital humano", "Capitalismo", "Catalaxia", 
        "Cálculo económico", "Competencia perfecta", "Conocimiento disperso", "Costos de oportunidad", 
        "Crítica del socialismo", "Curva de preferencia temporal", "Desajuste del mercado", "Desempleo natural", 
        "Destrucción creativa", "Dilema del prisionero", "División del trabajo", "Doble contingencia", 
        "Economía del bienestar", "Economía subjetiva", "Eficiencia de Pareto", "Eficiencia dinámica", 
        "Empresario", "Equilibrio económico", "Equilibrio general", "Escuela Austríaca", "Escuela de Viena", 
        "Estructura del capital", "Ëxternalidades", "Falacia del costo hundido", "Función empresarial", "Ganancia empresarial", 
        "Heterogeneidad del capital", "Horizonte temporal", "Imposición fiscal", "Incentivos económicos", 
        "Inflación", "Interés", "Intervencionismo", "Inversión de capital", "Ley de la oferta y la demanda", 
        "Ley de los rendimientos decrecientes", "Ley de Say", "Libertad económica", "Libertarismo", 
        "Margen de ganancia", "Margen de utilidad", "Método praxeológico", "Método subjetivo", "Moneda fiduciaria", 
        "Moneda sana", "Monopolio natural", "Niveles de intervención", "Óptimo de Pareto", "Orden espontáneo", 
        "Preferencia por la liquidez", "Preferencia temporal", "Precio de equilibrio", "Precios relativos", 
        "Problema del cálculo económico", "Proceso de mercado", "Propiedad común", "Propiedad privada", 
        "Racionalidad limitada", "Reducción de riesgos", "Rentabilidad", "Restricción presupuestaria", 
        "Riesgo moral", "Rutas del mercado", "Salario real", "Selección adversa", "Señales de precios", 
        "Sistema de precios", "Sociedad abierta", "Subjetivismo", "Subproducción", "Substitución", 
        "Tasa de interés natural", "Teoría de la eficiencia", "Teoría del capital", "Teoría del ciclo económico", 
        "Teoría del valor", "Teoría del valor subjetivo", "Teoría del valor y precio", "Título de propiedad", 
        "Tragedia de los comunes", "Utilidad", "Utilidad marginal", "Valor de cambio", "Valor de uso", "Valor esperado", 
        "Valor trabajo", "Ventaja comparativa", "Voluntarismo", "Vulnerabilidad económica"
    ]

    # Lista de autores de la Escuela Austríaca de Economía
    autores_austriacos = [
        "Ludwig von Mises", "Friedrich Hayek", "Carl Menger", "Eugen von Böhm-Bawerk", "Murray Rothbard", 
        "Israel Kirzner", "Hans-Hermann Hoppe", "Joseph Schumpeter", "Ludwig Lachmann", "Walter Block"
    ]

    def buscar_informacion(query, autor):
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": f"{query} {autor} Escuela Austríaca de Economía"
        })
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def generar_definicion(termino, autor, contexto):
        url = "https://api.together.xyz/inference"
        payload = json.dumps({
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": f"Contexto: {contexto}\n\nTérmino: {termino}\nAutor: {autor}\n\nProporciona una definición del término económico '{termino}' según el pensamiento de {autor}, un autor de la Escuela Austríaca de Economía. La definición debe ser concisa pero informativa, similar a una entrada de diccionario. Si es posible, incluye una referencia a una obra específica de {autor} que trate este concepto.\n\nDefinición:",
            "max_tokens": 2048,
            "temperature": 0,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["Término:"]
        })
        headers = {
            'Authorization': f'Bearer {TOGETHER_API_KEY}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()['output']['choices'][0]['text'].strip()

    def create_docx(termino, definiciones, fuentes):
        doc = Document()
        doc.add_heading('Diccionario Económico - Escuela Austríaca', 0)

        doc.add_heading('Término', level=1)
        doc.add_paragraph(termino)

        for autor, definicion in definiciones.items():
            doc.add_heading(f'Definición según {autor}', level=2)
            doc.add_paragraph(definicion)

        doc.add_heading('Fuentes', level=1)
        for fuente in fuentes:
            doc.add_paragraph(fuente, style='List Bullet')

        doc.add_paragraph('\nNota: Este documento fue generado por un asistente de IA. Verifica la información con fuentes académicas para un análisis más profundo.')

        return doc

    # Interfaz de usuario
    st.write("Elige un término económico de la lista o propón tu propio término:")

    opcion = st.radio("", ["Elegir de la lista", "Proponer mi propio término"])

    if opcion == "Elegir de la lista":
        termino = st.selectbox("Selecciona un término:", terminos_economicos)
    else:
        termino = st.text_input("Ingresa tu propio término económico:")

    # Selección de autores
    st.write("Selecciona uno o más autores de la Escuela Austríaca de Economía (máximo 5):")
    autores_seleccionados = st.multiselect("Autores", autores_austriacos)

    if len(autores_seleccionados) > 5:
        st.warning("Has seleccionado más de 5 autores. Por favor, selecciona un máximo de 5.")
    else:
        if st.button("Obtener definición"):
            if termino and autores_seleccionados:
                with st.spinner("Buscando información y generando definiciones..."):
                    definiciones = {}
                    todas_fuentes = []

                    for autor in autores_seleccionados:
                        # Buscar información relevante
                        resultados_busqueda = buscar_informacion(termino, autor)
                        contexto = "\n".join([item["snippet"] for item in resultados_busqueda.get("organic", [])])
                        fuentes = [item["link"] for item in resultados_busqueda.get("organic", [])]

                        # Generar definición
                        definicion = generar_definicion(termino, autor, contexto)

                        definiciones[autor] = definicion
                        todas_fuentes.extend(fuentes)

                    # Mostrar las definiciones
                    st.subheader(f"Definiciones para el término: {termino}")
                    for autor, definicion in definiciones.items():
                        st.markdown(f"**{autor}:** {definicion}")

                    # Botón para descargar el documento
                    doc = create_docx(termino, definiciones, todas_fuentes)
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    st.download_button(
                        label="Descargar definición en DOCX",
                        data=buffer,
                        file_name=f"Definicion_{termino.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.warning("Por favor, selecciona un término y al menos un autor.")

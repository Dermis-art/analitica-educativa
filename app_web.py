import pandas as pd
import streamlit as st


# --- 1. PROGRAMACIÓN ORIENTADA A OBJETOS (POO) ---
class Estudiante:
    def __init__(self, nombre: str, asistencia: float, parcial1: float, parcial2: float):
        self.nombre = nombre
        self.asistencia = asistencia
        self.parcial1 = parcial1
        self.parcial2 = parcial2

    def calcular_promedio(self) -> float:
        return round((self.parcial1 + self.parcial2) / 2, 1)

    def obtener_estado(self) -> str:
        if self.calcular_promedio() < 70 or self.asistencia < 75:
            return "En Riesgo"
        return "Satisfactorio"

    def a_diccionario(self) -> dict:
        return {
            "Estudiante": self.nombre,
            "Asistencia (%)": self.asistencia,
            "Parcial 1": self.parcial1,
            "Parcial 2": self.parcial2,
            "Promedio": self.calcular_promedio(),
            "Estado": self.obtener_estado(),
        }


class AnalizadorAula:
    def __init__(self, estudiantes: list):
        self.estudiantes = estudiantes
        self.df = pd.DataFrame([est.a_diccionario() for est in estudiantes])

    def promedio_general(self) -> float:
        if self.df.empty:
            return 0.0
        return round(self.df["Promedio"].mean(), 1)

    def asistencia_promedio(self) -> float:
        if self.df.empty:
            return 0.0
        return round(self.df["Asistencia (%)"].mean(), 1)

    def total_en_riesgo(self) -> int:
        if self.df.empty:
            return 0
        return int((self.df["Estado"] == "En Riesgo").sum())


# --- 2. MEMORIA DE SESIÓN (PARA NO PERDER DATOS AL RECARGAR) ---
if "estudiantes" not in st.session_state:
    st.session_state.estudiantes = [
        Estudiante("Ana", 95, 90, 92),
        Estudiante("Luis", 68, 65, 60),
        Estudiante("Carla", 88, 78, 84),
        Estudiante("Pedro", 72, 68, 70),
        Estudiante("Sofía", 98, 95, 96),
        Estudiante("Mateo", 60, 58, 62),
        Estudiante("Elena", 85, 82, 80),
    ]

# --- 3. BARRA LATERAL: FORMULARIO Y CARGA DE ARCHIVOS ---
st.set_page_config(page_title="Panel de Analítica Educativa", layout="wide")

with st.sidebar:
    st.header("Gestión de Estudiantes")

    # Función A: Formulario para inscribir estudiante nuevo en vivo
    with st.form("form_nuevo_estudiante", clear_on_submit=True):
        st.subheader("1. Registrar Nuevo")
        nombre = st.text_input("Nombre del estudiante")
        asistencia = st.number_input("Asistencia (%)", min_value=0.0, max_value=100.0, value=85.0)
        parcial1 = st.number_input("Nota Parcial 1", min_value=0.0, max_value=100.0, value=80.0)
        parcial2 = st.number_input("Nota Parcial 2", min_value=0.0, max_value=100.0, value=80.0)
        enviado = st.form_submit_button("Agregar al aula")

        if enviado:
            if nombre.strip():
                nuevo = Estudiante(nombre.strip(), asistencia, parcial1, parcial2)
                st.session_state.estudiantes.append(nuevo)
                st.success(f"{nombre} agregado correctamente.")
            else:
                st.error("Escribe el nombre del estudiante.")

    st.divider()

    # Función B: Subir archivo Excel o CSV propio
    st.subheader("2. Cargar desde Archivo")
    st.caption("Columnas requeridas: Estudiante, Asistencia, Parcial1, Parcial2")
    archivo_subido = st.file_uploader("Sube tu archivo CSV o Excel", type=("csv", "xlsx"))

    if archivo_subido is not None:
        if st.button("Importar datos del archivo"):
            try:
                if archivo_subido.name.endswith(".csv"):
                    df_subido = pd.read_csv(archivo_subido)
                else:
                    df_subido = pd.read_excel(archivo_subido)

                nuevos_importados = [
                    Estudiante(
                        str(fila.Estudiante),
                        float(fila.Asistencia),
                        float(fila.Parcial1),
                        float(fila.Parcial2),
                    )
                    for fila in df_subido.itertuples()
                ]
                st.session_state.estudiantes = nuevos_importados
                st.success(f"Se cargaron {len(nuevos_importados)} estudiantes.")
            except Exception as e:
                st.error(f"Error al leer el archivo: verifica los nombres de las columnas. ({e})")

# --- 4. PANEL PRINCIPAL ---
st.title("Panel de Rendimiento Académico")
st.write("Aplicación interactiva con **POO**, carga de archivos y exportación de reportes.")

analizador = AnalizadorAula(st.session_state.estudiantes)

col1, col2, col3 = st.columns(3)
col1.metric("Promedio General", f"{analizador.promedio_general()} pts")
col2.metric("Asistencia Promedio", f"{analizador.asistencia_promedio()}%")
col3.metric("Estudiantes en Riesgo", f"{analizador.total_en_riesgo()} de {len(st.session_state.estudiantes)}")

st.divider()

filtro = st.selectbox("Filtrar estudiantes por estado:", ("Todos", "En Riesgo", "Satisfactorio"))

if filtro == "Todos":
    df_mostrar = analizador.df
else:
    df_mostrar = analizador.df[analizador.df["Estado"] == filtro]

izq, der = st.columns(2)

with izq:
    st.subheader("Detalle de Estudiantes")
    st.dataframe(df_mostrar, hide_index=True)

    # Función C: Botón para descargar el reporte filtrado
    csv_descarga = df_mostrar.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="Descargar reporte filtrado (CSV)",
        data=csv_descarga,
        file_name=f"reporte_{filtro.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )

with der:
    st.subheader("Comparativa de Promedio y Asistencia")
    if not df_mostrar.empty:
        datos_grafico = df_mostrar.set_index("Estudiante").loc[:, ("Promedio", "Asistencia (%)")]
        st.bar_chart(datos_grafico)
    else:
        st.info("No hay estudiantes en esta categoría para graficar.")

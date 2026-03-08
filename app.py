import streamlit as st
import os
import cv2
from deepface import DeepFace

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Buscador de Hemeroteca", page_icon="📸", layout="wide")
st.title("📸 Buscador de Fotos del Periódico")
st.write("Sube la galería del evento y encuentra tus fotos al instante.")

# Crear carpetas temporales en el servidor
for folder in ['galeria', 'temp']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- INTERFAZ DE USUARIO ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Galería del Evento")
    galeria_archivos = st.file_uploader("Sube aquí las fotos de la fiesta", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with col2:
    st.header("2. Tu Selfie")
    selfie_archivo = st.file_uploader("Sube una foto de tu cara frontal", type=['jpg', 'jpeg', 'png'])

# --- MOTOR DE BÚSQUEDA ---
if st.button("🔍 Buscarme en las fotos", type="primary", use_container_width=True):
    if galeria_archivos and selfie_archivo:
        
        # 1. Guardar los archivos que ha subido el usuario
        for archivo in galeria_archivos:
            with open(os.path.join('galeria', archivo.name), "wb") as f:
                f.write(archivo.getbuffer())
        
        selfie_path = os.path.join('temp', selfie_archivo.name)
        with open(selfie_path, "wb") as f:
            f.write(selfie_archivo.getbuffer())

        st.info("Analizando rostros... Esto puede tardar unos segundos por foto.")
        
        # 2. Empezar a buscar
        fotos_exito = []
        archivos_guardados = os.listdir('galeria')
        
        # ¡Añadimos una barra de progreso visual!
        barra_progreso = st.progress(0)
        
        for i, foto in enumerate(archivos_guardados):
            ruta_target = os.path.join('galeria', foto)
            try:
                resultado = DeepFace.verify(
                    img1_path = selfie_path, 
                    img2_path = ruta_target, 
                    model_name = "VGG-Face",
                    enforce_detection = False
                )
                if resultado['verified']:
                    fotos_exito.append(ruta_target)
            except:
                pass # Si hay error en una foto, pasamos a la siguiente
            
            # Actualizar la barra de progreso
            barra_progreso.progress((i + 1) / len(archivos_guardados))

        # 3. Mostrar Resultados
        if fotos_exito:
            st.success(f"✨ ¡Bingo! Te hemos encontrado en {len(fotos_exito)} fotos.")
            st.markdown("---")
            
            # Mostrar las fotos en 3 columnas bonitas
            cols_resultado = st.columns(3)
            for idx, ruta_foto in enumerate(fotos_exito):
                img = cv2.imread(ruta_foto)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                with cols_resultado[idx % 3]:
                    st.image(img, caption=os.path.basename(ruta_foto), use_container_width=True)
        else:
            st.warning("🤷 No hemos encontrado tu cara en esta galería.")
            
    else:
        st.error("⚠️ Faltan archivos. Asegúrate de subir la galería y tu selfie antes de buscar.")
      

import streamlit as st
import sqlite3
import json
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cuentas Claras", page_icon="🍖", layout="centered", initial_sidebar_state="expanded")

# --- BARRA LATERAL (MONETIZACIÓN) ---
with st.sidebar:
    st.title("🍻 ¿Te salvamos la vida?")
    st.write("Si esta app te ahorró un dolor de cabeza matemático en tu junta, apáñanos con un aporte voluntario para seguir mejorándola.")
    st.link_button("💙 Aportar con Mercado Pago", "https://link.mercadopago.cl/appcuentasclaras")
    
    st.write("---")
    st.write("📢 **Espacio Publicitario Disponible**")
    st.caption("¿Tienes un local o negocio? Anúnciate aquí y llega a personas que están comprando para sus reuniones. Contáctanos.")

# --- BASE DE DATOS (MEMORIA LOCAL) ---
DB_NAME = "juntas_historial.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nombre_evento TEXT,
            total REAL,
            cuota REAL,
            participantes_json TEXT,
            transferencias_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_evento(nombre_evento, total, cuota, participantes, transferencias):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""
        INSERT INTO eventos (fecha, nombre_evento, total, cuota, participantes_json, transferencias_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_actual, nombre_evento, total, cuota, json.dumps(participantes), json.dumps(transferencias)))
    conn.commit()
    conn.close()

def obtener_historial():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, fecha, nombre_evento, total, cuota, transferencias_json FROM eventos ORDER BY id DESC")
    filas = c.fetchall()
    conn.close()
    return filas

init_db()

# --- LAS 3 PESTAÑAS PRINCIPALES ---
tab_calculo, tab_rapida, tab_historial = st.tabs(["🔥 Junta Compleja", "⚡ División Rápida", "📜 Historial Guardado"])

# ==========================================
# PESTAÑA 1: JUNTA COMPLEJA 
# ==========================================
with tab_calculo:
    st.title("🍖 Cuentas Claras")
    st.caption("Para cuando todos compraron cosas distintas.")

    nombre_evento = st.text_input("Nombre de la junta:", value="Asado de Fin de Semana")

    if "participantes" not in st.session_state:
        st.session_state.participantes = [
            {"nombre": "Jaime", "gasto": 35000},
            {"nombre": "Mauricio", "gasto": 25000},
            {"nombre": "Mariela", "gasto": 10000},
            {"nombre": "Juanito", "gasto": 0}
        ]

    st.write("### 👥 Participantes y Gastos")
    if st.button("➕ Agregar Persona"):
        st.session_state.participantes.append({"nombre": "", "gasto": 0})

    for i, persona in enumerate(st.session_state.participantes):
        col_nom, col_gas, col_del = st.columns([4, 4, 1])
        with col_nom:
            persona["nombre"] = st.text_input(f"Nombre #{i+1}", value=persona["nombre"], key=f"nom_{i}")
        with col_gas:
            persona["gasto"] = st.number_input(f"Gasto ($) #{i+1}", value=persona["gasto"], step=1000, key=f"gas_{i}")
        with col_del:
            st.write("")
            st.write("")
            if st.button("❌", key=f"del_{i}"):
                st.session_state.participantes.pop(i)
                st.rerun()

    st.write("---")
    st.write("### 🧾 Respaldo de Transparencia")
    boleta_compleja = st.file_uploader("Sube la foto de la boleta (Opcional)", type=["jpg", "jpeg", "png"], key="foto_1")

    if st.button("🔥 Calcular Cuentas", type="primary"):
        grupo = [p for p in st.session_state.participantes if p["nombre"].strip() != ""]
        
        if len(grupo) < 2:
            st.warning("Debes ingresar al menos 2 personas con nombre para calcular.")
        else:
            total = sum(p["gasto"] for p in grupo)
            cuota = total / len(grupo)
            
            st.success(f"Total gastado: ${total:,.0f} — Cuota por persona: ${cuota:,.0f}")
            
            deben = {}
            les_deben = {}
            
            for p in grupo:
                dif = p["gasto"] - cuota
                if dif < 0:
                    deben[p["nombre"]] = abs(dif)
                elif dif > 0:
                    les_deben[p["nombre"]] = dif
                    
            transferencias = []
            st.write("### 💸 Transferencias a realizar:")
            for deudor in list(deben.keys()):
                for acreedor in list(les_deben.keys()):
                    deuda_actual = deben[deudor]
                    credito_actual = les_deben[acreedor]
                    
                    if deuda_actual > 0 and credito_actual > 0:
                        pago = min(deuda_actual, credito_actual)
                        texto = f"👉 **{deudor}** le debe transferir **${pago:,.0f}** a **{acreedor}**"
                        st.info(texto)
                        transferencias.append(f"{deudor} -> ${pago:,.0f} a {acreedor}")
                        deben[deudor] -= pago
                        les_deben[acreedor] -= pago

            if boleta_compleja is not None:
                st.write("---")
                st.write("#### 📸 Boleta Adjunta:")
                st.image(boleta_compleja, use_container_width=True)

            guardar_evento(nombre_evento, total, cuota, grupo, transferencias)
            st.toast("¡Junta guardada en el historial!", icon="💾")

# ==========================================
# PESTAÑA 2: DIVISIÓN RÁPIDA
# ==========================================
with tab_rapida:
    st.title("⚡ Calculadora Rápida")
    st.caption("Para cuando una sola persona pagó la boleta completa y hay que dividir en partes iguales.")
    
    col1, col2 = st.columns(2)
    with col1:
        monto_boleta = st.number_input("Total de la boleta ($)", min_value=0, step=1000, value=40000)
    with col2:
        cantidad_personas = st.number_input("¿Entre cuántos se divide?", min_value=1, step=1, value=4)
        
    st.write("### 🧾 Respaldo de Transparencia")
    boleta_rapida = st.file_uploader("Sube la foto de la boleta para el grupo (Opcional)", type=["jpg", "jpeg", "png"], key="foto_2")

    if st.button("🚀 Dividir Boleta", type="primary"):
        cuota_rapida = monto_boleta / cantidad_personas
        st.success(f"### Cada uno te debe pagar: **${cuota_rapida:,.0f}**")
        
        if boleta_rapida is not None:
            st.write("---")
            st.write("#### 📸 Boleta Adjunta:")
            st.image(boleta_rapida, use_container_width=True)

# ==========================================
# PESTAÑA 3: HISTORIAL GUARDADO
# ==========================================
with tab_historial:
    st.write("### 📜 Juntas Guardadas en Memoria")
    historial = obtener_historial()
    
    if not historial:
        st.info("Aún no hay juntas registradas en la base de datos.")
    else:
        for item in historial:
            evento_id, fecha, titulo, tot, cuot, trans_json = item
            trans_lista = json.loads(trans_json)
            
            with st.expander(f"📅 {fecha} — **{titulo}** (${tot:,.0f})"):
                st.write(f"**Total:** ${tot:,.0f} — **Cuota unitaria:** ${cuot:,.0f}")
                st.write("**Pagos acordados:**")
                for t in trans_lista:
                    st.write(f"• {t}")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.title("Sistema de Gestión y Análisis de Inventario - TechZone")

# PREGUNTA 1
try:
    df = pd.read_excel("InventarioTechZone.xlsx")
except FileNotFoundError:
    st.error("No se encontró el archivo InventarioTechZone.xlsx")
    st.stop()

# PREGUNTA 2
df["FechaIngreso"] = pd.to_datetime(df["FechaIngreso"])

# PREGUNTA 10
df["ValorTotal"] = df["Precio"] * df["Stock"]
df["MargenGanancia"] = df["Precio"] * 0.12
df["DiasEnInventario"] = (pd.Timestamp.today() - df["FechaIngreso"]).dt.days

st.subheader("Inventario completo")
st.dataframe(df)

st.subheader("Filtros interactivos")

# PREGUNTA 3
categorias = st.multiselect(
    "Selecciona categoría",
    df["Categoria"].unique(),
    default=df["Categoria"].unique()
)

# PREGUNTA 4
estados = st.multiselect(
    "Selecciona estado",
    ["Disponible", "Agotado", "Descontinuado", "Crítico"],
    default=["Disponible", "Agotado", "Descontinuado", "Crítico"]
)

# PREGUNTA 5
precio_min, precio_max = st.slider(
    "Rango de precios",
    int(df["Precio"].min()),
    int(df["Precio"].max()),
    (int(df["Precio"].min()), int(df["Precio"].max()))
)

# PREGUNTA 6
busqueda = st.text_input("Buscar producto")

# PREGUNTA 7
usar_stock = st.checkbox("Filtrar por stock mínimo")

if usar_stock:
    stock_minimo = st.number_input("Stock mínimo", min_value=0, value=5)
else:
    stock_minimo = 0

df_filtrado = df[
    (df["Categoria"].isin(categorias)) &
    (df["Estado"].isin(estados)) &
    (df["Precio"] >= precio_min) &
    (df["Precio"] <= precio_max) &
    (df["Stock"] >= stock_minimo)
]

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["Producto"].str.contains(busqueda, case=False, na=False)
    ]

st.subheader("Inventario filtrado")
st.dataframe(df_filtrado)

# PREGUNTA 8 Y 9
st.subheader("Registro de nuevo producto")

def generar_codigo():
    return "PR-" + pd.Timestamp.now().strftime("%y%m%d-%H%M%S")

with st.form("form_producto"):
    nombre = st.text_input("Nombre del producto")
    categoria = st.selectbox("Categoría", ["Laptop", "Monitor", "Accesorio", "Periférico", "Componente"])
    precio = st.number_input("Precio unitario", min_value=0.0, step=1.0)
    stock = st.number_input("Stock disponible", min_value=0, step=1)
    fecha_ingreso = st.date_input("Fecha de ingreso")
    descontinuado = st.checkbox("Producto descontinuado")

    enviar = st.form_submit_button("Registrar producto")

    if enviar:
        if nombre == "":
            st.error("El nombre no puede estar vacío")
        elif precio <= 0:
            st.error("El precio debe ser mayor que 0")
        elif stock < 0:
            st.error("El stock debe ser mayor o igual a 0")
        elif fecha_ingreso > date.today():
            st.error("La fecha no puede ser futura")
        else:
            if descontinuado:
                estado = "Descontinuado"
            elif stock == 0:
                estado = "Agotado"
            elif stock < 5:
                estado = "Crítico"
            else:
                estado = "Disponible"

            nuevo_producto = {
                "Codigo": generar_codigo(),
                "Producto": nombre,
                "Categoria": categoria,
                "Precio": precio,
                "Stock": stock,
                "FechaIngreso": fecha_ingreso,
                "Estado": estado,
                "ValorTotal": precio * stock,
                "MargenGanancia": precio * 0.12,
                "DiasEnInventario": (date.today() - fecha_ingreso).days
            }

            df = pd.concat([df, pd.DataFrame([nuevo_producto])], ignore_index=True)
            st.success("Producto registrado correctamente")
            st.dataframe(pd.DataFrame([nuevo_producto]))

# PREGUNTA 11
st.subheader("Gráficos")

col1, col2 = st.columns(2)

with col1:
    st.write("Cantidad de productos por categoría")
    conteo_categoria = df_filtrado["Categoria"].value_counts()
    fig1, ax1 = plt.subplots()
    conteo_categoria.plot(kind="bar", ax=ax1)
    ax1.set_xlabel("Categoría")
    ax1.set_ylabel("Cantidad")
    st.pyplot(fig1)

with col2:
    st.write("Valor total por categoría")
    valor_categoria = df_filtrado.groupby("Categoria")["ValorTotal"].sum()
    fig2, ax2 = plt.subplots()
    valor_categoria.plot(kind="pie", autopct="%1.1f%%", ax=ax2)
    ax2.set_ylabel("")
    st.pyplot(fig2)

st.write("Top 5 productos más valiosos")
top5 = df_filtrado.sort_values("ValorTotal", ascending=False).head(5)

fig3, ax3 = plt.subplots()
ax3.bar(top5["Producto"], top5["ValorTotal"])
ax3.set_xlabel("Producto")
ax3.set_ylabel("Valor total")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig3)
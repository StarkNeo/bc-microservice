import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to the database development
"""conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port =os.getenv("PORT")
)"""

# Connect to the database production
conn = psycopg2.connect(os.getenv("URL_INTERNAL"))

cur = conn.cursor()

text_catalogo_impuestos = """CREATE TABLE IF NOT EXISTS catalogo_impuestos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT);"""

table_catalogo_impuestos = cur.execute(text_catalogo_impuestos)

text_cumplimiento = """CREATE TABLE IF NOT EXISTS cumplimiento_impuestos (
    id SERIAL PRIMARY KEY,
    rfc VARCHAR(13),
    razon_social TEXT,
    tipo_declaracion VARCHAR(15),
    mes INTEGER NOT NULL,
    ejercicio INTEGER NOT NULL,
    impuesto_id INT REFERENCES catalogo_impuestos(id),
    fecha_presentacion DATE,
    vencimiento DATE,
    numero_operacion VARCHAR(255),
    a_favor INTEGER,
    a_cargo INTEGER,
    actualizacion INTEGER,
    recargos INTEGER,
    cantidad_a_cargo INTEGER,
    compensaciones INTEGER,
    subsidio_empleo INTEGER,
    cantidad_a_pagar INTEGER,
    fecha_pago DATE);"""
table_cumplimiento = cur.execute(text_cumplimiento)
# conn.commit()

populate_catalogo_impuestos = """INSERT INTO catalogo_impuestos (nombre, descripcion) VALUES
        ('Impuesto al Valor Agregado Personas fisicas', 'IVA'),
        ('Impuesto al Valor Agregado Personas morales', 'IVA'),
        ('ISR personas físicas Actividad empresarial y profesional', 'ISR'),
        ('ISR personas físicas Arrendamiento de inmuebles', 'ISR'),
        ('ISR personas morales', 'ISR'),
        ('ISR POR PAGOS POR CUENTA DE TERCEROS O RETENCIONES POR', 'ISR RETENIDO'),
        ('ISR retenciones por salarios', 'ISR RETENIDO'),
        ('ISR RETENCIONES POR SERVICIOS PROFESIONALES REGIMEN SIMPLIFICADO DE CONFIANZA', 'ISR RETENIDO'),
        ('ISR simplificado de confianza Personas fisicas', 'ISR'),
        ('ISR simplificado de confianza Personas morales', 'ISR'),
        ('IVA retenciones', 'IVA RETENIDO'),
        ('IVA simplificado de confianza', 'IVA')

;"""

#catalogo = cur.execute("SELECT * FROM catalogo_impuestos LIMIT 10;")
#cur.execute(populate_catalogo_impuestos)
#conn.commit()
#cur.execute("SELECT * FROM catalogo_impuestos LIMIT 10;")
#print(cur.fetchall())


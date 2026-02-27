from pypdf import PdfReader
import csv
import os
import re
from dbconfig import cur
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)


def parse_text_date(date_str):
    # Define possible date formats
    date = date_str.strip()  # Remove leading/trailing whitespace
    date_formats = [
        "%d/%m/%Y",  # e.g., 31/12/2023
        "%d-%m-%Y",  # e.g., 31-12-2023
        "%Y/%m/%d",  # e.g., 2023/12/31
        "%Y-%m-%d",  # e.g., 2023-12-31
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Date format not recognized: {date_str}")

impuestos_dictionary={
     "Impuesto al Valor Agregado. Personas físicas": 1,
     "Impuesto al Valor Agregado. Personas morales": 2,
     "ISR personas físicas. Actividad empresarial y profesional": 3,
     "ISR personas físicas. Arrendamiento de inmuebles. (uso o goce)": 4,
     "ISR personas morales": 5,
     "ISR POR PAGOS POR CUENTA DE TERCEROS O RETENCIONES POR": 6,
     "ISR retenciones por salarios": 7,
     "ISR RETENCIONES POR SERVICIOS PROFESIONALES/RÉGIMEN SIMPLIFICADO DE": 8,
     "ISR simplificado de confianza. Personas físicas": 9,
     "ISR simplificado de confianza. Personas morales": 10,
     "IVA retenciones": 11,
     "IVA simplificado de confianza": 12
}

months_dictionary={
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}



def infoTaxesHandler(info):
    logging.info("--------------------INFORMACION DE LOS IMPUESTOS--------------")
    ### Separar por concepto de pago
    logging.info("--------------SEPARANDO POR CONCEPTO DE PAGO------------------")
    conceptos_pago = info.split("Concepto de pago")[1:]
    ### cuantos elementos hay en la lista sin contar el primer elemento
    logging.info(
        "------------------CANTIDAD DE CONCEPTOS DE PAGO ENCONTRADOS: --------------------"
    )
    
    filas = []  # conjunto de filas
    # recorrer los conceptos de pago
    for concepto in conceptos_pago:
        subconcepto = concepto.split("\n")
        if len(subconcepto[0].split(":")) < 2:
            next
        else:
            fila = {
                "actualizacion": 0,
                "recargos": 0,
                "a_favor": 0,
                "compensaciones": 0,
                #"fecha_pago": "",
            }
            nombre_impuesto = subconcepto[0].split(":")[1]
            for i, ch in enumerate(nombre_impuesto):
                if ch.isalpha():
                    resultado = nombre_impuesto[i:]                    
                    break
            fila["impuesto_id"] = impuestos_dictionary.get(resultado, 0)
            for sub in subconcepto[1:]:
                if len(sub) == 0:
                    next
                else:
                    subconcepto = sub.split(":")[0]
                    if subconcepto == "Parte actualizada":
                        fila["actualizacion"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    elif subconcepto == "Recargos":
                        fila["recargos"] =  0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    elif subconcepto == "A favor" or subconcepto == "Impuesto a favor":
                        fila["a_favor"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    elif subconcepto == "A cargo" or subconcepto == "Impuesto a cargo":
                        fila["a_cargo"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    elif subconcepto == "Compensaciones":
                        fila["compensaciones"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    elif subconcepto == "Cantidad a cargo":
                        fila["cantidad_a_cargo"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    elif subconcepto == "Cantidad a pagar":
                        fila["cantidad_a_pagar"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(a)","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(a)","-").replace(")",""))
                    elif subconcepto == "Subsidio para el empleo":
                        fila["subsidio_empleo"] = 0 if sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")","") == "" else int(sub.split(":")[1].strip().replace("$", "").replace(",", "").replace("(","-").replace(")",""))
                    
            filas.append(fila)
    return filas


def infoStatementHandler(info, filas):
    # 2da parte informacion de la declaracion
    info_dec_splitted = info.split("\n")
    version = False
    for element in info_dec_splitted:
        if "Versión" in element:
            version = True

    if version:
        linea = []

        for element in info_dec_splitted:
            if "RFC" in element:
                linea.append({"rfc": element.split(":")[1].split()[0]})
            elif "razón social" in element:
                linea.append({"razon_social": (element.split(":")[1]).replace("'", "")})
            elif "Nombre" in element:
                linea.append({"razon_social": (element.split(":")[1]).replace("'", "")})
            elif "Tipo de declaración" in element:
                linea.append({"tipo_declaracion": element.split(":")[1].split()[0]})                
            elif "Periodicidad" in element:
                linea.append({"mes": months_dictionary.get(element.split(":")[2].split()[0].lower(), 0)})  # periodo               
            elif "Ejercicio" in element:
                linea.append({"ejercicio": element.split(":")[1].split()[0]})
                linea.append({"fecha_presentacion": parse_text_date(element.split(":")[2].split()[0])})
            elif "Medio de presentación" in element:
                linea.append({"vencimiento": parse_text_date(element.split(":")[2])})
            elif "Versión" in element:
                linea.append(
                    {"numero_operacion": element.split(":")[2]}
                )  # fila["numero_operacion"] = element.split(":")[2]

        for att in linea:
            for key in att.keys():
                for fila in filas:
                    fila[key] = att[key]
    else:
        linea = []
        for element in info_dec_splitted:
            if "RFC" in element:
                linea.append({"rfc": element.split(":")[1].split()[0]})
                
            elif "razón social" in element:
                linea.append({"razon_social": (element.split(":")[1]).replace("'", "")})
                
            elif "Nombre" in element:
                linea.append({"razon_social": (element.split(":")[1]).replace("'", "")})
            elif "Tipo de declaración" in element:
                
                linea.append({"tipo_declaracion": element.split(":")[1].split()[0]})
                
            elif "Período de la declaración" in element:
              
                linea.append({"ejercicio": element.split(":")[2]})  # ejercicio
               
                linea.append({"mes": months_dictionary.get(element.split(":")[1].split()[0].lower(), 0)})  # periodo
                
            elif "Periodicidad" in element:
                linea.append({"mes": months_dictionary.get(element.split(":")[2].lower(), 0)})  # periodo
            elif "Ejercicio" in element:
                linea.append({"ejercicio": element.split(":")[1].split()[0]})
            elif "presentación" in element:
                linea.append({"fecha_presentacion": parse_text_date(element.split(":")[1].split()[0])})
            elif "Número de operación" in element:
                linea.append({"numero_operacion": element.split(":")[1]})
               
            elif "Vencimiento" in element:
                linea.append({"vencimiento":parse_text_date(element.split(":")[1].split()[0]) if element.split(":")[-1]=="" else parse_text_date(element.split(":")[-1])})
                
        for att in linea:
            for key in att.keys():
                for fila in filas:
                    fila[key] = att[key]

    return filas

#Exportar a Txt o Xls
def fileExporter(info):
    # Exportar a Txt o Xls
    heads = [
        "rfc",
        "razon_social",
        "tipo_declaracion",
        "mes",
        "ejercicio",
        "impuesto_id",
        "fecha_presentacion",
        "vencimiento",
        "numero_operacion",
        "a_favor",
        "a_cargo",
        "actualizacion",
        "recargos",
        "cantidad_a_cargo",
        "compensaciones",
        "subsidio_empleo",
        "cantidad_a_pagar",
        "fecha_pago",
    ]

    file_path = "control.csv"
    file_exists = os.path.isfile(file_path)
    is_empty = (
        not file_exists or os.path.getsize(file_path) == 0
    )  # Check if file is new or empty

    for fila in info:
        data = list(fila.values())
        
    with open(file_path, "a", newline="") as file:
        writer = csv.DictWriter(file, delimiter=",", fieldnames=heads)
        if is_empty:
            writer.writeheader()  # Only write headers if the file is empty
        for fila in info:
            writer.writerow(fila)

#Export to Database
def fileExporterDB(info):
    for fila in info:
        columns = ", ".join(fila.keys())
        values = ", ".join([f"'{value}'" for value in fila.values()])
        query = f"INSERT INTO cumplimiento_impuestos ({columns}) VALUES ({values});"
        cur.execute(query)
    cur.connection.commit()


def getPdfData(filename):
    reader = PdfReader(filename)
    page = reader.pages[0]
    text = page.extract_text()
    ### Primer Split dividirlo en dos tipos de informacion 1 la que contienen los impuestos y 2 la info de la declaracion
    info_taxes = text.split("ACUSE DE RECIBO")[0]
    info_statement = text.split("ACUSE DE RECIBO")[1]
    filas = infoTaxesHandler(info_taxes)
    rows = infoStatementHandler(info_statement, filas)
    fileExporterDB(rows)

def getCumplimientoData():
    cur.execute("""SELECT rfc, razon_social, tipo_declaracion, mes, 
                ejercicio, c.nombre, to_char(fecha_presentacion, 'DD-MM-YYYY'), numero_operacion, 
                a_favor, a_cargo, actualizacion, recargos, cantidad_a_cargo, 
                compensaciones, subsidio_empleo, cantidad_a_pagar
                FROM cumplimiento_impuestos
                JOIN catalogo_impuestos c ON cumplimiento_impuestos.impuesto_id = c.id
                ;""")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    return data

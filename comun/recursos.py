import os

try:
    from barcode import Code128
    from barcode.writer import ImageWriter
    HAY_BARCODE = True
except ImportError:
    HAY_BARCODE = False

try:
    import qrcode
    HAY_QR = True
except ImportError:
    HAY_QR = False

try:
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as ImagenExcel
    HAY_EXCEL = True
except ImportError:
    HAY_EXCEL = False

try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    HAY_PIL = True
except ImportError:
    HAY_PIL = False

CARPETA_SALIDA = "salida"

def _asegurar_carpeta():
    if not os.path.exists(CARPETA_SALIDA):
        os.makedirs(CARPETA_SALIDA)

def _cargar_fuente(tamano=18):
    if not HAY_PIL:
        return None
    try:
        return ImageFont.truetype("arial.ttf", tamano)
    except Exception:
        return ImageFont.load_default()

def generar_codigo_barras(codigo):
    _asegurar_carpeta()
    ruta_base = os.path.join(CARPETA_SALIDA, "barcode_" + codigo)
    if HAY_BARCODE:
        barras = Code128(codigo, writer=ImageWriter())
        return barras.save(ruta_base)
    ruta_txt = ruta_base + ".txt"
    with open(ruta_txt, "w", encoding="utf-8") as archivo:
        archivo.write("CODIGO DE BARRAS (texto): " + codigo + "\n")
    return ruta_txt

def generar_qr(contenido, nombre):
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_SALIDA, nombre)
    if HAY_QR:
        qr = qrcode.QRCode(version=2, box_size=10, border=4)
        qr.add_data(contenido)
        qr.make(fit=True)
        imagen = qr.make_image(fill_color="black", back_color="white")
        ruta_png = ruta + ".png"
        imagen.save(ruta_png)
        return ruta_png
    ruta_txt = ruta + ".txt"
    with open(ruta_txt, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
    return ruta_txt

def generar_rotulado_imagen(texto, nombre):
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_SALIDA, nombre)
    if HAY_PIL:
        imagen = PILImage.new("RGB", (620, 460), color="white")
        dibujo = ImageDraw.Draw(imagen)
        dibujo.multiline_text((20, 20), texto, fill="black",
                              font=_cargar_fuente(), spacing=6)
        ruta_png = ruta + ".png"
        imagen.save(ruta_png)
        return ruta_png
    ruta_txt = ruta + ".txt"
    with open(ruta_txt, "w", encoding="utf-8") as archivo:
        archivo.write(texto)
    return ruta_txt

def exportar_excel(nombre_archivo, encabezados, filas, imagenes=None):
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)
    if HAY_EXCEL:
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Reporte"
        hoja.append(encabezados)
        for fila in filas:
            hoja.append(fila)
        if imagenes:
            for ruta_img, celda in imagenes:
                if ruta_img and os.path.exists(ruta_img) and ruta_img.lower().endswith(".png"):
                    img = ImagenExcel(ruta_img)
                    img.width = 160
                    img.height = 160
                    hoja.add_image(img, celda)
        ruta_xlsx = ruta + ".xlsx"
        libro.save(ruta_xlsx)
        return ruta_xlsx
    ruta_csv = ruta + ".csv"
    with open(ruta_csv, "w", encoding="utf-8") as archivo:
        archivo.write(";".join(str(c) for c in encabezados) + "\n")
        for fila in filas:
            archivo.write(";".join(str(c) for c in fila) + "\n")
    return ruta_csv

def estado_librerias():
    def marca(ok):
        return "disponible" if ok else "NO instalada (se usa respaldo en texto)"
    return (
        "  python-barcode : " + marca(HAY_BARCODE) + "\n"
        "  qrcode         : " + marca(HAY_QR) + "\n"
        "  openpyxl       : " + marca(HAY_EXCEL) + "\n"
        "  pillow (PIL)   : " + marca(HAY_PIL)
    )

from io import BytesIO
from datetime import datetime
from collections import Counter

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)


def generar_pdf_ventas(ventas, titulo_periodo="Todo el historial"):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elementos = []
    estilos = getSampleStyleSheet()

    total_general = sum(venta.total for venta in ventas)
    cantidad_ventas = len(ventas)

    productos = [
        venta.producto.nombre
        for venta in ventas
    ]

    producto_mas_vendido = "Sin ventas"

    if productos:
        producto_mas_vendido = Counter(productos).most_common(1)[0][0]

    promedio = 0

    if cantidad_ventas > 0:
        promedio = total_general / cantidad_ventas

    titulo = Paragraph(
        "SmartGastro - Reporte de Ventas",
        estilos["Title"]
    )

    subtitulo = Paragraph(
        f"<b>Período:</b> {titulo_periodo}<br/>"
        f"<b>Generado el:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        estilos["Normal"]
    )

    elementos.append(titulo)
    elementos.append(subtitulo)
    elementos.append(Spacer(1, 18))

    resumen_data = [
        ["Ventas", "Total vendido", "Producto más vendido", "Promedio por venta"],
        [
            str(cantidad_ventas),
            f"${total_general:.2f}",
            producto_mas_vendido,
            f"${promedio:.2f}"
        ]
    ]

    resumen = Table(resumen_data, colWidths=[90, 120, 160, 120])

    resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ecfdf5")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#166534")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elementos.append(resumen)
    elementos.append(Spacer(1, 24))

    data = [
        ["ID", "Producto", "Cantidad", "Total", "Usuario", "Fecha"]
    ]

    for venta in ventas:
        data.append([
            str(venta.id),
            venta.producto.nombre,
            str(venta.cantidad),
            f"${venta.total:.2f}",
            venta.usuario.nombre,
            venta.fecha.strftime("%d/%m/%Y %H:%M")
        ])

    if cantidad_ventas == 0:
        data.append([
            "-",
            "Sin ventas para este período",
            "-",
            "-",
            "-",
            "-"
        ])

    tabla = Table(
        data,
        repeatRows=1,
        colWidths=[40, 120, 70, 80, 90, 110]
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16a34a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    pie = Paragraph(
        "Reporte generado automáticamente por SmartGastro MVP.",
        estilos["Italic"]
    )

    elementos.append(pie)

    doc.build(elementos)

    buffer.seek(0)
    return buffer
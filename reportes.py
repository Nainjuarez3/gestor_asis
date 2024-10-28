from fpdf import FPDF
from database import obtener_asistencia_por_profesor, conectar
import matplotlib.pyplot as plt


def generar_reporte_por_profesor(profesor, fecha_inicio, fecha_fin):
    """
    Genera un reporte de asistencia en PDF para un profesor en un rango de fechas específico.

    Parameters:
    profesor (str): Nombre del profesor.
    fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
    fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'.
    """
    registros = obtener_asistencia_por_profesor(profesor, fecha_inicio, fecha_fin)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, f'Reporte de Asistencia para {profesor}', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, 'Fecha', 1)
    pdf.cell(50, 10, 'Día Semana', 1)
    pdf.cell(50, 10, 'Hora Inicio', 1)
    pdf.cell(40, 10, 'Asistencia', 1)
    pdf.ln()
    pdf.set_font('Arial', '', 12)
    for registro in registros:
        fecha = registro[4]
        dia_semana = registro[1]
        hora_inicio = registro[2]
        presente = "Sí" if registro[3] else "No"
        pdf.cell(50, 10, fecha, 1)
        pdf.cell(50, 10, dia_semana, 1)
        pdf.cell(50, 10, hora_inicio, 1)
        pdf.cell(40, 10, presente, 1)
        pdf.ln()
    pdf.output(f'reporte_asistencia_{profesor}_{fecha_inicio}_a_{fecha_fin}.pdf')

def generar_reporte_por_materia(materia, fecha_inicio, fecha_fin):
    """
    Genera un reporte en PDF de asistencia por materia en un rango de fechas específico.

    Parameters:
    materia (str): Nombre de la materia.
    fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
    fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT profesor, COUNT(*) AS total_clases, SUM(CASE WHEN presente = 1 THEN 1 ELSE 0 END) AS clases_asistidas
        FROM asistencia_profesores
        WHERE dia_semana = ? AND fecha BETWEEN ? AND ?
        GROUP BY profesor
    """, (materia, fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    conexion.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, f'Reporte de Asistencia por Materia: {materia}', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 10, 'Profesor', 1)
    pdf.cell(40, 10, 'Total Clases', 1)
    pdf.cell(40, 10, 'Clases Asistidas', 1)
    pdf.cell(40, 10, 'Porcentaje', 1)
    pdf.ln()
    pdf.set_font('Arial', '', 12)
    for profesor, total_clases, clases_asistidas in registros:
        porcentaje = f"{(clases_asistidas / total_clases) * 100:.2f}%" if total_clases > 0 else "0%"
        pdf.cell(60, 10, profesor, 1)
        pdf.cell(40, 10, str(total_clases), 1)
        pdf.cell(40, 10, str(clases_asistidas), 1)
        pdf.cell(40, 10, porcentaje, 1)
        pdf.ln()
    pdf.output(f'reporte_asistencia_materia_{materia}_{fecha_inicio}_a_{fecha_fin}.pdf')


def generar_estadisticas_globales(fecha_inicio, fecha_fin):
    """
    Genera un reporte en PDF con el promedio general de asistencia por carrera.
    Incluye una gráfica de barras con el promedio de asistencia.
    Si no hay información registrada para alguna carrera, se imprime un mensaje indicando la ausencia de datos.

    Parameters:
    fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
    fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'.
    """
    conexion = conectar()
    cursor = conexion.cursor()

    # Consulta para obtener el promedio de asistencia por carrera utilizando la columna `carrera`
    query_carrera = """
        SELECT usuarios.carrera AS carrera, COUNT(asistencia_profesores.id) AS total_clases,
               SUM(CASE WHEN asistencia_profesores.presente = 1 THEN 1 ELSE 0 END) AS clases_asistidas
        FROM asistencia_profesores
        JOIN usuarios ON asistencia_profesores.profesor = usuarios.nombre
        WHERE asistencia_profesores.fecha BETWEEN ? AND ?
        GROUP BY usuarios.carrera
    """
    cursor.execute(query_carrera, (fecha_inicio, fecha_fin))
    registros_carrera = cursor.fetchall()
    conexion.close()

    # Preparar datos para la gráfica
    carreras = []
    porcentajes_asistencia = []
    carreras_esperadas = ["ICI", "ISET", "IME", "IM"]
    registros_dict = {registro[0]: registro for registro in registros_carrera}

    for carrera in carreras_esperadas:
        if carrera in registros_dict:
            _, total_clases, clases_asistidas = registros_dict[carrera]
            porcentaje = (clases_asistidas / total_clases * 100) if total_clases > 0 else 0
            carreras.append(carrera)
            porcentajes_asistencia.append(porcentaje)
        else:
            carreras.append(carrera)
            porcentajes_asistencia.append(0)

    # Crear la gráfica
    plt.figure(figsize=(8, 6))
    plt.bar(carreras, porcentajes_asistencia, color='skyblue')
    plt.title(f'Promedio de Asistencia por Carrera ({fecha_inicio} a {fecha_fin})')
    plt.xlabel('Carrera')
    plt.ylabel('Porcentaje de Asistencia (%)')
    plt.ylim(0, 100)
    plt.savefig('grafica_asistencia.png')  # Guardar la gráfica como imagen
    plt.close()

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Estadísticas Globales de Asistencia por Carrera', ln=True, align='C')
    
    # Agregar el rango de fechas debajo del título
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(200, 10, f"Rango de fechas: {fecha_inicio} a {fecha_fin}", ln=True, align='C')
    pdf.ln(10)

    # Mostrar el porcentaje de asistencia por carrera en el PDF
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, 'Promedio de Asistencia por Carrera:', ln=True)
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)

    for carrera, porcentaje in zip(carreras, porcentajes_asistencia):
        if porcentaje > 0:
            pdf.cell(200, 10, f"{carrera}: {porcentaje:.2f}%", ln=True)
        else:
            pdf.cell(200, 10, f"{carrera}: No hay información disponible", ln=True)

    pdf.ln(10)
    
    # Agregar la imagen de la gráfica al PDF
    pdf.image('grafica_asistencia.png', x=35, w=140)

    # Guardar el archivo PDF
    pdf.output(f'estadisticas_globales_{fecha_inicio}_a_{fecha_fin}.pdf')
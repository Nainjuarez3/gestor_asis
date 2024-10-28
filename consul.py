import sqlite3

# Conectar a la base de datos
conexion = sqlite3.connect('asistencia.db')
cursor = conexion.cursor()

# Consulta SQL para verificar registros de asistencia por carrera
query = """
    SELECT usuarios.rol AS carrera, COUNT(asistencia_profesores.id) AS total_clases,
           SUM(CASE WHEN asistencia_profesores.presente = 1 THEN 1 ELSE 0 END) AS clases_asistidas
    FROM asistencia_profesores
    JOIN usuarios ON asistencia_profesores.profesor = usuarios.nombre
    WHERE asistencia_profesores.fecha BETWEEN ? AND ?
    GROUP BY usuarios.rol
"""

# Define el rango de fechas a consultar
fecha_inicio = '2024-01-01'  # Ajusta a tus fechas deseadas
fecha_fin = '2024-12-31'     # Ajusta a tus fechas deseadas

# Ejecutar la consulta
cursor.execute(query, (fecha_inicio, fecha_fin))

# Obtener y mostrar los resultados
resultados = cursor.fetchall()

if resultados:
    for carrera, total_clases, clases_asistidas in resultados:
        print(f"Carrera: {carrera}, Total de Clases: {total_clases}, Clases Asistidas: {clases_asistidas}")
else:
    print("No se encontraron registros para el rango de fechas especificado.")

# Cerrar la conexión
conexion.close()

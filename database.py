import sqlite3
from datetime import datetime

def conectar():
    """
    Establece una conexión con la base de datos 'asistencia.db'.

    Returns:
    sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    return sqlite3.connect('asistencia.db')

def crear_tablas():
    """
    Crea las tablas 'usuarios' y 'asistencia_profesores' en la base de datos si no existen.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        rol TEXT NOT NULL,  
        correo TEXT UNIQUE NOT NULL,
        contrasena TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asistencia_profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profesor TEXT NOT NULL,
        dia_semana TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        presente BOOLEAN NOT NULL,
        fecha TEXT NOT NULL
    )
    ''')
    conexion.commit()
    conexion.close()

def crear_usuario(nombre, rol, correo, contrasena):
    """
    Crea un nuevo usuario en la tabla 'usuarios' si el correo no está registrado.

    Parameters:
    nombre (str): Nombre del usuario.
    rol (str): Rol del usuario (ej. 'admin', 'maestro').
    correo (str): Correo electrónico único del usuario.
    contrasena (str): Contraseña del usuario.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE correo = ?', (correo,))
    if cursor.fetchone() is None:
        cursor.execute('''
        INSERT INTO usuarios (nombre, rol, correo, contrasena)
        VALUES (?, ?, ?, ?)
        ''', (nombre, rol, correo, contrasena))
        conexion.commit()
    conexion.close()

def registrar_asistencia_profesor(profesor, dia_semana, hora_inicio, presente, fecha=None):
    """
    Registra la asistencia de un profesor en una fecha específica.

    Parameters:
    profesor (str): Nombre del profesor.
    dia_semana (str): Día de la semana.
    hora_inicio (str): Hora de inicio de la clase.
    presente (bool): Estado de asistencia (True si asistió, False si no).
    fecha (str, optional): Fecha del registro en formato 'YYYY-MM-DD'.
                          Si no se proporciona, se utiliza la fecha actual.
    """
    if fecha is None:
        fecha = datetime.now().strftime('%Y-%m-%d')
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
    INSERT INTO asistencia_profesores (profesor, dia_semana, hora_inicio, presente, fecha)
    VALUES (?, ?, ?, ?, ?)
    ''', (profesor, dia_semana, hora_inicio, presente, fecha))
    conexion.commit()
    conexion.close()

def obtener_usuario(correo, contrasena):
    """
    Obtiene un usuario de la base de datos basado en el correo y contraseña.

    Parameters:
    correo (str): Correo electrónico del usuario.
    contrasena (str): Contraseña del usuario.

    Returns:
    tuple or None: Datos del usuario si las credenciales coinciden, de lo contrario, None.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE correo = ? AND contrasena = ?', (correo, contrasena))
    usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_asistencia_por_profesor(profesor, fecha_inicio, fecha_fin):
    """
    Obtiene los registros de asistencia de un profesor en un rango de fechas.

    Parameters:
    profesor (str): Nombre del profesor.
    fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
    fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'.

    Returns:
    list: Lista de tuplas con los registros de asistencia del profesor.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
    SELECT profesor, dia_semana, hora_inicio, presente, fecha
    FROM asistencia_profesores
    WHERE profesor = ? AND fecha BETWEEN ? AND ?
    ORDER BY fecha
    """
    cursor.execute(query, (profesor, fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    conexion.close()
    return registros

def obtener_lista_maestros():
    """
    Obtiene una lista de nombres únicos de maestros registrados en la base de datos.

    Returns:
    list: Lista de nombres de maestros.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT DISTINCT nombre FROM usuarios WHERE rol = 'maestro'")
    maestros = [row[0] for row in cursor.fetchall()]
    conexion.close()
    return maestros

def obtener_lista_materias():
    """
    Obtiene una lista de materias únicas registradas en la tabla 'asistencia_profesores'.

    Returns:
    list: Lista de nombres de materias.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT DISTINCT dia_semana FROM asistencia_profesores")  # Ajusta el campo según la estructura real
    materias = [row[0] for row in cursor.fetchall()]
    conexion.close()
    return materias

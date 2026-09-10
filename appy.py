from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'alan',
    'password': '12345678',
    'database': 'wallstreet_db',
    'autocommit': True,
}


def conectar_db():
    return mysql.connector.connect(**DB_CONFIG)


def obtener_usuarios(limit=None):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        if limit:
            cursor.execute(
                """
                SELECT id, nombre, correo, telefono, fecha_nac, rol, fecha_registro
                FROM usuarios
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )
        else:
            cursor.execute(
                """
                SELECT id, nombre, correo, telefono, fecha_nac, rol, fecha_registro
                FROM usuarios
                ORDER BY id DESC
                """
            )

        usuarios = cursor.fetchall()
        cursor.close()
        conexion.close()
        return usuarios, None
    except Error as e:
        return [], f"No se pudo conectar a MySQL: {e}"


@app.route('/', methods=['GET', 'POST'])
def home():
    mensaje = ""
    error = ""

    usuarios, db_error = obtener_usuarios(limit=10)

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        fecha_nac = request.form.get('fecha_nac', '').strip()

        if not nombre or not correo or not telefono or not fecha_nac:
            error = 'Completa todos los campos del registro.'
        else:
            try:
                conexion = conectar_db()
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    INSERT INTO usuarios (nombre, correo, telefono, fecha_nac, rol)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (nombre, correo, telefono, fecha_nac, 'usuario')
                )
                conexion.commit()
                cursor.close()
                conexion.close()
                mensaje = f'Registro exitoso para {nombre}.'
                usuarios, db_error = obtener_usuarios(limit=10)
            except Error as e:
                error = f'Error al guardar en la base de datos: {e}'

    return render_template(
        'index_simple.html',
        usuarios=usuarios,
        mensaje=mensaje,
        error=error if error else db_error,
    )


@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    mensaje = ""
    error = ""
    usuarios, db_error = obtener_usuarios()

    if request.method == 'POST':
        accion = request.form.get('accion')
        usuario_id = request.form.get('id', '').strip()

        if accion == 'editar':
            nombre = request.form.get('nombre', '').strip()
            correo = request.form.get('correo', '').strip()
            telefono = request.form.get('telefono', '').strip()
            fecha_nac = request.form.get('fecha_nac', '').strip()
            rol = request.form.get('rol', '').strip()

            if not usuario_id or not nombre or not correo or not telefono or not fecha_nac or not rol:
                error = 'Completa todos los campos antes de actualizar.'
            else:
                if rol not in ('usuario', 'admin'):
                    error = 'El rol debe ser usuario o admin.'
                else:
                    try:
                        conexion = conectar_db()
                        cursor = conexion.cursor()
                        cursor.execute(
                            """
                            UPDATE usuarios
                            SET nombre = %s,
                                correo = %s,
                                telefono = %s,
                                fecha_nac = %s,
                                rol = %s
                            WHERE id = %s
                            """,
                            (nombre, correo, telefono, fecha_nac, rol, usuario_id)
                        )
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        mensaje = 'Usuario actualizado correctamente.'
                    except Error as e:
                        error = f'No se pudo actualizar el usuario: {e}'

        elif accion == 'eliminar':
            if not usuario_id:
                error = 'No se encontró el usuario a eliminar.'
            else:
                try:
                    conexion = conectar_db()
                    cursor = conexion.cursor()
                    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                    conexion.commit()
                    cursor.close()
                    conexion.close()
                    mensaje = 'Usuario eliminado correctamente.'
                except Error as e:
                    error = f'No se pudo eliminar el usuario: {e}'

    usuarios, db_error = obtener_usuarios()

    return render_template(
        'admin.html',
        usuarios=usuarios,
        mensaje=mensaje,
        error=error if error else db_error,
    )


@app.route('/gta-1')
def gta_1():
    return render_template('gta_1.html')


@app.route('/gta-2')
def gta_2():
    return render_template('gta_2.html')


@app.route('/gta-3')
def gta_3():
    return render_template('gta_3.html')


if __name__ == '__main__':
    app.run(debug=True)

import os
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'wallstreet.db')


def conectar_db():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            telefono TEXT NOT NULL,
            fecha_nac TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario' CHECK(rol IN ('usuario', 'admin')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conexion.commit()
    cursor.close()
    conexion.close()


inicializar_db()


def obtener_usuarios(limit=None):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        if limit:
            cursor.execute(
                """
                SELECT id, nombre, correo, telefono, fecha_nac, rol, fecha_registro
                FROM usuarios
                ORDER BY id DESC
                LIMIT ?
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

        usuarios = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        return usuarios, None
    except sqlite3.Error as e:
        return [], f"No se pudo conectar a SQLite: {e}"


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
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (nombre, correo, telefono, fecha_nac, 'usuario')
                )
                conexion.commit()
                cursor.close()
                conexion.close()
                mensaje = f'Registro exitoso para {nombre}.'
                usuarios, db_error = obtener_usuarios(limit=10)
            except sqlite3.Error as e:
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
                            SET nombre = ?,
                                correo = ?,
                                telefono = ?,
                                fecha_nac = ?,
                                rol = ?
                            WHERE id = ?
                            """,
                            (nombre, correo, telefono, fecha_nac, rol, usuario_id)
                        )
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        mensaje = 'Usuario actualizado correctamente.'
                    except sqlite3.Error as e:
                        error = f'No se pudo actualizar el usuario: {e}'

        elif accion == 'eliminar':
            if not usuario_id:
                error = 'No se encontró el usuario a eliminar.'
            else:
                try:
                    conexion = conectar_db()
                    cursor = conexion.cursor()
                    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
                    conexion.commit()
                    cursor.close()
                    conexion.close()
                    mensaje = 'Usuario eliminado correctamente.'
                except sqlite3.Error as e:
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

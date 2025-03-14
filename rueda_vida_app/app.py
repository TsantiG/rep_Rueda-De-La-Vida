from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
from functools import wraps
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Necesario para entornos sin interfaz gráfica
import io
import base64
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.spider import SpiderChart

app = Flask(__name__)

# Cargar configuraciones
app.config.from_object('config.Config')

# Inicializar la conexión a MySQL
mysql = MySQL(app)

# Función decorador para verificar si el usuario está logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Inicia sesión para acceder', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Función decorador para verificar si el usuario es administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or 'es_admin' not in session or not session['es_admin']:
            flash('No tienes permisos para acceder', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']
        sexo = request.form['sexo']
        tipo_empleado = request.form['tipo_empleado']
        contrasena = request.form['contrasena']
        confirm_contrasena = request.form['confirm_contrasena']
        
        # Validar contraseñas
        if contrasena != confirm_contrasena:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
        
        # Crear cursor para consultas
        cur = mysql.connection.cursor()
        
        # Verificar si el correo ya existe
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", [correo])
        user = cur.fetchone()
        
        if user:
            flash('Este correo ya está registrado', 'danger')
            cur.close()
            return render_template('register.html')
        
        # Insertar usuario
        hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')

        cur.execute("INSERT INTO usuarios (nombre, correo, sexo, tipo_empleado, contrasena) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, correo, sexo, tipo_empleado, hashed_password))
        
        # Confirmar cambios en la base de datos
        mysql.connection.commit()
        cur.close()
        
        flash('Te has registrado exitosamente. Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener datos del formulario
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        # Crear cursor para consultas
        cur = mysql.connection.cursor()
        
        # Verificar usuario
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", [correo])
        user = cur.fetchone()
        
        if user and check_password_hash(user['contrasena'], contrasena):
            # Crear sesión
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['nombre'] = user['nombre']
            session['correo'] = user['correo']
            session['es_admin'] = bool(user['es_admin'])
            
            flash('Has iniciado sesión exitosamente', 'success')
            
            if session['es_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
        
        cur.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Obtener historial de respuestas del usuario
    cur.execute("""
        SELECT rr.id, rr.fecha 
        FROM respuestas_rueda rr 
        WHERE rr.usuario_id = %s 
        ORDER BY rr.fecha DESC
    """, [session['user_id']])
    historial = cur.fetchall()
    
    cur.close()
    
    return render_template('dashboard.html', historial=historial)

@app.route('/rueda_form')
@login_required
def rueda_form():
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Obtener categorías
    cur.execute("SELECT * FROM categorias ORDER BY id")
    categorias = cur.fetchall()
    
    cur.close()
    
    return render_template('rueda_form.html', categorias=categorias)

@app.route('/guardar_rueda', methods=['POST'])
@login_required
def guardar_rueda():
    if request.method == 'POST':
        # Crear cursor para consultas
        cur = mysql.connection.cursor()
        
        # Crear entrada en respuestas_rueda
        cur.execute("INSERT INTO respuestas_rueda (usuario_id) VALUES (%s)", 
                    [session['user_id']])
        respuesta_id = cur.connection.insert_id()
        
        # Obtener categorías
        cur.execute("SELECT * FROM categorias")
        categorias = cur.fetchall()
        
        # Guardar respuestas para cada categoría
        for categoria in categorias:
            valor = request.form.get(f'cat_{categoria["id"]}')
            if valor:
                cur.execute("INSERT INTO detalle_respuestas (respuesta_id, categoria_id, valor) VALUES (%s, %s, %s)",
                            (respuesta_id, categoria["id"], valor))
        
        # Confirmar cambios en la base de datos
        mysql.connection.commit()
        cur.close()
        
        flash('Tu rueda de la vida ha sido guardada exitosamente', 'success')
        return redirect(url_for('ver_resultado', respuesta_id=respuesta_id))
    
    return redirect(url_for('rueda_form'))

@app.route('/descargar_pdf/<int:respuesta_id>')
@login_required
def descargar_pdf(respuesta_id):
    # Verificar que el usuario tenga acceso a esta respuesta
    cur = mysql.connection.cursor()
    
    # Verificar que la respuesta pertenezca al usuario o sea admin
    cur.execute("""
        SELECT * FROM respuestas_rueda 
        WHERE id = %s AND (usuario_id = %s OR %s = TRUE)
    """, (respuesta_id, session['user_id'], session.get('es_admin', False)))
    
    respuesta = cur.fetchone()
    
    if not respuesta:
        flash('No tienes permiso para ver estos resultados', 'danger')
        return redirect(url_for('dashboard'))
    
    # Obtener información del usuario
    cur.execute("""
        SELECT u.nombre, u.correo, u.sexo, u.tipo_empleado, rr.fecha
        FROM usuarios u
        JOIN respuestas_rueda rr ON u.id = rr.usuario_id
        WHERE rr.id = %s
    """, [respuesta_id])
    
    info_usuario = cur.fetchone()
    
    # Obtener detalles de la respuesta
    cur.execute("""
        SELECT c.nombre, dr.valor 
        FROM detalle_respuestas dr
        JOIN categorias c ON dr.categoria_id = c.id
        WHERE dr.respuesta_id = %s
    """, [respuesta_id])
    
    detalles = cur.fetchall()
    cur.close()
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Título
    elements.append(Paragraph("Informe de Rueda de la Vida", title_style))
    elements.append(Spacer(1, 12))
    
    # Información del usuario
    elements.append(Paragraph("Información del Usuario", heading_style))
    elements.append(Spacer(1, 6))
    
    user_data = [
        ["Nombre:", info_usuario['nombre']],
        ["Correo:", info_usuario['correo']],
        ["Sexo:", info_usuario['sexo']],
        ["Tipo de Empleado:", info_usuario['tipo_empleado']],
        ["Fecha de Evaluación:", info_usuario['fecha'].strftime('%d/%m/%Y %H:%M')]
    ]
    
    user_table = Table(user_data, colWidths=[100, 300])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(user_table)
    elements.append(Spacer(1, 12))
    
    # Resultados
    elements.append(Paragraph("Resultados por Categoría", heading_style))
    elements.append(Spacer(1, 6))
    
    # Tabla de resultados
    result_data = [["Categoría", "Valor (1-10)"]]
    for detalle in detalles:
        result_data.append([detalle['nombre'], str(detalle['valor'])])
    
    result_table = Table(result_data, colWidths=[250, 150])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(result_table)
    elements.append(Spacer(1, 12))
    
    # Gráfico de radar (rueda de la vida)
    elements.append(Paragraph("Representación Gráfica", heading_style))
    elements.append(Spacer(1, 6))
    
    # Preparar datos para el gráfico
    categorias = [detalle['nombre'] for detalle in detalles]
    valores = [detalle['valor'] for detalle in detalles]
    
    # Crear gráfico de radar
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)
    
    # Número de categorías
    N = len(categorias)
    
    # Ángulos para cada categoría (en radianes)
    angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
    angles += angles[:1]  # Cerrar el círculo
    
    # Valores para cada categoría
    valores += valores[:1]  # Cerrar el círculo
    
    # Dibujar el gráfico
    ax.plot(angles, valores, linewidth=1, linestyle='solid')
    ax.fill(angles, valores, alpha=0.1)
    
    # Añadir etiquetas
    plt.xticks(angles[:-1], categorias)
    
    # Configurar límites del eje y
    ax.set_rlabel_position(0)
    plt.yticks([2, 4, 6, 8, 10], ["2", "4", "6", "8", "10"], color="grey", size=7)
    plt.ylim(0, 10)
    
    # Guardar gráfico en memoria
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    
    # Añadir imagen al PDF
    img = Image(img_buffer, width=400, height=400)
    elements.append(img)
    
    # Añadir interpretación
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Interpretación", heading_style))
    elements.append(Spacer(1, 6))
    
    # Encontrar categorías con mayor y menor puntuación
    max_cat = max(detalles, key=lambda x: x['valor'])
    min_cat = min(detalles, key=lambda x: x['valor'])
    
    elements.append(Paragraph(f"Fortaleza: {max_cat['nombre']} ({max_cat['valor']}/10)", normal_style))
    elements.append(Paragraph(f"Área de mejora: {min_cat['nombre']} ({min_cat['valor']}/10)", normal_style))
    elements.append(Spacer(1, 6))
    
    # Añadir recomendaciones generales
    elements.append(Paragraph("Recomendaciones:", normal_style))
    elements.append(Paragraph("• Enfócate en mejorar las áreas con puntuación menor a 5.", normal_style))
    elements.append(Paragraph("• Mantén el equilibrio entre todas las áreas de tu vida.", normal_style))
    elements.append(Paragraph("• Establece metas específicas para cada categoría.", normal_style))
    
    # Construir el PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Enviar el archivo
    return send_file(
        buffer,
        download_name=f'rueda_vida_{respuesta_id}.pdf',
        mimetype='application/pdf',
        as_attachment=True
    )

@app.route('/resultados/<int:respuesta_id>')
@login_required
def ver_resultado(respuesta_id):
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Verificar que la respuesta pertenezca al usuario
    cur.execute("""
        SELECT * FROM respuestas_rueda 
        WHERE id = %s AND usuario_id = %s
    """, (respuesta_id, session['user_id']))
    respuesta = cur.fetchone()
    
    if not respuesta and not session['es_admin']:
        flash('No tienes permiso para ver estos resultados', 'danger')
        return redirect(url_for('dashboard'))
    
    # Obtener detalles de la respuesta
    cur.execute("""
        SELECT c.nombre, dr.valor 
        FROM detalle_respuestas dr
        JOIN categorias c ON dr.categoria_id = c.id
        WHERE dr.respuesta_id = %s
    """, [respuesta_id])
    detalles = cur.fetchall()
    
    # Obtener fecha de la respuesta
    cur.execute("SELECT fecha FROM respuestas_rueda WHERE id = %s", [respuesta_id])
    fecha = cur.fetchone()['fecha']
    
    cur.close()
    
    # Preparar datos para el gráfico
    categorias = []
    valores = []
    for detalle in detalles:
        categorias.append(detalle['nombre'])
        valores.append(detalle['valor'])
    
    return render_template('resultados.html', 
                           respuesta_id=respuesta_id,
                           fecha=fecha,
                           categorias=json.dumps(categorias),
                           valores=json.dumps(valores))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Obtener estadísticas generales
    cur.execute("SELECT COUNT(*) as total_usuarios FROM usuarios WHERE es_admin = FALSE")
    total_usuarios = cur.fetchone()['total_usuarios']
    
    cur.execute("SELECT COUNT(*) as total_respuestas FROM respuestas_rueda")
    total_respuestas = cur.fetchone()['total_respuestas']
    
    # Obtener usuarios recientes
    cur.execute("""
        SELECT id, nombre, correo, fecha_registro 
        FROM usuarios 
        WHERE es_admin = FALSE 
        ORDER BY fecha_registro DESC 
        LIMIT 5
    """)
    usuarios_recientes = cur.fetchall()
    
    # Obtener respuestas recientes
    cur.execute("""
        SELECT rr.id, u.nombre, rr.fecha 
        FROM respuestas_rueda rr
        JOIN usuarios u ON rr.usuario_id = u.id
        ORDER BY rr.fecha DESC 
        LIMIT 5
    """)
    respuestas_recientes = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/dashboard.html',
                           total_usuarios=total_usuarios,
                           total_respuestas=total_respuestas,
                           usuarios_recientes=usuarios_recientes,
                           respuestas_recientes=respuestas_recientes)

@app.route('/admin/usuarios')
@login_required
@admin_required
def admin_usuarios():
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Obtener todos los usuarios (excepto administradores)
    cur.execute("""
        SELECT id, nombre, correo, sexo, tipo_empleado, fecha_registro 
        FROM usuarios 
        WHERE es_admin = FALSE 
        ORDER BY fecha_registro DESC
    """)
    usuarios = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/usuarios.html', usuarios=usuarios)
@app.route('/admin/agregar_usuario', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_agregar_usuario():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']
        sexo = request.form['sexo']
        tipo_empleado = request.form['tipo_empleado']
        contrasena = request.form['contrasena']
        
        # Crear cursor para consultas
        cur = mysql.connection.cursor()
        
        # Verificar si el correo ya existe
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", [correo])
        user = cur.fetchone()
        
        if user:
            flash('Este correo ya está registrado', 'danger')
            cur.close()
            return render_template('admin/agregar_usuario.html')
        
        # Insertar usuario
        hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')
        cur.execute("INSERT INTO usuarios (nombre, correo, sexo, tipo_empleado, contrasena) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, correo, sexo, tipo_empleado, hashed_password))
        
        # Confirmar cambios en la base de datos
        mysql.connection.commit()
        cur.close()
        
        flash('Usuario agregado exitosamente', 'success')
        return redirect(url_for('admin_usuarios'))
    
    return render_template('admin/agregar_usuario.html')

@app.route('/admin/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_editar_usuario(usuario_id):
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']
        sexo = request.form['sexo']
        tipo_empleado = request.form['tipo_empleado']
        nueva_contrasena = request.form.get('nueva_contrasena')
        
        # Verificar si el correo ya existe y no es del usuario actual
        cur.execute("SELECT * FROM usuarios WHERE correo = %s AND id != %s", (correo, usuario_id))
        user = cur.fetchone()
        
        if user:
            flash('Este correo ya está registrado por otro usuario', 'danger')
            cur.close()
            return redirect(url_for('admin_editar_usuario', usuario_id=usuario_id))
        
        # Actualizar usuario
        if nueva_contrasena:
            # Si se proporciona nueva contraseña, actualizarla también
            hashed_password = generate_password_hash(nueva_contrasena, method='pbkdf2:sha256')
            cur.execute("""
                UPDATE usuarios 
                SET nombre = %s, correo = %s, sexo = %s, tipo_empleado = %s, contrasena = %s 
                WHERE id = %s
            """, (nombre, correo, sexo, tipo_empleado, hashed_password, usuario_id))
        else:
            # Si no se proporciona nueva contraseña, mantener la actual
            cur.execute("""
                UPDATE usuarios 
                SET nombre = %s, correo = %s, sexo = %s, tipo_empleado = %s 
                WHERE id = %s
            """, (nombre, correo, sexo, tipo_empleado, usuario_id))
        
        # Confirmar cambios en la base de datos
        mysql.connection.commit()
        
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('admin_usuarios'))
    
    # Obtener información del usuario para mostrar en el formulario
    cur.execute("SELECT id, nombre, correo, sexo, tipo_empleado FROM usuarios WHERE id = %s", [usuario_id])
    usuario = cur.fetchone()
    
    cur.close()
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    return render_template('admin/editar_usuario.html', usuario=usuario)

@app.route('/admin/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def admin_eliminar_usuario(usuario_id):
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Verificar que el usuario existe y no es administrador
    cur.execute("SELECT es_admin FROM usuarios WHERE id = %s", [usuario_id])
    usuario = cur.fetchone()
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    if usuario['es_admin']:
        flash('No se puede eliminar un usuario administrador', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    # Eliminar registros relacionados primero (respuestas_rueda y detalle_respuestas)
    # 1. Obtener IDs de respuestas_rueda del usuario
    cur.execute("SELECT id FROM respuestas_rueda WHERE usuario_id = %s", [usuario_id])
    respuestas = cur.fetchall()
    
    # 2. Eliminar detalle_respuestas para cada respuesta
    for respuesta in respuestas:
        cur.execute("DELETE FROM detalle_respuestas WHERE respuesta_id = %s", [respuesta['id']])
    
    # 3. Eliminar respuestas_rueda del usuario
    cur.execute("DELETE FROM respuestas_rueda WHERE usuario_id = %s", [usuario_id])
    
    # 4. Finalmente, eliminar el usuario
    cur.execute("DELETE FROM usuarios WHERE id = %s", [usuario_id])
    
    # Confirmar cambios en la base de datos
    mysql.connection.commit()
    cur.close()
    
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/ver_rueda/<int:usuario_id>')
@login_required
@admin_required
def admin_ver_ruedas_usuario(usuario_id):
    # Crear cursor para consultas
    cur = mysql.connection.cursor()
    
    # Obtener información del usuario
    cur.execute("SELECT nombre, correo FROM usuarios WHERE id = %s", [usuario_id])
    usuario = cur.fetchone()
    
    # Obtener respuestas del usuario
    cur.execute("""
        SELECT rr.id, rr.fecha 
        FROM respuestas_rueda rr 
        WHERE rr.usuario_id = %s 
        ORDER BY rr.fecha DESC
    """, [usuario_id])
    respuestas = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/ver_rueda.html', 
                           usuario=usuario, 
                           respuestas=respuestas,
                           usuario_id=usuario_id)

@app.route('/admin/generar_reporte', methods=['GET', 'POST'])
@login_required
@admin_required
def generar_reporte():
    cur = mysql.connection.cursor()
    
    # Obtener lista de tipos de empleados
    cur.execute("SELECT DISTINCT tipo_empleado FROM usuarios WHERE tipo_empleado IS NOT NULL")
    tipos_empleado = cur.fetchall()

    if request.method == 'POST':
        sexo = request.form.get('sexo')
        tipo_empleado = request.form.get('tipo_empleado')
        formato = request.form.get('formato')

        # Consulta base para obtener promedios por categoría
        query_promedios = """
            SELECT 
                c.nombre as categoria,
                AVG(dr.valor) as promedio,
                COUNT(DISTINCT u.id) as total_usuarios
            FROM categorias c
            LEFT JOIN detalle_respuestas dr ON c.id = dr.categoria_id
            LEFT JOIN respuestas_rueda rr ON dr.respuesta_id = rr.id
            LEFT JOIN usuarios u ON rr.usuario_id = u.id
            WHERE 1=1
        """
        params_promedios = []

        if sexo:
            query_promedios += " AND u.sexo = %s"
            params_promedios.append(sexo)
        if tipo_empleado:
            query_promedios += " AND u.tipo_empleado = %s"
            params_promedios.append(tipo_empleado)

        query_promedios += " GROUP BY c.nombre"

        # Ejecutar consulta de promedios
        cur.execute(query_promedios, params_promedios)
        datos_promedio = cur.fetchall()

        # Consulta para distribución por sexo
        query_sexo = """
            SELECT 
                u.sexo,
                COUNT(DISTINCT u.id) as total
            FROM usuarios u
            JOIN respuestas_rueda rr ON u.id = rr.usuario_id
            WHERE 1=1
        """
        params_sexo = []
        
        if tipo_empleado:
            query_sexo += " AND u.tipo_empleado = %s"
            params_sexo.append(tipo_empleado)
            
        query_sexo += " GROUP BY u.sexo"
        
        # Ejecutar consulta de distribución por sexo
        cur.execute(query_sexo, params_sexo)
        datos_sexo = cur.fetchall()
        
        # Consulta para distribución por tipo de empleado
        query_tipo = """
            SELECT 
                u.tipo_empleado,
                COUNT(DISTINCT u.id) as total
            FROM usuarios u
            JOIN respuestas_rueda rr ON u.id = rr.usuario_id
            WHERE 1=1
        """
        params_tipo = []
        
        if sexo:
            query_tipo += " AND u.sexo = %s"
            params_tipo.append(sexo)
            
        query_tipo += " GROUP BY u.tipo_empleado"
        
        # Ejecutar consulta de distribución por tipo de empleado
        cur.execute(query_tipo, params_tipo)
        datos_tipo = cur.fetchall()

        # Obtener detalles individuales para el reporte
        query_individuales = """
            SELECT 
                u.nombre,
                u.correo,
                u.sexo,
                u.tipo_empleado,
                c.nombre as categoria,
                dr.valor
            FROM usuarios u
            JOIN respuestas_rueda rr ON u.id = rr.usuario_id
            JOIN detalle_respuestas dr ON rr.id = dr.respuesta_id
            JOIN categorias c ON dr.categoria_id = c.id
            WHERE 1=1
        """
        params_individuales = []
        
        if sexo:
            query_individuales += " AND u.sexo = %s"
            params_individuales.append(sexo)
        if tipo_empleado:
            query_individuales += " AND u.tipo_empleado = %s"
            params_individuales.append(tipo_empleado)

        cur.execute(query_individuales, params_individuales)
        datos_individuales = cur.fetchall()
        
        cur.close()

        if not datos_promedio:
            flash('No hay datos para mostrar con los filtros seleccionados.', 'warning')
            return redirect(url_for('generar_reporte'))

        if formato == 'pdf':
            return generar_pdf_completo(datos_promedio, datos_sexo, datos_tipo, datos_individuales, sexo, tipo_empleado)
        elif formato == 'csv':
            return generar_csv_completo(datos_promedio, datos_sexo, datos_tipo, datos_individuales, sexo, tipo_empleado)

    return render_template('admin/generar_reporte.html', tipos_empleado=tipos_empleado)

def generar_pdf_completo(datos_promedio, datos_sexo, datos_tipo, datos_individuales, sexo, tipo_empleado):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("Reporte de Rueda de la Vida", styles['Title']))
    elements.append(Spacer(1, 12))

    # Filtros aplicados
    filtros = f"Filtros aplicados: Sexo: {'Todos' if not sexo else sexo}, "
    filtros += f"Tipo de Empleado: {'Todos' if not tipo_empleado else tipo_empleado}"
    elements.append(Paragraph(filtros, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Sección 1: Distribución demográfica
    elements.append(Paragraph("Distribución Demográfica", styles['Heading2']))
    elements.append(Spacer(1, 6))
    
    # Gráfico de distribución por sexo
    if datos_sexo:
        plt.figure(figsize=(6, 4))
        sexos = [row['sexo'] if row['sexo'] else 'No especificado' for row in datos_sexo]
        totales_sexo = [row['total'] for row in datos_sexo]
        
        plt.pie(totales_sexo, labels=sexos, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Distribución por Sexo')
        
        img_buffer_sexo = io.BytesIO()
        plt.savefig(img_buffer_sexo, format='png')
        plt.close()
        img_buffer_sexo.seek(0)
        
        elements.append(Paragraph("Distribución por Sexo", styles['Heading3']))
        elements.append(Image(img_buffer_sexo, width=250, height=200))
        elements.append(Spacer(1, 6))
        
        # Tabla de distribución por sexo
        data_sexo = [['Sexo', 'Total']]
        for row in datos_sexo:
            data_sexo.append([
                row['sexo'] if row['sexo'] else 'No especificado',
                str(row['total'])
            ])
        
        table_sexo = Table(data_sexo)
        table_sexo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table_sexo)
    
    elements.append(Spacer(1, 12))
    
    # Gráfico de distribución por tipo de empleado
    if datos_tipo:
        plt.figure(figsize=(8, 4))
        tipos = [row['tipo_empleado'] if row['tipo_empleado'] else 'No especificado' for row in datos_tipo]
        totales_tipo = [row['total'] for row in datos_tipo]
        
        plt.bar(tipos, totales_tipo)
        plt.title('Distribución por Tipo de Empleado')
        plt.xlabel('Tipo de Empleado')
        plt.ylabel('Cantidad')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_buffer_tipo = io.BytesIO()
        plt.savefig(img_buffer_tipo, format='png')
        plt.close()
        img_buffer_tipo.seek(0)
        
        elements.append(Paragraph("Distribución por Tipo de Empleado", styles['Heading3']))
        elements.append(Image(img_buffer_tipo, width=400, height=200))
        elements.append(Spacer(1, 6))
        
        # Tabla de distribución por tipo de empleado
        data_tipo = [['Tipo de Empleado', 'Total']]
        for row in datos_tipo:
            data_tipo.append([
                row['tipo_empleado'] if row['tipo_empleado'] else 'No especificado',
                str(row['total'])
            ])
        
        table_tipo = Table(data_tipo)
        table_tipo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table_tipo)
    
    elements.append(Spacer(1, 12))
    
    # Sección 2: Promedios por categoría
    elements.append(Paragraph("Promedios por Categoría", styles['Heading2']))
    elements.append(Spacer(1, 6))

    # Tabla de promedios
    data = [['Categoría', 'Promedio', 'Total Usuarios']]
    for row in datos_promedio:
        data.append([
            row['categoria'],
            f"{float(row['promedio']):.2f}",
            str(row['total_usuarios'])
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Generar gráfico de barras para promedios
    plt.figure(figsize=(8, 6))
    categorias = [row['categoria'] for row in datos_promedio]
    promedios = [float(row['promedio']) for row in datos_promedio]
    
    plt.bar(categorias, promedios)
    plt.title('Promedios por Categoría')
    plt.xlabel('Categoría')
    plt.ylabel('Promedio')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardar gráfico en memoria
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)
    
    # Agregar gráfico al PDF
    elements.append(Image(img_buffer, width=400, height=300))
    
    # Construir el PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        download_name='reporte_rueda_vida.pdf',
        mimetype='application/pdf'
    )

def generar_csv_completo(datos_promedio, datos_sexo, datos_tipo, datos_individuales, sexo, tipo_empleado):
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Escribir encabezado
    writer.writerow(['Reporte de Rueda de la Vida'])
    writer.writerow([f'Filtros - Sexo: {"Todos" if not sexo else sexo}, Tipo de Empleado: {"Todos" if not tipo_empleado else tipo_empleado}'])
    writer.writerow([])

    # Escribir distribución por sexo
    writer.writerow(['DISTRIBUCIÓN POR SEXO'])
    writer.writerow(['Sexo', 'Total'])
    for row in datos_sexo:
        writer.writerow([
            row['sexo'] if row['sexo'] else 'No especificado',
            row['total']
        ])
    
    writer.writerow([])
    
    # Escribir distribución por tipo de empleado
    writer.writerow(['DISTRIBUCIÓN POR TIPO DE EMPLEADO'])
    writer.writerow(['Tipo de Empleado', 'Total'])
    for row in datos_tipo:
        writer.writerow([
            row['tipo_empleado'] if row['tipo_empleado'] else 'No especificado',
            row['total']
        ])
    
    writer.writerow([])

    # Escribir promedios
    writer.writerow(['PROMEDIOS POR CATEGORÍA'])
    writer.writerow(['Categoría', 'Promedio', 'Total Usuarios'])
    for row in datos_promedio:
        writer.writerow([
            row['categoria'],
            f"{float(row['promedio']):.2f}",
            row['total_usuarios']
        ])

    # Escribir datos individuales
    writer.writerow([])
    writer.writerow(['DATOS INDIVIDUALES'])
    writer.writerow(['Nombre', 'Correo', 'Sexo', 'Tipo de Empleado', 'Categoría', 'Valor'])
    for row in datos_individuales:
        writer.writerow([
            row['nombre'],
            row['correo'],
            row['sexo'],
            row['tipo_empleado'],
            row['categoria'],
            row['valor']
        ])

    buffer.seek(0)
    
    return send_file(
        io.BytesIO(buffer.getvalue().encode('utf-8')),
        download_name='reporte_rueda_vida.csv',
        mimetype='text/csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
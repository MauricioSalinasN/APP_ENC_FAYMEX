# app.py - Backend de la aplicación web
# Este archivo maneja la lógica del servidor para conectar a la base de datos de Azure SQL.

# Importar las bibliotecas necesarias
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import logging

# Configuración de logging para ver lo que sucede en la terminal
logging.basicConfig(level=logging.INFO)

# Inicializa la aplicación Flask
app = Flask(__name__)
# La clave secreta es necesaria para que los mensajes flash funcionen
app.secret_key = 'tu_clave_secreta_aqui'

# --- CONFIGURACIÓN DE TU BASE DE DATOS DE AZURE SQL ---
# ADVERTENCIA: No uses credenciales sensibles directamente en el código para producción.
# Debes usar variables de entorno o Azure Key Vault para mayor seguridad.
server = 'server-bd-faymex.database.windows.net'
database = 'BD_Faymex'
username = 'msalinas'
password = 'msn-2009'
driver = '{ODBC Driver 17 for SQL Server}' # Asegúrate de que este driver esté instalado

# Crea la cadena de conexión
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def home():
    """
    Ruta de inicio que sirve la página de entrevista HTML y muestra los datos existentes.
    """
    conn = None
    interviews = []
    try:
        logging.info("Intentando conectar a la base de datos de Azure SQL para obtener los datos...")
        conn = pyodbc.connect(connection_string, autocommit=True)
        cursor = conn.cursor()
        logging.info("Conexión exitosa. Obteniendo datos.")
        
        # Consulta para seleccionar todas las entrevistas ordenadas por fecha de registro
        sql_query = "SELECT * FROM datos_entrevista ORDER BY fecha_registro DESC"
        cursor.execute(sql_query)
        
        columns = [column[0] for column in cursor.description]
        
        for row in cursor.fetchall():
            interviews.append(dict(zip(columns, row)))
        
        logging.info("Datos obtenidos con éxito.")
        
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error(f"Error de base de datos al obtener datos: {sqlstate}")
    except Exception as e:
        logging.error(f"Error inesperado al obtener datos: {str(e)}")
    finally:
        if conn:
            conn.close()
            logging.info("Conexión a la base de datos cerrada.")

    return render_template('datos_entrevista.html', interviews=interviews)


@app.route('/submit', methods=['POST'])
def submit():
    """
    Recibe los datos del formulario y los inserta en la base de datos de Azure SQL.
    """
    conn = None
    try:
        logging.info("Intentando conectar a la base de datos de Azure SQL para guardar datos...")
        conn = pyodbc.connect(connection_string, autocommit=True)
        cursor = conn.cursor()
        logging.info("Conexión exitosa.")

        # Obtener datos del formulario
        nombre_contacto = request.form['nombre_contacto']
        cargo = request.form['cargo']
        departamento = request.form['departamento']
        fecha_entrevista_str = request.form['fecha_entrevista']
        fecha_entrevista = datetime.strptime(fecha_entrevista_str, '%Y-%m-%d').date()

        # Manejar la opción "Otro"
        if departamento == 'Otro':
            departamento = request.form['otro_departamento']

        # Obtener los valores de los checkboxes para "Desafíos"
        desafio_datos_dispersos = 'desafio_datos_dispersos' in request.form
        desafio_acceso_dificil = 'desafio_acceso_dificil' in request.form
        desafio_falta_reporte = 'desafio_falta_reporte' in request.form
        desafio_info_no_actualizada = 'desafio_info_no_actualizada' in request.form
        desafio_dificil_generar_reporte = 'desafio_dificil_generar_reporte' in request.form

        # Obtener los valores de los checkboxes para "Proceso más largo"
        proceso_mas_largo_manual = 'proceso_mas_largo_manual' in request.form
        proceso_mas_largo_multiples_fuentes = 'proceso_mas_largo_multiples_fuentes' in request.form
        proceso_mas_largo_espera_reportes = 'proceso_mas_largo_espera_reportes' in request.form
        proceso_mas_largo_validacion_datos = 'proceso_mas_largo_validacion_datos' in request.form
        
        # Obtener los valores de los checkboxes para "Infraestructura"
        infraestructura_dependencia_manual = 'infraestructura_dependencia_manual' in request.form
        infraestructura_falta_estandarizacion = 'infraestructura_falta_estandarizacion' in request.form
        infraestructura_vulnerabilidades = 'infraestructura_vulnerabilidades' in request.form
        infraestructura_poca_escalabilidad = 'infraestructura_poca_escalabilidad' in request.form

        # Obtener los valores de los checkboxes para "Decisión"
        decision_optimizacion_recursos = 'decision_optimizacion_recursos' in request.form
        decision_reduccion_costos = 'decision_reduccion_costos' in request.form
        decision_mejora_planificacion = 'decision_mejora_planificacion' in request.form
        decision_identificacion_ineficiencias = 'decision_identificacion_ineficiencias' in request.form

        comentarios = request.form['comentarios']
        fecha_registro = datetime.now()

        # Sentencia SQL para la inserción de datos
        # Asegúrate de que el orden de las columnas coincida con los datos que estás insertando
        query = """
            INSERT INTO datos_entrevista (
                nombre_contacto, cargo, departamento, fecha_entrevista,
                desafio_datos_dispersos, desafio_acceso_dificil, desafio_falta_reporte,
                desafio_info_no_actualizada, desafio_dificil_generar_reporte,
                proceso_mas_largo_manual, proceso_mas_largo_multiples_fuentes,
                proceso_mas_largo_espera_reportes, proceso_mas_largo_validacion_datos,
                infraestructura_dependencia_manual, infraestructura_falta_estandarizacion,
                infraestructura_vulnerabilidades, infraestructura_poca_escalabilidad,
                decision_optimizacion_recursos, decision_reduccion_costos,
                decision_mejora_planificacion, decision_identificacion_ineficiencias,
                comentarios, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Ejecutar la consulta con los datos del formulario
        cursor.execute(query, 
            nombre_contacto, cargo, departamento, fecha_entrevista,
            desafio_datos_dispersos, desafio_acceso_dificil,
            desafio_falta_reporte, desafio_info_no_actualizada,
            desafio_dificil_generar_reporte, proceso_mas_largo_manual,
            proceso_mas_largo_multiples_fuentes, proceso_mas_largo_espera_reportes,
            proceso_mas_largo_validacion_datos,
            infraestructura_dependencia_manual, infraestructura_falta_estandarizacion,
            infraestructura_vulnerabilidades, infraestructura_poca_escalabilidad,
            decision_optimizacion_recursos, decision_reduccion_costos,
            decision_mejora_planificacion, decision_identificacion_ineficiencias,
            comentarios, fecha_registro
        )
        conn.commit()
        logging.info("Datos insertados con éxito.")
        # Agregamos un mensaje flash para mostrar en la siguiente página
        flash('¡Información guardada con éxito!', 'success')
        return redirect(url_for('home'))

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error(f"Error de base de datos: {sqlstate}")
        # En caso de error, también podemos usar flash para notificar al usuario
        flash(f"Error al guardar la información: {ex}", 'error')
        return redirect(url_for('home'))
    except Exception as e:
        logging.error(f"Error inesperado al guardar la información: {str(e)}")
        flash(f"Error inesperado: {e}", 'error')
        return redirect(url_for('home'))
    finally:
        if conn:
            conn.close()
            logging.info("Conexión a la base de datos cerrada.")

if __name__ == '__main__':
    app.run(debug=True)

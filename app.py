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

    # Asegúrate de que este sea el nombre correcto de tu archivo HTML para la página principal
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

        # Obtener datos del formulario de manera robusta
        nombre_contacto = request.form.get('nombre_contacto')
        cargo = request.form.get('cargo')
        departamento = request.form.get('departamento')
        fecha_entrevista_str = request.form.get('fecha_entrevista')
        comentarios = request.form.get('comentarios')
        fecha_registro = datetime.now()

        # Manejar la opción "Otro" para el departamento
        if departamento == 'Otro':
            departamento = request.form.get('otro_departamento')

        # Obtener los valores de los checkboxes de forma correcta
        proceso_mas_largo_list = request.form.getlist('proceso_mas_largo')
        desafio_info_list = request.form.getlist('desafio_info')
        infraestructura_desafio_list = request.form.getlist('infraestructura_desafio')
        decision_list = request.form.getlist('decision')

        # Convertir las listas de valores a booleanos para la base de datos
        proceso_mas_largo_manual = 'proceso_manual' in proceso_mas_largo_list
        proceso_mas_largo_multiples_fuentes = 'multiples_fuentes' in proceso_mas_largo_list
        proceso_mas_largo_espera_reportes = 'espera_reportes' in proceso_mas_largo_list
        proceso_mas_largo_validacion_datos = 'validacion_datos' in proceso_mas_largo_list
        
        desafio_info_desactualizada = 'desactualizada' in desafio_info_list
        desafio_info_falta_acceso = 'falta_acceso' in desafio_info_list
        desafio_info_datos_dispersos = 'datos_dispersos' in desafio_info_list
        desafio_info_falta_reporte = 'falta_reporte' in desafio_info_list
        desafio_info_dificil_generar_reporte = 'dificil_generar_reporte' in desafio_info_list

        infraestructura_dependencia_manual = 'dependencia_manual' in infraestructura_desafio_list
        infraestructura_falta_estandarizacion = 'falta_estandarizacion' in infraestructura_desafio_list
        infraestructura_vulnerabilidades = 'vulnerabilidades' in infraestructura_desafio_list
        infraestructura_poca_escalabilidad = 'poca_escalabilidad' in infraestructura_desafio_list

        decision_optimizacion_recursos = 'optimizacion_recursos' in decision_list
        decision_reduccion_costos = 'reduccion_costos' in decision_list
        decision_mejora_planificacion = 'mejora_planificacion' in decision_list
        decision_identificacion_ineficiencias = 'identificacion_ineficiencias' in decision_list

        # Sentencia SQL para la inserción de datos
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
            nombre_contacto, cargo, departamento, fecha_entrevista_str,
            desafio_info_datos_dispersos, desafio_info_falta_acceso,
            desafio_info_falta_reporte, desafio_info_desactualizada,
            desafio_info_dificil_generar_reporte, proceso_mas_largo_manual,
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
        flash('¡Información guardada con éxito!', 'success')
        return redirect(url_for('home'))

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error(f"Error de base de datos: {sqlstate}")
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

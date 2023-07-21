# my_script.py
import pandas as pd
import psycopg2

# Instalar la librería Pandas si no está instalada (esto es opcional si ya tienes la librería instalada en el contenedor)
try:
    import pandas as pd
except ImportError:
    import os
    os.system("pip install pandas")

def extract_data():
    # Código para extraer los datos
    # ...

if __name__ == "__main__":
    data = extract_data()
    
    if data is not None:
        # Convertir los datos en un DataFrame
        df = pd.DataFrame(data['data']['defensa_FAA_0006'])
        
        # Realizar las transformaciones necesarias en el DataFrame
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Conectar a la base de datos de Redshift con las credenciales
        conn = psycopg2.connect(
            host="data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com",
            port="5439",
            database="data-engineer-database",
            user="ldunjo_coderhouse",
            password="8Vj7WC4EMi"
        )
        
        # Cargar los datos en la tabla de Redshift
        # Usar método to_sql() de Pandas para cargar el DataFrame en la tabla de Redshift
        # Parámetro if_exists se establece en "replace" para reemplazar la tabla existente si ya existe:
        df.to_sql(name="Def_FFAA", con=conn, if_exists="replace", index=False)
        
        # Cerrar la conexión a la base de datos
        conn.close()

#Crear el Dockerfile
#Crearemos un archivo llamado Dockerfile para construir la imagen del contenedor con las dependencias necesarias.

# Dockerfile
# Usa una imagen base que contenga Python y Airflow preinstalados
FROM apache/airflow:2.0.1

# Instalar las dependencias necesarias (Pandas y psycopg2)
RUN pip install pandas psycopg2

# Copiar el script al directorio /usr/local/airflow dentro del contenedor
COPY my_script.py /usr/local/airflow/my_script.py

# Configurar el directorio de trabajo para Airflow
WORKDIR /usr/local/airflow


#Crear el DAG de Airflow
#Crea un archivo Python para definir el DAG de Airflow que ejecutará el script dentro del contenedor
#Asegúrate de colocar este archivo Python en una carpeta llamada 'dags'.

# /path/to/your/dags_folder/my_dag.py
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta

# Define el DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 7, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_dag',
    default_args=default_args,
    description='Ejecuta el script en un contenedor Docker',
    schedule_interval=timedelta(days=1),
)

# Define la tarea para ejecutar el contenedor Docker
docker_task = DockerOperator(
    task_id='run_my_script',
    image='my_script_image:latest',  # Cambia 'my_script_image' por el nombre que le des a la imagen en el Dockerfile
    command='python my_script.py',   # Cambia 'my_script.py' por el nombre del script en el contenedor
    dag=dag,
)

#  Crear el archivo de configuración de Airflow (opcional)
# Si es necesario, puedes crear un archivo de configuración para Airflow 
# que especifique la ubicación de la carpeta de DAGs y otros ajustes. 


# /path/to/your/config_folder/airflow.cfg
[core]
dags_folder = /path/to/your/dags_folder

#Construir la imagen de Docker
#Desde la ubicación donde se encuentre el Dockerfile, ejecuta el siguiente comando para construir la imagen de Docker:

docker build -t my_script_image:latest .


#Iniciar el contenedor
#iniciar el contenedor de Docker y ejecutar el DAG de Airflow con el siguiente comando:

docker run -d -v /path/to/your/dags_folder:/usr/local/airflow/dags my_script_image:latest

import paramiko
import mysql.connector

# Datos de la instancia EC2
ec2_host = '16.170.250.70'
ec2_user = 'ec2-user'
private_key_path = '../../clave-1.pem'

# Datos de la base de datos RDS
rds_host = '172.31.14.58'
rds_port = 3306
db_user = 'admin'
db_password = 'Sistemas2023!'
db_database = 'Gymtar'

# Establecer conexión SSH a la instancia EC2
private_key = paramiko.RSAKey(filename=private_key_path)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Inicializar la variable de conexión
connection = None

try:
    ssh_client.connect(ec2_host, username=ec2_user, pkey=private_key)
    print("Conexión SSH exitosa")

    # Configuración de la conexión a la base de datos RDS
    db_config = {
        'host': rds_host,
        'user': db_user,
        'password': db_password,
        'database': db_database,
        'port': rds_port,
    }

    # Intentar establecer la conexión a la base de datos
    try:
        connection = mysql.connector.connect(**db_config)
        print("Conexión a la base de datos exitosa")

        # A partir de aquí, puedes ejecutar consultas y realizar otras operaciones en la base de datos

    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

    finally:
        # Asegúrate de cerrar la conexión a la base de datos al finalizar
        if connection and connection.is_connected():
            connection.close()
            print("Conexión a la base de datos cerrada")

finally:
    # Asegúrate de cerrar la conexión SSH al finalizar
    if ssh_client:
        ssh_client.close()
        print("Conexión SSH cerrada")

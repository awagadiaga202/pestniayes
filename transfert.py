import MySQLdb
import psycopg2

# Connexion à MariaDB
maria_conn = MySQLdb.connect(
    host="localhost",
    user="root",        # ou ton utilisateur
    passwd="root",          # ou ton mot de passe
    db="prestniayes_db",
    port=3307           # <- ici le port correct
)

maria_cursor = maria_conn.cursor()

# Connexion à PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    dbname="prestniayes_db",
    user="postgres",
    password="root"
)
pg_cursor = pg_conn.cursor()

# Récupérer toutes les tables MariaDB
maria_cursor.execute("SHOW TABLES;")
tables = [t[0] for t in maria_cursor.fetchall()]

for table in tables:
    print(f"Transfert de la table {table}...")

    # Récupérer les données MariaDB
    maria_cursor.execute(f"SELECT * FROM {table};")
    rows = maria_cursor.fetchall()

    # Récupérer le nom des colonnes
    columns = [desc[0] for desc in maria_cursor.description]
    cols_str = ", ".join(columns)
    vals_str = ", ".join(["%s"] * len(columns))

    # Insérer les données dans PostgreSQL
    for row in rows:
        pg_cursor.execute(
            f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str})", row
        )

pg_conn.commit()

maria_cursor.close()
maria_conn.close()
pg_cursor.close()
pg_conn.close()

print("Transfert terminé ✅")

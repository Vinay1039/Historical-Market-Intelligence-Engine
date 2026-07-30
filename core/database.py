import oracledb
from core import config

# Initialize Oracle Thick Client if instantclient directory exists
try:
    oracledb.init_oracle_client(lib_dir=r"C:\instantclient_23_0")
except Exception:
    pass

_pool = None

def init_db_pool():
    """Initializes high-performance Oracle connection pool."""
    global _pool
    if _pool is None:
        dsn = f"{config.DB_HOST}:{config.DB_PORT}/{config.DB_SERVICE_NAME}"
        _pool = oracledb.create_pool(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            dsn=dsn,
            min=2,
            max=10,
            increment=1
        )
        print("[SUCCESS] Oracle connection pool initialized successfully.")

def close_db_pool():
    """Closes Oracle connection pool on application shutdown."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        print("[INFO] Oracle connection pool closed.")

def get_db_connection():
    """Acquires a database connection from the pool."""
    global _pool
    if _pool is None:
        init_db_pool()
    return _pool.acquire()

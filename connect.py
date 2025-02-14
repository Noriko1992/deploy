import os
import tempfile
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SSL証明書の取得
ssl_cert = os.getenv("SSL_CA_STR")
if not ssl_cert:
    raise ValueError("❌ SSL_CA_STR が設定されていません！")

# SSL証明書の一時ファイル作成
def create_ssl_cert_tempfile():
    pem_content = ssl_cert.replace("\\n", "\n").replace("\\", "")
    temp_pem = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w")
    temp_pem.write(pem_content)
    temp_pem.close()
    return temp_pem.name

ssl_ca_path = create_ssl_cert_tempfile()

# 環境変数 `DB_URL` を取得
DATABASE_URL = os.getenv("DB_URL")
if not DATABASE_URL:
    raise ValueError("❌ DB_URL が設定されていません！")

# SQLAlchemy エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ca": ssl_ca_path
        }
    }
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MySQL に直接接続する関数
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        ssl_ca=ssl_ca_path
    )

# 環境変数のチェック（デバッグ用）
print(f"✅ DATABASE_URL: {DATABASE_URL}")

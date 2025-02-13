import os
import tempfile
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
import atexit
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# 環境変数の取得
DATABASE_URL = os.getenv("DB_URL")
pem_content = os.getenv("SSL_CA_STR")

# 環境変数が読み込まれていることを確認
print(f"✅ DATABASE_URL: {DATABASE_URL}")
print(f"✅ SSL_CA_STR: {pem_content[:30]}...")  # セキュリティ上、冒頭30文字のみ表示

# 必須環境変数のチェック
required_vars = {
    "DB_URL": DATABASE_URL,
    "SSL_CA_STR": pem_content
}

missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"❌ 必須環境変数が設定されていません: {', '.join(missing_vars)}")

# SSL証明書の一時ファイル作成
pem_content = pem_content.replace("\\n", "\n").replace("\\", "")

# 一時ファイル作成
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".pem") as temp_pem:
    temp_pem.write(pem_content)
    temp_pem_path = temp_pem.name

# 一時ファイルの存在確認
print(f"✅ Temporary SSL CA certificate file created at: {temp_pem_path}")
with open(temp_pem_path, "r") as temp_pem:
    print("===== Temporary certificate file content: =====")
    print(temp_pem.read()[:200])  # セキュリティのため、最初の200文字のみ表示

# SQLAlchemy エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ca": temp_pem_path
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
        ssl_ca=temp_pem_path
    )

# Python正常終了時に一時ファイルを削除
def cleanup_temp_file(path):
    if os.path.exists(path):
        os.remove(path)
        print(f"✅ Temporary SSL CA certificate file deleted: {path}")

atexit.register(cleanup_temp_file, temp_pem_path)

# 環境変数のチェック（デバッグ用）
print(f"✅ MySQL USER: {os.getenv('MYSQL_USER')}")
print(f"✅ MySQL HOST: {os.getenv('MYSQL_HOST')}")
print(f"✅ MySQL DATABASE: {os.getenv('MYSQL_DATABASE')}")

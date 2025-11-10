import os
import sys
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env opcional (apenas se existir e se python-dotenv estiver disponível)
env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=True)
    except Exception as e:
        print(f"WARNING: .env encontrado, mas python-dotenv indisponível: {e}")

def env_bool(key: str, default: bool = False) -> bool:
    return str(os.getenv(key, str(default))).lower() in {"1", "true", "t", "yes", "y", "on"}

# Segurança
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-padrao-insegura")
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")]

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    # "drf_yasg",  # Swagger opcional: será ativado abaixo se estiver instalado
    "pagamentos.apps.PagamentosConfig",
]

# Ativa Swagger apenas se instalou o pacote E setou ENABLE_SWAGGER=True
if env_bool("ENABLE_SWAGGER", False):
    try:
        import drf_yasg  # noqa
        INSTALLED_APPS.append("drf_yasg")
    except Exception:
        print("WARNING: ENABLE_SWAGGER=True, mas 'drf_yasg' não está instalado.")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------- Banco de Dados (sem dj_database_url) ----------
def parse_database_url(url: str):
    """
    Suporta:
    - postgres://usuario:senha@host:port/dbname
    - postgresql://usuario:senha@host:port/dbname
    - sqlite:///caminho.db   ou sqlite:///:memory:
    """
    if not url:
        return None
    u = urlparse(url)
    if u.scheme in ("postgres", "postgresql"):
        name = u.path.lstrip("/") or os.getenv("DATABASE_NAME", "pagamentos_webhook3")
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": name,
            "USER": u.username or "postgres",
            "PASSWORD": u.password or "",
            "HOST": u.hostname or "localhost",
            "PORT": str(u.port or "5432"),
        }
    if u.scheme == "sqlite":
        path = u.path
        name = ":memory:" if path == "/:memory:" else (path or (BASE_DIR / "db.sqlite3"))
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": name}
    raise ValueError(f"DB URL scheme não suportado: {u.scheme}")

DATABASE_URL = os.getenv("DATABASE_URL", "")
db_cfg = parse_database_url(DATABASE_URL) if DATABASE_URL else None

if db_cfg:
    DATABASES = {"default": db_cfg}
else:
    default_db = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "pagamentos_webhook3"),
        "USER": os.getenv("DATABASE_USER", "postgres"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", ""),
        "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
    # Em tests (ou USE_SQLITE=True), usa sqlite
    if "test" in sys.argv or env_bool("USE_SQLITE", False):
        default_db = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    DATABASES = {"default": default_db}
# --------------------------------------------------------

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF + JWT
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_VERIFY_SIGNATURE = env_bool("STRIPE_VERIFY_SIGNATURE", True)

# Modo Demo
DEMO_MODE = env_bool("DEMO_MODE", False)
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")

# drf-yasg: remover renderers compatíveis antigos (silencia o warning)
SWAGGER_USE_COMPAT_RENDERERS = False

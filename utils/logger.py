"""
Модуль настройки логирования для бота.
"""
import sys
from pathlib import Path
from loguru import logger

# Создаем директорию для логов если её нет
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

logger.remove()

# ==================== КОНСОЛЬНЫЙ ВЫВОД ====================
logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

# ==================== ОСНОВНОЙ ЛОГ-ФАЙЛ ====================
logger.add(
    LOGS_DIR / "bot_{time:YYYY-MM-DD}.log",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
    level="INFO",
    rotation="00:00",
    retention="7 days",
    compression="zip",
    encoding="utf-8",
)

# ==================== ФАЙЛ ТОЛЬКО ДЛЯ ОШИБОК ====================
logger.add(
    LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}\n"
        "{exception}"
    ),
    level="WARNING",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)

# ==================== JSON ЛОГ (опционально) ====================
logger.add(
    LOGS_DIR / "bot_{time:YYYY-MM-DD}.json",
    format="{message}",
    level="INFO",
    rotation="00:00",
    retention="7 days",
    compression="zip",
    serialize=True,
)

# Логируем успешную инициализацию
logger.info("📝 Логирование инициализировано")
logger.info(f"📁 Директория логов: {LOGS_DIR.absolute()}")

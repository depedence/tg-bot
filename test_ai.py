"""
Тестовый скрипт для проверки генерации квестов.
"""
from services.ai_service import generate_daily_quest, generate_weekly_quest

print("🧪 Тестируем генерацию дейли квеста...\n")

daily = generate_daily_quest(user_name="Банк")
print("📋 Дейли квест:")
print(f"Название: {daily['title']}")
print(f"Описание: {daily['description']}")
print(f"Сложность: {daily['difficulty']}")

print("\n" + "="*50 + "\n")

print("🧪 Тестируем генерацию недельного квеста...\n")

weekly = generate_weekly_quest(user_name="Банк")
print("📋 Недельный квест:")
print(f"Название: {weekly['title']}")
print(f"Описание: {weekly['description']}")
print(f"Сложность: {weekly['difficulty']}")

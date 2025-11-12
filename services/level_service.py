"""
Сервис для работы с системой уровней и опыта.
"""

def calculate_exp_for_level(level: int) -> int:
    if level == 1:
        return 0  # Для первого уровня не нужен опыт

    base_exp = 10
    return base_exp + (level - 2) * 5


def calculate_total_exp_to_level(level: int) -> int:
    total = 0
    for lvl in range(2, level + 1):
        total += calculate_exp_for_level(lvl)
    return total


def get_level_from_experience(experience: int) -> tuple[int, int, int]:
    level = 1
    total_exp = 0

    while True:
        exp_for_next = calculate_exp_for_level(level + 1)
        if total_exp + exp_for_next > experience:
            # Нашли текущий уровень
            current_level_exp = experience - total_exp
            return level, current_level_exp, exp_for_next

        total_exp += exp_for_next
        level += 1


def calculate_quest_exp(quest_type: str, completed_tasks: int, total_tasks: int) -> int:
    if quest_type == "daily":
        exp_per_task = 1
        bonus = 1
    else:  # weekly
        exp_per_task = 3
        bonus = 3

    exp = completed_tasks * exp_per_task

    # Если все задания выполнены - бонус
    if completed_tasks == total_tasks:
        exp += bonus

    return exp

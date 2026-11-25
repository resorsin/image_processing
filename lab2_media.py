# -*- coding: utf-8 -*-
"""
Лабораторная работа №2. Часть Б.
Обработка изображений в иерархической файловой системе.
Вариант 30: 1) Box-фильтр (усреднение), 2) Цветокоррекция по шаблону.
"""
import os
from datetime import datetime
from PIL import Image, ImageFilter, ImageStat

INPUT_DIR = os.path.join("Lab2_Media", "data", "input")
OUTPUT_DIR = os.path.join("Lab2_Media", "data", "output")
LOG_FILE = os.path.join("Lab2_Media", "logs", "history.txt")


def log_write(file_name, filter_name, status):
    """Дописывает строку в журнал в режиме 'a' (append) - история не стирается."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] Файл: {file_name} | Фильтр: {filter_name} | Статус: {status}\n"
    with open(LOG_FILE, "a", encoding="UTF-8") as f:
        f.write(line)


def box_filter(img, size):
    """Box-фильтр: усреднение пикселей в квадратном окне size x size (все веса равны)."""
    radius = size // 2
    return img.filter(ImageFilter.BoxBlur(radius))


def color_correction(img, template):
    """Цветокоррекция по шаблону: перенос среднего и разброса по каждому каналу R, G, B."""
    img = img.convert("RGB")
    template = template.convert("RGB")
    st_img = ImageStat.Stat(img)      # статистика исходного изображения
    st_tpl = ImageStat.Stat(template)  # статистика шаблона (эталона)

    channels = img.split()
    corrected = []
    for ch, m_i, s_i, m_t, s_t in zip(
        channels, st_img.mean, st_img.stddev, st_tpl.mean, st_tpl.stddev
    ):
        # если разброс почти нулевой - коэффициент масштаба не применяем (защита от деления на 0)
        ratio = (s_t / s_i) if s_i > 1e-3 else 1.0
        corrected.append(
            ch.point(lambda v, m_i=m_i, ratio=ratio, m_t=m_t:
                     max(0, min(255, round((v - m_i) * ratio + m_t))))
        )
    return Image.merge("RGB", corrected)


def main():
    # --- 1. Потоковый ввод: спрашиваем имя файла ---
    file_name = input("Введите имя файла для обработки (image1.jpg или image2.png): ").strip()
    file_path = os.path.join(INPUT_DIR, file_name)

    # --- 2. Поиск файла и 3. обработка ошибок прав доступа ---
    try:
        img = Image.open(file_path)
        img.load()  # принудительно читаем данные (PIL читает лениво)
    except FileNotFoundError:
        print("Ошибка: Файл не найден")
        log_write(file_name, "открытие файла", "Файл не найден")
        return
    except PermissionError:
        print(f"Ошибка: Нет прав на чтение файла {file_name}. Обратитесь к администратору")
        log_write(file_name, "открытие файла", "Ошибка доступа")
        return

    original = img.convert("RGB")  # неизменяемый слепок исходника (в ОЗУ)
    current = original.copy()      # рабочая копия, к ней применяются фильтры
    print(f"Файл {file_name} успешно открыт.")
    log_write(file_name, "открытие файла", "Успешно")

    # --- Меню: фильтры применяются только по выбору пользователя ---
    while True:
        print("\n===== МЕНЮ =====")
        print("1 - Box-фильтр (усреднение)")
        print("2 - Цветокоррекция по шаблону")
        print("3 - Отменить изменения (вернуть исходник)")
        print("4 - Сохранить результат в output/result.jpg")
        print("0 - Выход")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            try:
                size = int(input("Размер окна усреднения (нечетное, напр. 3, 5, 7): ").strip())
                if size < 1:
                    raise ValueError
            except ValueError:
                print("Нужно ввести положительное целое число.")
                continue
            current = box_filter(current, size)
            print(f"Box-фильтр применен (окно {size}x{size}).")
            log_write(file_name, f"Box-фильтр ({size}x{size})", "Успешно")

        elif choice == "2":
            tpl_name = input("Имя файла-шаблона (Enter = template.jpg): ").strip() or "template.jpg"
            tpl_path = os.path.join(INPUT_DIR, tpl_name)
            try:
                with Image.open(tpl_path) as tpl:
                    tpl.load()
                    current = color_correction(current, tpl)
                print(f"Цветокоррекция по шаблону '{tpl_name}' применена.")
                log_write(file_name, f"Цветокоррекция по шаблону ({tpl_name})", "Успешно")
            except FileNotFoundError:
                print("Ошибка: Файл не найден")
                log_write(file_name, "Цветокоррекция по шаблону", "Файл не найден")
            except PermissionError:
                print(f"Ошибка: Нет прав на чтение файла {tpl_name}. Обратитесь к администратору")
                log_write(file_name, "Цветокоррекция по шаблону", "Ошибка доступа")

        elif choice == "3":
            current = original.copy()  # откат: берем сохраненный слепок из ОЗУ
            print("Изменения отменены, показан исходник.")
            log_write(file_name, "Отмена изменений", "Успешно")

        elif choice == "4":
            out_path = os.path.join(OUTPUT_DIR, "result.jpg")
            current.save(out_path)
            print(f"Результат сохранен: {out_path}")
            log_write(file_name, "Сохранение result.jpg", "Успешно")

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Нет такого пункта меню.")


if __name__ == "__main__":
    main()

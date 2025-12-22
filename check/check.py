#!/usr/bin/env python3
"""
Тесты для модуля ядра Linux с параметрами:
- idx (индекс в строке, 0-63)
- ch_val (символ ASCII, 0-255)
- my_str (строка, только чтение)
"""

import os
import subprocess
import time
import sys

class KernelModuleTester:
    def __init__(self, module_name="my_module"):
        self.module_name = module_name
        self.params_path = f"/sys/module/{module_name}/parameters"
        
        # Проверяем, загружен ли модуль
        if not self.is_module_loaded():
            print(f"Модуль {module_name} не загружен!")
            print("Загрузите модуль командой: sudo insmod my_module.ko")
            sys.exit(1)
    
    def is_module_loaded(self):
        """Проверяет, загружен ли модуль"""
        try:
            with open("/proc/modules", "r") as f:
                for line in f:
                    if line.startswith(f"{self.module_name} "):
                        return True
            return False
        except:
            return False
    
    def read_param(self, param_name):
        """Читает значение параметра модуля"""
        try:
            with open(f"{self.params_path}/{param_name}", "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Ошибка чтения {param_name}: {e}")
            return None
    
    def write_param(self, param_name, value):
        """Записывает значение в параметр модуля (требует sudo)"""
        try:
            result = subprocess.run(
                ["sudo", "sh", "-c", f"echo '{value}' > {self.params_path}/{param_name}"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Ошибка записи {param_name}={value}: {e}")
            return False
    
    def clear_dmesg(self):
        """Очищает журнал ядра"""
        subprocess.run(["sudo", "dmesg", "-C"], capture_output=True)
    
    def get_module_logs(self, lines=10):
        """Получает последние логи модуля из ядра"""
        try:
            result = subprocess.run(
                ["dmesg", "|", "grep", self.module_name, "|", "tail", f"-{lines}"],
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except:
            return ""

def run_test(test_name, test_func):
    """Запускает тест и выводит результат"""
    print(f"\n{'='*60}")
    print(f"ТЕСТ: {test_name}")
    print('='*60)
    
    try:
        result = test_func()
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"Результат: {status}")
        return result
    except Exception as e:
        print(f"❌ ОШИБКА В ТЕСТЕ: {e}")
        return False

def main():
    print("🚀 ЗАПУСК ТЕСТОВ МОДУЛЯ ЯДРА")
    print(f"Время: {time.ctime()}")
    
    tester = KernelModuleTester()
    tester.clear_dmesg()
    
    passed_tests = 0
    total_tests = 0
    
    # Тест 1: Исходное состояние модуля
    def test_initial_state():
        print("Проверка начального состояния модуля...")
        
        idx = tester.read_param("idx")
        ch_val = tester.read_param("ch_val")
        my_str = tester.read_param("my_str")
        
        print(f"  idx = {idx}")
        print(f"  ch_val = {ch_val}")
        print(f"  my_str = {my_str}")
        
        logs = tester.get_module_logs(5)
        print(f"\nЛоги загрузки:\n{logs}")
        
        return idx == "0" and "A (65)" in ch_val and "Default string" in my_str
    
    # Тест 2: Слишком большой idx (должен вернуть ошибку)
    def test_idx_too_large():
        print("Попытка установить idx=100 (максимум 63)...")
        
        # Сохраняем старое значение
        old_idx = tester.read_param("idx")
        
        # Пытаемся установить недопустимое значение
        success = tester.write_param("idx", "100")
        
        # Проверяем, что значение не изменилось
        new_idx = tester.read_param("idx")
        
        logs = tester.get_module_logs(3)
        print(f"Логи ядра:\n{logs}")
        
        # Восстанавливаем старое значение
        tester.write_param("idx", old_idx)
        
        # Тест пройден, если значение не изменилось (модуль отверг изменение)
        return new_idx == old_idx and "out of range" in logs.lower()
    
    # Тест 3: Отрицательный idx (должен вернуть ошибку)
    def test_idx_negative():
        print("Попытка установить idx=-5 (минимально 0)...")
        
        old_idx = tester.read_param("idx")
        
        # Пытаемся установить отрицательное значение
        success = tester.write_param("idx", "-5")
        
        new_idx = tester.read_param("idx")
        
        logs = tester.get_module_logs(3)
        print(f"Логи ядра:\n{logs}")
        
        tester.write_param("idx", old_idx)
        
        return new_idx == old_idx
    
    # Тест 4: Неправильный ch_val (больше 255)
    def test_ch_val_too_large():
        print("Попытка установить ch_val=300 (максимум 255)...")
        
        old_ch_val = tester.read_param("ch_val")
        
        success = tester.write_param("ch_val", "300")
        
        new_ch_val = tester.read_param("ch_val")
        
        logs = tester.get_module_logs(3)
        print(f"Логи ядра:\n{logs}")
        
        tester.write_param("ch_val", old_ch_val)
        
        return new_ch_val == old_ch_val and "out of range" in logs.lower()
    
    # Тест 5: Неправильный ch_val (не числовое значение)
    def test_ch_val_invalid():
        print("Попытка установить ch_val='abc' (не число)...")
        
        old_ch_val = tester.read_param("ch_val")
        
        success = tester.write_param("ch_val", "abc")
        
        new_ch_val = tester.read_param("ch_val")
        
        logs = tester.get_module_logs(3)
        print(f"Логи ядра:\n{logs}")
        
        tester.write_param("ch_val", old_ch_val)
        
        return new_ch_val == old_ch_val
    
    # Тест 6: Корректное изменение idx
    def test_valid_idx():
        print("Проверка корректного изменения idx=10...")
        
        old_idx = tester.read_param("idx")
        old_my_str = tester.read_param("my_str")
        
        success = tester.write_param("idx", "10")
        
        new_idx = tester.read_param("idx")
        new_my_str = tester.read_param("my_str")
        
        logs = tester.get_module_logs(3)
        print(f"Логи ядра:\n{logs}")
        
        tester.write_param("idx", old_idx)
        
        return new_idx == "10" and "idx value = 10" in logs
    
    # Тест 7: Корректное изменение ch_val
    def test_valid_ch_val():
        print("Проверка корректного изменения ch_val=88 ('X')...")
        
        old_ch_val = tester.read_param("ch_val")
        old_idx = tester.read_param("idx")
        old_my_str = tester.read_param("my_str")
        
        # Сначала установим idx=5
        tester.write_param("idx", "5")
        
        # Затем установим ch_val
        success = tester.write_param("ch_val", "88")
        
        new_ch_val = tester.read_param("ch_val")
        new_my_str = tester.read_param("my_str")
        
        logs = tester.get_module_logs(5)
        print(f"Логи ядра:\n{logs}")
        
        # Восстанавливаем
        tester.write_param("ch_val", old_ch_val)
        tester.write_param("idx", old_idx)
        
        return "X" in new_ch_val and "ch_val value = X (88)" in logs
    
    # Тест 8: Изменение строки через idx и ch_val
    def test_string_modification():
        print("Проверка изменения строки через idx и ch_val...")
        
        # Сохраняем оригинальные значения
        original_idx = tester.read_param("idx")
        original_ch_val = tester.read_param("ch_val")
        original_my_str = tester.read_param("my_str")
        
        print(f"Исходная строка: {original_my_str}")
        
        # Устанавливаем idx=0 и ch_val='H' (72)
        tester.write_param("idx", "0")
        tester.write_param("ch_val", "72")  # 'H'
        time.sleep(0.1)
        
        str1 = tester.read_param("my_str")
        print(f"После idx=0, ch_val='H': {str1}")
        
        # Устанавливаем idx=1 и ch_val='e' (101)
        tester.write_param("idx", "1")
        tester.write_param("ch_val", "101")  # 'e'
        time.sleep(0.1)
        
        str2 = tester.read_param("my_str")
        print(f"После idx=1, ch_val='e': {str2}")
        
        # Восстанавливаем
        tester.write_param("idx", original_idx)
        tester.write_param("ch_val", original_ch_val)
        
        logs = tester.get_module_logs(10)
        print(f"\nЛоги изменений:\n{logs}")
        
        return "H" in str1 and str1 != original_my_str
    
    # Тест 9: Проверка, что my_str только для чтения
    def test_my_str_readonly():
        print("Попытка изменить my_str напрямую (должна быть ошибка)...")
        
        original_my_str = tester.read_param("my_str")
        
        # Пытаемся записать в my_str
        success = tester.write_param("my_str", "Hello World")
        
        new_my_str = tester.read_param("my_str")
        
        return new_my_str == original_my_str
    
    # Запускаем все тесты
    tests = [
        ("Начальное состояние", test_initial_state),
        ("Слишком большой idx (100)", test_idx_too_large),
        ("Отрицательный idx (-5)", test_idx_negative),
        ("Слишком большой ch_val (300)", test_ch_val_too_large),
        ("Некорректный ch_val ('abc')", test_ch_val_invalid),
        ("Корректный idx (10)", test_valid_idx),
        ("Корректный ch_val (88='X')", test_valid_ch_val),
        ("Изменение строки через параметры", test_string_modification),
        ("my_str только для чтения", test_my_str_readonly),
    ]
    
    results = []
    for test_name, test_func in tests:
        total_tests += 1
        if run_test(test_name, test_func):
            passed_tests += 1
            results.append((test_name, True))
        else:
            results.append((test_name, False))
        time.sleep(0.5)  # Пауза между тестами
    
    # Вывод итогов
    print(f"\n{'='*60}")
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print('='*60)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nПройдено тестов: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"\n⚠️  Не пройдено тестов: {total_tests - passed_tests}")
    
    # Дополнительная информация
    print(f"\n{'='*60}")
    print("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ")
    print('='*60)
    
    print("\nТекущие значения параметров:")
    print(f"  idx:     {tester.read_param('idx')}")
    print(f"  ch_val:  {tester.read_param('ch_val')}")
    print(f"  my_str:  {tester.read_param('my_str')}")
    
    print("\nПоследние логи модуля:")
    print(tester.get_module_logs(5))

if __name__ == "__main__":
    # Проверяем, запущен ли скрипт с правами root
    if os.geteuid() == 0:
        print("⚠️  Внимание: скрипт запущен от root!")
        print("Рекомендуется запускать от обычного пользователя.")
        response = input("Продолжить? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    main()
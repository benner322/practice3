## Учебная Виртуальная Машина (Вариант 4)
Быстрый старт

# Этап 1: Ассемблер Установи зависимости
`pip install PyYAML`

Проверь работу ассемблера
`python assembler.py tests.yaml tests.bin 1`
Ожидаемый вывод: покажет внутреннее представление команд


# Этап 2: Интерпретатор и память
Скомпилируй программу копирования массива
`python assembler.py array_copy.yaml array_copy.bin 0`

Запусти интерпретатор
`python vm.py array_copy.bin dump.xml 200 202`
Результат: файл dump.xml с скопированными значениями


# Этап 3: АЛУ (операция <=) Скомпилируй тест операции <=
`python assembler.py test_less_eq.yaml test_less_eq.bin 0`

Запусти с АЛУ
`python vm.py test_less_eq.bin dump_less_eq.xml 600 600`
Результат: в dump_less_eq.xml будет значение 1 (true)

Файлы проекта
assembler.py – ассемблер (YAML → бинарный)

vm.py – интерпретатор с памятью и АЛУ

*.yaml – программы на ассемблере

*.bin – скомпилированные программы

*.xml – дампы памяти после выполнения

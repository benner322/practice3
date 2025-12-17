import sys
import struct
import xml.etree.ElementTree as ET
from xml.dom import minidom


class UVM:
    """Учебная Виртуальная Машина (Вариант 4)"""

    def __init__(self, code_size=65536, data_size=65536):
        # Раздельная память: команды и данные
        self.code_memory = bytearray(code_size)
        self.data_memory = [0] * data_size
        self.stack = []  # Стек УВМ
        self.ip = 0  # Instruction Pointer
        self.running = True

        # Инициализация тестовых данных для array_copy
        self.data_memory[100] = 10
        self.data_memory[101] = 20
        self.data_memory[102] = 30

    def load_code(self, bin_path):
        """Загружает бинарный код в память команд."""
        with open(bin_path, 'rb') as f:
            code = f.read()
        self.code_memory[:len(code)] = code
        print(f"Загружено {len(code)} байт кода из {bin_path}")

    def decode_command(self):
        """Декодирует команду по текущему IP."""
        # Проверяем, не вышли ли за пределы памяти команд
        if self.ip + 3 > len(self.code_memory):
            return None, None

        # Читаем 3 байта команды
        cmd_bytes = self.code_memory[self.ip:self.ip + 3]
        if cmd_bytes == b'\x00\x00\x00':
            return None, None

        # Распаковываем в 32-битное слово
        word = struct.unpack('<I', cmd_bytes + b'\x00')[0]

        # A: биты 0-2
        a = word & 0b111

        # B: биты 3-... (читаем максимум 16 бит)
        b = (word >> 3) & 0xFFFF

        return a, b

    def execute_load_const(self, b):
        """Выполняет команду загрузки константы (A=5)."""
        self.stack.append(b)
        self.ip += 3
        print(f"[LOAD_CONST] Загружена константа {b} на стек")

    def execute_read_mem(self, b):
        """Выполняет чтение из памяти (A=4)."""
        addr = b
        if 0 <= addr < len(self.data_memory):
            value = self.data_memory[addr]
            self.stack.append(value)
            print(f"[READ_MEM] Прочитано из памяти [{addr}] = {value}")
        else:
            raise IndexError(f"Попытка чтения из недопустимого адреса: {addr}")
        self.ip += 3

    def execute_write_mem(self, b):
        """Выполняет запись в память (A=2)."""
        if not self.stack:
            raise RuntimeError("Стек пуст при записи в память")

        value = self.stack.pop()
        addr = b

        if 0 <= addr < len(self.data_memory):
            self.data_memory[addr] = value
            print(f"[WRITE_MEM] Записано в память [{addr}] = {value}")
        else:
            raise IndexError(f"Попытка записи в недопустимый адрес: {addr}")

        self.ip += 3

    def execute_less_or_eq(self, b):
        """Пропускаем команду <= на этапе 2 (будет на этапе 3)."""
        print(f"[LESS_OR_EQ] Пропуск команды (адрес {b}) - реализация в этапе 3")
        self.ip += 3

    def execute(self):
        """Основной цикл выполнения программы."""
        print("\n=== Начало выполнения программы ===")
        step = 0

        while self.running:
            a, b = self.decode_command()

            if a is None:
                print("Достигнут конец программы")
                break

            step += 1
            print(f"\nШаг {step}: IP={self.ip}, A={a}, B={b}")

            if a == 5:  # load_const
                self.execute_load_const(b)
            elif a == 4:  # read_mem
                self.execute_read_mem(b)
            elif a == 2:  # write_mem
                self.execute_write_mem(b)
            elif a == 1:  # less_or_eq
                self.execute_less_or_eq(b)
            else:
                raise ValueError(f"Неизвестный код операции: {a}")

        print(f"\n=== Выполнение завершено. Шагов: {step} ===")
        print(f"Состояние стека: {self.stack}")

    def dump_memory_xml(self, start_addr, end_addr, output_path):
        """Создает дамп памяти в формате XML."""


        print(f"\nСоздание дампа памяти с {start_addr} по {end_addr}...")

        root = ET.Element("memory_dump")
        root.set("start", hex(start_addr))
        root.set("end", hex(end_addr))

        for addr in range(start_addr, min(end_addr + 1, len(self.data_memory))):
            cell = ET.SubElement(root, "cell")
            cell.set("address", hex(addr))
            cell.set("value", str(self.data_memory[addr]))
            cell.set("dec", str(self.data_memory[addr]))

        # Форматируем XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)

        print(f"Дамп сохранен в {output_path}")
        return xml_str


def main():
    """Точка входа для CLI."""
    if len(sys.argv) != 5:
        print("Использование: python vm.py <код.bin> <дамп.xml> <начальный_адрес> <конечный_адрес>")
        print("Пример: python vm.py array_copy.bin dump.xml 200 202")
        sys.exit(1)

    code_file = sys.argv[1]
    dump_file = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])

    if start_addr > end_addr:
        print("Ошибка: начальный адрес больше конечного")
        sys.exit(1)

    try:
        # Создаем и настраиваем ВМ
        vm = UVM()

        # Загружаем программу
        vm.load_code(code_file)

        # Выполняем программу
        vm.execute()

        # Создаем дамп
        vm.dump_memory_xml(start_addr, end_addr, dump_file)

        print("\n✅ Этап 2 завершен успешно!")

    except Exception as e:
        print(f"\n❌ Ошибка выполнения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

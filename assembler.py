import sys
import yaml
import struct

# Коды операций (A)
OPCODES = {
    'load_const': 5,
    'read_mem': 4,
    'write_mem': 2,
    'less_or_eq': 1
}

# Размеры команд в байтах
CMD_SIZE = {
    'load_const': 3,
    'read_mem': 3,
    'write_mem': 3,
    'less_or_eq': 3
}


def encode_command(op, value):
    """Кодирует команду в байты согласно спецификации."""
    a = OPCODES[op]

    if op == 'load_const':
        # A: биты 0-2, B: биты 3-11
        word = (a & 0b111) | ((value & 0x1FF) << 3)
    elif op in ['read_mem', 'less_or_eq']:
        # A: биты 0-2, B: биты 3-15
        word = (a & 0b111) | ((value & 0x1FFF) << 3)
    elif op == 'write_mem':
        # A: биты 0-2, B: биты 3-18
        word = (a & 0b111) | ((value & 0x3FFF) << 3)
    else:
        raise ValueError(f"Неизвестная операция: {op}")

    # Упаковываем в little-endian и обрезаем до нужного размера
    return struct.pack('<I', word)[:CMD_SIZE[op]]


def assemble(src_path, bin_path, test_mode=False):
    """Основная функция ассемблирования."""
    # Читаем YAML
    with open(src_path, 'r') as f:
        program = yaml.safe_load(f)

    binary = bytearray()
    internal_repr = []

    # Обрабатываем каждую команду
    for cmd in program:
        for op, value in cmd.items():
            if op not in OPCODES:
                raise ValueError(f"Неизвестная мнемоника: {op}")

            # Кодируем команду
            code = encode_command(op, value)
            binary.extend(code)

            # Сохраняем для вывода в тестовом режиме
            internal_repr.append({
                'op': op,
                'A': OPCODES[op],
                'B': value,
                'bytes': list(code)
            })

    # Записываем бинарный файл
    with open(bin_path, 'wb') as f:
        f.write(binary)

    # Выводим внутреннее представление в тестовом режиме
    if test_mode:
        print("=== Внутреннее представление ===")
        for instr in internal_repr:
            hex_bytes = [f'0x{b:02X}' for b in instr['bytes']]
            print(f"{instr['op']}: A={instr['A']}, B={instr['B']}, bytes={hex_bytes}")
        print("===============================")

    print(f"✅ Ассемблирование завершено: {len(binary)} байт записано в {bin_path}")
    return binary


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python assembler.py <входной.yaml> <выходной.bin> <тестовый_режим:0|1>")
        print("Пример: python assembler.py tests.yaml tests.bin 1")
        sys.exit(1)

    src_file = sys.argv[1]
    out_file = sys.argv[2]
    test_mode = bool(int(sys.argv[3]))

    try:
        assemble(src_file, out_file, test_mode)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

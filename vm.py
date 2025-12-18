import sys
import struct
import xml.etree.ElementTree as ET
from xml.dom import minidom

class UVM:
    def __init__(self, code_size=65536, data_size=65536):
        self.code_memory = bytearray(code_size)
        self.data_memory = [0] * data_size
        self.stack = []
        self.ip = 0
        self.data_memory[500] = 15
        self.data_memory[501] = 20
    
    def load_code(self, bin_path):
        with open(bin_path, 'rb') as f:
            code = f.read()
        self.code_memory[:len(code)] = code
    
    def decode_command(self):
        if self.ip + 3 > len(self.code_memory):
            return None, None
        cmd_bytes = self.code_memory[self.ip:self.ip + 3]
        if cmd_bytes == b'\x00\x00\x00':
            return None, None
        word = struct.unpack('<I', cmd_bytes + b'\x00')[0]
        a = word & 0b111
        b = (word >> 3) & 0xFFFF
        return a, b
    
    def execute_load_const(self, b):
        self.stack.append(b)
        self.ip += 3
    
    def execute_read_mem(self, b):
        addr = b
        if 0 <= addr < len(self.data_memory):
            value = self.data_memory[addr]
            self.stack.append(value)
        else:
            raise IndexError(f"Read invalid address: {addr}")
        self.ip += 3
    
    def execute_write_mem(self, b):
        if not self.stack:
            raise RuntimeError("Stack underflow")
        addr = self.stack.pop()  # адрес из стека
        value = self.stack.pop()  # значение из стека (новый верх стека после извлечения адреса)
        if 0 <= addr < len(self.data_memory):
            self.data_memory[addr] = value
        else:
            raise IndexError(f"Write invalid address: {addr}")
        self.ip += 3
    
    def execute_less_or_eq(self, b):
        if len(self.stack) < 2:
            raise RuntimeError("Stack underflow")
        right = self.stack.pop()  # второй операнд из стека
        addr = b  # адрес первого операнда из поля B
        left = self.data_memory[addr]  # первый операнд из памяти по адресу B
        result = 1 if left <= right else 0
        self.stack.append(result)
        self.ip += 3
    
    def execute(self):
        while True:
            a, b = self.decode_command()
            if a is None:
                break
            if a == 5:
                self.execute_load_const(b)
            elif a == 4:
                self.execute_read_mem(b)
            elif a == 2:
                self.execute_write_mem(b)
            elif a == 1:
                self.execute_less_or_eq(b)
            else:
                raise ValueError(f"Unknown opcode: {a}")
    
    def dump_memory_xml(self, start_addr, end_addr, output_path):
        root = ET.Element("memory_dump")
        root.set("start", hex(start_addr))
        root.set("end", hex(end_addr))
        for addr in range(start_addr, min(end_addr + 1, len(self.data_memory))):
            cell = ET.SubElement(root, "cell")
            cell.set("address", hex(addr))
            cell.set("value", str(self.data_memory[addr]))
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        return xml_str

def main():
    if len(sys.argv) != 5:
        print("Usage: python vm.py <code.bin> <dump.xml> <start> <end>")
        sys.exit(1)
    code_file = sys.argv[1]
    dump_file = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])
    if start_addr > end_addr:
        print("Error: start > end")
        sys.exit(1)
    try:
        vm = UVM()
        vm.load_code(code_file)
        vm.execute()
        vm.dump_memory_xml(start_addr, end_addr, dump_file)
        print(f"Dump saved to {dump_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


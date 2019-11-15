# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 11:19:18 2019

@author: pablo
"""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.SP = 7
        self.e = 0
        self.l = 0
        self.g = 0
        self.commands = {
            'LDI': int("10000010", 2),
            'PRN': int("01000111", 2),
            'HLT': int("00000001", 2),
            'MUL': int("10100010", 2),
            'PUSH': int("01000101", 2),
            'POP': int("01000110", 2),
            'CMP': int("10100111", 2),
            'JMP': int("01010100 ", 2),
            'JEQ': int("01010101", 2),
            'JNE': int("01010110", 2),
        }
        self.branchtable = {
            self.commands['LDI']: self.ldi,
            self.commands['PRN']: self.prn,
            self.commands['HLT']: self.hlt,
            self.commands['MUL']: self.mul,
            self.commands['PUSH']: self.push,
            self.commands['POP']: self.pop,
            self.commands['CMP']: self.cmp,
            self.commands['JMP']: self.jmp,
            self.commands['JEQ']: self.jeq,
            self.commands['JNE']: self.jne,
        }
        
    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    # Process comments:
                    # Ignore anything after a # symbol
                    comment_split = line.split("#")
                    # Convert any numbers from binary strings to integers
                    num = comment_split[0].strip()
                    try:
                        val = int(num, 2)
                    except ValueError:
                        continue
                    self.ram[address] = val
                    address += 1
                    # print(f"{val:08b}: {val:d}")
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        # return value stored in passed in address
        return self.ram[address]

    def ram_write(self, value, address):
        # writes the given value into given address
        self.ram[address] = value

    # assign passed in reg to passed in value
    def ldi(self, reg_a, value):
        self.reg[reg_a] = value
        self.pc += 3

    # print value at reg passed in
    def prn(self, reg_a):
        print(f'Value: {self.reg[reg_a]}')
        self.pc += 2

    # call alu to multiply two passed in registers
    def mul(self, reg_a, reg_b):
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3

    # stop the cpu
    def hlt(self):
        self.pc += 1
        print('Stopping...')
        return False

    # push the value in the given register to the stack
    def push(self, reg):
        val = self.reg[reg]
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = val
        self.pc += 2

    # pop the value at the top of the stack into the given register
    def pop(self, reg):
        val = self.ram[self.reg[self.SP]]
        self.reg[reg] = val
        self.reg[self.SP] += 1
        self.pc += 2

    # Jump to the address stored in the given register
    def jmp(self, reg):
        val = self.reg[reg]
        self.pc = val

    # Compare the values in two registers
    def cmp(self, reg_a, reg_b):
        # clear flags from last time cmp ran
        self.e, self.l, self.g = 0, 0, 0
        # get values from registers
        val_1, val_2 = self.reg[reg_a], self.reg[reg_b]
        # check comparisons
        if val_1 == val_2:
            self.e = 1
        elif val_1 < val_2:
            self.l = 1
        elif val_1 > val_2:
            self.g = 1
        self.pc += 3

    # if e flag is false jump to the address stored in the given register
    def jne(self, reg):
        if self.e == 0:
            self.pc = self.reg[reg]
        else:
            self.pc += 2

    # if e flag is true jump to the address stored in the given register
    def jeq(self, reg):
        if self.e == 1:
            self.pc = self.reg[reg]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            command = self.ram[self.pc]
            num_params = int(bin(command >> 6).replace("0b", ""), 2)
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]
            if command not in self.branchtable:
                print(f'command: {command} not recognized')
                running = False
            if num_params == 2:
                self.branchtable[command](operand_a, operand_b)
            elif num_params == 1:
                self.branchtable[command](operand_a)
            else:
                running = self.branchtable[command]()

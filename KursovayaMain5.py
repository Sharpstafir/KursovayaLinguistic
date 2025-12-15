from typing import List

# Таблица шифровки ключевых слов и символов
token_table = {
    "=": 2,
    "+": 3,
    "-": 4,
    "*": 5,
    "/": 6,
    "(": 7,
    ")": 8,
    ",": 9,
    ":": 10,
    ";": 11,
    "программа": 12,
    "переменные": 13,
    "вещественные": 14,
    "целые": 15,
    "ввод": 16,
    "вывод": 17,
    "цикл": 18,
    "от": 19,
    "до": 20,
    "с": 21,
    "шагом": 22,
    "выполнить": 23,
    "конец.": 24

}

# Таблица типов для преобразования
type_table = {
    "вещественные": "REAL",
    "целые": "INTEGER"
}

# Таблица переменных (идентификаторов)
variable_table = {}
variable_counter = 0

# Исходный код
code = """
программа Р;
переменные s: вещественные;
                      i, n: целые;
s=1;
ввод n;
                     цикл 1 от 1 до n с шагом 2
выполнить s=s*i/(i+1);
вывод s;
конец.
"""

lines = [line.strip() for line in code.strip().split('\n') if line.strip()]


def translate_line(line):
    # Заменяем специальные символы на пробелы вокруг них
    line = (line.replace("=", " = ")
            .replace("+", " + ")
            .replace("-", " - ")
            .replace("*", " * ")
            .replace("/", " / ")
            .replace("(", " ( ")
            .replace(")", " ) ")
            .replace(",", " , ")
            .replace(":", " : ")
            .replace(";", " ; "))

    tokens = line.split()
    print(tokens)
    translated_tokens = []

    for token in tokens:
        if token in token_table:
            translated_tokens.append(str(token_table[token]))
        elif token.isdigit():
            translated_tokens.append("1")  # const
            translated_tokens.append(token)
        else:
            # Обработка идентификаторов
            if token not in variable_table:
                global variable_counter
                variable_table[token] = variable_counter
                variable_counter += 1
            translated_tokens.append("0")  # ид
            translated_tokens.append(str(variable_table[token]))

    return " ".join(translated_tokens)


translated_code = [translate_line(line) for line in lines]

print("Таблица шифровки:")
for key, value in sorted(token_table.items(), key=lambda item: item[1]):
    print(f"{key}\t{value}")

print("\nТаблица переменных:")
for key, value in sorted(variable_table.items(), key=lambda item: item[1]):
    print(f"{value}\t{key}")

print("\nПереведенный код:")
for line in translated_code:
    print(line)

# Преобразуем output в массив с числами лексем
newest_tokens = ' '.join(translated_code)
newest_tokens = newest_tokens.split(" ")
newest_tokens = list(map(int, newest_tokens))
lexems = []
i = 0
while i < len(newest_tokens):
    if (i < len(newest_tokens) - 1 and newest_tokens[i] == 0) or (i < len(newest_tokens) - 1 and newest_tokens[i] == 1):
        lexems.append([newest_tokens[i], newest_tokens[i + 1]])
        i += 2
    else:
        lexems.append(newest_tokens[i])
        i += 1

# Словарь с лексемами (обратный для генерации)
reverse_lexemes_map = {v: k for k, v in token_table.items()}

# Словарь типов (обратный)
reverse_type_map = {v: k for k, v in type_table.items()}


# Идентификаторы
identifiersMap = variable_table.items()

class RecursiveDescent:
    def __init__(self, lexemes: List, lexemesMap, identifiersMap):
        self.lexemes = lexemes
        self.lexemes.append(0)
        self.lexemesMap = lexemesMap
        self.identifiersMap = identifiersMap
        self.invertedIdMap = self.swap_dict(self.identifiersMap)
        self.postfix_notation = []

        self.cursor = 0

    def swap_dict(self, d):
        d = dict((v, k) for k, v in d.items())
        return d

    def add_postfix(self, lexeme):
        if type(lexeme) is list:
            if lexeme[0] == 0:
                self.postfix_notation.append(self.invertedIdMap[lexeme[1]])
            else:
                self.postfix_notation.append(str(lexeme[1]))
        elif type(lexeme) is int:
            self.postfix_notation.append(lexeme)
        else:
            self.postfix_notation.append(lexeme)



    def disassemble(self):
        # print(self.lexemes)
        # print(self.lexemesMap)
        # print(self.identifiersMap)
        print("\nПереведённый код:\n----------------------------------------------")

        if self.programm_name():
            print(True)
        else:
            print(False)

        if self.variable_section():
            print(True)
        else:
            print(False)

        if self.operators_section():
            print(True)
        else:
            print(True)
        print(self.postfix_notation)


    # <Имя программы> -> <ид>
    def programm_name(self):
        succeeded = False
        programm_name_print = 'Null'
        # print('summand')
        if self.lexemes[self.cursor] == 12:
            print(self.lexemes[self.cursor])
            self.cursor +=1
        if type(self.lexemes[self.cursor]) is list and self.lexemes[self.cursor][0] == 0:
            current_ident = self.lexemes[self.cursor]
        if self.value():
            pass
            self.add_postfix(current_ident)
            self.add_postfix("программа")
        if self.lexemes[self.cursor] == self.lexemesMap[";"]:
            print(self.lexemes[self.cursor])
            self.cursor +=1
            succeeded = True

        return succeeded

    # def variables_section(self) -> bool:
    #     succeeded = False
    #     variables_section_print = 'NULL'
    #     if self.variables_list():
    #         # while self.lexemes[self.cursor] == self.lexemesMap[";"]:
    #         # print('test',self.lexemes[self.cursor])
    #         succeeded = True
    #     return succeeded
    #
    #
    # def variables_list(self) -> bool:
    #     succeeded = False
    #     variable_list_print ='NULL'
    #     if self.lexemes[self.cursor]==self.lexemesMap["переменные"]:
    #         self.cursor+=1
    #         if self.lexemes[self.cursor] is list and self.lexemes[self.cursor][0] == 0:
    #             self.add_postfix(self.lexemes[self.cursor])
    #         while self.value() and self.lexemes[self.cursor]+1 != self.lexemesMap['=']:
    #             # print('summand is true')
    #             succeeded = True
    #             while (self.lexemes[self.cursor] == self.lexemesMap[","]):
    #                 print(self.lexemesMap[","])
    #                 self.cursor+=1
    #                 self.add_postfix(self.lexemes[self.cursor])
    #                 if self.value():
    #                     pass
    #             if self.lexemes[self.cursor] == self.lexemesMap[':']:
    #                 self.cursor+=1
    #                 self.add_postfix(self.lexemes[self.cursor])
    #                 print(self.lexemes[self.cursor])
    #                 print(self.lexemesMap[':'])
    #                 print(self.lexemesMap[';'])
    #                 self.cursor+=2
    #                 if self.lexemes[self.cursor+1] == self.lexemesMap['=']:
    #                     break
    #         if variable_list_print != 'NULL':
    #             print(variable_list_print)
    #         succeeded = True
    #     return succeeded

    # <раздел переменных> -> <объявление переменных> { ; <объявление переменных> } ;
    def variable_section(self):
        succeeded = False
        if self.declaration_variables():
            succeeded = True
            while True:
                if self.lexemes[self.cursor + 2] == self.lexemesMap[":"]:
                    if self.lexemes[self.cursor] != [';']:
                        break
                if not self.declaration_variables():
                    succeeded = False
                    break
            if self.lexemes[self.cursor] == [';']:
                succeeded = True

        return succeeded

    # <объявление переменных> -> <список переменных> : <тип>
    def declaration_variables(self) -> bool:
        succeeded = False
        if self.list_variables():
            if self.lexemes[self.cursor] == self.lexemesMap[':']:
                self.cursor+=1
                if self.type():
                    succeeded = True
                    self.cursor+=1
        return succeeded


    # <список переменных> -> ид {, ид}
    def list_variables(self):
        succeeded = False
        if self.lexemes[self.cursor] == self.lexemesMap['переменные']:
            self.cursor+=1
        # print('test!!!!!!!!!!!!!', self.lexemes[self.cursor])
        # print(type(self.lexemes[self.cursor]) is list , self.lexemes[self.cursor][0] == 0)
        if type(self.lexemes[self.cursor]) is list and self.lexemes[self.cursor][0] == 0:
            self.add_postfix(self.lexemes[self.cursor])
            self.cursor += 1
            succeeded = True
            while True:
                if self.lexemes[self.cursor] != [',']:
                    break

                if (self.lexemes[self.cursor] is list and self.lexemes[self.cursor][0] != 0) or (self.lexemes[self.cursor] is not list):
                    succeeded = False
                self.add_postfix(self.lexemes[self.cursor])
                self.cursor += 1
        return succeeded


    # <тип> -> целые / вещественные
    def type(self):
        succeeded = False
        if self.lexemes[self.cursor] == self.lexemesMap['целые'] or self.lexemes[self.cursor] == self.lexemesMap['вещественные']:
            succeeded = True
            self.add_postfix(self.lexemes[self.cursor])
        return succeeded

    # <раздел операторов> -> <оператор>
    def operators_section(self) -> bool:
        succeeded = False
        if self.operator():
            # while self.lexemes[self.cursor] == self.lexemesMap[";"]:
            while True:
                # print('test',self.lexemes[self.cursor])
                succeeded = True
                if not self.operator():
                    succeeded = False
                    break

        return succeeded

    # <оператор> -> <условный оператор> / <присваивание>
    def operator(self) -> bool:

        succeeded = False
        if  self.assignment() or self.input_statement() or self.outpout_statement():
            succeeded = True
        return succeeded

    def input_statement(self):
        if self.lexemes[self.cursor] == self.lexemesMap['ввод']:
            self.cursor+=1
            if self.value():
                pass
            print(self.lexemesMap['ввод'])
            print(self.lexemesMap[';'])
    def outpout_statement(self):
        if self.lexemes[self.cursor] == self.lexemesMap['вывод']:
            self.cursor+=1
            if self.value():
                pass
            print(self.lexemesMap['вывод'])
            print(self.lexemesMap[';'])


    # <присваивание> -> ид = <арифметическое выражение>
    def assignment(self) -> bool:
        succeeded = False
        assignment_print = 'NULL'
        assignment_print2 = 'NULL'
        assignment_print3 = 'NULL'

        # смотрю почему последняя строка не выыводится
        # print('assignment', self.lexemes[self.cursor])
        # if type(self.lexemes[self.cursor]) is list:
        #     print('assignment with if list',self.lexemes[self.cursor][0], self.lexemes[self.cursor])

        if type(self.lexemes[self.cursor]) is list and self.lexemes[self.cursor][0] == 0:
            indent_id = self.lexemes[self.cursor][1]
            assignment_print = f"0 {indent_id}"
            self.add_postfix(indent_id)
            self.cursor += 1
            if self.lexemes[self.cursor] == self.lexemesMap["="]:
                assignment_print2 = self.lexemes[self.cursor]
                self.cursor += 1
                if self.arithmetic_expression():
                    succeeded = True
                self.add_postfix("=")
                if self.lexemes[self.cursor]==self.lexemesMap[';']:
                    assignment_print3 = self.lexemes[self.cursor]
                    self.cursor+=1
        if assignment_print != 'NULL':
            print(assignment_print)
        if assignment_print2 != 'NULL':
            print(assignment_print2)
        if assignment_print2 != 'NULL':
            print(assignment_print3)
        return succeeded


    # <арифмитическое выражение> -> <слагаемое> {+ <слагаемое>} {- <слагаемое>}
    def arithmetic_expression(self) -> bool:
        succeeded = False
        # print('arithmetuic')
        # print('arithmetic expression')
        aithmetic_expression_print = 'NULL'
        if self.summand():
            # print('summand is true')
            succeeded = True
            while (self.lexemes[self.cursor] == self.lexemesMap["+"] or
                   self.lexemes[self.cursor] == self.lexemesMap["-"]):
                aithmetic_expression_print = self.lexemes[self.cursor]
                self.add_postfix(self.lexemes[self.cursor])
                self.cursor += 1
                if not self.summand():
                    succeeded = False
        if aithmetic_expression_print != 'NULL':
            print(aithmetic_expression_print)
        # print ('arithmos is', succeeded, self.lexemes[self.cursor])
        return succeeded

    # <слагаемое> -> <значение> {* <значение>}
    def summand(self) -> bool:
        succeeded = False
        summand_print = 'Null'
        # print('summand')
        if self.value():
            succeeded = True
            while (self.lexemes[self.cursor] == self.lexemesMap["*"] or
                   self.lexemes[self.cursor] == self.lexemesMap["/"]):
                summand_print = self.lexemes[self.cursor]
                self.add_postfix(self.lexemes[self.cursor])
                self.cursor += 1
                if not self.value():
                    succeeded = False
        if summand_print != 'Null':
            print (summand_print)
        return succeeded

    # <значение>: <значение> -> ид / конст / ( <арифметическое выражение>)
    def value(self) -> bool:
        succeeded = False
        # print('value')
        if type(self.lexemes[self.cursor]) is list:
            data = self.lexemes[self.cursor][1]
            print(f"{self.lexemes[self.cursor][0]} {data}")
            self.cursor += 1
            succeeded = True
        elif self.lexemes[self.cursor] == self.lexemesMap["("]:
            print(self.lexemes[self.cursor])
            self.cursor += 1
            if self.arithmetic_expression():
                print('danger')
                succeeded = True
                if self.lexemes[self.cursor] == self.lexemesMap[")"]:
                    print(self.lexemes[self.cursor])
                    self.cursor += 1
                    succeeded = True
        return succeeded


class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = []

    def generate(self):
        self.code.append("PROGRAM P")
        self.code.append("IMPLICIT NONE")
        for typ, names in self.ast['vars']:
            self.code.append(f"{typ} :: {', '.join(names)}")
        for stmt in self.ast['body']:
            self.code.append(self.gen_stmt(stmt))
        self.code.append("END PROGRAM P")
        return '\n'.join(self.code)

    def gen_stmt(self, stmt):
        if stmt[0] == "input":
            return f"READ(*,*) {stmt[1]}"
        elif stmt[0] == "output":
            return f"WRITE(*,*) {stmt[1]}"
        elif stmt[0] == "assign":
            return f"{stmt[1]} = {self.gen_expr(stmt[2])}"
        elif stmt[0] == "loop":
            lines = []
            lines.append(f"DO {stmt[1]} = {self.gen_expr(stmt[2])}, {self.gen_expr(stmt[3])}, {self.gen_expr(stmt[4])}")
            lines.append(f"  {self.gen_stmt(stmt[5])}")
            lines.append("END DO")
            return '\n'.join(lines)

    def gen_expr(self, expr):
        if expr[0] == "id":
            return expr[1]
        elif expr[0] == "const":
            return str(expr[1])
        elif expr[0] in {"+", "-", "*", "/"}:
            return f"({self.gen_expr(expr[1])} {expr[0]} {self.gen_expr(expr[2])})"
        return ""



parser = RecursiveDescent(lexems, token_table, variable_table)
ast = parser.disassemble()


if ast is None:
    print("Ошибка разбора программы.")
else:
    generator = CodeGenerator(ast)
    fortran_code = generator.generate()

    print("\nСгенерированный код на Фортране:\n----------------------------------------------")
    print(fortran_code)

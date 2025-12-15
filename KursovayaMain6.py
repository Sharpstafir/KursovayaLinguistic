from typing import List
import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from Interface1 import Ui_MainWindow

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
                     цикл i от 1 до n с шагом 2
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

    def currentLexemeIs(self, lexemes: list[str] ) -> (bool, str):
        for lexeme in lexemes:
            if self.lexemes[self.cursor] == self.lexemesMap[lexeme]:
                self.cursor += 1
                return True, lexeme
        return False, ""

    def disassemble(self) -> tuple[list[str], bool]:
        if self.program():
            return self.postfix_notation, True
        else:
            return self.postfix_notation, False

    # <программа> -> <имя программы> переменные <раздел переменных> <раздел операторов> конец.
    def program(self):
        succeeded = False
        if self.name_program():
            correct, _ = self.currentLexemeIs(["переменные"])
            if correct:
                self.add_postfix("переменные")
                self.add_postfix("(")
                if self.variable_section():
                    self.add_postfix(")")
                    if self.operators_section():
                        correct, _ = self.currentLexemeIs(["конец."])
                        if correct:
                            succeeded = True
        print(self.postfix_notation)
        return succeeded


    # <имя программы> -> программа ид ;
    def name_program(self):
        succeeded = False
        correct, _ = self.currentLexemeIs(["программа"])
        if correct:
            if type(self.lexemes[self.cursor]) is list and self.lexemes[self.cursor][0] == 0:
                current_ident = self.lexemes[self.cursor]
                self.cursor += 1
                correct, _ = self.currentLexemeIs([";"])
                if correct:
                    succeeded = True
                    # self.add_postfix(";")
                self.add_postfix(current_ident)
            self.add_postfix("программа")
        return succeeded

    # <раздел переменных> -> <объявление переменных> { ; <объявление переменных> } ;
    def variable_section(self):
        succeeded = False
        if self.declaration_variables():
            succeeded = True
            while True:
                if self.lexemes[self.cursor + 4] == self.lexemesMap[":"]:
                    correct, _ = self.currentLexemeIs([";"])
                    if not correct:
                        break
                if not self.declaration_variables():
                    succeeded = False
                    break
            correct, _ = self.currentLexemeIs([";"])
            if correct:
                succeeded = True

        return succeeded

    # <объявление переменных> -> <список переменных> : <тип>
    def declaration_variables(self) -> bool:
        succeeded = False
        if self.list_variables():
            correct, _ = self.currentLexemeIs([":"])
            if correct:
                if self.type():
                    succeeded = True
        return succeeded


    # <список переменных> -> ид {, ид}
    def list_variables(self):
        succeeded = False
        if self.is_ident():
            self.add_postfix(self.lexemes[self.cursor])
            self.cursor += 1
            succeeded = True
            while True:
                correct, _ = self.currentLexemeIs([","])
                if not correct:
                    break

                if not self.is_ident():
                    succeeded = False
                self.add_postfix(self.lexemes[self.cursor])
                self.cursor += 1
        return succeeded


    # <тип> -> целые / вещественные
    def type(self):
        succeeded = False
        correct, lexeme = self.currentLexemeIs(["целые", "вещественные"])
        if correct:
            succeeded = True
            self.add_postfix(lexeme)
        return succeeded


    # <раздел операторов> -> <оператор> {; <оператор>}
    def operators_section(self) -> bool:
        succeeded = False
        if self.operator():
            succeeded = True
            while True:

                correct, _ = self.currentLexemeIs([";"])
                print(self.lexemes[self.cursor], 'input', correct)
                if not correct:
                    break
                if not self.operator():
                    succeeded = False

        return succeeded

    # <оператор> -> <присваивание> / <условный оператор>
    def operator(self) -> bool:
        succeeded = False
        if self.assignment() or self.loop() or self.input_val() or self.output_val():
            succeeded = True
        return succeeded

    # <присваивание> -> ид := <арифмитическое выражение>
    def assignment(self) -> bool:
        succeeded = False
        if self.is_ident():
            ident = self.lexemes[self.cursor]
            self.cursor += 1
            self.add_postfix(ident)
            correct, _ = self.currentLexemeIs(["="])
            if correct:
                if self.arithmetic_expression():
                    succeeded = True
                self.add_postfix("=")
        return succeeded

    # <цикл> -> пока <выражение цикла> выполнить <тело цикла>
    def loop(self) -> bool:
        succeeded = False
        print('cycle', self.lexemes[self.cursor])
        correct, _ = self.currentLexemeIs(["цикл"])
        if correct:
            self.add_postfix("цикл")
            self.add_postfix("(")
            if self.cycle_expression():
                self.add_postfix(")")
                correct, _ = self.currentLexemeIs(["выполнить"])
                if correct:
                    if self.loop_body():
                        succeeded = True
        return succeeded

    def loop_body(self) -> bool:
        succeeded = False
        if self.operator():
            succeeded = True
        else:
            correct, _ = self.currentLexemeIs(["("])
            self.add_postfix("(")
            if correct:
                if self.operators_section():
                    correct, _ = self.currentLexemeIs([")"])
                    if correct:
                        succeeded = True
                        self.add_postfix(")")
        return succeeded



    def cycle_expression(self) -> bool:
        succeeded = False
        if self.is_ident():
            self.add_postfix(self.lexemes[self.cursor])
            self.cursor+=1
            correct, _ = self.currentLexemeIs(["от"])
            if correct:
                if self.arithmetic_expression():
                    succeeded = True
                    self.postfix_notation.append(self.lexemesMap[","])
            correct, _ = self.currentLexemeIs(['до'])
            if correct:
                if self.arithmetic_expression():
                    succeeded = True
                    self.postfix_notation.append(self.lexemesMap[","])
            correct, _ = self.currentLexemeIs(['с'])
            correct, _ = self.currentLexemeIs(['шагом'])
            if correct:
                if self.arithmetic_expression():
                    succeeded = True
                    self.postfix_notation.append(self.lexemesMap[","])
        return succeeded

    # <тело условия> -> <оператор> / begin <раздел операторов> end
    def condition_body(self) -> bool:
        succeeded = False
        if self.operator():
            succeeded = True
        else:
            correct, _ = self.currentLexemeIs(["("])
            if correct:
                if self.operators_section():
                    correct, _ = self.currentLexemeIs([")"])
                    if correct:
                        succeeded = True
                        self.postfix_notation.append(self.lexemesMap["end"])
                self.postfix_notation.append(self.lexemesMap["begin"])
        return succeeded

    # <арифмитическое выражение> -> <слагаемое> {+ <слагаемое>} {- <слагаемое>}
    def arithmetic_expression(self) -> bool:
        succeeded = False
        if self.summand():
            succeeded = True
            while True:
                correct, lexeme = self.currentLexemeIs(["+", "-"])
                if not correct:
                    break

                if not self.summand():
                    succeeded = False
                self.add_postfix(lexeme)
        return succeeded

    def summand(self) -> bool:
        succeeded = False
        if self.value():
            succeeded = True
            while True:
                correct, lexeme = self.currentLexemeIs(["*", "/"])
                if not correct:
                    break

                if not self.value():
                    succeeded = False
                self.add_postfix(lexeme)
        return succeeded

    # <значение>: <значение> -> ид / конст / ( <арифметическое выражение> )
    def value(self) -> bool:
        succeeded = False
        if type(self.lexemes[self.cursor]) is list:
            self.add_postfix(self.lexemes[self.cursor])
            self.cursor += 1
            succeeded = True
        else:
            correct, _ = self.currentLexemeIs(["("])
            if correct:
                if self.arithmetic_expression():
                    correct, _ = self.currentLexemeIs([")"])
                    if correct:
                        succeeded = True
                        self.add_postfix(")")
                self.add_postfix("(")
        return succeeded

    def is_ident(self) -> bool:
        return type(self.lexemes[self.cursor]) is list and self.lexemes[self.cursor][0] == 0

    # <ввод> -> ввод(ид)
    def input_val(self):
        succeeded = False
        correct, _ = self.currentLexemeIs(["ввод"])
        if correct:
            if self.is_ident():
                ident = self.lexemes[self.cursor]
                self.cursor += 1
                correct, _ = self.currentLexemeIs([";"])
                self.cursor-=1
                if correct:
                    succeeded = True
                self.add_postfix(ident)
            self.add_postfix("ввод")

        return succeeded

    # <вывод> -> вывод  ( ид )
    def output_val(self):
        succeeded = False
        correct, _ = self.currentLexemeIs(["вывод"])
        if correct:
            if self.is_ident():
                ident = self.lexemes[self.cursor]
                self.cursor += 1
                correct, _ = self.currentLexemeIs([")"])
                if correct:
                    succeeded = True
                self.add_postfix(ident)
            self.add_postfix("вывод")

        return succeeded


class PostfixGenerator:
    def __init__(self, postfix_notation):
        self.postfix_notation = postfix_notation
        self.index_ident = 1

        self.a = {
            "ввод": "read",
            "вывод": "print",
            "вещественные": "real",
            "целые": "integer",
        }

    def generate(self, start_index):
        print(self.postfix_notation, 'a')
        stack = []
        code = ""
        index = start_index
        while index < len(self.postfix_notation):
            token = self.postfix_notation[index]
            if token == "программа":
                name_program = stack.pop()
                code += f"program {name_program};\n"
            elif token == "переменные":
                index += 1
                code_indent = ""
                identifiers = []
                while token != ")":
                    index += 1
                    token = self.postfix_notation[index]
                    if token in ["вещественные", "целые"]:
                        identifiers_str = ", ".join(identifiers)
                        code_indent += f"{identifiers_str}: {self.a[token]};\n"
                        identifiers = []
                    else:
                        identifiers.append(token)
                code += f"var\n{code_indent}begin\n"
            elif token == "=":
                val = stack.pop()
                dest = stack.pop()

                code += f"{dest} := {val};\n"
            elif token == "ввод":
                ident = stack.pop()
                code += f"read({ident});\n"
            elif token == "вывод":
                ident = stack.pop()
                code += f"write({ident});\n"
            elif token == "цикл":
                # code_fragments[index_code_fragment]
                loop_expression, index = self.generate(index+1)
                loop_body, index = self.generate(index+1)
                code += f"while ({loop_expression}) do\nbegin\n{loop_body}end;\n"
            elif token in ["+", "-", "/", "*"]:
                ident2 = stack.pop()
                try:
                    ident1 = stack.pop()
                except:
                    pass
                # code += f"T{self.index_ident} := {ident1}{token}{ident2};\n"
                try:
                    stack.append(f"{ident1}{token}{ident2}")
                except:
                    stack.append(f"{token}{ident2}")
                self.index_ident += 1
            elif token in ["=", "!=", ">", ">=", "<", "<="]:
                ident2 = stack.pop()
                try:
                    ident1 = stack.pop()
                except:
                    pass
                code += f"{ident1}{token}{ident2}"
            elif token == ")" and start_index != 0:
                break
            else:
                stack.append(token)
            index += 1
        if start_index == 0:
            code += "end."

        return code, index



parser = RecursiveDescent(lexems, token_table, variable_table)
ast = parser.disassemble()[0]

generator = PostfixGenerator(ast)
print(generator.generate(0)[0])

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.textEdit.setText(code)
        self.ui.pushButton.clicked.connect(self.Translate)

    def translation(self):
        parser = RecursiveDescent(lexems, token_table, variable_table)
        ast = parser.disassemble()[0]

        generator = PostfixGenerator(ast)
        return(generator.generate(0)[0])
    def Translate(self):
        source_code = self.ui.textEdit.toPlainText()
        self.ui.textEdit_2.setText(self.translation(source_code))
        self.ui.textEdit_3.setText(generator.generate(0)[0])
        self.ui.textEdit_4.setText(generator.generate(0)[0])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageWindow()
    window.show()
    sys.exit(app.exec_())
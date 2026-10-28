import re

from pygments.lexers import PythonLexer
from pygments.style import Style
from pygments.token import (
    Token,
    Text,
    Keyword,
    Name,
    String,
    Comment,
    Number,
    Operator,
    Punctuation,
)


# ==================================================
# 1. Custom Python Lexer
# ==================================================

class VSCodePythonLexer(PythonLexer):

    name = "VSCode Python Notes"
    aliases = ["vscodepython"]

    def get_tokens_unprocessed(self, text):

        bracket_stack = []
        pending_def_paren = False
        last_value = ""

        for index, token, value in super().get_tokens_unprocessed(text):

            # ------------------------------------------
            # 1. def / class
            # ------------------------------------------

            if token in Keyword and value in {"def", "class"}:

                if value == "def":
                    pending_def_paren = True

                yield index, Keyword.Declaration, value
                last_value = value
                continue

            # ------------------------------------------
            # 2. True / False
            # ------------------------------------------

            if value in {"True", "False"} and token in Keyword:

                yield index, Keyword.Constant, value
                last_value = value
                continue

            # ------------------------------------------
            # 3. Brackets
            # ------------------------------------------

            if token in Punctuation:

                for offset, char in enumerate(value):

                    if char in "([{":

                        if char == "(" and pending_def_paren:
                            context = "signature"
                            pending_def_paren = False

                        elif char == "(" and (
                            last_value.isidentifier()
                            or last_value in {")", "]"}
                        ):
                            context = "call"

                        else:
                            context = "other"

                        bracket_stack.append(context)

                        level = (len(bracket_stack) - 1) % 3 + 1

                        yield (
                            index + offset,
                            getattr(Punctuation, f"Bracket{level}"),
                            char,
                        )

                    elif char in ")]}":

                        level = (max(len(bracket_stack), 1) - 1) % 3 + 1

                        yield (
                            index + offset,
                            getattr(Punctuation, f"Bracket{level}"),
                            char,
                        )

                        if bracket_stack:
                            bracket_stack.pop()

                    else:
                        yield index + offset, token, char

                    last_value = char

                continue

            # ------------------------------------------
            # 4. Function definitions and parameters
            # ------------------------------------------

            in_signature = "signature" in bracket_stack

            if token in Name:

                # 함수 선언의 매개변수
                if in_signature and token is Name:

                    yield index, Name.Variable.Parameter, value
                    last_value = value
                    continue

                # 함수 호출의 키워드 인수
                in_call = "call" in bracket_stack

                if (
                    in_call
                    and token is Name
                    and re.match(
                        r"\s*=(?!=)",
                        text[index + len(value):]
                    )
                ):

                    yield index, Name.Variable.Parameter, value
                    last_value = value
                    continue

                # 예외 이름
                if (
                    value.endswith("Error")
                    or value.endswith("Exception")
                ):

                    yield index, Name.Exception, value
                    last_value = value
                    continue

                # print, sum 등 내장 함수
                if value == "print":

                    yield index, Name.Builtin, value
                    last_value = value
                    continue

            # ------------------------------------------
            # 5. Default token
            # ------------------------------------------

            yield index, token, value

            if value.strip():
                last_value = value


# ==================================================
# 2. Custom Pygments Style
# ==================================================

class VSCodeNotesStyle(Style):

    background_color = "#FFFFFF"
    default_style = ""

    styles = {

        # ------------------------------------------
        # 일반 코드
        # ------------------------------------------

        Token:                    "#000000",
        Text:                     "#000000",
        Name:                     "#000000",

        # ------------------------------------------
        # 예약어
        # ------------------------------------------

        Keyword:                  "#B87300",
        Keyword.Namespace:        "#B87300",

        # def, class / True, False
        Keyword.Declaration:      "#356B9A",
        Keyword.Constant:         "#356B9A",

        # ------------------------------------------
        # 함수와 변수
        # ------------------------------------------

        # 함수 선언 이름
        Name.Function:            "#85835A",

        # 데코레이터
        Name.Decorator:           "#85835A",

        # 내장 함수: 톤다운된 빨간색
        Name.Builtin:             "#B03A35",

        # 매개변수 및 키워드 인수
        Name.Variable.Parameter:  "#397B91",

        # 클래스와 예외
        Name.Class:               "#387C74",
        Name.Exception:           "#387C74",

        # ------------------------------------------
        # 문자열과 주석
        # ------------------------------------------

        String:                   "#397D45",
        Comment:                  "#607765",

        # ------------------------------------------
        # 숫자와 연산자
        # ------------------------------------------

        Number:                   "#000000",
        Operator:                 "#000000",

        # ------------------------------------------
        # 괄호
        # ------------------------------------------

        Punctuation:              "#000000",

        # 가장 바깥쪽 괄호: 어두운 노란색
        Punctuation.Bracket1:     "#A58736",

        # 두 번째 괄호: 청록색
        Punctuation.Bracket2:     "#438C84",

        # 세 번째 괄호: 붉은색
        Punctuation.Bracket3:     "#B65A55",
    }
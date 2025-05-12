from pyparsing import nestedExpr, ParserElement
import re

# 한글 수식을 Latex 수식으로 변환하는 프로그램
# 터미널에 수식을 입력하면 변환된 수식을 출력해줌


ParserElement.enablePackrat()

def parse_over_expression(text):
    if text.count('{') != text.count('}'):
        print(f"Skipping malformed input: {text}")
        return text

    brace_expr = nestedExpr('{', '}')
    parsed = brace_expr.parseString('{' + text + '}').asList()[0]

    def process(parsed_list):
        result = ''
        i = 0
        while i < len(parsed_list):
            item = parsed_list[i]
            if isinstance(item, list) and i + 1 < len(parsed_list) and parsed_list[i + 1] == 'over' and i + 2 < len(parsed_list):
                left = process(item)
                right = process(parsed_list[i + 2])
                result += f"\\frac{{{left}}}{{{right}}}"
                i += 3
            else:
                if isinstance(item, list):
                    result += '{' + process(item) + '}'
                else:
                    result += item
                i += 1
        return result

    return process(parsed)

def transform_equation(eq_str: str) -> str:
    # 0) 백틱(`) 제거
    eq_str = eq_str.replace("`", "")

    # 1) 앞뒤 따옴표(' 또는 ") 제거
    eq_str = eq_str.strip("'\"")

    # 2) \r, \n 등 개행문자 제거
    eq_str = eq_str.replace("\r\n", "").replace("\n", "").replace("\r", "")

    # 3) sqrt -> \sqrt, % -> \%
    eq_str = eq_str.replace("sqrt", r"\sqrt")
    eq_str = eq_str.replace("%", r"\%")

    # 5) prime -> '
    eq_str = eq_str.replace("prime", "'")

    # 6) 그리스 문자 처리
    greek_lower = [
        "alpha", "beta", "gamma", "delta", "epsilon", "zeta",
        "eta", "theta", "iota", "kappa", "lambda", "mu",
        "nu", "xi", "omicron", "pi", "rho", "sigma", "tau",
        "upsilon", "phi", "chi", "psi", "omega", "varepsilon"
    ]
    greek_upper = [
        "ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA",
        "ETA", "THETA", "IOTA", "KAPPA", "LAMBDA", "MU",
        "NU", "XI", "OMICRON", "PI", "RHO", "SIGMA", "TAU",
        "UPSILON", "PHI", "CHI", "PSI", "OMEGA"
    ]

    # (A) 대문자 그리스 문자 처리
    for letter in greek_upper:
        pattern = rf"\b{letter}(?=_|\^|\b)"
        replacement = rf"\\{letter.capitalize()} "
        eq_str = re.sub(pattern, replacement, eq_str)

    # (B) 소문자 그리스 문자 처리
    for letter in greek_lower:
        pattern = rf"\b{letter}(?=_|\^|\b)"
        replacement = rf"\\{letter} "
        eq_str = re.sub(pattern, replacement, eq_str)

    # 7) left / right -> \left / \right
    eq_str = re.sub(r"\bleft\b",  r"\\left ",  eq_str, flags=re.IGNORECASE)
    eq_str = re.sub(r"\bright\b", r"\\right ", eq_str, flags=re.IGNORECASE)

    # 8) leq / geq / times -> \leq / \geq / \times
    eq_str = re.sub(r"\bleq\b",   r"\\leq ",   eq_str, flags=re.IGNORECASE)
    eq_str = re.sub(r"\bgeq\b",   r"\\geq ",   eq_str, flags=re.IGNORECASE)
    eq_str = re.sub(r"\btimes\b", r"\\times ", eq_str, flags=re.IGNORECASE)

    # 모든공백제거
    eq_str = eq_str.replace(" ", "")
    
    # 4) { ... }over{ ... } -> \frac{...}{...}
    eq_str = parse_over_expression(eq_str)
    
    # 주요 LaTeX 명령어 뒤에 공백 강제 삽입
    eq_str = re.sub(r"(\\frac\{.*?\}\{.*?\})", r"\1 ", eq_str)

    # 단일 명령어 뒤에 공백
    commands_with_space = [
        # 기호들
        r"\\geq", r"\\leq", r"\\times", r"\\sqrt",
        r"\\left", r"\\right",

        # 소문자 그리스 문자
        r"\\alpha", r"\\beta", r"\\gamma", r"\\delta", r"\\epsilon", r"\\zeta",
        r"\\eta", r"\\theta", r"\\iota", r"\\kappa", r"\\lambda", r"\\mu",
        r"\\nu", r"\\xi", r"\\omicron", r"\\pi", r"\\rho", r"\\sigma",
        r"\\tau", r"\\upsilon", r"\\phi", r"\\chi", r"\\psi", r"\\omega",
        r"\\varepsilon",

        # 대문자 그리스 문자
        r"\\Alpha", r"\\Beta", r"\\Gamma", r"\\Delta", r"\\Epsilon", r"\\Zeta",
        r"\\Eta", r"\\Theta", r"\\Iota", r"\\Kappa", r"\\Lambda", r"\\Mu",
        r"\\Nu", r"\\Xi", r"\\Omicron", r"\\Pi", r"\\Rho", r"\\Sigma",
        r"\\Tau", r"\\Upsilon", r"\\Phi", r"\\Chi", r"\\Psi", r"\\Omega"
    ]

    for cmd in commands_with_space:
        eq_str = re.sub(rf"({cmd})(?!\s)", r"\1 ", eq_str)

    return eq_str

def main():
    print("수식 변환기 (종료하려면 'q' 또는 'quit' 입력)")
    print("=" * 50)
    
    while True:
        print("\n수식을 입력하세요:")
        user_input = input("> ").strip()
        
        if user_input.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
            
        if not user_input:
            continue
            
        try:
            converted = transform_equation(user_input)
            print("\n변환 결과:")
            print(f"${converted}$")
        except Exception as e:
            print(f"변환 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 
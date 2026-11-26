import ast
import operator
import tkinter as tk
from tkinter import messagebox

# العمليات الحسابية المسموح بها فقط
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression):
    """حساب التعبير بعد التحقق من أن مكوناته عمليات حسابية آمنة فقط."""
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            # حد بسيط لمنع الأسس الضخمة جداً
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("الأس كبير جداً")
            return BINARY_OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
            return UNARY_OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("عملية غير مدعومة")

    result = evaluate(tree)
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("الآلة الحاسبة | Calculator")
        self.root.geometry("360x510")
        self.root.resizable(False, False)
        self.root.configure(bg="#172033")

        self.expression = tk.StringVar(value="")
        self.result = tk.StringVar(value="0")

        title = tk.Label(
            root, text="CALCULATOR", font=("Arial", 17, "bold"),
            bg="#172033", fg="#e8eefc"
        )
        title.pack(pady=(18, 8))

        display = tk.Frame(root, bg="#24314b", padx=14, pady=12)
        display.pack(fill="x", padx=16, pady=(0, 14))

        tk.Label(
            display, textvariable=self.expression, anchor="e",
            font=("Arial", 14), bg="#24314b", fg="#aab8d3",
            height=2
        ).pack(fill="x")

        tk.Label(
            display, textvariable=self.result, anchor="e",
            font=("Arial", 28, "bold"), bg="#24314b", fg="white",
            height=1
        ).pack(fill="x")

        buttons = [
            ("C", "⌫", "(", ")"),
            ("7", "8", "9", "÷"),
            ("4", "5", "6", "×"),
            ("1", "2", "3", "-"),
            ("0", ".", "%", "+"),
            ("^", "=", "", ""),
        ]

        keypad = tk.Frame(root, bg="#172033")
        keypad.pack(expand=True, fill="both", padx=16, pady=(0, 16))

        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                if not label:
                    continue
                is_operator = label in {"÷", "×", "-", "+", "^", "%"}
                is_action = label in {"C", "⌫", "="}
                bg = "#3d5afe" if label == "=" else (
                    "#34435f" if is_action or is_operator else "#25334d"
                )
                fg = "white"
                button = tk.Button(
                    keypad, text=label, font=("Arial", 17, "bold"),
                    bg=bg, fg=fg, activebackground="#526b91",
                    activeforeground="white", relief="flat", bd=0,
                    command=lambda value=label: self.press(value)
                )
                button.grid(
                    row=r, column=c, sticky="nsew",
                    padx=4, pady=4, ipadx=4, ipady=8
                )

        for r in range(6):
            keypad.rowconfigure(r, weight=1)
        for c in range(4):
            keypad.columnconfigure(c, weight=1)

        self.root.bind("<Key>", self.handle_keyboard)

    def press(self, value):
        current = self.expression.get()

        if value == "C":
            self.expression.set("")
            self.result.set("0")
        elif value == "⌫":
            self.expression.set(current[:-1])
        elif value == "=":
            self.calculate()
        else:
            self.expression.set(current + value)

    def calculate(self):
        expression = self.expression.get().strip()
        if not expression:
            return
        try:
            answer = safe_calculate(expression)
            self.result.set(str(answer))
        except ZeroDivisionError:
            self.result.set("لا يمكن القسمة على صفر")
        except (SyntaxError, ValueError, OverflowError):
            self.result.set("خطأ في العملية")
        except Exception:
            self.result.set("خطأ")

    def handle_keyboard(self, event):
        key = event.char
        if key in "0123456789.+-()%":
            self.press(key)
        elif key == "*":
            self.press("×")
        elif key == "/":
            self.press("÷")
        elif key == "^":
            self.press("^")
        elif event.keysym == "Return":
            self.calculate()
        elif event.keysym == "BackSpace":
            self.press("⌫")
        elif event.keysym == "Escape":
            self.press("C")


if __name__ == "__main__":
    window = tk.Tk()
    app = Calculator(window)
    window.mainloop()

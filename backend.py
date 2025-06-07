import math

class CalculatorBackend:
    def __init__(self):
        self.expression = ""

    def input(self, char):
        if char == "π":
            self.expression += str(math.pi)
        elif char == "÷":
            self.expression += "/"
        elif char == "×":
            self.expression += "*"
        elif char == "√":
            # For square root, we'll need to handle this specially
            if self.expression:
                try:
                    result = math.sqrt(float(eval(self.expression)))
                    self.expression = str(result)
                except:
                    self.expression = "Error"
            else:
                self.expression = "√("
        elif char == "x²":
            # For square, we'll need to handle this specially
            if self.expression:
                try:
                    result = float(eval(self.expression)) ** 2
                    self.expression = str(result)
                except:
                    self.expression = "Error"
        else:
            self.expression += str(char)

    def clear(self):
        self.expression = ""

    def evaluate(self):
        try:
            # Replace mod with % for Python evaluation
            expr = self.expression.replace("mod", "%")
            result = str(eval(expr))
            self.expression = result  # To allow chaining like 2+2=4+3
            return result
        except:
            self.expression = ""
            return "Error"

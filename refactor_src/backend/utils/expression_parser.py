# /utils/expression_parser.py
from sympy import sympify, lambdify, symbols, SympifyError, diff
import numpy as np
def get_derivative(expr_str):
    """
    Tính đạo hàm của một biểu thức dạng chuỗi và trả về chuỗi biểu diễn đạo hàm.
    """
    try:
        x = symbols('x')
        expr = sympify(expr_str)
        derivative_expr = diff(expr, x)
        return str(derivative_expr)
    except (SympifyError, TypeError, SyntaxError):
        # Nếu có lỗi, trả về chuỗi rỗng để nơi gọi xử lý
        return ""
    
def parse_expression(expr_str):
    """
    Phân tích một chuỗi biểu thức thành các hàm số có thể gọi được.
    Trả về một dict chứa các hàm f, f' và f''.
    """
    try:
        x = symbols('x')
        expr = sympify(expr_str)
        
        # Tạo các hàm số có thể gọi
        f = lambdify(x, expr, 'numpy')
        f_prime = lambdify(x, expr.diff(x), 'numpy')
        f_double_prime = lambdify(x, expr.diff(x).diff(x), 'numpy')
        
        return {
            "success": True,
            "f": f,
            "f_prime": f_prime,
            "f_double_prime": f_double_prime,
            "expr": expr
        }
    except (SympifyError, TypeError, SyntaxError) as e:
        return {
            "success": False,
            "error": f"Biểu thức không hợp lệ: {str(e)}"
        }

def parse_phi_expression(expr_str):
    """
    Phân tích hàm lặp phi(x) cho phương pháp lặp đơn.
    """
    try:
        x = symbols('x')
        expr = sympify(expr_str)
        
        phi = lambdify(x, expr, 'numpy')
        phi_prime = lambdify(x, expr.diff(x), 'numpy')
        
        return {
            "success": True,
            "phi": phi,
            "phi_prime": phi_prime
        }
    except (SympifyError, TypeError, SyntaxError) as e:
        return {
            "success": False,
            "error": f"Hàm lặp φ(x) không hợp lệ: {str(e)}"
        }
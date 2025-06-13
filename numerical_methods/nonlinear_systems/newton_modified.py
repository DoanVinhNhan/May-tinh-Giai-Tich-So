# May-tinh-Giai-Tich-So/numerical_methods/nonlinear_systems/newton_modified.py

import numpy as np
import pandas as pd
from sympy import symbols, sympify, Matrix

def solve_newton_modified_system(n, expr_list, x0_list, stop_option, stop_value):
    """
    Giải hệ phương trình phi tuyến F(X) = 0 bằng phương pháp Newton cải tiến.
    
    Args:
        n (int): Số lượng phương trình.
        expr_list (list): Danh sách các chuỗi biểu thức cho F(X).
        x0_list (list): Vector lặp ban đầu X_0.
        stop_option (str): Điều kiện dừng.
        stop_value (float): Giá trị điều kiện dừng.

    Returns:
        dict: Kết quả tính toán.
    """
    try:
        # 1. Khởi tạo
        variables = symbols(f'x1:{n+1}')
        F = Matrix([sympify(expr) for expr in expr_list])
        X = Matrix(x0_list)
        X0 = Matrix(x0_list)

        # 2. Tính ma trận Jacobi và nghịch đảo của nó TẠI ĐIỂM X0
        J = F.jacobian(variables)
        J0_val = J.subs({variables[i]: X0[i] for i in range(n)}).evalf()
        
        if J0_val.det() == 0:
            return {"success": False, "error": "Ma trận Jacobi tại điểm ban đầu J(X₀) suy biến. Không thể tính J(X₀)⁻¹."}
        
        J0_inv = J0_val.inv()

        iterations_data = []
        
        # 3. Vòng lặp chính
        if stop_option == 'iterations':
            max_iter = int(stop_value)
            for k in range(max_iter):
                X_prev = X.copy()
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                
                # Công thức lặp Newton cải tiến
                X = X - J0_inv * F_val

                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                abs_err = float(max(abs(X - X_prev)))
                rel_err = abs_err / float(max(abs(X))) if float(max(abs(X))) != 0 else float('inf')
                step_info['absolute_error'] = abs_err
                step_info['relative_error'] = rel_err
                iterations_data.append(step_info)

        else: # Sai số
            tol = float(stop_value)
            k = 0
            check_prev = float('inf')
            while k < 200:
                X_prev = X.copy()
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()

                X = X - J0_inv * F_val

                abs_err = float(max(abs(X - X_prev)))
                rel_err = abs_err / float(max(abs(X))) if float(max(abs(X))) != 0 else float('inf')

                # Kiểm tra phân kỳ (sai số sau lớn hơn sai số trước)
                check = abs_err if stop_option == 'absolute_error' else rel_err
                if check > check_prev:
                    return {"success": False, "error": f"Dãy lặp phân kỳ tại bước {k+1} (sai số tăng)."}
                check_prev = check

                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                step_info['absolute_error'] = abs_err
                step_info['relative_error'] = rel_err
                iterations_data.append(step_info)

                if check < tol:
                    break
                
                k += 1
            if k == 200:
                 return {"success": False, "error": "Phương pháp không hội tụ sau 200 lần lặp."}

        # 4. Trả về kết quả
        return {
            "success": True,
            "solution": [float(val) for val in X],
            "iterations": len(iterations_data),
            "jacobian_matrix": str(J),
            "J0_inv_matrix": [[float(v) for v in row] for row in J0_inv.tolist()],
            "steps": iterations_data,
            "message": f"Hội tụ sau {len(iterations_data)} lần lặp."
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi: {str(e)}\n{traceback.format_exc()}"}
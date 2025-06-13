# May-tinh-Giai-Tich-So/numerical_methods/nonlinear_systems/newton.py

import numpy as np
import pandas as pd
from sympy import symbols, sympify, Matrix, latex

def solve_newton_system(n, expr_list, x0_list, stop_option, stop_value):
    """
    Giải hệ phương trình phi tuyến F(X) = 0 bằng phương pháp Newton.
    
    Args:
        n (int): Số lượng phương trình (và số ẩn).
        expr_list (list): Danh sách các chuỗi biểu thức cho f1, f2, ..., fn.
        x0_list (list): Danh sách các giá trị cho vector lặp ban đầu X_0.
        stop_option (str): Điều kiện dừng ('absolute_error', 'relative_error', 'iterations').
        stop_value (float): Giá trị cho điều kiện dừng (epsilon, delta, hoặc số lần lặp N).

    Returns:
        dict: Chứa kết quả, các bước lặp và thông tin chẩn đoán.
    """
    try:
        # 1. Khởi tạo biến và biểu thức SymPy
        variables = symbols(f'x1:{n+1}')
        F = Matrix([sympify(expr) for expr in expr_list])
        X = Matrix(x0_list)
        
        # 2. Tính ma trận Jacobi tượng trưng
        J = F.jacobian(variables)

        iterations_data = []
        
        # 3. Vòng lặp chính
        if stop_option == 'iterations':
            max_iter = int(stop_value)
            for k in range(max_iter):
                X_prev = X.copy()
                
                # Thế giá trị số vào F và J
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                J_val = J.subs({variables[i]: X[i] for i in range(n)}).evalf()

                if J_val.det() == 0:
                    return {"success": False, "error": f"Ma trận Jacobi suy biến tại bước lặp {k+1}. Không thể tiếp tục."}

                # Công thức lặp Newton
                X = X - J_val.inv() * F_val

                # Ghi lại dữ liệu bước lặp
                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                abs_err = float(max(abs(X - X_prev)))
                rel_err = abs_err / float(max(abs(X))) if float(max(abs(X))) != 0 else float('inf')
                step_info['absolute_error'] = abs_err
                step_info['relative_error'] = rel_err
                iterations_data.append(step_info)

        else: # Sai số tuyệt đối hoặc tương đối
            tol = float(stop_value)
            k = 0
            while k < 200: # Giới hạn tối đa 200 lần lặp để tránh treo
                X_prev = X.copy()

                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                J_val = J.subs({variables[i]: X[i] for i in range(n)}).evalf()

                if J_val.det() == 0:
                    return {"success": False, "error": f"Ma trận Jacobi suy biến tại bước lặp {k+1}."}

                X = X - J_val.inv() * F_val

                # Tính sai số
                abs_err = float(max(abs(X - X_prev)))
                rel_err = abs_err / float(max(abs(X))) if float(max(abs(X))) != 0 else float('inf')

                # Ghi lại dữ liệu
                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                step_info['absolute_error'] = abs_err
                step_info['relative_error'] = rel_err
                iterations_data.append(step_info)

                # Kiểm tra điều kiện dừng
                if stop_option == 'absolute_error' and abs_err < tol:
                    break
                if stop_option == 'relative_error' and rel_err < tol:
                    break
                
                k += 1
            if k == 200:
                 return {"success": False, "error": "Phương pháp không hội tụ sau 200 lần lặp."}
        try:
            J_latex = [[latex(elem) for elem in row] for row in J.tolist()]
        except Exception as e:
            print(f"Lỗi chuyển đổi Jacobi sang LaTeX: {e}")
        # 4. Trả về kết quả
        return {
            "success": True,
            "solution": [float(val) for val in X],
            "iterations": len(iterations_data),
            "jacobian_matrix_latex": J_latex,
            "steps": iterations_data,
            "message": f"Hội tụ sau {len(iterations_data)} lần lặp."
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi: {str(e)}\n{traceback.format_exc()}"}
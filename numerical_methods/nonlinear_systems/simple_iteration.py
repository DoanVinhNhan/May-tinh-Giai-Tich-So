# May-tinh-Giai-Tich-So/numerical_methods/nonlinear_systems/simple_iteration.py

import numpy as np
import pandas as pd
from sympy import symbols, sympify, Matrix, lambdify
from scipy.optimize import differential_evolution

def find_global_maximum_on_box(func, variables, bounds):
    """Tìm GTLN của hàm nhiều biến trên miền hộp bằng thuật toán di truyền."""
    objective_func = lambda x: -np.abs(func(*x))
    try:
        result = differential_evolution(objective_func, bounds, maxiter=200, popsize=15, tol=1e-4)
        return -result.fun if result.success else -np.inf
    except Exception:
        return -np.inf

def solve_simple_iteration_system(n, expr_list, x0_list, a0_list, b0_list, stop_option, stop_value):
    """
    Giải hệ phương trình phi tuyến X = phi(X) bằng phương pháp lặp đơn.
    """
    try:
        # 1. Khởi tạo
        variables = symbols(f'x1:{n+1}')
        phi = Matrix([sympify(expr) for expr in expr_list])
        X = Matrix(x0_list)
        bounds = list(zip(a0_list, b0_list))

        # 2. Kiểm tra điều kiện hội tụ (Ánh xạ co)
        J = phi.jacobian(variables)
        
        # Tạo ma trận chứa GTLN của từng đạo hàm riêng trên miền D
        J_max_vals = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                # Lambdify để tăng tốc độ tính toán
                func_to_optimize = lambdify(variables, J[i, j], 'numpy')
                max_val = find_global_maximum_on_box(func_to_optimize, variables, bounds)
                if max_val == -np.inf:
                    return {"success": False, "error": f"Không thể tìm GTLN cho ∂φ_{i+1}/∂x_{j+1}. Có thể biểu thức quá phức tạp."}
                J_max_vals[i, j] = max_val
        
        # Tính hệ số co K theo chuẩn hàng và chuẩn cột
        max_row_sum = np.max(np.sum(np.abs(J_max_vals), axis=1)) # Chuẩn vô cùng
        max_col_sum = np.max(np.sum(np.abs(J_max_vals), axis=0)) # Chuẩn 1
        K = min(max_row_sum, max_col_sum)

        if K >= 1:
            return {"success": False, "error": f"Điều kiện hội tụ không thỏa mãn. Hệ số co K ≈ {K:.4f} >= 1."}

        # 3. Vòng lặp
        iterations_data = []
        if stop_option == 'iterations':
            max_iter = int(stop_value)
            for k in range(max_iter):
                X_prev = X.copy()
                X = phi.subs({variables[i]: X[i] for i in range(n)}).evalf()

                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                abs_err = float(max(abs(X - X_prev)))
                rel_err = abs_err / float(max(abs(X))) if float(max(abs(X))) != 0 else float('inf')
                step_info['absolute_error'] = abs_err
                step_info['relative_error'] = rel_err
                iterations_data.append(step_info)
        else:
            tol = float(stop_value)
            # Tính sai số tiên nghiệm dựa trên sai số hậu nghiệm
            priori_tol = tol * (1 - K) / K if K != 0 else tol

            k = 0
            while k < 200:
                X_prev = X.copy()
                X = phi.subs({variables[i]: X[i] for i in range(n)}).evalf()

                abs_err = float(max(abs(X - X_prev)))
                rel_err = abs_err / float(max(abs(X))) if float(max(abs(X))) != 0 else float('inf')
                
                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                step_info['absolute_error'] = abs_err
                step_info['relative_error'] = rel_err
                iterations_data.append(step_info)

                check_val = abs_err if stop_option == 'absolute_error' else rel_err
                if check_val < priori_tol:
                    break
                
                k += 1
            if k == 200:
                 return {"success": False, "error": "Phương pháp không hội tụ sau 200 lần lặp."}

        # 4. Trả về kết quả
        return {
            "success": True,
            "solution": [float(val) for val in X],
            "iterations": len(iterations_data),
            "jacobian_phi": str(J),
            "contraction_factor_K": K,
            "a_priori_error_abs": priori_tol if stop_option == 'absolute_error' else None,
            "a_priori_error_rel": priori_tol if stop_option == 'relative_error' else None,
            "steps": iterations_data,
            "message": f"Hội tụ sau {len(iterations_data)} lần lặp."
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi: {str(e)}\n{traceback.format_exc()}"}
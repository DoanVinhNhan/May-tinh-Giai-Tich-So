import numpy as np
from sympy import symbols, sympify, Matrix

def solve_newton_modified_system(n, expr_list, x0_list, stop_option, stop_value, norm_choice):
    """
    Giải hệ phương trình phi tuyến F(X) = 0 bằng phương pháp Newton cải tiến.
    
    Args:
        (Các tham số tương tự như PP Newton chuẩn)
        norm_choice (str): Lựa chọn chuẩn tính sai số ('1' hoặc 'infinity').

    Returns:
        dict: Kết quả tính toán.
    """
    try:
        variables = symbols(f'x1:{n+1}')
        F = Matrix([sympify(expr) for expr in expr_list])
        X = Matrix(x0_list)
        X0 = Matrix(x0_list)
        J = F.jacobian(variables)
        J0_val = J.subs({variables[i]: X0[i] for i in range(n)}).evalf()
        
        if J0_val.det() == 0:
            return {"success": False, "error": "Ma trận Jacobi tại điểm ban đầu J(X₀) suy biến."}
        
        J0_inv = J0_val.inv()
        iterations_data = []

        if stop_option == 'iterations':
            max_iter = int(stop_value)
            for k in range(max_iter):
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                X = X - J0_inv * F_val

                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                iterations_data.append(step_info)
        else:
            tol = float(stop_value)
            for k in range(200):
                X_prev = X.copy()
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                X = X - J0_inv * F_val

                # Tính sai số dựa trên chuẩn được chọn
                diff_vec_abs = np.abs(np.array(X.tolist(), dtype=float) - np.array(X_prev.tolist(), dtype=float)).flatten()
                current_vec_abs = np.abs(np.array(X.tolist(), dtype=float)).flatten()
                
                if norm_choice == '1':
                    abs_err = float(np.sum(diff_vec_abs))
                    norm_X = float(np.sum(current_vec_abs))
                else: # Mặc định là chuẩn vô cùng
                    abs_err = float(np.max(diff_vec_abs))
                    norm_X = float(np.max(current_vec_abs))

                rel_err = abs_err / norm_X if norm_X > 1e-12 else float('inf')

                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                step_info['error'] = abs_err if stop_option == 'absolute_error' else rel_err
                iterations_data.append(step_info)

                if (stop_option == 'absolute_error' and abs_err < tol) or \
                   (stop_option == 'relative_error' and rel_err < tol):
                    break
            else:
                 return {"success": False, "error": "Phương pháp không hội tụ sau 200 lần lặp."}

        return {
            "success": True,
            "solution": [float(val) for val in X],
            "iterations": len(iterations_data),
            "J0_inv_matrix": [[float(v) for v in row] for row in J0_inv.tolist()],
            "steps": iterations_data,
            "message": f"Hội tụ sau {len(iterations_data)} lần lặp."
        }
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi: {str(e)}\n{traceback.format_exc()}"}

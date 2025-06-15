import numpy as np
from sympy import symbols, sympify, Matrix, latex

def solve_newton_system(n, expr_list, x0_list, stop_option, stop_value, norm_choice):
    """
    Giải hệ phương trình phi tuyến F(X) = 0 bằng phương pháp Newton.
    
    Args:
        n (int): Số lượng phương trình (và số ẩn).
        expr_list (list): Danh sách các chuỗi biểu thức cho f1, f2, ..., fn.
        x0_list (list): Danh sách các giá trị cho vector lặp ban đầu X_0.
        stop_option (str): Điều kiện dừng ('absolute_error', 'relative_error', 'iterations').
        stop_value (float): Giá trị cho điều kiện dừng (epsilon, delta, hoặc số lần lặp N).
        norm_choice (str): Lựa chọn chuẩn tính sai số ('1' hoặc 'infinity').

    Returns:
        dict: Chứa kết quả, các bước lặp và thông tin chẩn đoán.
    """
    try:
        variables = symbols(f'x1:{n+1}')
        F = Matrix([sympify(expr) for expr in expr_list])
        X = Matrix(x0_list)
        J = F.jacobian(variables)
        iterations_data = []

        # Vòng lặp chính
        if stop_option == 'iterations':
            max_iter = int(stop_value)
            for k in range(max_iter):
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                J_val = J.subs({variables[i]: X[i] for i in range(n)}).evalf()
                if J_val.det() == 0:
                    return {"success": False, "error": f"Ma trận Jacobi suy biến tại bước lặp {k+1}."}
                
                X = X - J_val.inv() * F_val
                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                iterations_data.append(step_info)
        else:
            tol = float(stop_value)
            for k in range(200): # Giới hạn tối đa 200 lần lặp
                X_prev = X.copy()
                F_val = F.subs({variables[i]: X[i] for i in range(n)}).evalf()
                J_val = J.subs({variables[i]: X[i] for i in range(n)}).evalf()

                if J_val.det() == 0:
                    return {"success": False, "error": f"Ma trận Jacobi suy biến tại bước lặp {k+1}."}

                X = X - J_val.inv() * F_val

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
        
        try:
            J_latex = [[latex(elem) for elem in row] for row in J.tolist()]
        except Exception:
            J_latex = [[str(elem) for elem in row] for row in J.tolist()]
            
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

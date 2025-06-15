import numpy as np
from sympy import symbols, sympify, Matrix, lambdify
from scipy.optimize import differential_evolution

def find_global_maximum_on_box(func, variables, bounds):
    """Tìm GTLN của hàm nhiều biến trên miền hộp bằng thuật toán di truyền."""
    objective_func = lambda x: -np.abs(func(*x))
    try:
        # Tăng maxiter để có kết quả ổn định hơn
        result = differential_evolution(objective_func, bounds, maxiter=300, popsize=20, tol=1e-5, recombination=0.7)
        return -result.fun if result.success else -np.inf
    except Exception:
        return -np.inf

def solve_simple_iteration_system(n, expr_list, x0_list, a0_list, b0_list, stop_option, stop_value):
    """
    Giải hệ phương trình phi tuyến X = phi(X) bằng phương pháp lặp đơn.
    """
    try:
        variables = symbols(f'x1:{n+1}')
        phi = Matrix([sympify(expr) for expr in expr_list])
        X = Matrix(x0_list)
        bounds = list(zip(a0_list, b0_list))
        J = phi.jacobian(variables)

        # Tính ma trận GTLN của các đạo hàm riêng
        J_max_vals = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                func_to_optimize = lambdify(variables, J[i, j], 'numpy')
                max_val = find_global_maximum_on_box(func_to_optimize, variables, bounds)
                if max_val == -np.inf:
                    return {"success": False, "error": f"Không thể tìm GTLN cho ∂φ_{i+1}/∂x_{j+1}."}
                J_max_vals[i, j] = max_val
        
        # Xác định hệ số co K và chuẩn tương ứng
        max_row_sum = np.max(np.sum(np.abs(J_max_vals), axis=1))
        max_col_sum = np.max(np.sum(np.abs(J_max_vals), axis=0))
        
        if max_row_sum < max_col_sum:
            K = max_row_sum
            norm_to_use = 'infinity'
        else:
            K = max_col_sum
            norm_to_use = '1'

        if K >= 1:
            return {"success": False, "error": f"Điều kiện hội tụ không thỏa mãn. Hệ số co K ≈ {K:.4f} (tính theo chuẩn {norm_to_use}) >= 1."}

        iterations_data = []
        if stop_option == 'iterations':
            max_iter = int(stop_value)
            for k in range(max_iter):
                X = phi.subs({variables[i]: X[i] for i in range(n)}).evalf()
                step_info = {f"x{i+1}": float(X[i]) for i in range(n)}
                step_info['k'] = k + 1
                iterations_data.append(step_info)
        else:
            tol = float(stop_value)
            priori_tol = tol * (1 - K) / K if K > 1e-12 else tol

            for k in range(200):
                X_prev = X.copy()
                X = phi.subs({variables[i]: X[i] for i in range(n)}).evalf()
                
                current_vec = np.array(X.tolist(), dtype=float).flatten()
                prev_vec = np.array(X_prev.tolist(), dtype=float).flatten()
                diff_vec_abs = np.abs(current_vec - prev_vec)

                # Tính sai số hậu nghiệm theo chuẩn tương ứng
                if norm_to_use == '1':
                    abs_err = np.sum(diff_vec_abs)
                    norm_X = np.sum(np.abs(current_vec))
                else:
                    abs_err = np.max(diff_vec_abs)
                    norm_X = np.max(np.abs(current_vec))
                
                rel_err = abs_err / norm_X if norm_X > 1e-12 else float('inf')

                step_info = {f"x{i+1}": val for i, val in enumerate(current_vec)}
                step_info['k'] = k + 1
                step_info['error'] = abs_err if stop_option == 'absolute_error' else rel_err
                iterations_data.append(step_info)
                
                # Điều kiện dừng dựa trên sai số tiên nghiệm
                check_val = abs_err if stop_option == 'absolute_error' else rel_err
                if check_val < priori_tol:
                    break
            else:
                 return {"success": False, "error": "Phương pháp không hội tụ sau 200 lần lặp."}

        return {
            "success": True,
            "solution": [float(val) for val in X],
            "iterations": len(iterations_data),
            "steps": iterations_data,
            "message": f"Hội tụ sau {len(iterations_data)} lần lặp.",
            "J_max_vals": J_max_vals.tolist(),
            "max_row_sum": float(max_row_sum),
            "max_col_sum": float(max_col_sum),
            "contraction_factor_K": float(K),
            "norm_used_for_K": norm_to_use
        }
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi: {str(e)}\n{traceback.format_exc()}"}

# /numerical_methods/root_finding/newton.py
import numpy as np
from scipy.optimize import minimize_scalar
from utils.expression_parser import get_derivative, parse_expression

def solve_newton(f_expr, a, b, mode, value, stop_condition, max_iter=100):
    try:
        # 1. Phân tích biểu thức f, f', f''
        parsed_f = parse_expression(f_expr)
        if not parsed_f.get('success'): return parsed_f
        f = parsed_f.get('f')
        Df = parsed_f.get('f_prime')
        D2f = parsed_f.get('f_double_prime')

        # 2. Kiểm tra điều kiện hội tụ (f', f'' không đổi dấu)
        try:
            x_check = np.linspace(a, b, 20)
            fp_signs = np.sign([Df(x) for x in x_check])
            fpp_signs = np.sign([D2f(x) for x in x_check])
            if np.any(fp_signs == 0) or np.any(fpp_signs == 0):
                return {"success": False, "error": "Đạo hàm f'(x) hoặc f''(x) bằng 0 bên trong khoảng."}
            if len(set(fp_signs)) > 1 or len(set(fpp_signs)) > 1:
                return {"success": False, "error": "Điều kiện hội tụ: f'(x) và f''(x) phải không đổi dấu trên [a, b]."}
        except Exception as e:
            return {"success": False, "error": f"Không thể kiểm tra đạo hàm trên khoảng [a, b]. Lỗi: {e}"}

        # 3. Tính các hằng số m1, M2 (trong code là M1)
        try:
            x_range = np.linspace(a, b, 1000)
            f_prime_values = np.abs([Df(x) for x in x_range])
            f_double_prime_values = np.abs([D2f(x) for x in x_range])
            m1 = np.min(f_prime_values)
            M2 = np.max(f_double_prime_values) # M2 là max|f''(x)|
            if m1 < 1e-12:
                return {"success": False, "error": "Đạo hàm f'(x) có giá trị gần bằng 0 trong khoảng, không đảm bảo công thức sai số."}
        except Exception as e:
            return {"success": False, "error": f"Không thể tính m1, M2 trên khoảng [a, b]. Lỗi: {e}"}

        # 4. Chọn điểm bắt đầu x0 (điểm Fourier)
        if f(a) * D2f(a) > 0:
            x0 = a
        elif f(b) * D2f(b) > 0:
            x0 = b
        else: # Nếu không có điểm Fourier ở biên, chọn điểm giữa
            x0 = (a + b) / 2
            if f(x0) * D2f(x0) <= 0: # Cảnh báo nếu điểm giữa cũng không thỏa
                 return {"success": False, "error": "Không tìm thấy điểm Fourier thỏa mãn f(x)f''(x) > 0. Hội tụ không được đảm bảo."}

        steps = []
        x_k = x0
        iterations_to_run = int(value) if mode == 'iterations' else max_iter
        
        for k in range(iterations_to_run):
            f_xk = f(x_k)
            df_xk = Df(x_k)
            
            if abs(df_xk) < 1e-12:
                return {"success": False, "error": f"Đạo hàm bằng 0 tại x = {x_k}. Không thể tiếp tục.", "steps":steps}

            x_k_plus_1 = x_k - f_xk / df_xk
            
            # Kiểm tra điều kiện dừng
            done = False
            tol = float(value)

            step_info = {'k': k, 'x_k': x_k, 'f(x_k)': f_xk, "f'(x_k)": df_xk}

            if mode == 'iterations':
                if k + 1 >= tol:
                    done = True
            elif mode == 'absolute_error':
                if stop_condition == 'f_xn':
                    error = np.abs(f(x_k_plus_1)) / m1 # |f(x_n+1)|/m1
                    step_info['|f(x_{n+1})|/m1'] = error
                    if error < tol: done = True
                else: # xn_xn-1
                    error = (M2 / (2 * m1)) * np.abs(x_k_plus_1 - x_k)**2
                    step_info['(M2/2m1)|x_{n+1}-x_n|^2'] = error
                    if error < tol: done = True
            elif mode == 'relative_error':
                if abs(x_k_plus_1) < 1e-12: # Tránh chia cho 0
                    done = False
                elif stop_condition == 'f_xn':
                    error = np.abs(f(x_k_plus_1)) / (m1 * np.abs(x_k_plus_1))
                    step_info['|f(x_{n+1})|/(m1|x_{n+1}|)'] = error
                    if error < tol: done = True
                else: # xn_xn-1
                    error = (M2 / (2 * m1)) * (np.abs(x_k_plus_1 - x_k)**2) / np.abs(x_k_plus_1)
                    step_info['(M2/2m1)|x_{n+1}-x_n|^2/|x_{n+1}|'] = error
                    if error < tol: done = True
            
            steps.append(step_info)
            
            x_k = x_k_plus_1

            if not (a <= x_k <= b):
                return {"success": False, "error": f"Điểm lặp x_{k+1} = {x_k:.6f} nằm ngoài khoảng [{a}, {b}].", "steps": steps}
            
            if done:
                break
        
        if mode != 'iterations' and not done:
            return {"success": False, "error": f"Phương pháp không hội tụ sau {iterations_to_run} lần lặp.", "steps": steps}

        return {
            "success": True, "solution": x_k, "iterations": k + 1, "steps": steps,
            "m1": m1, "M2": M2
        }
        
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi trong quá trình thực thi: {str(e)}\n{traceback.format_exc()}"}
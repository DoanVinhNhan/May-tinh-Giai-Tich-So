import numpy as np
from scipy.optimize import minimize_scalar
from utils.expression_parser import get_derivative, parse_expression

def solve_newton(f_expr, a, b, tol=1e-6, max_iter=100, mode='absolute_error', stop_condition='f_xn'):
    try:
        # === BẮT ĐẦU SỬA LỖI ===
        # Xử lý f(x)
        parsed_f = parse_expression(f_expr)
        if not parsed_f.get('success'):
            return {"success": False, "error": f"Lỗi cú pháp trong hàm f(x): {parsed_f.get('error')}"}
        f = parsed_f.get('f')  # Lấy đúng hàm từ dictionary

        # Xử lý f'(x)
        Df_expr = get_derivative(f_expr)
        parsed_Df = parse_expression(Df_expr)
        if not parsed_Df.get('success'):
            return {"success": False, "error": f"Lỗi cú pháp trong hàm f'(x): {parsed_Df.get('error')}"}
        Df = parsed_Df.get('f') # Lấy đúng hàm từ dictionary

        # Xử lý f''(x)
        D2f_expr = get_derivative(Df_expr)
        parsed_D2f = parse_expression(D2f_expr)
        if not parsed_D2f.get('success'):
            return {"success": False, "error": f"Lỗi cú pháp trong hàm f''(x): {parsed_D2f.get('error')}"}
        D2f = parsed_D2f.get('f') # Lấy đúng hàm từ dictionary
        # === KẾT THÚC SỬA LỖI ===

        # === START: TÍNH m1 VÀ M1 === (Phần này giữ nguyên)
        res_m1 = minimize_scalar(lambda x: np.abs(Df(x)), bounds=(a, b), method='bounded')
        m1 = res_m1.fun

        res_M1 = minimize_scalar(lambda x: -np.abs(D2f(x)), bounds=(a, b), method='bounded')
        M1 = -res_M1.fun
        # === END: TÍNH m1 VÀ M1 ===

        # Phần còn lại của hàm giữ nguyên vì f, Df, D2f giờ đã là các hàm tính toán đúng
        if f(a) * D2f(a) > 0:
            x0 = a
        elif f(b) * D2f(b) > 0:
            x0 = b
        else:
            x0 = (a + b) / 2

        steps = []
        x_k = x0
        
        # Kiểm tra điều kiện hội tụ tại nhiều điểm trên [a, b]
        N_check = 20
        x_check = np.linspace(a, b, N_check)
        h = 1e-6
        fp_signs = []
        fpp_signs = []
        for x in x_check:
            try:
                fp = Df(x) if Df else (f(x + h) - f(x - h)) / (2 * h)
                fpp = D2f(x) if D2f else (f(x + h) - 2*f(x) + f(x - h)) / (h**2)
                fp_signs.append(np.sign(fp))
                fpp_signs.append(np.sign(fpp))
            except Exception:
                fp_signs.append(0)
                fpp_signs.append(0)
        # Loại bỏ các điểm đạo hàm gần 0
        fp_signs = [s for s in fp_signs if abs(s) > 1e-8]
        fpp_signs = [s for s in fpp_signs if abs(s) > 1e-8]
        monotonic_fp = all(s > 0 for s in fp_signs) or all(s < 0 for s in fp_signs)
        monotonic_fpp = all(s > 0 for s in fpp_signs) or all(s < 0 for s in fpp_signs)
        monotonic_warning = None
        if not monotonic_fp or not monotonic_fpp:
            monotonic_warning = f"Cảnh báo: f'(x) hoặc f''(x) có thể đổi dấu trên [{a}, {b}]. Phương pháp Newton chỉ đảm bảo hội tụ nếu f'(x), f''(x) liên tục và không đổi dấu."

        # Kiểm tra điều kiện hội tụ tại hai đầu mút
        if Df(a) * Df(b) <= 0 or D2f(a) * D2f(b) <= 0:
            return {"success": False, "error": "Điều kiện hội tụ f'(x) và f''(x) không đổi dấu trên [a, b] không thỏa mãn."}

        for k in range(max_iter):
            f_xk = f(x_k)
            df_xk = Df(x_k)
            
            if abs(df_xk) < 1e-12:
                return {"success": False, "error": f"Đạo hàm bằng 0 tại x = {x_k}. Không thể tiếp tục."}

            x_k_plus_1 = x_k - f_xk / df_xk
            
            error = abs(x_k_plus_1 - x_k)
            if mode == 'relative_error' and abs(x_k_plus_1) > 1e-12:
                error = error / abs(x_k_plus_1)

            steps.append({
                'k': k, 'x_k': x_k, 'f_xk': f_xk,
                'df_xk': df_xk, 'x_k+1': x_k_plus_1, 'error': error
            })
            
            stop_check_value = abs(f(x_k_plus_1)) if stop_condition == 'f_xn' else abs(x_k_plus_1 - x_k)

            if stop_check_value < tol:
                return {
                    "success": True, 
                    "solution": x_k_plus_1, 
                    "iterations": k + 1, 
                    "steps": steps,
                    "m1": m1,
                    "M1": M1,
                    "warning": monotonic_warning
                }
            
            x_k = x_k_plus_1
            
            if not (a <= x_k <= b):
                return {"success": False, "error": f"Điểm lặp x_{k+1} = {x_k} nằm ngoài khoảng [{a}, {b}]."}

        return {"success": False, "error": "Phương pháp không hội tụ sau số lần lặp tối đa."}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Lỗi trong quá trình thực thi: {str(e)}"}
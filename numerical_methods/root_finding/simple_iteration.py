# /numerical_methods/root_finding/simple_iteration.py

import numpy as np
from utils.expression_parser import get_derivative, parse_expression

def solve_simple_iteration(phi_expr, a, b, x0, mode, value, max_iter=200):
    """
    Giải phương trình x = phi(x) bằng phương pháp lặp đơn.
    Đã sửa lỗi logic điều kiện dừng và số lần lặp.
    """
    try:
        # Chuyển đổi chuỗi biểu thức thành hàm tính toán
        parsed_phi = parse_expression(phi_expr)
        if not parsed_phi.get('success'):
            return parsed_phi
            
        phi = parsed_phi.get('f') # Sử dụng chung parse_expression
        Dphi = parsed_phi.get('f_prime')

        # Kiểm tra điều kiện cách ly nghiệm f(x) = phi(x) - x
        f = lambda x: phi(x) - x
        fa = f(a)
        fb = f(b)
        if fa * fb >= 0:
            return {'success': False, 'error': f'Khoảng [{a}, {b}] không phải là khoảng cách ly nghiệm vì f(a)={fa:.4f} và f(b)={fb:.4f} không trái dấu.'}

        # Kiểm tra điều kiện hội tụ q = max|phi'(x)|
        q = -1
        try:
            # Kiểm tra q = max|phi'(x)| trên [a,b]
            test_points = np.linspace(a, b, 200)
            q_vals = np.abs([Dphi(p) for p in test_points])
            q = np.max(q_vals)
            if q >= 1:
                return {"success": False, "error": f"Điều kiện hội tụ không thỏa mãn. Hệ số co q ≈ {q:.4f} >= 1."}
        except Exception as e:
            return {"success": False, "error": f"Không thể tính đạo hàm của hàm lặp φ'(x) để xét điều kiện hội tụ. Lỗi: {e}"}

        steps = []
        x_k = x0
        
        # Xác định số lần lặp
        iterations_to_run = int(value) if mode == 'iterations' else max_iter
        
        for k in range(iterations_to_run):
            x_k_plus_1 = phi(x_k)
            
            # Tính các loại sai số để ghi nhận
            abs_diff = np.abs(x_k_plus_1 - x_k)
            
            # Công thức sai số tiên nghiệm
            abs_error_formula = (q / (1 - q)) * abs_diff if (1-q) != 0 else float('inf')
            rel_error_formula = abs_error_formula / np.abs(x_k_plus_1) if np.abs(x_k_plus_1) > 1e-12 else float('inf')
            
            # Ghi lại bước lặp
            step_info = {
                'k': k,
                'x_k': x_k,
                'phi(x_k)': x_k_plus_1,
                '|x_k+1 - x_k|': abs_diff
            }
            if mode == 'absolute_error':
                step_info['error'] = abs_error_formula
            elif mode == 'relative_error':
                 step_info['error'] = rel_error_formula
            
            steps.append(step_info)
            
            # Kiểm tra điều kiện dừng (chỉ khi không phải mode lặp)
            done = False
            if mode == 'absolute_error':
                if abs_error_formula < float(value):
                    done = True
            elif mode == 'relative_error':
                if rel_error_formula < float(value):
                    done = True
            
            # Cập nhật cho vòng lặp tiếp theo
            x_k = x_k_plus_1
            
            if not (a <= x_k <= b):
                return {"success": False, "error": f"Điểm lặp x_{k+1} = {x_k:.6f} nằm ngoài khoảng [{a}, {b}].", "steps": steps}
            
            if done:
                break
        
        if mode != 'iterations' and not done:
             return {"success": False, "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp.", "steps": steps}

        return {"success": True, "solution": x_k, "iterations": len(steps), "steps": steps, "q": q}

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi trong quá trình thực thi: {str(e)}\n{traceback.format_exc()}"}
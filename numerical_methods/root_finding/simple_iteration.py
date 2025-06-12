import numpy as np
from utils.expression_parser import get_derivative, parse_expression

def solve_simple_iteration(phi_expr, a, b, x0, tol=1e-6, max_iter=100, mode='absolute_error'):
    try:
        phi = parse_expression(phi_expr)
        
        # Kiểm tra điều kiện cách ly nghiệm
        fa = phi(a) - a
        fb = phi(b) - b
        if fa * fb >= 0:
            return {'success': False, 'error': f'Khoảng [{a}, {b}] không phải là khoảng cách ly nghiệm vì f(a)={fa:.4f} và f(b)={fb:.4f} không trái dấu.'}

        # Kiểm tra điều kiện hội tụ ban đầu
        try:
            Dphi_expr = get_derivative(phi_expr)
            Dphi = parse_expression(Dphi_expr)
            # Kiểm tra q = max|g'(x)| trên [a,b]
            test_points = np.linspace(a, b, 100)
            q = np.max(np.abs([Dphi(p) for p in test_points]))
            if q >= 1:
                return {"success": False, "error": f"Điều kiện hội tụ không thỏa mãn. |φ'(x)| = q ≈ {q:.4f} >= 1."}
        except Exception:
            # Bỏ qua nếu không tính được đạo hàm, sẽ kiểm tra trong vòng lặp
            pass

        steps = []
        x_k = x0 # Gán x0 ban đầu
        
        for k in range(max_iter):
            x_k_plus_1 = phi(x_k)
            
            error = abs(x_k_plus_1 - x_k)
            if mode == 'relative_error' and abs(x_k_plus_1) > 1e-12:
                error = error / abs(x_k_plus_1)
            
            # Ghi lại bước lặp
            steps.append({
                'k': k,
                'x_k': x_k,
                'phi(x_k)': x_k_plus_1, # phi(x_k) chính là x_{k+1}
                'error': error
            })
            
            if error < tol:
                return {"success": True, "solution": x_k_plus_1, "iterations": k + 1, "steps": steps}
            
            # Cập nhật cho vòng lặp tiếp theo
            x_k = x_k_plus_1
            
            if not (a <= x_k <= b):
                return {"success": False, "error": f"Điểm lặp x_{k+1} = {x_k} nằm ngoài khoảng [{a}, {b}]."}

        return {"success": False, "error": "Phương pháp không hội tụ sau số lần lặp tối đa."}

    except Exception as e:
        return {"success": False, "error": f"Lỗi trong quá trình thực thi: {str(e)}"}
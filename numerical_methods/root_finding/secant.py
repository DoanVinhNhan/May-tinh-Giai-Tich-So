# /numerical_methods/root_finding/secant.py
import numpy as np

def solve_secant(parsed_expr, a, b, mode, value, stop_condition):
    """
    Giải phương trình f(x) = 0 bằng phương pháp Dây cung (Secant).
    """
    f = parsed_expr['f']
    f_prime = parsed_expr['f_prime']
    f_double_prime = parsed_expr['f_double_prime']
    steps = []

    # 1. Kiểm tra điều kiện hội tụ
    if f(a) * f(b) >= 0:
        return {"success": False, "error": "Điều kiện f(a) * f(b) < 0 không thỏa mãn."}
    if f_prime(a) * f_prime(b) <= 0 or f_double_prime(a) * f_double_prime(b) <= 0:
        return {"success": False, "error": "Điều kiện hội tụ f'(x) và f''(x) không đổi dấu trên [a, b] không thỏa mãn."}
        
    # 2. Chọn điểm cố định d và điểm lặp x0
    if f(a) * f_double_prime(a) > 0:
        d = a  # Điểm Fourier
        x0 = b
    elif f(b) * f_double_prime(b) > 0:
        d = b  # Điểm Fourier
        x0 = a
    else:
        return {"success": False, "error": "Không tìm thấy điểm Fourier để làm điểm cố định."}

    # 3. Tính hằng số
    m1 = min(np.abs(f_prime(a)), np.abs(f_prime(b)))
    M1 = max(np.abs(f_prime(a)), np.abs(f_prime(b)))
    if m1 == 0:
        return {"success": False, "error": "Đạo hàm f'(x) bằng 0 tại biên."}

    x_curr = x0
    
    for i in range(200):
        f_curr = f(x_curr)
        f_d = f(d)
        
        step_info = {"n": i, "x_n": x_curr, "f(x_n)": f_curr}

        # Kiểm tra điều kiện dừng
        done = False
        if mode == 'iterations' and i >= int(value):
            done = True
        elif mode == 'absolute_error':
            if stop_condition == 'f_xn':
                error = np.abs(f_curr) / m1
                step_info['|f(x_n)|/m1'] = error
                if error <= value: done = True
            else: # xn_xn-1
                # Với i=0, x_prev là d. Cho các lần sau, x_prev chính là d.
                x_prev_for_error = d if i == 0 else steps[-1]['x_n']
                error = ((M1 - m1) / m1) * np.abs(x_curr - x_prev_for_error)
                step_info['(M1-m1)|x_n-d|/m1'] = error
                if error <= value: done = True
        
        steps.append(step_info)
        if done:
            break

        # Cập nhật x_curr
        denominator = f_curr - f_d
        if denominator == 0:
            return {"success": False, "error": "Mẫu số f(x_n) - f(d) bằng 0."}
        
        x_curr = x_curr - (f_curr * (x_curr - d)) / denominator
    else:
        return {"success": False, "error": "Không hội tụ sau 200 lần lặp."}

    return {"success": True, "solution": x_curr, "steps": steps, "iterations": len(steps)}
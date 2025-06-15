# /numerical_methods/root_finding/secant.py
import numpy as np

def solve_secant(parsed_expr, a, b, mode, value, stop_condition):
    """
    Giải phương trình f(x) = 0 bằng phương pháp Dây cung (Secant).
    Đã sửa lỗi logic điều kiện dừng.
    """
    f = parsed_expr['f']
    f_prime = parsed_expr['f_prime']
    f_double_prime = parsed_expr['f_double_prime']
    steps = []

    # 1. Kiểm tra điều kiện f(a)f(b) < 0
    if f(a) * f(b) >= 0:
        return {"success": False, "error": "Điều kiện f(a) * f(b) < 0 không thỏa mãn."}

    # 2. Kiểm tra tính đơn điệu của f' và f''
    try:
        x_check = np.linspace(a, b, 20)
        fp_signs = np.sign([f_prime(x) for x in x_check])
        fpp_signs = np.sign([f_double_prime(x) for x in x_check])
        if np.any(fp_signs == 0) or np.any(fpp_signs == 0):
             return {"success": False, "error": "Đạo hàm f'(x) hoặc f''(x) bằng 0 bên trong khoảng."}
        if len(set(fp_signs)) > 1 or len(set(fpp_signs)) > 1:
            return {"success": False, "error": "Điều kiện hội tụ f'(x) và f''(x) không đổi dấu trên [a, b] không thỏa mãn."}
    except Exception as e:
        return {"success": False, "error": f"Không thể kiểm tra đạo hàm trên khoảng [a, b]. Lỗi: {e}"}
        
    # 3. Chọn điểm cố định d (điểm Fourier) và điểm lặp x0
    if f(a) * f_double_prime(a) > 0:
        d, x0 = a, b
    elif f(b) * f_double_prime(b) > 0:
        d, x0 = b, a
    else:
        return {"success": False, "error": "Không tìm thấy điểm Fourier để làm điểm cố định."}

    # 4. Tính các hằng số m1, M1
    try:
        x_range = np.linspace(a, b, 1000)
        f_prime_values = np.abs([f_prime(x) for x in x_range])
        m1 = np.min(f_prime_values)
        M1 = np.max(f_prime_values)
        if m1 < 1e-12:
            return {"success": False, "error": "Đạo hàm f'(x) có giá trị gần bằng 0 trong khoảng, không đảm bảo công thức sai số."}
    except Exception as e:
        return {"success": False, "error": f"Không thể tính m1, M1 trên khoảng [a, b]. Lỗi: {e}"}

    x_curr = x0
    iterations_to_run = int(value) if mode == 'iterations' else 200
    
    for i in range(iterations_to_run):
        f_curr = f(x_curr)
        f_d = f(d)
        
        step_info = {"n": i, "x_n": x_curr, "f(x_n)": f_curr}
        
        # Cập nhật x_next
        x_prev = x_curr
        denominator = f_curr - f_d
        if abs(denominator) < 1e-12:
            return {"success": False, "error": "Mẫu số f(x_n) - f(d) bằng 0.", "steps": steps}
        x_curr = x_curr - (f_curr * (x_curr - d)) / denominator
        
        # Kiểm tra điều kiện dừng
        done = False
        tol = float(value)
        
        if mode == 'iterations':
            if i + 1 >= tol:
                done = True
        elif mode == 'absolute_error':
            if stop_condition == 'f_xn':
                error = np.abs(f_curr) / m1
                step_info['|f(x_n)|/m1'] = error
                if error < tol: done = True
            else: # xn_xn-1
                error = ((M1 - m1) / m1) * np.abs(x_curr - x_prev)
                step_info['(M1-m1)|x_n-x_{n-1}|/m1'] = error
                if error < tol: done = True
        elif mode == 'relative_error':
            if abs(x_curr) < 1e-12: # Tránh chia cho 0
                done = False
            elif stop_condition == 'f_xn':
                error = np.abs(f_curr) / (m1 * np.abs(x_curr))
                step_info['|f(x_n)|/(m1|x_n|)'] = error
                if error < tol: done = True
            else: # xn_xn-1
                error = ((M1 - m1) / m1) * np.abs(x_curr - x_prev) / np.abs(x_curr)
                step_info['(M1-m1)|x_n-x_{n-1}|/(m1|x_n|)'] = error
                if error < tol: done = True
        
        steps.append(step_info)
        if done:
            break

    if mode != 'iterations' and not done:
        return {"success": False, "error": f"Không hội tụ sau {iterations_to_run} lần lặp.", "steps": steps}

    return {"success": True, "solution": x_curr, "steps": steps, "iterations": len(steps), "m1": m1, "M1": M1}
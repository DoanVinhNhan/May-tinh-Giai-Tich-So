# /numerical_methods/root_finding/newton.py
import numpy as np

def solve_newton(parsed_expr, a, b, mode, value, stop_condition):
    """
    Giải phương trình f(x) = 0 bằng phương pháp Newton.

    Args:
        parsed_expr (dict): Dict chứa các hàm f, f_prime, f_double_prime.
        a (float): Điểm đầu của khoảng cách ly.
        b (float): Điểm cuối của khoảng cách ly.
        mode (str): Điều kiện dừng ('absolute_error', 'relative_error', 'iterations').
        value (float): Giá trị cho điều kiện dừng.
        stop_condition (str): Công thức sai số ('f_xn' hoặc 'xn_xn-1').
    
    Returns:
        dict: Kết quả chứa nghiệm, các bước lặp và trạng thái thành công.
    """
    f = parsed_expr['f']
    f_prime = parsed_expr['f_prime']
    f_double_prime = parsed_expr['f_double_prime']
    steps = []

    # 1. Kiểm tra điều kiện hội tụ
    if f_prime(a) * f_prime(b) <= 0 or f_double_prime(a) * f_double_prime(b) <= 0:
        return {"success": False, "error": "Điều kiện hội tụ f'(x) và f''(x) không đổi dấu trên [a, b] không thỏa mãn."}
    
    # 2. Chọn điểm bắt đầu x0 (Fourier's condition)
    if f(a) * f_double_prime(a) > 0:
        x0 = a
    elif f(b) * f_double_prime(b) > 0:
        x0 = b
    else:
        return {"success": False, "error": "Không tìm thấy điểm bắt đầu x0 thỏa mãn điều kiện Fourier."}

    # 3. Tính hằng số
    m1 = min(np.abs(f_prime(a)), np.abs(f_prime(b)))
    if m1 == 0:
        return {"success": False, "error": "Đạo hàm f'(x) bằng 0 tại biên, không thể chia."}
        
    M2 = max(np.abs(f_double_prime(a)), np.abs(f_double_prime(b)))
    
    x_curr = x0
    x_prev = x_curr + 1 # Khởi tạo để vòng lặp đầu tiên chạy

    for i in range(200): # Giới hạn 200 lần lặp
        f_val = f(x_curr)
        f_prime_val = f_prime(x_curr)

        if f_prime_val == 0:
            return {"success": False, "error": f"Đạo hàm bằng 0 tại x = {x_curr}."}

        # Ghi lại bước hiện tại
        step_info = {"n": i, "x_n": x_curr, "f(x_n)": f_val}
        
        # Kiểm tra điều kiện dừng TRƯỚC khi cập nhật
        done = False
        if mode == 'iterations' and i >= int(value):
            done = True
        elif mode == 'absolute_error':
            if stop_condition == 'f_xn':
                error = np.abs(f_val) / m1
                step_info['|f(x_n)|/m1'] = error
                if error <= value: done = True
            else: # 'xn_xn-1'
                error = (M2 / (2 * m1)) * (x_curr - x_prev)**2
                step_info['M2|x_n-x_{n-1}|²/(2m1)'] = error
                if error <= value: done = True
        elif mode == 'relative_error':
            if stop_condition == 'f_xn':
                 error = np.abs(f_val) / (m1 * np.abs(x_curr)) if x_curr != 0 else float('inf')
                 step_info['|f(x_n)|/(m1|x_n|)'] = error
                 if error <= value: done = True
            else: # 'xn_xn-1'
                error = (M2 / (2 * m1 * np.abs(x_curr))) * (x_curr - x_prev)**2 if x_curr != 0 else float('inf')
                step_info['M2|x_n-x_{n-1}|²/(2m1|x_n|)'] = error
                if error <= value: done = True

        steps.append(step_info)
        if done:
            break
            
        # Cập nhật cho lần lặp tiếp theo
        x_prev = x_curr
        x_curr = x_prev - f_val / f_prime_val

    else: # Nếu vòng lặp hoàn tất mà không `break`
        return {"success": False, "error": "Phương pháp không hội tụ sau 200 lần lặp."}

    return {"success": True, "solution": x_curr, "steps": steps, "iterations": len(steps)}

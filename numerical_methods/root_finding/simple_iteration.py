# /numerical_methods/root_finding/simple_iteration.py
import numpy as np

def solve_simple_iteration(parsed_phi, a, b, x0_str, mode, value):
    """
    Giải phương trình x = phi(x) bằng phương pháp Lặp đơn.
    """
    phi = parsed_phi['phi']
    phi_prime = parsed_phi['phi_prime']
    steps = []

    try:
        x0 = float(x0_str)
    except (ValueError, TypeError):
        return {"success": False, "error": "Điểm bắt đầu x0 không hợp lệ."}

    if not (a <= x0 <= b):
        return {"success": False, "error": "Điểm bắt đầu x0 phải nằm trong khoảng [a, b]."}

    # 1. Tính q và kiểm tra điều kiện hội tụ
    # Lấy mẫu trên khoảng để tìm max
    test_points = np.linspace(a, b, 100)
    q = np.max(np.abs(phi_prime(test_points)))

    if q >= 1:
        return {"success": False, "error": f"Điều kiện hội tụ không thỏa mãn. |φ'(x)| = {q:.4f} >= 1."}
        
    x_curr = x0
    x_prev = x_curr + 1 # Khởi tạo

    for i in range(200):
        step_info = {"n": i, "x_n": x_curr}
        
        # 2. Kiểm tra điều kiện dừng
        done = False
        error_val = np.abs(x_curr - x_prev)

        if i > 0: # Chỉ kiểm tra từ lần lặp thứ 2
            if mode == 'iterations' and i >= int(value):
                done = True
            elif mode == 'absolute_error':
                stop_val = value
                step_info[f'|x_n-x_{"n-1"}|'] = error_val
                if (q / (1 - q)) * error_val <= stop_val: done = True
            elif mode == 'relative_error':
                stop_val = value
                relative_error = (q / (1 - q)) * (error_val / np.abs(x_curr)) if x_curr !=0 else float('inf')
                step_info[f'q|x_n-x_{"n-1"}|/((1-q)|x_n|)'] = relative_error
                if relative_error <= stop_val: done = True

        steps.append(step_info)
        if done:
            break

        # 3. Cập nhật
        x_prev = x_curr
        x_curr = phi(x_prev)

    else:
        return {"success": False, "error": "Không hội tụ sau 200 lần lặp."}

    return {"success": True, "solution": x_curr, "steps": steps, "iterations": len(steps), "q_value": q}
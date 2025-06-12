# /numerical_methods/root_finding/bisection.py
import numpy as np
import pandas as pd

def solve_bisection(f, a, b, mode, value):
    steps = []
    # Kiểm tra tính đơn điệu xấp xỉ trên [a, b] bằng đạo hàm số
    N_check = 20
    x_check = np.linspace(a, b, N_check)
    h = 1e-6
    deriv_signs = []
    for x in x_check:
        try:
            fp = (f(x + h) - f(x - h)) / (2 * h)
            deriv_signs.append(np.sign(fp))
        except Exception:
            deriv_signs.append(0)
    # Loại bỏ các điểm đạo hàm gần 0
    deriv_signs = [s for s in deriv_signs if abs(s) > 1e-8]
    is_monotonic = all(s > 0 for s in deriv_signs) or all(s < 0 for s in deriv_signs)
    if not is_monotonic:
        return {'success': False, 'error': f'Hàm f(x) không đơn điệu trên [{a}, {b}].'}

    # Kiểm tra điều kiện cách ly nghiệm ngay trong hàm
    fa = f(a)
    fb = f(b)
    if fa * fb >= 0:
        return {'success': False, 'error': f'Khoảng [{a}, {b}] không phải là khoảng cách ly nghiệm vì f(a)={fa:.4f} và f(b)={fb:.4f} không trái dấu.'}

    if mode == "absolute_error":
        epsilon = float(value)
        c_prev = a
        c = (a + b) / 2
        i = 0
        while np.abs(c - c_prev) >= epsilon:
            if i != 0: c_prev = c
            c = (a + b) / 2
            steps.append({"n": i, "a": a, "b": b, "c": c, "f(c)": f(c), "error": np.abs(c - c_prev)})
            if f(c) == 0.0: break
            if f(a) * f(c) < 0: b = c
            else: a = c
            i += 1
            if i > 200: return {"success": False, "error": "Vượt quá 200 lần lặp. Phương pháp có thể không hội tụ."}
        
        steps.append({"n": i, "a": a, "b": b, "c": c, "f(c)": f(c), "error": np.abs(c - c_prev)})
        solution = c

        return {"success": True, "solution": solution, "steps": steps, "iterations": len(steps)}

    elif mode == "relative_error":
        delta = float(value)
        c_prev = a
        c = (a + b) / 2
        i = 0
        while np.abs(c - c_prev) / np.abs(c) if c != 0 else np.inf >= delta:
            if i != 0: c_prev = c
            c = (a + b) / 2
            error = np.abs(c - c_prev) / np.abs(c) if c != 0 else float('inf')
            steps.append({"n": i, "a": a, "b": b, "c": c, "f(c)": f(c), "relative_error": error})
            if f(c) == 0.0: break
            if f(a) * f(c) < 0: b = c
            else: a = c
            i += 1
            if i > 200: return {"success": False, "error": "Vượt quá 200 lần lặp."}
        
        error = np.abs(c - c_prev) / np.abs(c) if c != 0 else float('inf')
        steps.append({"n": i, "a": a, "b": b, "c": c, "f(c)": f(c), "relative_error": error})
        solution = c

        return {"success": True, "solution": solution, "steps": steps, "iterations": len(steps)}

    elif mode == "iterations":
        n_iters = int(value)
        c = a
        for i in range(n_iters):
            c_prev = c
            c = (a + b) / 2
            steps.append({"n": i, "a": a, "b": b, "c": c, "f(c)": f(c)})
            if f(c) == 0.0: break
            if f(a) * f(c) < 0: b = c
            else: a = c
        solution = c

        return {"success": True, "solution": solution, "steps": steps, "iterations": len(steps)}
        
    else:
        return {"success": False, "error": "Chế độ không hợp lệ."}
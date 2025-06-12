# /numerical_methods/root_finding/bisection.py
import numpy as np
import pandas as pd

def solve_bisection(f, a, b, mode, value):
    steps = []
    
    # Kiểm tra điều kiện ban đầu
    if f(a) * f(b) >= 0:
        return {"success": False, "error": "Điều kiện f(a) * f(b) < 0 không thỏa mãn."}

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
        
    else:
        return {"success": False, "error": "Chế độ không hợp lệ."}

    return {"success": True, "solution": solution, "steps": steps, "iterations": len(steps)}
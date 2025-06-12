import numpy as np

def solve_inverse_newton(A, eps=1e-5, max_iter=100, x0_method='auto', **kwargs):
    """
    Tìm ma trận nghịch đảo gần đúng bằng phương pháp lặp Newton.
    Xₖ₊₁ = Xₖ(2E - AXₖ)
    """
    try:
        n = A.shape[0]
        if n != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}
        if np.linalg.det(A) == 0:
            return {"success": False, "error": "Ma trận suy biến, không có nghịch đảo."}

        E = np.identity(n)
        steps = []
        
        # Chọn X₀ ban đầu
        X0_1 = A.T / (np.linalg.norm(A, 2)**2)
        q1 = np.linalg.norm(E - A @ X0_1, 2)
        
        X0_2 = A.T / (np.linalg.norm(A, 1) * np.linalg.norm(A, np.inf))
        q2 = np.linalg.norm(E - A @ X0_2, 2)
        
        method_used = ""
        if x0_method == 'method1':
            X_k = X0_1
            q = q1
            method_used = "X₀ = Aᵀ / ||A||₂²"
        elif x0_method == 'method2':
            X_k = X0_2
            q = q2
            method_used = "X₀ = Aᵀ / (||A||₁·||A||∞)"
        else: # auto
             if q1 < q2:
                X_k = X0_1
                q = q1
                method_used = "Tự động chọn X₀ = Aᵀ / ||A||₂²"
             else:
                X_k = X0_2
                q = q2
                method_used = "Tự động chọn X₀ = Aᵀ / (||A||₁·||A||∞)"

        if q >= 1:
            return {"success": False, "error": f"Điều kiện hội tụ không thỏa mãn với {method_used} (q = {q:.4f} >= 1)."}

        steps.append({
            "message": f"Bước 1: Chọn ma trận ban đầu X₀ bằng phương pháp {method_used}",
            "q": q,
            "matrix": X_k.tolist()
        })

        table_rows = []
        
        for i in range(max_iter):
            X_k_plus_1 = X_k @ (2 * E - A @ X_k)
            
            error = np.linalg.norm(X_k_plus_1 - X_k, 'fro')
            
            if i < 5 or i > max_iter - 5 or error <= eps:
                 table_rows.append([
                    str(i+1),
                    f"{X_k_plus_1[0,0]:.6f}, ...",
                    f"{error:.6e}"
                ])
            elif i == 5:
                 table_rows.append(["...", "...", "..."])

            if error < eps:
                break
                
            X_k = X_k_plus_1

        steps.append({
            "message": "Bảng quá trình lặp",
            "table": {
                "headers": ["Lần lặp k", "Xₖ (ví dụ)", "||Xₖ - Xₖ₋₁||_fro"],
                "rows": table_rows
            }
        })
        
        inv_A = X_k_plus_1
        check_matrix = A @ inv_A

        return {
            "success": True,
            "message": f"Hội tụ sau {i+1} lần lặp.",
            "inverse": inv_A.tolist(),
            "check": check_matrix.tolist(),
            "steps": steps
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
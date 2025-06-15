# doanvinhnhan/may-tinh-giai-tich-so/May-tinh-Giai-Tich-So-main/numerical_methods/linear_algebra/inverse/newton_inverse.py
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

        iteration_details = []
        
        for i in range(max_iter):
            X_k_plus_1 = X_k @ (2 * E - A @ X_k)
            
            error = np.linalg.norm(X_k_plus_1 - X_k, 'fro')
            
            # Ghi lại ma trận X và sai số của bước lặp này
            iteration_details.append({
                "iteration_number": i + 1,
                "matrix_Xk": X_k_plus_1.tolist(),
                "error_fro": error
            })

            if error < eps:
                break
                
            X_k = X_k_plus_1
        
        # Đưa các bước lặp chi tiết vào kết quả trả về
        steps.append({
            "message": "Quá trình lặp:",
            "iterations": iteration_details
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
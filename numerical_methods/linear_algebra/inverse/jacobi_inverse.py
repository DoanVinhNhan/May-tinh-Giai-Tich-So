import numpy as np

def solve_inverse_jacobi(A, eps=1e-5, max_iter=100, **kwargs):
    """
    Tìm ma trận nghịch đảo gần đúng bằng phương pháp lặp Jacobi.
    Yêu cầu ma trận chéo trội.
    """
    try:
        n = A.shape[0]
        if n != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}

        # Kiểm tra chéo trội
        diag_abs = np.abs(np.diag(A))
        sum_abs_off_diag = np.sum(np.abs(A), axis=1) - diag_abs
        if not np.all(diag_abs > sum_abs_off_diag):
            return {"success": False, "error": "Ma trận không chéo trội hàng. Phương pháp Jacobi có thể không hội tụ."}

        steps = []
        
        # Tạo ma trận lặp B và vector D
        D = np.diag(np.diag(A))
        R = A - D
        inv_D = np.diag(1.0 / np.diag(A))
        B = -inv_D @ R
        
        steps.append({
            "message": "Thiết lập công thức lặp Xₖ₊₁ = B·Xₖ + D⁻¹",
            "B": B.tolist(),
            "D_inv": inv_D.tolist()
        })

        # Bắt đầu lặp
        X_k = np.identity(n) # Chọn X₀ = E
        table_rows = []

        for i in range(max_iter):
            X_k_plus_1 = B @ X_k + inv_D
            
            # Đánh giá sai số
            error = np.linalg.norm(X_k_plus_1 - X_k, np.inf)
            
            # Ghi lại bảng
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
                "headers": ["Lần lặp k", "Xₖ (ví dụ)", "||Xₖ - Xₖ₋₁||∞"],
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
# May-tinh-Giai-Tich-So/numerical_methods/linear_algebra/iterative_methods/jacobi.py
import numpy as np

def solve_jacobi(matrix_a, matrix_b, x0, eps=1e-5, max_iter=100):
    """
    Giải hệ phương trình Ax=b bằng phương pháp lặp Jacobi.
    Yêu cầu ma trận A chéo trội để đảm bảo hội tụ.
    """
    try:
        n = matrix_a.shape[0]
        if n != matrix_a.shape[1]:
            return {"success": False, "error": "Ma trận A phải là ma trận vuông."}
        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)
        if x0.ndim == 1:
            x0 = x0.reshape(-1, 1)

        # Kiểm tra điều kiện chéo trội (điều kiện đủ để hội tụ)
        diag_abs = np.abs(np.diag(matrix_a))
        sum_abs_off_diag = np.sum(np.abs(matrix_a), axis=1) - diag_abs
        warning_message = None
        if not np.all(diag_abs > sum_abs_off_diag):
            warning_message = "Cảnh báo: Ma trận không chéo trội hàng. Phương pháp Jacobi có thể không hội tụ."

        steps = []
        x_k = x0.copy()

        # Tách A = D - R
        D = np.diag(np.diag(matrix_a))
        R = D - matrix_a
        inv_D = np.diag(1.0 / np.diag(matrix_a))
        
        # Ma trận lặp T = D⁻¹R và vector c = D⁻¹b
        T = inv_D @ R
        c = inv_D @ matrix_b

        steps.append({
            "message": "Thiết lập công thức lặp Xₖ₊₁ = T·Xₖ + c",
            "T": T.tolist(),
            "c": c.tolist()
        })
        
        table_rows = []

        for i in range(max_iter):
            x_k_plus_1 = T @ x_k + c
            
            error = np.linalg.norm(x_k_plus_1 - x_k, np.inf)
            
            table_rows.append({
                "k": i + 1,
                "x_k": [val for val in x_k_plus_1.flatten()],
                "error": error
            })

            if error < eps:
                break
            
            x_k = x_k_plus_1
        
        steps.append({
            "message": "Bảng quá trình lặp",
            "table": table_rows
        })

        if i == max_iter -1 and error >= eps:
             return {"success": False, "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp."}

        return {
            "success": True,
            "message": f"Hội tụ sau {i + 1} lần lặp.",
            "warning": warning_message,
            "solution": x_k_plus_1.tolist(),
            "iterations": i + 1,
            "steps": steps
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
import numpy as np
import traceback

def solve_jacobi(matrix_a, matrix_b, x0, eps=1e-5, max_iter=100):
    """
    Giải hệ phương trình Ax=b bằng phương pháp lặp Jacobi.
    Yêu cầu ma trận A phải chéo trội hàng hoặc cột để chạy.
    """
    try:
        # --- Khởi tạo và kiểm tra đầu vào ---
        n = matrix_a.shape[0]
        if n != matrix_a.shape[1]:
            return {"success": False, "error": "Ma trận A phải là ma trận vuông."}
        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)
        if x0.ndim == 1:
            x0 = x0.reshape(-1, 1)

        diag_elements = np.diag(matrix_a)
        if np.any(np.isclose(diag_elements, 0)):
            return {"success": False, "error": "Ma trận có phần tử trên đường chéo chính bằng 0."}
        
        # --- Kiểm tra điều kiện chéo trội ---
        diag_abs = np.abs(diag_elements)
        row_sum = np.sum(np.abs(matrix_a), axis=1) - diag_abs
        col_sum = np.sum(np.abs(matrix_a), axis=0) - diag_abs

        is_row_dominant = np.all(diag_abs > row_sum)
        is_col_dominant = np.all(diag_abs > col_sum)

        T = np.diag(1.0 / diag_elements)
        
        # --- Thiết lập tham số dựa trên loại chéo trội ---
        if is_row_dominant:
            dominance_type = "row"
            norm_used = "infinity"
            norm = np.inf
            B_iter = np.identity(n) - T @ matrix_a
            contraction_coefficient = np.linalg.norm(B_iter, norm)
            stopping_factor = contraction_coefficient / (1 - contraction_coefficient)
        elif is_col_dominant:
            dominance_type = "column"
            norm_used = "1"
            norm = 1
            B1_conv = np.identity(n) - matrix_a @ T
            contraction_coefficient = np.linalg.norm(B1_conv, norm)
            lambda_factor = np.max(diag_abs) / np.min(diag_abs)
            stopping_factor = lambda_factor * contraction_coefficient / (1 - contraction_coefficient)
        else:
            # THAY ĐỔI: Dừng lại và báo lỗi nếu không chéo trội
            return {
                "success": False,
                "error": "Ma trận không chéo trội hàng hoặc cột. Không thể đảm bảo hội tụ cho phương pháp Jacobi."
            }
        
        B_iter = np.identity(n) - T @ matrix_a
        d_iter = T @ matrix_b

        # --- Quá trình lặp ---
        x_k = x0.copy()
        table_rows = []
        final_error = float('inf')

        for i in range(max_iter):
            x_k_plus_1 = B_iter @ x_k + d_iter
            diff_norm = np.linalg.norm(x_k_plus_1 - x_k, norm)
            estimated_error = stopping_factor * diff_norm

            table_rows.append({
                "k": i + 1,
                "x_k": x_k_plus_1.tolist(),
                "error": estimated_error,
                "error_norm": diff_norm
            })
            
            final_error = estimated_error
            if final_error < eps:
                break
            
            x_k = x_k_plus_1
        
        if i == max_iter - 1 and final_error >= eps:
             return {
                 "success": False, 
                 "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp.",
                 "steps": [{"table": table_rows}]
            }

        return {
            "success": True,
            "message": f"Hội tụ sau {i + 1} lần lặp.",
            "solution": x_k_plus_1.tolist(),
            "iterations": i + 1,
            "steps": [{"message": "Bảng quá trình lặp", "table": table_rows}],
            "contraction_coefficient": contraction_coefficient,
            "norm_used": norm_used,
            "dominance_type": dominance_type
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
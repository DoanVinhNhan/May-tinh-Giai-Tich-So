import numpy as np
import traceback

def solve_jacobi(matrix_a, matrix_b, x0, eps=1e-5, max_iter=100):
    """
    Giải hệ phương trình Ax=b bằng phương pháp lặp Jacobi.
    Hỗ trợ cả ma trận chéo trội hàng và cột, và sử dụng công thức
    sai số hậu nghiệm tương ứng từ tài liệu.
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

        # --- Thiết lập công thức lặp ---
        diag_elements = np.diag(matrix_a)
        if np.any(np.isclose(diag_elements, 0)):
            return {"success": False, "error": "Ma trận có phần tử trên đường chéo chính bằng 0."}
        
        T = np.diag(1.0 / diag_elements)
        B_iter = np.identity(n) - T @ matrix_a
        d_iter = T @ matrix_b
        
        # --- Phân tích hội tụ và xác định tham số ---
        diag_abs = np.abs(diag_elements)
        row_sum = np.sum(np.abs(matrix_a), axis=1) - diag_abs
        col_sum = np.sum(np.abs(matrix_a), axis=0) - diag_abs

        is_row_dominant = np.all(diag_abs > row_sum)
        is_col_dominant = np.all(diag_abs > col_sum)

        norm = None
        stopping_factor = None
        contraction_coefficient = None
        dominance_type = "none"
        norm_used = "none"
        warning_message = None

        if is_row_dominant:
            dominance_type = "row"
            norm_used = "infinity"
            norm = np.inf
            contraction_coefficient = np.linalg.norm(B_iter, norm)
        elif is_col_dominant:
            dominance_type = "column"
            norm_used = "1"
            norm = 1
            B1_conv = np.identity(n) - matrix_a @ T
            contraction_coefficient = np.linalg.norm(B1_conv, norm)
        else:
            dominance_type = "none"
            norm_used = "infinity"
            norm = np.inf
            contraction_coefficient = np.linalg.norm(B_iter, norm)
            warning_message = "Cảnh báo: Ma trận không chéo trội hàng hay cột. Phương pháp có thể không hội tụ."

        if contraction_coefficient >= 1:
            if warning_message is None:
                 warning_message = f"Cảnh báo: Hệ số co q = {contraction_coefficient:.4f} >= 1. Phương pháp có thể không hội tụ."
            stopping_factor = None
        else:
            if dominance_type == "column":
                lambda_factor = np.max(diag_abs) / np.min(diag_abs)
                stopping_factor = lambda_factor * contraction_coefficient / (1 - contraction_coefficient)
            else:
                stopping_factor = contraction_coefficient / (1 - contraction_coefficient)

        # --- Quá trình lặp ---
        x_k = x0.copy()
        table_rows = []
        final_error = float('inf')

        for i in range(max_iter):
            x_k_plus_1 = B_iter @ x_k + d_iter
            diff_norm = np.linalg.norm(x_k_plus_1 - x_k, norm)
            estimated_error = stopping_factor * diff_norm if stopping_factor is not None else float('inf')

            # Chuyển đổi x_k thành list 1D để tương thích với các hàm lặp khác
            table_rows.append({
                "k": i + 1,
                "x_k": x_k_plus_1.flatten().tolist(),
                "error": estimated_error
            })
            
            final_error = estimated_error

            if final_error < eps:
                break
            
            x_k = x_k_plus_1
        
        # --- Chuẩn bị kết quả trả về ---
        if i == max_iter - 1 and final_error >= eps:
             return {
                 "success": False, 
                 "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp.",
                 "steps": table_rows
            }

        return {
            "success": True,
            "message": f"Hội tụ sau {i + 1} lần lặp.",
            "warning": warning_message,
            "solution": x_k_plus_1.tolist(),
            "iterations": i + 1,
            # THAY ĐỔI QUAN TRỌNG: Trả về danh sách các bước lặp đơn giản
            "steps": [{
                "message": "Bảng quá trình lặp",
                "table": table_rows
            }],
            # Các thông tin phân tích hội tụ vẫn được giữ nguyên
            "contraction_coefficient": contraction_coefficient,
            "norm_used": norm_used,
            "dominance_type": dominance_type
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
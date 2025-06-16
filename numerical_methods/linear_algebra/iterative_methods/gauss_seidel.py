import numpy as np
import traceback

def solve_gauss_seidel(matrix_a, matrix_b, x0, eps=1e-5, max_iter=100):
    """
    Giải hệ phương trình Ax=B bằng phương pháp lặp Gauss-Seidel.
    - Yêu cầu ma trận A phải chéo trội hàng hoặc cột.
    - Tự động chọn chuẩn (1 hoặc vô cùng) và tính hệ số co (q, s) tương ứng.
    - Điều kiện dừng dựa trên công thức sai số hậu nghiệm.
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
            return {"success": False, "error": "Ma trận có phần tử trên đường chéo chính bằng 0, không thể thực hiện phép chia."}

        # --- Kiểm tra chéo trội hàng và cột nghiêm ngặt ---
        diag_abs = np.abs(diag_elements)
        row_sum_off_diag = np.sum(np.abs(matrix_a), axis=1) - diag_abs
        col_sum_off_diag = np.sum(np.abs(matrix_a), axis=0) - diag_abs

        is_row_dominant = np.all(diag_abs > row_sum_off_diag)
        is_col_dominant = np.all(diag_abs > col_sum_off_diag)

        s, q, norm, dominance_type = 0, 0, 0, ""

        if is_row_dominant:
            dominance_type = "chéo trội hàng"
            norm = np.inf
            s = 0  # Theo công thức (1.51) 
            
            # Tính q cho trường hợp chéo trội hàng theo (1.51) 
            q_num = np.zeros(n)
            q_den = np.zeros(n)
            for i in range(n):
                q_num[i] = np.sum(np.abs(matrix_a[i, :i]))
                q_den[i] = np.abs(matrix_a[i, i]) - np.sum(np.abs(matrix_a[i, i+1:]))
            q_den[np.isclose(q_den, 0)] = 1e-15 
            q = np.max(q_num / q_den)

        elif is_col_dominant:
            dominance_type = "chéo trội cột"
            norm = 1
            
            # Tính s cho trường hợp chéo trội cột theo (1.52) 
            s_num = np.zeros(n)
            for j in range(n):
                s_num[j] = np.sum(np.abs(matrix_a[j+1:, j]))
            s = np.max(s_num / diag_abs)
            
            # Tính q cho trường hợp chéo trội cột theo (1.52) 
            q_num = np.zeros(n)
            q_den = np.zeros(n)
            for j in range(n):
                q_num[j] = np.sum(np.abs(matrix_a[:j, j]))
                q_den[j] = np.abs(matrix_a[j, j]) - np.sum(np.abs(matrix_a[j+1:, j]))
            q_den[np.isclose(q_den, 0)] = 1e-15
            q = np.max(q_num / q_den)
        
        else:
            return {
                "success": False,
                "error": "Ma trận không chéo trội hàng hoặc cột. Không thể đảm bảo hội tụ cho phương pháp Gauss-Seidel."
            }

        # --- Tính toán hệ số cho điều kiện dừng ---
        denominator = (1 - s) * (1 - q)
        if np.isclose(denominator, 0):
             return {"success": False, "error": f"Hệ số q={q:.4f} hoặc s={s:.4f} không hợp lệ, gây lỗi chia cho 0 trong công thức sai số."}
        stopping_factor = q / denominator

        # --- Quá trình lặp ---
        x_k = x0.copy().astype(float)
        table_rows = []
        final_error = float('inf')

        for i in range(max_iter):
            x_prev = x_k.copy()
            for j in range(n):
                sum1 = np.dot(matrix_a[j, :j], x_k[:j, :])
                sum2 = np.dot(matrix_a[j, j+1:], x_prev[j+1:, :])
                x_k[j, :] = (matrix_b[j, :] - sum1 - sum2) / matrix_a[j, j]
            
            # Sử dụng chuẩn phù hợp dựa trên loại chéo trội
            diff_norm = np.linalg.norm(x_k - x_prev, norm)
            
            # Sai số hậu nghiệm theo công thức (1.50) 
            estimated_error = stopping_factor * diff_norm
            final_error = estimated_error
            
            table_rows.append({
                "k": i + 1,
                "x_k": x_k.tolist(),
                "error": estimated_error,
                "error_norm": diff_norm  # Thêm dòng này
            })

            # Kiểm tra điều kiện dừng
            if estimated_error < eps:
                break
        
        if i == max_iter - 1 and final_error >= eps:
            return {
                "success": False, 
                "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp.",
                "steps": [{"table": table_rows}]
            }

        return {
            "success": True,
            "message": f"Hội tụ sau {i + 1} lần lặp.",
            "solution": x_k.tolist(),
            "iterations": i + 1,
            "steps": [{"message": "Bảng quá trình lặp", "table": table_rows}],
            "contraction_coefficient_q": q,
            "contraction_coefficient_s": s,
            "norm_used": "vô cùng" if norm == np.inf else "1",
            "dominance_type": dominance_type
        }
    except Exception as e:
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
import numpy as np
import traceback

def solve_inverse_jacobi(A, x0_method='method1', eps=1e-5, max_iter=100):
    """
    Tìm ma trận nghịch đảo gần đúng bằng phương pháp lặp Jacobi.
    Cho phép chọn X0 như Newton: method1 = A.T / ||A||_2^2, method2 = A.T / (||A||_1 * ||A||_inf)
    """
    try:
        n = A.shape[0]
        if n != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}

        diag_elements = np.diag(A)
        diag_abs = np.abs(diag_elements)
        row_sum = np.sum(np.abs(A), axis=1) - diag_abs
        col_sum = np.sum(np.abs(A), axis=0) - diag_abs

        is_row_dominant = np.all(diag_abs > row_sum)
        is_col_dominant = np.all(diag_abs > col_sum)

        if is_row_dominant:
            dominance_type = "row"
            norm_used = "infinity"
            norm = np.inf
            stop_formula = r"||X^{(k+1)} - X^{(k)}||_\infty < \epsilon"
        elif is_col_dominant:
            dominance_type = "column"
            norm_used = "1"
            norm = 1
            stop_formula = r"||X^{(k+1)} - X^{(k)}||_1 < \epsilon"
        else:
            return {"success": False, "error": "Ma trận không chéo trội hàng hoặc cột. Không thể đảm bảo hội tụ cho phương pháp Jacobi."}

        D = np.diag(diag_elements)
        R = A - D
        D_inv = np.diag(1.0 / diag_elements)
        
        if is_row_dominant:
            # Dùng đúng như Jacobi giải hệ: B = I - T @ A
            B = np.eye(n) - D_inv @ A
            contraction_coefficient = np.linalg.norm(B, norm)
        elif is_col_dominant:
            # Dùng đúng như Jacobi giải hệ: B = I - A @ T
            B = np.eye(n) - A @ D_inv
            contraction_coefficient = np.linalg.norm(B, norm)
        else:
            return {"success": False, "error": "Ma trận không chéo trội hàng hoặc cột. Không thể đảm bảo hội tụ cho phương pháp Jacobi."}

        # Chọn X0 như Newton
        X0_1 = A.T / (np.linalg.norm(A, 2) ** 2)
        X0_2 = A.T / (np.linalg.norm(A, 1) * np.linalg.norm(A, np.inf))
        if x0_method == 'method1':
            X_k = X0_1
            x0_label = "X₀ = Aᵀ / ||A||₂²"
        elif x0_method == 'method2':
            X_k = X0_2
            x0_label = "X₀ = Aᵀ / (||A||₁·||A||∞)"
        else:
            return {"success": False, "error": "x0_method không hợp lệ. Chỉ hỗ trợ 'method1' và 'method2'."}

        steps = []
        steps.append({
            "message": f"Bước 1: Chọn ma trận ban đầu {x0_label}",
            "matrix": X_k.tolist()
        })
        table_rows = []
        final_error = float('inf')

        # Tính hệ số ước lượng sai số hậu nghiệm
        if contraction_coefficient < 1:
            stopping_factor = contraction_coefficient / (1 - contraction_coefficient)
        else:
            stopping_factor = None

        for i in range(max_iter):
            X_k_plus_1 = B @ X_k + D_inv
            diff_norm = np.linalg.norm(X_k_plus_1 - X_k, norm)
            if stopping_factor is not None:
                estimated_error = stopping_factor * diff_norm
            else:
                estimated_error = diff_norm
            table_rows.append({
                "k": i + 1,
                "x_k": X_k_plus_1.tolist(),
                "error": estimated_error,
                "error_aposteriori": estimated_error if stopping_factor is not None else None,
                "error_norm": diff_norm
            })
            final_error = estimated_error
            if final_error < eps:
                break
            X_k = X_k_plus_1

        if i == max_iter - 1 and final_error >= eps:
            return {
                "success": False,
                "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp.",
                "steps": [{"table": table_rows}]
            }

        inv_A = X_k_plus_1
        check_matrix = A @ inv_A

        steps.append({
            "message": "Bảng quá trình lặp",
            "table": table_rows
        })

        return {
            "success": True,
            "message": f"Hội tụ sau {i + 1} lần lặp.",
            "inverse": inv_A.tolist(),
            "check": check_matrix.tolist(),
            "steps": steps,
            "contraction_coefficient": contraction_coefficient,
            "norm_used": norm_used,
            "dominance_type": dominance_type,
            "stop_formula": stop_formula,
            "x0_method": x0_method,
            "x0_label": x0_label
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
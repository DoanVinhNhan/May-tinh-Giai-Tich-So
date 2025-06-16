import numpy as np
import traceback

def _gauss_seidel_solver(A, b, eps, max_iter):
    """
    Hàm trợ giúp: Giải một hệ phương trình Ax = b bằng phương pháp Gauss-Seidel.
    """
    n = len(b)
    x = np.zeros(n)
    iteration_details = []

    for k in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            if A[i, i] == 0:
                # Tránh lỗi chia cho 0 nếu phần tử đường chéo bằng 0
                raise ValueError(f"Phần tử đường chéo a[{i},{i}] bằng 0, không thể tiếp tục.")
            
            sum1 = np.dot(A[i, :i], x[:i])
            sum2 = np.dot(A[i, i + 1:], x_old[i + 1:])
            x[i] = (b[i] - sum1 - sum2) / A[i, i]
        
        error = np.linalg.norm(x - x_old, np.inf)
        iteration_details.append({
            'k': k + 1,
            'x_k': x.tolist(),
            'error': error
        })
        if error < eps:
            break
    
    return x, iteration_details

def solve_inverse_gauss_seidel(A, x0_method='method1', eps=1e-5, max_iter=100):
    """
    Tìm ma trận nghịch đảo gần đúng bằng phương pháp lặp Gauss-Seidel.
    Cho phép chọn X0 như Newton/Jacobi: method1 = A.T / ||A||_2^2, method2 = A.T / (||A||_1 * ||A||_inf)
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
            return {"success": False, "error": "Ma trận không chéo trội hàng hoặc cột. Không thể đảm bảo hội tụ cho phương pháp Gauss-Seidel."}

        # Tính hệ số co q, s như giải hệ
        if is_row_dominant:
            q_num = np.zeros(n)
            q_den = np.zeros(n)
            for i in range(n):
                q_num[i] = np.sum(np.abs(A[i, :i]))
                q_den[i] = np.abs(A[i, i]) - np.sum(np.abs(A[i, i+1:]))
            q_den[np.isclose(q_den, 0)] = 1e-15
            q = np.max(q_num / q_den)
            s = 0
        else:  # is_col_dominant
            s_num = np.zeros(n)
            for j in range(n):
                s_num[j] = np.sum(np.abs(A[j+1:, j]))
            s = np.max(s_num / diag_abs)
            q_num = np.zeros(n)
            q_den = np.zeros(n)
            for j in range(n):
                q_num[j] = np.sum(np.abs(A[:j, j]))
                q_den[j] = np.abs(A[j, j]) - np.sum(np.abs(A[j+1:, j]))
            q_den[np.isclose(q_den, 0)] = 1e-15
            q = np.max(q_num / q_den)

        denominator = (1 - s) * (1 - q)
        if np.isclose(denominator, 0):
            return {"success": False, "error": f"Hệ số q={q:.4f} hoặc s={s:.4f} không hợp lệ, gây lỗi chia cho 0 trong công thức sai số."}
        stopping_factor = q / denominator

        # Chọn X0 như Newton/Jacobi
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

        for i in range(max_iter):
            X_prev = X_k.copy()
            # Lặp Gauss-Seidel cho từng cột
            for j in range(n):
                e_j = np.zeros((n, 1))
                e_j[j, 0] = 1
                x_col = X_k[:, j].reshape(-1, 1)
                for it in range(1):  # chỉ 1 lần cho mỗi bước lặp ngoài
                    for row in range(n):
                        sum1 = np.dot(A[row, :row], x_col[:row, 0])
                        sum2 = np.dot(A[row, row+1:], x_col[row+1:, 0])
                        x_col[row, 0] = (e_j[row, 0] - sum1 - sum2) / A[row, row]
                X_k[:, j] = x_col[:, 0]
            diff_norm = np.linalg.norm(X_k - X_prev, norm)
            estimated_error = stopping_factor * diff_norm
            table_rows.append({
                "k": i + 1,
                "x_k": X_k.tolist(),
                "error": estimated_error,
                "error_aposteriori": estimated_error,
                "error_norm": diff_norm
            })
            final_error = estimated_error
            if final_error < eps:
                break

        if i == max_iter - 1 and final_error >= eps:
            return {
                "success": False,
                "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp.",
                "steps": [{"table": table_rows}]
            }

        inv_A = X_k
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
            "contraction_coefficient_q": q,
            "contraction_coefficient_s": s,
            "norm_used": norm_used,
            "dominance_type": dominance_type,
            "stop_formula": stop_formula,
            "x0_method": x0_method,
            "x0_label": x0_label
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
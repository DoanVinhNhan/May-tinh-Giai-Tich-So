# May-tinh-Giai-Tich-So/numerical_methods/linear_algebra/iterative_methods/gauss_seidel.py
import numpy as np

def solve_gauss_seidel(matrix_a, matrix_b, x0, eps=1e-5, max_iter=100):
    """
    Giải hệ phương trình Ax=b bằng phương pháp lặp Gauss-Seidel.
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
            warning_message = "Cảnh báo: Ma trận không chéo trội hàng. Phương pháp Gauss-Seidel có thể không hội tụ."

        steps = []
        x_k = x0.copy()
        
        table_rows = []

        for i in range(max_iter):
            x_prev = x_k.copy()
            
            # Cập nhật từng thành phần của x
            for j in range(n):
                sum1 = np.dot(matrix_a[j, :j], x_k[:j, 0])
                sum2 = np.dot(matrix_a[j, j+1:], x_prev[j+1:, 0])
                if matrix_a[j, j] == 0:
                    return {"success": False, "error": f"Phần tử trên đường chéo chính A[{j+1},{j+1}] bằng 0."}
                x_k[j, 0] = (matrix_b[j, 0] - sum1 - sum2) / matrix_a[j, j]
            
            error = np.linalg.norm(x_k - x_prev, np.inf)
            
            table_rows.append({
                "k": i + 1,
                "x_k": [val for val in x_k.flatten()],
                "error": error
            })
            
            if error < eps:
                break
        
        steps.append({
            "message": "Bảng quá trình lặp",
            "table": table_rows
        })

        if i == max_iter - 1 and error >= eps:
            return {"success": False, "error": f"Phương pháp không hội tụ sau {max_iter} lần lặp."}

        return {
            "success": True,
            "message": f"Hội tụ sau {i + 1} lần lặp.",
            "warning": warning_message,
            "solution": x_k.tolist(),
            "iterations": i + 1,
            "steps": steps
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
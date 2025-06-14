import numpy as np

def solve_gauss_seidel(matrix_a, matrix_b, x0, eps=1e-5, max_iter=100):
    """
    Giải hệ phương trình Ax=B bằng phương pháp lặp Gauss-Seidel,
    xử lý toàn bộ ma trận B cùng lúc bằng các phép toán trên ma trận.
    """
    try:
        n = matrix_a.shape[0]
        if n != matrix_a.shape[1]:
            return {"success": False, "error": "Ma trận A phải là ma trận vuông."}

        # Đảm bảo matrix_b và x0 là ma trận 2D để xử lý nhất quán
        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)
        if x0.ndim == 1:
            x0 = x0.reshape(-1, 1)

        # Kiểm tra kích thước các ma trận có tương thích không
        if matrix_a.shape[0] != matrix_b.shape[0] or matrix_a.shape[0] != x0.shape[0] or matrix_b.shape[1] != x0.shape[1]:
            return {"success": False, "error": "Kích thước các ma trận A, B, và x0 không tương thích."}

        # Kiểm tra điều kiện chéo trội (điều kiện đủ để hội tụ)
        diag_abs = np.abs(np.diag(matrix_a))
        sum_abs_off_diag = np.sum(np.abs(matrix_a), axis=1) - diag_abs
        warning_message = None
        if not np.all(diag_abs > sum_abs_off_diag):
            warning_message = "Cảnh báo: Ma trận không chéo trội hàng. Phương pháp Gauss-Seidel có thể không hội tụ."

        # --- Bắt đầu quá trình lặp ma trận ---
        x_k = x0.copy().astype(float)  # Dùng float để đảm bảo tính toán chính xác

        table_rows = []

        for i in range(max_iter):
            x_prev = x_k.copy()

            # Cập nhật từng HÀNG của ma trận nghiệm X
            for j in range(n):
                # sum1 là tổng các A[j,k]*X[k,:] với k < j (dùng giá trị X mới cập nhật)
                sum1 = np.dot(matrix_a[j, :j], x_k[:j, :])
                
                # sum2 là tổng các A[j,k]*X[k,:] với k > j (dùng giá trị X của bước lặp trước)
                sum2 = np.dot(matrix_a[j, j+1:], x_prev[j+1:, :])

                # Kiểm tra phần tử trên đường chéo chính
                if matrix_a[j, j] == 0:
                    return {"success": False, "error": f"Phần tử trên đường chéo chính A[{j+1},{j+1}] bằng 0, không thể chia."}

                # Cập nhật cả hàng j của ma trận x_k cùng một lúc
                x_k[j, :] = (matrix_b[j, :] - sum1 - sum2) / matrix_a[j, j]

            # Tính sai số. np.linalg.norm(..., np.inf) cho ma trận là chuẩn tổng hàng lớn nhất.
            error = np.linalg.norm(x_k - x_prev, np.inf)
            
            # Ghi lại các bước, x_k bây giờ là toàn bộ ma trận X ở bước lặp i
            table_rows.append({
                "k": i + 1,
                "x_k": x_k.tolist(),
                "error": error
            })

            if error < eps:
                break
        
        steps = [{
            "message": "Bảng quá trình lặp của ma trận nghiệm X",
            "table": table_rows
        }]

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
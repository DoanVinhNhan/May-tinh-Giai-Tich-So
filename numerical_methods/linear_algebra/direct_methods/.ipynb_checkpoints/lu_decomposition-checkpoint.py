import numpy as np

def solve_lu(matrix_a, matrix_b):
    """
    Giải hệ phương trình AX=B bằng phương pháp phân tách LU (Doolittle).
    Đã sửa lỗi NameError và xử lý chính xác ma trận suy biến.
    """
    try:
        n = matrix_a.shape[0]
        if n != matrix_a.shape[1]:
            return {"success": False, "error": "Phương pháp LU yêu cầu ma trận A phải là ma trận vuông."}

        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)
        num_b_cols = matrix_b.shape[1]

        L = np.zeros((n, n))
        U = np.zeros((n, n))
        
        # Bước 1: Phân tách A = LU
        for i in range(n):
            for k in range(i, n):
                s = L[k, :i] @ U[:i, i]
                L[k, i] = matrix_a[k, i] - s
            
            U[i, i] = 1.0
            for k in range(i + 1, n):
                if abs(L[i, i]) < 1e-15:
                    U[i, k] = 0
                    continue
                s = L[i, :i] @ U[:i, k]
                U[i, k] = (matrix_a[i, k] - s) / L[i, i]
        
        decomposition_steps = { "L": L.tolist(), "U": U.tolist() }

        is_singular = np.any(np.abs(np.diag(L)) < 1e-15)

        # Bước 2: Giải Ly = B
        y = np.zeros((n, num_b_cols))
        for i in range(n):
            s = L[i, :i] @ y[:i, :]
            if abs(L[i, i]) < 1e-15:
                if np.any(np.abs(matrix_b[i, :] - s) > 1e-15):
                    return {"success": True, "status": "no_solution", "message": "Hệ vô nghiệm (phát hiện mâu thuẫn khi giải Ly=b).", "decomposition": decomposition_steps, "intermediate_y": y.tolist()}
                y[i, :] = 0.0
            else:
                y[i, :] = (matrix_b[i, :] - s) / L[i, i]
        
        # Bước 3: Giải Ux = y
        if is_singular:
            uy_aug = np.hstack([U, y])
            rank = np.linalg.matrix_rank(U)
            
            for i in range(rank, n):
                 if np.any(np.abs(uy_aug[i, n:]) > 1e-15):
                    return {"success": True, "status": "no_solution", "message": f"Hệ vô nghiệm (Hạng(A)={rank} < Hạng([A|B])).", "decomposition": decomposition_steps, "intermediate_y": y.tolist()}

            # SỬA LỖI Ở ĐÂY: Dùng `n` thay cho `num_vars`
            pivot_columns = [i for i in range(n) if abs(U[i,i]) > 1e-15]
            free_vars_indices = [i for i in range(n) if i not in pivot_columns]

            Xp = np.zeros((n, num_b_cols))
            for i in range(rank - 1, -1, -1):
                pivot_col = pivot_columns[i]
                sum_val = U[i, pivot_col+1:n] @ Xp[pivot_col+1:, :]
                Xp[pivot_col, :] = (y[i, :] - sum_val) / U[i, pivot_col]
            
            num_free_vars = len(free_vars_indices)
            null_space_vectors = np.zeros((n, num_free_vars))
            for k, free_idx in enumerate(free_vars_indices):
                v = np.zeros(n)
                v[free_idx] = 1
                for i in range(rank - 1, -1, -1):
                    pivot_col = pivot_columns[i]
                    sum_val = np.dot(U[i, pivot_col+1:n], v[pivot_col+1:])
                    v[pivot_col] = -sum_val / U[i, pivot_col]
                null_space_vectors[:, k] = v

            return {"success": True, "status": "infinite_solutions", "message": f"Hệ có vô số nghiệm (Hạng={rank} < Số ẩn={n}).", "decomposition": decomposition_steps, "intermediate_y": y.tolist(),
                    "general_solution": {"particular_solution": Xp.tolist(), "null_space_vectors": null_space_vectors.tolist(), "num_free_vars": num_free_vars}
            }
        else: # NGHIỆM DUY NHẤT
            x = np.zeros((n, num_b_cols))
            for i in range(n - 1, -1, -1):
                s = U[i, i+1:] @ x[i+1:, :]
                x[i, :] = (y[i, :] - s) / U[i, i]
            
            return {
                "success": True, "status": "unique_solution",
                "message": "Hệ có nghiệm duy nhất tìm bằng phân tách LU.",
                "solution": x.tolist(), "decomposition": decomposition_steps,
                "intermediate_y": y.tolist()
            }
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi nghiêm trọng: {traceback.format_exc()}"}
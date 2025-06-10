import numpy as np

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

def solve_gauss_jordan(matrix_a, matrix_b):
    """
    Giải hệ phương trình tuyến tính AX = B bằng phương pháp khử Gauss-Jordan
    với quy tắc chọn pivot đặc biệt và không hoán vị hàng.
    Đã sửa lỗi để xử lý đầy đủ các trường hợp nghiệm.
    """
    try:
        # --- KHỞI TẠO VÀ KIỂM TRA ĐẦU VÀO ---
        ZERO_TOLERANCE = 1e-15
        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)

        if matrix_a.shape[0] != matrix_b.shape[0]:
            return {"success": False, "error": f"Số hàng của ma trận A ({matrix_a.shape[0]}) và B ({matrix_b.shape[0]}) phải bằng nhau."}

        augmented_matrix = np.hstack((matrix_a.copy().astype(float), matrix_b.copy().astype(float)))
        num_rows, num_cols = augmented_matrix.shape
        num_vars = matrix_a.shape[1]
        num_b_cols = matrix_b.shape[1]
        
        intermediate_steps = [{"message": "Ma trận bổ sung ban đầu [A|B]:", "matrix": augmented_matrix.copy().tolist()}]

        pivoted_rows = []
        pivoted_cols = []
        
        # --- QUÁ TRÌNH KHỬ GAUSS-JORDAN ---
        max_pivots = min(num_rows, num_vars)
        for step in range(max_pivots):
            pivot_r, pivot_c = -1, -1
            found_one = False
            for r in range(num_rows):
                if r in pivoted_rows: continue
                for c in range(num_vars):
                    if c in pivoted_cols: continue
                    if augmented_matrix[r, c] == 1.0:
                        pivot_r, pivot_c = r, c
                        found_one = True
                        break
                if found_one: break
            
            if not found_one:
                max_val = ZERO_TOLERANCE
                for r in range(num_rows):
                    if r in pivoted_rows: continue
                    for c in range(num_vars):
                        if c in pivoted_cols: continue
                        if abs(augmented_matrix[r, c]) > max_val:
                            max_val = abs(augmented_matrix[r, c])
                            pivot_r, pivot_c = r, c
            
            if pivot_r == -1: break
            
            pivot_element = augmented_matrix[pivot_r, pivot_c]
            pivoted_rows.append(pivot_r)
            pivoted_cols.append(pivot_c)

            intermediate_steps.append({"message": f"Bước {len(intermediate_steps)}: Chọn pivot là {pivot_element:.4f} tại ({pivot_r + 1}, {pivot_c + 1}).", "matrix": augmented_matrix.copy().tolist()})
            
            augmented_matrix[pivot_r, :] /= pivot_element
            
            for i in range(num_rows):
                if i != pivot_r:
                    factor = augmented_matrix[i, pivot_c]
                    if abs(factor) > ZERO_TOLERANCE:
                         augmented_matrix[i, :] -= factor * augmented_matrix[pivot_r, :]
            
            augmented_matrix[np.abs(augmented_matrix) < ZERO_TOLERANCE] = 0.0
            intermediate_steps.append({"message": f"Bước {len(intermediate_steps)}: Khử các phần tử trong cột {pivot_c+1}.", "matrix": augmented_matrix.copy().tolist()})

        # --- KẾT LUẬN NGHIỆM ---
        rank = len(pivoted_rows)
        for r in range(num_rows):
            is_row_all_zero_in_A = np.all(np.abs(augmented_matrix[r, :num_vars]) < ZERO_TOLERANCE)
            is_b_part_nonzero = np.any(np.abs(augmented_matrix[r, num_vars:]) >= ZERO_TOLERANCE)
            if is_row_all_zero_in_A and is_b_part_nonzero:
                return {"success": True, "status": "no_solution", "message": "Hệ phương trình vô nghiệm.", "intermediate_steps": intermediate_steps, "solution_matrix": augmented_matrix.tolist()}

        pivots_map = sorted(zip(pivoted_cols, pivoted_rows))
        pivoted_cols = [p[0] for p in pivots_map]
        pivoted_rows = [p[1] for p in pivots_map]

        if rank < num_vars: # VÔ SỐ NGHIỆM
            free_vars_indices = [i for i in range(num_vars) if i not in pivoted_cols]
            
            Xp = np.zeros((num_vars, num_b_cols))
            for i, r_idx in enumerate(pivoted_rows):
                pivot_col = pivoted_cols[i]
                Xp[pivot_col, :] = augmented_matrix[r_idx, num_vars:]
            
            num_free_vars = len(free_vars_indices)
            null_space_vectors = np.zeros((num_vars, num_free_vars))
            for k, free_idx in enumerate(free_vars_indices):
                null_space_vectors[free_idx, k] = 1.0 # Set an tự do = 1
                for i, r_idx in enumerate(pivoted_rows):
                    pivot_col = pivoted_cols[i]
                    null_space_vectors[pivot_col, k] = -augmented_matrix[r_idx, free_idx]
            
            return {
                "success": True, "status": "infinite_solutions",
                "message": f"Hệ có vô số nghiệm (Hạng={rank} < Số ẩn={num_vars}).",
                "intermediate_steps": intermediate_steps,
                "general_solution": {
                    "particular_solution": Xp.tolist(),
                    "null_space_vectors": null_space_vectors.tolist(),
                    "num_free_vars": num_free_vars
                }
            }
        else: # NGHIỆM DUY NHẤT
            solution = np.zeros((num_vars, num_b_cols))
            for i, r_idx in enumerate(pivoted_rows):
                pivot_col = pivoted_cols[i]
                solution[pivot_col, :] = augmented_matrix[r_idx, num_vars:]

            return {
                "success": True, "status": "unique_solution", "message": "Hệ phương trình có nghiệm duy nhất.",
                "solution": zero_small(solution).tolist(), "intermediate_steps": intermediate_steps
            }
            
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi nghiêm trọng: {traceback.format_exc()}"}
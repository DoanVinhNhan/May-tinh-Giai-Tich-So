import numpy as np

def solve_gauss_elimination(matrix_a, matrix_b):
    try:
        ZERO_TOLERANCE = 1e-15
        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)

        augmented_matrix = np.hstack((matrix_a.copy().astype(float), matrix_b.copy().astype(float)))
        num_rows, num_cols = augmented_matrix.shape
        num_vars = matrix_a.shape[1]
        num_b_cols = matrix_b.shape[1]
        
        forward_steps = []
        forward_steps.append({ "message": "Ma trận bổ sung ban đầu [A|B]:", "matrix": augmented_matrix.copy().tolist() })
        
        pivot_row = 0
        pivot_columns = []
        col_index = 0
        while pivot_row < num_rows and col_index < num_vars:
            if abs(augmented_matrix[pivot_row, col_index]) < ZERO_TOLERANCE:
                swap_with_row = -1
                for k in range(pivot_row + 1, num_rows):
                    if abs(augmented_matrix[k, col_index]) > ZERO_TOLERANCE:
                        swap_with_row = k
                        break
                if swap_with_row != -1:
                    augmented_matrix[[pivot_row, swap_with_row]] = augmented_matrix[[swap_with_row, pivot_row]]
                    forward_steps.append({ "message": f"Bước {len(forward_steps)}: Đổi hàng {pivot_row + 1} và {swap_with_row + 1} để có phần tử giải khác 0.", "matrix": augmented_matrix.copy().tolist() })
            
            pivot_element = augmented_matrix[pivot_row, col_index]
            if abs(pivot_element) < ZERO_TOLERANCE:
                col_index += 1
                continue
            
            pivot_columns.append(col_index)
            for i in range(pivot_row + 1, num_rows):
                factor = augmented_matrix[i, col_index] / pivot_element
                if abs(factor) > ZERO_TOLERANCE:
                    augmented_matrix[i, :] -= factor * augmented_matrix[pivot_row, :]
            
            augmented_matrix[np.abs(augmented_matrix) < ZERO_TOLERANCE] = 0.0
            forward_steps.append({ "message": f"Bước {len(forward_steps)}: Dùng hàng {pivot_row+1} để khử các phần tử trong cột {col_index+1}.", "matrix": augmented_matrix.copy().tolist() })
            pivot_row += 1
            col_index += 1

        rank = pivot_row
        for r in range(rank, num_rows):
            if np.any(np.abs(augmented_matrix[r, num_vars:]) > ZERO_TOLERANCE):
                return { "success": True, "status": "no_solution", "message": f"Hệ phương trình vô nghiệm (Hạng(A) < Hạng([A|B])).", "forward_steps": forward_steps, "backward_steps": [] }
        
        backward_steps = []
        if rank < num_vars: # VÔ SỐ NGHIỆM
            free_vars_indices = [i for i in range(num_vars) if i not in pivot_columns]
            
            Xp = np.zeros((num_vars, num_b_cols))
            y = augmented_matrix[:, num_vars:]
            for i in range(rank - 1, -1, -1):
                pivot_col = pivot_columns[i]
                sum_val = augmented_matrix[i, pivot_col+1:num_vars] @ Xp[pivot_col+1:, :]
                Xp[pivot_col, :] = (y[i, :] - sum_val) / augmented_matrix[i, pivot_col]

            num_free_vars = len(free_vars_indices)
            null_space_vectors = np.zeros((num_vars, num_free_vars))
            for k, free_idx in enumerate(free_vars_indices):
                v = np.zeros(num_vars)
                v[free_idx] = 1
                for i in range(rank - 1, -1, -1):
                    pivot_col = pivot_columns[i]
                    sum_val = np.dot(augmented_matrix[i, pivot_col+1:num_vars], v[pivot_col+1:])
                    v[pivot_col] = -sum_val / augmented_matrix[i, pivot_col]
                null_space_vectors[:, k] = v
            
            return {
                "success": True, "status": "infinite_solutions",
                "message": f"Hệ có vô số nghiệm (Hạng={rank} < Số ẩn={num_vars}).",
                "forward_steps": forward_steps, "backward_steps": [],
                "general_solution": {
                    "particular_solution": Xp.tolist(),
                    "null_space_vectors": null_space_vectors.tolist(),
                    "num_free_vars": num_free_vars
                }
            }
        else: # NGHIỆM DUY NHẤT
            solution = np.zeros((num_vars, num_b_cols))
            for i in range(rank - 1, -1, -1):
                sum_ax = augmented_matrix[i, i+1:num_vars] @ solution[i+1:, :]
                x_i_row = (augmented_matrix[i, num_vars:] - sum_ax) / augmented_matrix[i, i]
                solution[i, :] = x_i_row
                backward_steps.append({ "message": f"Bước {len(backward_steps)+1}: Từ hàng {i+1}, tính dòng {i+1} của ma trận nghiệm X.", "solution_so_far": solution.copy().tolist()})
            
            return {
                "success": True, "status": "unique_solution", "message": "Hệ phương trình có nghiệm duy nhất.",
                "solution": solution.tolist(), "forward_steps": forward_steps, "backward_steps": backward_steps
            }
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi nghiêm trọng: {traceback.format_exc()}"}
import numpy as np

def solve_inverse_gauss_jordan(A, **kwargs):
    """
    Tính ma trận nghịch đảo bằng phương pháp Gauss-Jordan.
    Biến đổi ma trận [A|E] thành [E|A⁻¹].
    """
    try:
        if A.shape[0] != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}
        
        n = A.shape[0]
        # Tạo ma trận bổ sung [A|E]
        E = np.identity(n)
        aug_matrix = np.hstack((A.copy(), E.copy()))
        
        steps = []
        steps.append({
            "message": "Bước 0: Ma trận bổ sung ban đầu [A|E]",
            "matrix": aug_matrix.tolist()
        })

        # Quá trình khử về dạng bậc thang
        for i in range(n):
            # Tìm pivot
            pivot_row = i
            max_val = abs(aug_matrix[i, i])
            for j in range(i + 1, n):
                if abs(aug_matrix[j, i]) > max_val:
                    max_val = abs(aug_matrix[j, i])
                    pivot_row = j
            
            # Hoán vị hàng nếu cần
            if pivot_row != i:
                aug_matrix[[i, pivot_row]] = aug_matrix[[pivot_row, i]]
                steps.append({
                    "message": f"Bước {len(steps)}: Hoán vị hàng {i+1} và {pivot_row+1}",
                    "matrix": aug_matrix.tolist()
                })

            pivot_val = aug_matrix[i, i]
            if np.isclose(pivot_val, 0):
                return {"success": False, "error": "Ma trận suy biến, không có nghịch đảo."}

            # Chuẩn hóa hàng pivot
            aug_matrix[i, :] /= pivot_val
            steps.append({
                "message": f"Bước {len(steps)}: Chuẩn hóa hàng {i+1} (chia cho {pivot_val:.4f})",
                "matrix": aug_matrix.tolist()
            })

            # Khử các phần tử khác trong cột pivot
            for j in range(n):
                if i != j:
                    factor = aug_matrix[j, i]
                    aug_matrix[j, :] -= factor * aug_matrix[i, :]
            
            steps.append({
                "message": f"Bước {len(steps)}: Khử các phần tử khác trong cột {i+1}",
                "matrix": aug_matrix.tolist()
            })

        inv_A = aug_matrix[:, n:]
        check_matrix = A @ inv_A
        
        return {
            "success": True,
            "message": "Tính ma trận nghịch đảo bằng Gauss-Jordan thành công.",
            "inverse": inv_A.tolist(),
            "check": check_matrix.tolist(),
            "steps": steps
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
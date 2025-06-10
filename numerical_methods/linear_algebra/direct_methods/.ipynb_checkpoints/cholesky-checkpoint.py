import numpy as np
import cmath

def complex_to_dict(c):
    """Chuyển đổi một số phức thành object có thể serialize."""
    return {'re': c.real, 'im': c.imag}

def serialize_matrix(matrix):
    """Chuyển đổi ma trận (có thể chứa số phức) thành list có thể serialize."""
    matrix = np.atleast_2d(matrix)
    if np.iscomplexobj(matrix):
        return [[complex_to_dict(cell) for cell in row] for row in matrix]
    return matrix.tolist()

def solve_cholesky(matrix_a, matrix_b):
    """
    Giải hệ phương trình AX=B bằng phương pháp Cholesky.
    Cải thiện thông báo lỗi để rõ ràng và chính xác hơn.
    """
    try:
        n = matrix_a.shape[0]
        if n != matrix_a.shape[1]:
            return {"success": False, "error": "Phương pháp Cholesky yêu cầu ma trận A phải là ma trận vuông."}

        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)

        is_symmetric = np.allclose(matrix_a, matrix_a.T)
        
        M = matrix_a
        d = matrix_b
        
        transformation_message = "Ma trận A đối xứng, tiến hành phân tách trực tiếp."
        if not is_symmetric:
            transformation_message = "Ma trận A không đối xứng. Chuyển hệ về dạng AᵀAx = Aᵀb."
            M = matrix_a.T @ matrix_a
            d = matrix_a.T @ matrix_b
        
        # Thêm bước kiểm tra tính xác định dương tường minh bằng giá trị riêng
        try:
            eigenvalues = np.linalg.eigvalsh(M)
            if np.min(eigenvalues) <= 1e-15:
                err_msg = "Lỗi: Ma trận không xác định dương (có giá trị riêng không dương)."
                if not is_symmetric:
                     err_msg = "Lỗi: Ma trận A không đối xứng và ma trận AᵀA tạo ra không xác định dương."
                return {"success": False, "error": err_msg}
        except np.linalg.LinAlgError:
            return {"success": False, "error": "Lỗi tính toán giá trị riêng. Ma trận có vấn đề về số học."}

        # Bước phân tách Cholesky M = U^T * U
        U = np.zeros((n, n), dtype=float) # Khởi tạo là float, sẽ chuyển sang complex nếu cần
        for i in range(n):
            sum_k = U[:i, i].T.conjugate() @ U[:i, i]
            val_inside_sqrt = M[i, i] - sum_k
            
            U[i, i] = np.sqrt(val_inside_sqrt)
            
            for j in range(i + 1, n):
                sum_k = U[:i, i].T.conjugate() @ U[:i, j]
                U[i, j] = (M[i, j] - sum_k) / U[i, i]
        
        decomposition_steps = { "U": serialize_matrix(U), "Ut": serialize_matrix(U.T.conjugate()), "M": M.tolist(), "d": d.tolist() }

        # Giải hệ
        Ut = U.T.conjugate()
        y = np.linalg.solve(Ut, d)
        x = np.linalg.solve(U, y)
        
        return {
            "success": True, "status": "unique_solution",
            "message": "Hệ có nghiệm duy nhất tìm bằng phân tách Cholesky.",
            "transformation_message": transformation_message,
            "solution": serialize_matrix(x),
            "decomposition": decomposition_steps,
            "intermediate_y": serialize_matrix(y)
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi nghiêm trọng: {traceback.format_exc()}"}
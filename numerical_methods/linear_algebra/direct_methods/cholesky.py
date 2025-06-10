import numpy as np
import cmath

def serialize_matrix(matrix):
    import numpy as np
    matrix = np.atleast_2d(matrix)
    def safe_number(val):
        if isinstance(val, (float, np.floating)):
            if np.isnan(val):
                return "NaN"
            if np.isposinf(val):
                return "Infinity"
            if np.isneginf(val):
                return "-Infinity"
            return float(val)
        return val
    if np.iscomplexobj(matrix):
        def complex_to_dict(c):
            return {'re': safe_number(c.real), 'im': safe_number(c.imag)}
        return [[complex_to_dict(cell) for cell in row] for row in matrix]
    return [[safe_number(cell) for cell in row] for row in matrix]

def cholesky_decomposition(A):
    """
    Phân tích Cholesky: A = LL^T, trả về L và các bước trung gian.
    """
    n = len(A)
    L = np.zeros((n, n))
    steps = []
    for i in range(n):
        for j in range(i+1):
            if i == j:
                sum_ = sum(L[i][k]**2 for k in range(j))
                L[i][j] = np.sqrt(A[i][i] - sum_)
            else:
                sum_ = sum(L[i][k]*L[j][k] for k in range(j))
                L[i][j] = (A[i][j] - sum_) / L[j][j]
        steps.append({
            'step': i+1,
            'L': L.copy()
        })
    return L, steps

def solve_cholesky(matrix_a, matrix_b):
    """
    Giải hệ phương trình AX=B bằng phương pháp Cholesky.
    Đảm bảo mọi giá trị trả về đều JSON serializable.
    """
    try:
        # Nếu đầu vào là list, chuyển sang np.ndarray
        matrix_a = np.array(matrix_a)
        matrix_b = np.array(matrix_b)

        # Nếu B là vector, reshape về cột
        if matrix_b.ndim == 1:
            matrix_b = matrix_b.reshape(-1, 1)

        is_symmetric = np.allclose(matrix_a, matrix_a.T)
        if is_symmetric:
            M = matrix_a
            d = matrix_b
            transformation_message = "Ma trận A đối xứng, tiến hành phân tách trực tiếp."
        else:
            transformation_message = "Ma trận A không đối xứng. Chuyển hệ về dạng AᵀAx = Aᵀb."
            M = matrix_a.T @ matrix_a
            d = matrix_a.T @ matrix_b

        n = M.shape[0]

        # Kiểm tra xác định dương bằng giá trị riêng
        try:
            eigenvalues = np.linalg.eigvalsh(M)
            if np.min(eigenvalues) <= 1e-12:
                if not is_symmetric:
                    err_msg = "Ma trận A không đối xứng và ma trận AᵀA tạo ra không xác định dương. Không thể giải bằng Cholesky."
                else:
                    err_msg = "Ma trận không xác định dương (có giá trị riêng không dương). Không thể giải bằng Cholesky."
                return {"success": False, "error": err_msg}
        except np.linalg.LinAlgError:
            return {"success": False, "error": "Lỗi tính toán giá trị riêng. Ma trận có vấn đề về số học."}

        # Bước phân tách Cholesky M = U^T * U
        U = np.zeros((n, n), dtype=float)
        for i in range(n):
            sum_k = U[:i, i].T.conjugate() @ U[:i, i]
            val_inside_sqrt = M[i, i] - sum_k
            if val_inside_sqrt <= 0:
                return {"success": False, "error": "Ma trận không xác định dương, không thể phân tích Cholesky."}
            U[i, i] = np.sqrt(val_inside_sqrt)
            for j in range(i + 1, n):
                sum_k = U[:i, i].T.conjugate() @ U[:i, j]
                U[i, j] = (M[i, j] - sum_k) / U[i, i]

        decomposition_steps = {
            "U": serialize_matrix(U),
            "Ut": serialize_matrix(U.T.conjugate()),
            "M": serialize_matrix(M),
            "d": serialize_matrix(d)
        }

        # Giải hệ
        Ut = U.T.conjugate()
        y = np.linalg.solve(Ut, d)
        x = np.linalg.solve(U, y)

        # Đảm bảo mọi giá trị trả về đều là kiểu Python cơ bản
        return {
            "success": True,
            "status": "unique_solution",
            "message": "Hệ có nghiệm duy nhất tìm bằng phân tách Cholesky.",
            "transformation_message": transformation_message,
            "solution": serialize_matrix(x),
            "decomposition": decomposition_steps,
            "intermediate_y": serialize_matrix(y)
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": str(traceback.format_exc())}

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

# Trong tất cả các hàm trả về kết quả số, hãy áp dụng zero_small trước khi trả về.
# Ví dụ:
# return zero_small(result)
# hoặc nếu trả về dict, hãy zero_small cho từng trường số/mảng số.
import numpy as np
import scipy.linalg

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

def lu_decomposition(A):
    """
    Phân tích LU không pivoting, trả về L, U và các bước trung gian.
    """
    A = np.array(A, dtype=float)
    n, m = A.shape
    if n != m:
        raise ValueError("Ma trận A phải là ma trận vuông.")
    if np.linalg.matrix_rank(A) < n:
        raise ValueError("Ma trận A suy biến, không thể phân tích LU (det(A) = 0).")
    L = np.zeros((n, n))
    U = np.zeros((n, n))
    steps = []
    for i in range(n):
        for k in range(i, n):
            sum_ = sum(L[i][j] * U[j][k] for j in range(i))
            U[i][k] = A[i][k] - sum_
        if np.isclose(U[i][i], 0):
            raise ValueError(f"Phần tử U[{i},{i}] = 0. Hệ có thể vô nghiệm hoặc vô số nghiệm, không thể phân tích LU.")
        L[i][i] = 1
        for k in range(i+1, n):
            sum_ = sum(L[k][j] * U[j][i] for j in range(i))
            L[k][i] = (A[k][i] - sum_) / U[i][i]
        steps.append({
            'step': i+1,
            'L': L.copy(),
            'U': U.copy()
        })
    return L, U, steps

def gauss_jordan(aug):
    aug = aug.astype(float)
    n, m = aug.shape
    pivots = []
    row = 0
    for col in range(m):
        if row >= n:
            break
        max_row = np.argmax(np.abs(aug[row:, col])) + row
        if np.isclose(aug[max_row, col], 0):
            continue
        if max_row != row:
            aug[[row, max_row]] = aug[[max_row, row]]
        aug[row] = aug[row] / aug[row, col]
        for r in range(n):
            if r != row:
                aug[r] -= aug[r, col] * aug[row]
        pivots.append(col)
        row += 1
    return aug, pivots

def extract_general_solution(rref, pivots, n, num_rhs):
    m = rref.shape[1] - num_rhs
    free_vars = [i for i in range(m) if i not in pivots]
    solutions = []
    for rhs in range(num_rhs):
        sol = {}
        for i in range(m):
            if i in pivots:
                row = pivots.index(i)
                sol[f"x{i+1}"] = rref[row, m+rhs]
            else:
                sol[f"x{i+1}"] = f"t_{free_vars.index(i)+1}"
        solutions.append(sol)
    return solutions

def serialize_matrix(matrix):
    import numpy as np
    matrix = np.atleast_2d(matrix)
    if np.iscomplexobj(matrix):
        def complex_to_dict(c):
            return {'re': c.real, 'im': c.imag}
        return [[complex_to_dict(cell) for cell in row] for row in matrix]
    return matrix.tolist()

def solve_lu(matrix_a, matrix_b):
    """
    Giải hệ phương trình AX=B bằng phân rã LU (có pivoting),
    trả về nghiệm đúng cho cả 3 trường hợp (vô nghiệm, duy nhất, vô số nghiệm),
    hỗ trợ nhiều vế phải.
    Tất cả các số có trị tuyệt đối nhỏ hơn 1e-15 sẽ được làm tròn thành 0 trong kết quả trả về.
    Ngoài ra, trả về các bước trung gian của LU không pivoting (lu_steps).
    """
    try:
        A = np.asarray(matrix_a, dtype=float)
        B = np.asarray(matrix_b, dtype=float)
        if B.ndim == 1:
            B = B.reshape(-1, 1)
        m, n = A.shape
        if m != B.shape[0]:
            return {"success": False, "error": "Số hàng của A và B không khớp."}
        # 1. Phân rã LU có pivoting
        try:
            P, L, U = scipy.linalg.lu(A)
        except Exception as e:
            return {"success": False, "error": f"Lỗi khi phân rã LU: {e}"}
        # 1b. Phân rã LU không pivoting để lấy các bước trung gian
        try:
            _, _, lu_steps = lu_decomposition(A)
            # Chuyển các bước sang dạng list để tương thích JSON
            lu_steps_serialized = []
            for step in lu_steps:
                lu_steps_serialized.append({
                    'step': step['step'],
                    'L': zero_small(step['L']).tolist(),
                    'U': zero_small(step['U']).tolist()
                })
        except Exception as e:
            lu_steps_serialized = []
        # 2. Phân tích hạng
        rank_A = np.linalg.matrix_rank(A)
        AB = np.hstack((A, B))
        rank_AB = np.linalg.matrix_rank(AB)
        # 3. Kết luận và tìm nghiệm
        if rank_A < rank_AB:
            return {
                "success": True,
                "status": "no_solution",
                "message": f"Hệ vô nghiệm (rank(A)={rank_A} < rank([A|B])={rank_AB})",
                "decomposition": {"L": zero_small(L).tolist(), "U": zero_small(U).tolist(), "P": zero_small(P).tolist()},
                "intermediate_y": None,
                "lu_steps": lu_steps_serialized
            }
        elif rank_A == n:
            # Nghiệm duy nhất
            ket_luan = f"Hệ có nghiệm duy nhất (rank(A) = rank([A|B]) = {rank_A} = số ẩn)"
            # Giải Ly = PB
            Y = scipy.linalg.solve_triangular(L, P @ B, lower=True)
            # Giải UX = Y
            X = scipy.linalg.solve_triangular(U, Y)
            return {
                "success": True,
                "status": "unique_solution",
                "message": ket_luan,
                "solution": zero_small(X).tolist(),
                "decomposition": {"L": zero_small(L).tolist(), "U": zero_small(U).tolist(), "P": zero_small(P).tolist()},
                "intermediate_y": zero_small(Y).tolist(),
                "lu_steps": lu_steps_serialized
            }
        else:
            # Vô số nghiệm
            ket_luan = f"Hệ có vô số nghiệm (rank(A) = {rank_A} < số ẩn = {n})"
            # Nghiệm riêng (least squares)
            nghiem_rieng, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
            # Null space
            null_space = scipy.linalg.null_space(A)
            return {
                "success": True,
                "status": "infinite_solutions",
                "message": ket_luan,
                "decomposition": {"L": zero_small(L).tolist(), "U": zero_small(U).tolist(), "P": zero_small(P).tolist()},
                "intermediate_y": None,
                "general_solution": {
                    "particular_solution": zero_small(nghiem_rieng).tolist(),
                    "null_space_vectors": zero_small(null_space).tolist(),
                    "num_free_vars": null_space.shape[1] if null_space.ndim == 2 else 0
                },
                "lu_steps": lu_steps_serialized
            }
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi nghiêm trọng: {traceback.format_exc()}"}
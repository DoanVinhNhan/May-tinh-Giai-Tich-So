import numpy as np

def getCharPolynomial(A):
    """
    Lấy đa thức đặc trưng từ ma trận Frobenius (dạng đồng hành).
    """
    n = A.shape[0]
    p = np.zeros(n + 1, dtype=float)
    p[0] = 1.0
    if n > 0:
        p[1:] = -A[0, :].real
    return p

def danilevsky_algorithm(A):
    """
    Thuật toán Danilevsky - Phiên bản ổn định và tương thích JSON.
    """
    if A.shape[0] != A.shape[1]:
        return {'success': False, 'error': 'Ma trận đầu vào phải là ma trận vuông.'}

    # --- Các hàm phụ để định dạng, đảm bảo tương thích JSON ---
    def format_complex_number(c):
        """Chuyển đổi một số phức thành chuỗi hoặc số thực."""
        if not isinstance(c, complex) or abs(c.imag) < 1e-9:
            # Sử dụng .real để lấy phần thực nếu c là số phức có phần ảo nhỏ
            real_part = c.real if isinstance(c, complex) else c
            return float(f"{real_part:.10g}")
        return f"{c.real:.10g}{c.imag:+.10g}j"

    def format_matrix_for_json(m):
        """Định dạng một ma trận NumPy (có thể chứa số phức) thành list các list tương thích JSON."""
        return [[format_complex_number(c) for c in row] for row in m.tolist()]

    n = A.shape[0]
    similar = A.copy().astype(complex)
    back = np.eye(n, dtype=complex)
    steps_log = [{'desc': 'Ma trận ban đầu', 'matrix': format_matrix_for_json(A.copy())}]

    # --- Giai đoạn 1: Biến đổi ma trận về dạng tam giác trên theo khối Frobenius ---
    for k in range(n - 1, 0, -1):
        if abs(similar[k, k - 1]) < 1e-9:
            swap_col_j = -1
            for j in range(k - 2, -1, -1):
                if abs(similar[k, j]) > 1e-9:
                    swap_col_j = j
                    break
            
            if swap_col_j == -1:
                steps_log.append({'desc': f'Hàng {k+1} không cần biến đổi (tạo thành khối riêng).', 'matrix': format_matrix_for_json(similar.copy())})
                continue
            
            j = swap_col_j
            P = np.eye(n)
            P[j, j], P[k - 1, k - 1] = 0, 0
            P[j, k - 1], P[k - 1, j] = 1, 1
            
            similar = P @ similar @ P
            back = back @ P
            steps_log.append({
                'desc': f'Hoán vị cột {j+1} và {k} để tạo phần tử giải.',
                'matrix': format_matrix_for_json(similar.copy()),
                'C': format_matrix_for_json(P)
            })

        M = np.eye(n, dtype=complex)
        M[k - 1, :] = similar[k, :]
        
        # Kiểm tra nếu M suy biến trước khi tính nghịch đảo
        if np.linalg.cond(M) > 1/np.finfo(M.dtype).eps:
             return {'success': False, 'error': f'Ma trận biến đổi M ở bước k={k} bị suy biến, không thể tiếp tục.'}

        M_inv = np.linalg.inv(M)

        similar = M @ similar @ M_inv
        back = back @ M_inv
        steps_log.append({
            'desc': f'Sau khi biến đổi hàng {k+1}.',
            'matrix': format_matrix_for_json(similar.copy()),
            'M': format_matrix_for_json(M),
            'M_inv': format_matrix_for_json(M_inv)
        })
        
    steps_log.append({'desc': 'Ma trận cuối (dạng tam giác trên theo khối Frobenius)', 'matrix': format_matrix_for_json(similar.copy())})
    
    # --- Giai đoạn 2: Trích xuất kết quả từ các khối ---
    final_eigenvalues = []
    final_eigenvectors = []

    boundaries = [n]
    for k in range(n - 1, 0, -1):
        if np.all(np.abs(similar[k, :k]) < 1e-9):
            boundaries.append(k)
    boundaries.append(0)
    boundaries = sorted(list(set(boundaries)))

    for i in range(len(boundaries) - 1):
        start, end = boundaries[i], boundaries[i+1]
        F_block = similar[start:end, start:end]
        
        poly_coeffs = getCharPolynomial(F_block)
        eigvals = np.roots(poly_coeffs)
        final_eigenvalues.extend(eigvals)
        
        for val in eigvals:
            y_F = np.power(val, np.arange(F_block.shape[0] - 1, -1, -1)).reshape(-1, 1)
            y_similar = np.zeros((n, 1), dtype=complex)
            y_similar[start:end, :] = y_F
            x_A = back @ y_similar
            final_eigenvectors.append(x_A)

    # --- Giai đoạn 3: Định dạng kết quả cuối cùng cho JSON ---
    def format_eigenvector(v):
        max_abs_idx = np.argmax(np.abs(v))
        if np.abs(v[max_abs_idx, 0]) > 1e-9:
            v = v / v[max_abs_idx, 0]
        
        formatted_list = [format_complex_number(c) for c in v.flatten()]
        return [[item] for item in formatted_list]

    total_char_poly_coeffs = np.poly(final_eigenvalues)

    results = {
        'success': True,
        'eigenvalues': [format_complex_number(v) for v in final_eigenvalues],
        'eigenvectors': [format_eigenvector(vec) for vec in final_eigenvectors],
        'frobenius_matrix': "Ma trận cuối cùng là dạng tam giác trên theo khối Frobenius",
        'char_poly': [format_complex_number(c) for c in total_char_poly_coeffs],
        'steps': steps_log
    }
    return results
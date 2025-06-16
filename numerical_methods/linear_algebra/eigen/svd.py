import numpy as np

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

def svd_power_deflation(A, num_singular=None, num_iter=20, tol=1e-15, y_init=None):
    """
    Tính SVD của ma trận A bằng phương pháp power method + deflation.
    Trả về step-by-step cho từng giá trị kỳ dị, ghi rõ ma trận deflation và vector riêng tại mỗi bước.
    
    THUẬT TOÁN ĐÚNG:
    1. Tính B₀ = A^T * A
    2. Dùng power method để tìm λ₁ và v₁ từ B₀
    3. Deflation: B₁ = B₀ - λ₁ * v₁ * v₁^T
    4. Lặp lại trên B₁ để tìm λ₂, v₂, ...
    
    Args:
        A: np.ndarray, ma trận đầu vào (m, n)
        num_singular: số giá trị kỳ dị cần tìm (mặc định: min(m, n))
        num_iter: số bước lặp tối đa cho mỗi singular value
        tol: ngưỡng hội tụ
        y_init: vector khởi đầu (n, 1) hoặc (n,) cho lần đầu (nếu None thì dùng ngẫu nhiên)
    Returns:
        dict: chứa U, Sigma, V_transpose, và step-by-step
    """
    A = np.array(A, dtype=float)
    m, n = A.shape
    
    # Chia trường hợp để tối ưu hiệu quả
    if m < n:
        # Trường hợp m > n: Dùng A^T * A để tìm right singular vectors
        Matrix_work = A.T @ A  # Kích thước (n, n)
        vector_size = n  # Vector có kích thước n
        use_ATA = True
    else:
        # Trường hợp m <= n: Dùng A * A^T để tìm left singular vectors
        Matrix_work = A @ A.T  # Kích thước (m, m)
        vector_size = m  # Vector có kích thước m
        use_ATA = False
    
    Matrix_work_original = Matrix_work.copy()
    singular_values = []
    vectors = []  # Sẽ chứa right vectors (nếu m>n) hoặc left vectors (nếu m<=n)
    steps = []
    
    # Số giá trị kỳ dị tối đa có thể tìm
    max_singular = min(m, n)
    k = num_singular if num_singular is not None else max_singular
    k = min(k, max_singular)  # Đảm bảo không vượt quá giới hạn
    
    for s in range(k):
        # Khởi tạo véctơ khởi đầu với kích thước phù hợp
        if s == 0 and y_init is not None:
            y = np.array(y_init).reshape(-1, 1)
            if y.shape[0] != vector_size:
                raise ValueError(f"Vector khởi đầu phải có kích thước ({vector_size}, 1) hoặc ({vector_size},)")
            y = y / np.linalg.norm(y)
        else:
            y = np.random.rand(vector_size, 1)
            y = y / np.linalg.norm(y)
        
        y_steps = [y.copy()]
        lambda_steps = []
        matrix_before_deflation = Matrix_work.copy()
        
        # Power method trên Matrix_work
        for i in range(num_iter):
            y_new = Matrix_work @ y
            norm_y_new = np.linalg.norm(y_new)
            
            if norm_y_new < tol:
                # Ma trận đã cạn kiệt, không còn giá trị kỳ dị có ý nghĩa
                break
                
            y_new = y_new / norm_y_new
            lambda_new = float(y_new.T @ Matrix_work @ y_new)
            
            y = y_new
            y_steps.append(y.copy())
            lambda_steps.append(lambda_new)
            
            # Kiểm tra hội tụ
            if i > 0 and abs(lambda_steps[-1] - lambda_steps[-2]) < tol:
                break
        
        # Nếu không tìm được giá trị riêng có ý nghĩa, dừng lại
        if not lambda_steps or lambda_steps[-1] < tol:
            break
            
        # Tính singular value từ eigenvalue
        singular = np.sqrt(abs(lambda_steps[-1]))
        singular_values.append(singular)
        
        # Normalize vector
        y = y / np.linalg.norm(y)
        vectors.append(y.copy())
        
        # DEFLATION ĐÚNG: Thực hiện trên chính ma trận Matrix_work
        # B_{k+1} = B_k - λ_k * v_k * v_k^T
        Matrix_work = Matrix_work - lambda_steps[-1] * (y @ y.T)
        
        # Lưu step-by-step
        steps.append({
            'singular_index': s+1,
            'deflation_matrix_before': zero_small(matrix_before_deflation).tolist(),
            'deflation_matrix_after': zero_small(Matrix_work.copy()).tolist(),
            'lambda_steps': [float(l) for l in lambda_steps],
            'y_steps': [v.flatten().tolist() for v in y_steps],
            'singular_value': float(singular),
            'vector': y.flatten().tolist(),
        })
    
    # Nếu không tìm được giá trị kỳ dị nào
    if not singular_values:
        return {
            'success': False,
            'error': 'Không thể tìm được giá trị kỳ dị nào với tolerance đã cho'
        }
    
    # Tạo ma trận U và V tùy theo trường hợp
    if use_ATA:
        # Trường hợp m > n: vectors chứa right singular vectors
        V = np.hstack(vectors) if vectors else np.zeros((n, 1))
        # Tính U = A * V * Σ^(-1)
        U_list = []
        for i in range(len(singular_values)):
            sigma = singular_values[i]
            if sigma > tol:
                u = A @ vectors[i] / sigma
                # Normalize u
                u_norm = np.linalg.norm(u)
                if u_norm > tol:
                    u = u / u_norm
                U_list.append(u)
        U = np.hstack(U_list) if U_list else np.zeros((m, 1))
    else:
        # Trường hợp m <= n: vectors chứa left singular vectors
        U = np.hstack(vectors) if vectors else np.zeros((m, 1))
        # Tính V = A^T * U * Σ^(-1)
        V_list = []
        for i in range(len(singular_values)):
            sigma = singular_values[i]
            if sigma > tol:
                v = A.T @ vectors[i] / sigma
                # Normalize v
                v_norm = np.linalg.norm(v)
                if v_norm > tol:
                    v = v / v_norm
                V_list.append(v)
        V = np.hstack(V_list) if V_list else np.zeros((n, 1))
    
    # Tạo Sigma matrix (full size)
    Sigma = np.zeros((m, n))
    num_values = min(len(singular_values), min(m, n))
    for i in range(num_values):
        Sigma[i, i] = singular_values[i]
    
    # Tính rank thực sự (số giá trị kỳ dị > ngưỡng)
    effective_singular_values = [s for s in singular_values if s > tol]
    r = len(effective_singular_values)
    
    # Tạo dạng rút gọn dựa trên rank thực sự
    diag_len = r if r > 0 else 1
    U_reduced = U[:, :diag_len] if U.shape[1] >= diag_len else U
    Sigma_reduced = np.diag(effective_singular_values) if r > 0 else np.zeros((1, 1))
    Vt_reduced = V.T[:diag_len, :] if V.shape[1] >= diag_len else V.T
    # Tổng thành phần
    svd_sum_components = []
    for i in range(len(effective_singular_values)):
        if i < U.shape[1] and i < V.shape[1]:
            svd_sum_components.append({
                "sigma": float(effective_singular_values[i]),
                "u": U[:, i].tolist(),
                "v": V[:, i].tolist()
            })
    
    # Tính ma trận xấp xỉ từ SVD
    def compute_approximations():
        # Xấp xỉ đầy đủ
        A_full_approx = U_reduced @ Sigma_reduced @ Vt_reduced
        
        # Xấp xỉ rút gọn (chỉ dùng rank thực sự)  
        A_reduced_approx = U_reduced @ Sigma_reduced @ Vt_reduced
        
        # Xấp xỉ từng thành phần (rank-1 approximations)
        rank_approximations = []
        A_cumulative = np.zeros_like(A)
        
        for i in range(r):
            if i < len(effective_singular_values) and i < U.shape[1] and i < V.shape[1]:
                # Xấp xỉ rank-1: σᵢ * uᵢ * vᵢ^T
                rank_1_approx = effective_singular_values[i] * np.outer(U[:, i], V[:, i])
                A_cumulative += rank_1_approx
                
                rank_approximations.append({
                    "rank": i + 1,
                    "singular_value": float(effective_singular_values[i]),
                    "rank_1_component": zero_small(rank_1_approx).tolist(),
                    "cumulative_approximation": zero_small(A_cumulative.copy()).tolist(),
                    "frobenius_error": float(np.linalg.norm(A - A_cumulative, 'fro'))
                })
        
        return {
            "full_approximation": zero_small(A_full_approx).tolist(),
            "reduced_approximation": zero_small(A_reduced_approx).tolist(), 
            "rank_approximations": rank_approximations,
            "reconstruction_error_full": float(np.linalg.norm(A - A_full_approx, 'fro')),
            "reconstruction_error_reduced": float(np.linalg.norm(A - A_reduced_approx, 'fro'))
        }
    
    approximations = compute_approximations()
    
    # Trả về kết quả
    return {
        'success': True,
        'rank': r,
        'U': zero_small(U).tolist(),
        'Sigma': zero_small(Sigma).tolist(),
        'V_transpose': zero_small(V.T).tolist(),
        'U_reduced': zero_small(U_reduced).tolist(),
        'Sigma_reduced': zero_small(Sigma_reduced).tolist(),
        'Vt_reduced': zero_small(Vt_reduced).tolist(),
        'svd_sum_components': svd_sum_components,
        'intermediate_steps': {
            'matrix_used': f"{'A^T*A' if use_ATA else 'A*A^T'} (kích thước {Matrix_work_original.shape})",
            'original_matrix': zero_small(Matrix_work_original).tolist(),
            'singular_values': [float(s) for s in singular_values],
            'effective_rank': r,
            'steps': steps
        },
        "approximations": approximations
    }

def svd_numpy(A):
    """
    Tính SVD bằng numpy (chuẩn).
    Args:
        A: np.ndarray, ma trận đầu vào (m, n)
    Returns:
        dict: chứa U, Sigma, V_transpose, và các bước trung gian
    """
    try:
        if A.size == 0:
            return {"success": False, "error": "Ma trận đầu vào không được rỗng."}
        m, n = A.shape
        U, s, Vt = np.linalg.svd(A, full_matrices=False)
        
        # Tính rank thực sự (số giá trị kỳ dị > ngưỡng)
        effective_singular_values = s[s > 1e-15]  # Lọc giá trị kỳ dị có ý nghĩa
        r = len(effective_singular_values)  # Rank thực sự
        
        # Tạo ma trận Sigma đầy đủ và rút gọn
        Sigma = np.zeros((m, n))
        diag_len_full = min(m, n, s.shape[0])
        Sigma[:diag_len_full, :diag_len_full] = np.diag(s[:diag_len_full])
        
        # Tạo dạng rút gọn dựa trên rank thực sự
        diag_len = r if r > 0 else 1  # Tránh trường hợp r = 0
        U_reduced = U[:, :diag_len]
        Sigma_reduced = np.diag(effective_singular_values) if r > 0 else np.zeros((1, 1))
        Vt_reduced = Vt[:diag_len, :]
        
        return {
            "success": True,
            "rank": r,  # Thêm thông tin rank
            "U": zero_small(U).tolist(),
            "Sigma": zero_small(Sigma).tolist(),
            "V_transpose": zero_small(Vt).tolist(),
            "U_reduced": zero_small(U_reduced).tolist(),
            "Sigma_reduced": zero_small(Sigma_reduced).tolist(),
            "Vt_reduced": zero_small(Vt_reduced).tolist(),
            "svd_sum_components": [
                {
                    "sigma": float(sigma_i),
                    "u": u_i.tolist(),
                    "v": v_i.tolist()
                }
                for sigma_i, u_i, v_i in zip(effective_singular_values, U.T[:r], Vt[:r])  # Chỉ lấy r thành phần có ý nghĩa
            ],
            "intermediate_steps": {
                "note": "Không có các bước trung gian chi tiết khi dùng numpy.linalg.svd.",
                "effective_rank": r  # Thông tin rank
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Lỗi trong quá trình tính toán SVD (numpy): {str(e)}"}

def calculate_svd(A, method='default', **kwargs):
    """
    Thực hiện phân tích giá trị kỳ dị (SVD) cho một ma trận A.
    method: 'default' (dùng numpy), 'power' (dùng power method + deflation)
    kwargs: các tham số cho power method (num_singular, num_iter, tol, y_init)
    """
    if method == 'power':
        num_singular = kwargs.get('num_singular', None)
        num_iter = kwargs.get('num_iter', 20)
        tol = kwargs.get('tol', 1e-8)
        y_init = kwargs.get('y_init', None)
        return svd_power_deflation(A, num_singular=num_singular, num_iter=num_iter, tol=tol, y_init=y_init)
    else:
        return svd_numpy(A)

def calculate_svd_approximation(A, method='rank-k', **kwargs):
    """
    Tính toán xấp xỉ ma trận A bằng SVD dựa trên các phương pháp khác nhau.

    Args:
        A (np.ndarray): Ma trận đầu vào.
        method (str): Phương pháp xấp xỉ ('rank-k', 'threshold', 'error-bound').
        **kwargs: Các tham số cho từng phương pháp:
            k (int): Hạng mong muốn cho 'rank-k'.
            threshold (float): Ngưỡng giá trị kỳ dị cho 'threshold'.
            error_bound (float): Ngưỡng sai số TƯƠNG ĐỐI cho 'error-bound'.

    Returns:
        dict: Một từ điển chứa kết quả chi tiết.
    """
    try:
        A = np.array(A, dtype=float)
        if A.ndim != 2:
            return {"success": False, "error": "Đầu vào phải là một ma trận 2D."}

        U, s, Vt = np.linalg.svd(A, full_matrices=False)
        original_rank = np.sum(s > 1e-10)
        
        # Norm của ma trận gốc, dùng cho sai số tương đối
        A_norm = np.linalg.norm(A)

        k = 0
        method_used = ""
        info = {}

        if method == 'rank-k':
            k = int(kwargs.get('k', 1))
            if k > len(s) or k < 1:
                return {"success": False, "error": f"Hạng k phải nằm trong khoảng [1, {len(s)}]."}
            method_used = f"Xấp xỉ hạng k={k}"
            info['k_requested'] = k

        elif method == 'threshold':
            threshold = float(kwargs.get('threshold', 0.1))
            k = np.sum(s >= threshold)
            if k == 0:
                k = 1 # Giữ lại ít nhất 1 thành phần
            method_used = f"Giữ giá trị kỳ dị >= {threshold}"
            info['threshold'] = threshold

        elif method == 'error-bound':
            # Giá trị error_bound giờ được diễn giải là SAI SỐ TƯƠNG ĐỐI
            relative_error_bound = float(kwargs.get('error_bound', 0.01))
            method_used = f"Sai số tương đối <= {relative_error_bound*100:.2f}%"
            info['target_relative_error_bound'] = relative_error_bound

            if A_norm == 0:
                k = 0
            else:
                # Tính ngưỡng sai số tuyệt đối từ sai số tương đối
                target_absolute_error_norm_sq = (relative_error_bound * A_norm) ** 2
                
                k = len(s)
                cumulative_error_norm_sq = 0
                
                # Lặp từ giá trị kỳ dị nhỏ nhất
                for i in range(len(s) - 1, -1, -1):
                    # Nếu tổng bình phương sai số vẫn nhỏ hơn ngưỡng, ta có thể loại bỏ giá trị kỳ dị này
                    if cumulative_error_norm_sq + s[i]**2 < target_absolute_error_norm_sq:
                        cumulative_error_norm_sq += s[i]**2
                        k -= 1
                    else:
                        break # Dừng lại khi không thể loại bỏ thêm
                
                if k == 0: k = 1 # Giữ ít nhất 1 thành phần

        # Xây dựng lại ma trận xấp xỉ
        A_approx = np.dot(U[:, :k], np.dot(np.diag(s[:k]), Vt[:k, :]))

        error_matrix = A - A_approx
        absolute_error = np.linalg.norm(error_matrix)
        relative_error = (absolute_error / A_norm) * 100 if A_norm > 0 else 0

        # Thông tin chi tiết về các thành phần
        total_energy = np.sum(s**2)
        retained_energy = np.sum(s[:k]**2)
        info['energy_ratio'] = (retained_energy / total_energy) * 100 if total_energy > 0 else 100
        
        retained_components = [{"index": i + 1, "singular_value": val, "contribution": (val**2/total_energy)*100 if total_energy > 0 else 0} for i, val in enumerate(s[:k])]
        discarded_components = [{"index": i + 1, "singular_value": val, "contribution": (val**2/total_energy)*100 if total_energy > 0 else 0} for i, val in enumerate(s[k:], start=k)]

        return {
            "success": True,
            "method_used": method_used,
            "original_matrix": A.tolist(),
            "approximated_matrix": A_approx.tolist(),
            "error_matrix": error_matrix.tolist(),
            "original_rank": int(original_rank),
            "effective_rank": k,
            "absolute_error": absolute_error,
            "relative_error": relative_error,
            "retained_components": retained_components,
            "discarded_components": discarded_components,
            "detailed_info": info
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi tính toán: {str(e)}"}
import numpy as np

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

def svd_power_deflation(A, num_singular=None, num_iter=20, tol=1e-15, y_init=None):
    """
    Tính SVD của ma trận A bằng phương pháp power method + deflation.
    Trả về step-by-step cho từng giá trị kỳ dị, ghi rõ ma trận deflation và vector riêng tại mỗi bước.
    Args:
        A: np.ndarray, ma trận đầu vào (m, n)
        num_singular: số giá trị kỳ dị cần tìm (mặc định: min(m, n))
        num_iter: số bước lặp tối đa cho mỗi singular value
        tol: ngưỡng hội tụ
        y_init: vector khởi đầu (n, 1) hoặc (n,) cho lần đầu (nếu None thì dùng ngẫu nhiên)
    Returns:
        dict: chứa U, Sigma, V_transpose, và step-by-step
    """
    m, n = A.shape
    ATA = A.T @ A
    ATA_work = ATA.copy()
    singular_values = []
    right_vecs = []
    steps = []
    k = num_singular if num_singular is not None else min(m, n)
    for s in range(k):
        # Khởi tạo véctơ khởi đầu
        if s == 0 and y_init is not None:
            y = np.array(y_init).reshape(-1, 1)
            if y.shape[0] != n:
                raise ValueError("Vector khởi đầu phải có kích thước (n, 1) hoặc (n,)")
            y = y / np.linalg.norm(y)
        else:
            y = np.random.rand(n, 1)
            y = y / np.linalg.norm(y)
        y_steps = [y.copy()]
        lambda_steps = []
        matrix_steps = [ATA_work.copy()]
        for i in range(num_iter):
            y_new = ATA_work @ y
            y_new = y_new / np.linalg.norm(y_new)
            lambda_new = float(y_new.T @ ATA_work @ y_new)
            y = y_new
            y_steps.append(y.copy())
            lambda_steps.append(lambda_new)
            if i > 0 and abs(lambda_steps[-1] - lambda_steps[-2]) < tol:
                break
        singular = np.sqrt(abs(lambda_steps[-1]))
        singular_values.append(singular)
        right_vecs.append(y)
        # Deflation: loại bỏ thành phần vừa tìm được
        ATA_work = ATA_work - lambda_steps[-1] * (y @ y.T)
        matrix_steps.append(ATA_work.copy())
        # Lưu step-by-step, ghi rõ ma trận deflation và vector riêng tại mỗi bước
        steps.append({
            'singular_index': s+1,
            'deflation_matrix_before': zero_small(matrix_steps[0]).tolist(),
            'deflation_matrix_after': zero_small(matrix_steps[1]).tolist(),
            'lambda_steps': [float(l) for l in lambda_steps],
            'y_steps': [v.flatten().tolist() for v in y_steps],
            'singular_value': float(singular),
            'right_vec': (y / np.linalg.norm(y)).flatten().tolist(),  # Đưa về chuẩn 2 bằng 1
        })
    # Tạo ma trận V từ các vector riêng tìm được
    V = np.hstack(right_vecs)
    # Tính U = AV/σ
    U = []
    for i in range(len(singular_values)):
        sigma = singular_values[i]
        if sigma > tol:
            u = A @ right_vecs[i] / sigma
        else:
            u = np.zeros((m, 1))
        U.append(u)
    U = np.hstack(U)
    # Chuẩn hóa U
    for i in range(U.shape[1]):
        norm = np.linalg.norm(U[:, i])
        if norm > 0:
            U[:, i] /= norm
    # Tạo Sigma
    Sigma = np.zeros((m, n))
    for i in range(len(singular_values)):
        Sigma[i, i] = singular_values[i]
    # Tính rank thực sự (số giá trị kỳ dị > ngưỡng)
    effective_singular_values = [s for s in singular_values if s > tol]
    r = len(effective_singular_values)  # Rank thực sự
    
    # Tạo dạng rút gọn dựa trên rank thực sự
    diag_len = r if r > 0 else 1  # Tránh trường hợp r = 0
    U_reduced = U[:, :diag_len]
    Sigma_reduced = Sigma[:diag_len, :diag_len]
    Vt_reduced = V.T[:diag_len, :]
    # Tổng thành phần
    svd_sum_components = [
        {
            "sigma": float(singular_values[i]),
            "u": U[:, i].tolist(),
            "v": V[:, i].tolist()
        }
        for i in range(diag_len)
    ]
    # Tính ma trận xấp xỉ từ SVD
    def compute_approximations():
        # Xấp xỉ đầy đủ
        A_full_approx = U @ Sigma @ V.T
        
        # Xấp xỉ rút gọn (chỉ dùng rank thực sự)  
        A_reduced_approx = U_reduced @ Sigma_reduced @ Vt_reduced
        
        # Xấp xỉ từng thành phần (rank-1 approximations)
        rank_approximations = []
        A_cumulative = np.zeros_like(A)
        
        for i in range(r):
            # Xấp xỉ rank-1: σᵢ * uᵢ * vᵢ^T
            rank_1_approx = singular_values[i] * np.outer(U[:, i], V[:, i])
            A_cumulative += rank_1_approx
            
            rank_approximations.append({
                "rank": i + 1,
                "singular_value": float(singular_values[i]),
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
        'rank': r,  # Thêm thông tin rank
        'U': zero_small(U).tolist(),
        'Sigma': zero_small(Sigma).tolist(),
        'V_transpose': zero_small(V.T).tolist(),
        'U_reduced': zero_small(U_reduced).tolist(),
        'Sigma_reduced': zero_small(Sigma_reduced).tolist(),
        'Vt_reduced': zero_small(Vt_reduced).tolist(),
        'svd_sum_components': svd_sum_components,
        'intermediate_steps': {
            'A_transpose_A': zero_small(ATA).tolist(),
            'singular_values': [float(s) for s in singular_values],
            'effective_rank': r,  # Thông tin rank trong steps
            'steps': steps
        },
        "approximations": approximations  # Thêm thông tin về các ma trận xấp xỉ
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
import numpy as np

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

def svd_power_deflation(A, num_singular=None, num_iter=20, tol=1e-8, verbose=False):
    """
    Tính SVD của ma trận A bằng phương pháp power method + deflation.
    Trả về step-by-step cho từng giá trị kỳ dị.
    Args:
        A: np.ndarray, ma trận đầu vào (m, n)
        num_singular: số giá trị kỳ dị cần tìm (mặc định: min(m, n))
        num_iter: số bước lặp tối đa cho mỗi singular value
        tol: ngưỡng hội tụ
        verbose: nếu True, trả về chi tiết từng bước
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
        # Khởi tạo véctơ ngẫu nhiên
        y = np.random.rand(n, 1)
        y = y / np.linalg.norm(y)
        y_steps = [y.copy()]
        lambda_steps = []
        for i in range(num_iter):
            y_new = ATA_work @ y
            y_new = y_new / np.linalg.norm(y_new)
            lambda_new = float(y_new.T @ ATA_work @ y_new)
            y = y_new
            y_steps.append(y.copy())
            lambda_steps.append(lambda_new)
            # Kiểm tra hội tụ
            if i > 0 and abs(lambda_steps[-1] - lambda_steps[-2]) < tol:
                break
        singular = np.sqrt(abs(lambda_steps[-1]))
        singular_values.append(singular)
        right_vecs.append(y)
        # Deflation: loại bỏ thành phần vừa tìm được
        ATA_work = ATA_work - lambda_steps[-1] * (y @ y.T)
        # Lưu step-by-step
        steps.append({
            'singular_index': s+1,
            'lambda_steps': [float(l) for l in lambda_steps],
            'y_steps': [v.flatten().tolist() for v in y_steps],
            'singular_value': float(singular),
            'right_vec': y.flatten().tolist(),
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
    # Trả về kết quả
    return {
        'success': True,
        'U': zero_small(U).tolist(),
        'Sigma': zero_small(Sigma).tolist(),
        'V_transpose': zero_small(V.T).tolist(),
        'intermediate_steps': {
            'A_transpose_A': zero_small(ATA).tolist(),
            'singular_values': [float(s) for s in singular_values],
            'steps': steps
        }
    }

def calculate_svd(A, init_matrix=None, method='default', **kwargs):
    """
    Thực hiện phân tích giá trị kỳ dị (SVD) đầy đủ cho một ma trận A.
    method: 'default' (dùng numpy), 'power' (dùng power method + deflation)
    """
    if method == 'power':
        return svd_power_deflation(A, **kwargs)
    try:
        # Kiểm tra ma trận đầu vào không rỗng
        if A.size == 0:
            return {"success": False, "error": "Ma trận đầu vào không được rỗng."}

        m, n = A.shape

        # --- Bước 1: Tính V và các giá trị kỳ dị từ A.T @ A ---
        # AtA là ma trận (n, n)
        AtA = A.T @ A
        # Nếu có ma trận khởi đầu, dùng nó để khởi tạo V (chỉ hỗ trợ nếu kích thước phù hợp)
        if init_matrix is not None:
            try:
                V = np.array(init_matrix, dtype=float)
                if V.shape != (n, n):
                    return {"success": False, "error": f"Ma trận khởi đầu phải có kích thước ({n},{n})"}
                # Chuẩn hóa V thành ma trận trực chuẩn (orthonormal)
                V, _ = np.linalg.qr(V)
                # Tính trị riêng của AtA trong hệ cơ sở mới
                AtA_in_V = V.T @ AtA @ V
                eigenvalues_V = np.diag(AtA_in_V)
            except Exception as e:
                return {"success": False, "error": f"Lỗi với ma trận khởi đầu: {str(e)}"}
        else:
            # Trị riêng của AtA là bình phương của các giá trị kỳ dị.
            # Vector riêng của AtA là các cột của ma trận V.
            eigenvalues_V, V = np.linalg.eigh(AtA)
        # Sắp xếp các trị riêng và vector riêng tương ứng theo thứ tự giảm dần
        sorted_indices_V = np.argsort(eigenvalues_V)[::-1]
        eigenvalues_V_sorted = eigenvalues_V[sorted_indices_V]
        V = V[:, sorted_indices_V]
        # Tính các giá trị kỳ dị (sigma)
        singular_values = np.sqrt(np.abs(eigenvalues_V_sorted))
        # Tạo ma trận Sigma có kích thước (m, n)
        Sigma = np.zeros((m, n))
        diag_len = min(m, n, singular_values.shape[0])
        Sigma[:diag_len, :diag_len] = np.diag(singular_values[:diag_len])
        # --- Bước 2: Tính ma trận U đầy đủ (full U) từ A @ A.T ---
        # AAt là ma trận (m, m)
        # Các vector riêng của AAt tạo thành các cột của ma trận U.
        AAt = A @ A.T
        eigenvalues_U, U = np.linalg.eigh(AAt)
        # Sắp xếp các vector riêng của U theo thứ tự trị riêng giảm dần
        # để đảm bảo tính tương ứng với V
        sorted_indices_U = np.argsort(eigenvalues_U)[::-1]
        U = U[:, sorted_indices_U]
        # Trả về kết quả cuối cùng và các bước trung gian
        return {
            "success": True,
            "U": zero_small(U).tolist(),
            "Sigma": zero_small(Sigma).tolist(),
            "V_transpose": zero_small(V.T).tolist(),
            "intermediate_steps": {
                "A_transpose_A": zero_small(AtA).tolist(),
                "eigenvalues_of_ATA": zero_small(eigenvalues_V_sorted).tolist(),
                "singular_values": zero_small(singular_values).tolist(),
                "V_matrix": zero_small(V).tolist(),
                "init_matrix_used": zero_small(init_matrix).tolist() if init_matrix is not None else None
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Lỗi trong quá trình tính toán SVD: {str(e)}"}


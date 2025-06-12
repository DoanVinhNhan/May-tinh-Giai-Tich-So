import numpy as np

def zero_small(x, tol=1e-15):
    x = np.array(x)
    x[np.abs(x) < tol] = 0.0
    return x

def svd_power_deflation(A, num_singular=None, num_iter=20, tol=1e-8, y_init=None):
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
        Sigma = np.zeros((m, n))
        diag_len = min(m, n, s.shape[0])
        Sigma[:diag_len, :diag_len] = np.diag(s[:diag_len])
        return {
            "success": True,
            "U": zero_small(U).tolist(),
            "Sigma": zero_small(Sigma).tolist(),
            "V_transpose": zero_small(Vt).tolist(),
            "intermediate_steps": {
                "singular_values": zero_small(s).tolist()
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


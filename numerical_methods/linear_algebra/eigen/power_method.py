import numpy as np

# ==============================================================================
# CÁC HÀM TIỆN ÍCH (HELPER FUNCTIONS)
# ==============================================================================
def _format_complex_number(c, precision=5):
    """
    Định dạng một số phức hoặc số thực để hiển thị.
    """
    tol = 1e-20
    # Trường hợp số thực
    if not np.iscomplexobj(c) or abs(c.imag) < tol:
        real_part = c.real if np.iscomplexobj(c) else c
        if abs(real_part) < tol:
            return "0"
        return str(round(real_part, precision))
    
    # Trường hợp số phức
    real_part_val = c.real
    imag_part_val = c.imag

    if abs(real_part_val) < tol and abs(imag_part_val) < tol:
        return "0"

    parts = []
    if abs(real_part_val) > tol:
        parts.append(str(round(real_part_val, precision)))
    
    if abs(imag_part_val) > tol:
        sign = "+" if imag_part_val > 0 else "-"
        imag_abs = abs(imag_part_val)
        
        if abs(imag_abs - 1.0) < tol:
            imag_str = f"{sign}1j"
        else:
            imag_str = f"{sign}{round(imag_abs, precision)}j"
        
        if not parts:
            imag_str = imag_str.replace("+", "")

        parts.append(imag_str)

    result = "".join(parts).replace("+-", "-")
    return result if result else "0"


def _format_vector(vec, precision=5):
    """Định dạng một vector để hiển thị."""
    return [_format_complex_number(c, precision) for c in vec]

# ==============================================================================
# TRIỂN KHAI PHƯƠNG PHÁP LŨY THỪA (DỰA TRÊN TÀI LIỆU)
# ==============================================================================

def _solve_for_complex_pair(A, x_stable, tol, max_iter):
    """
    Hàm này được gọi khi phương pháp lặp đơn giản không hội tụ.
    Nó giải quyết trường hợp có một cặp giá trị riêng phức liên hợp trội.
    Dựa trên mối quan hệ tuyến tính của 3 vector lặp liên tiếp: z₂ - pz₁ + qz₀ ≈ 0.
    """
    # Lấy 3 vector liên tiếp
    z0 = x_stable / np.linalg.norm(x_stable)
    z1 = A @ z0
    z2 = A @ z1
    
    # Lập hệ phương trình tuyến tính để tìm p, q.
    # Chọn 2 chỉ số i, j để lập hệ. Chọn những chỉ số có giá trị lớn để tránh suy biến.
    n = A.shape[0]
    indices = np.argsort(np.abs(z0.flatten()))[-2:]
    i, j = indices[0], indices[1]

    # Hệ phương trình:
    # z₂[i] = p*z₁[i] - q*z₀[i]
    # z₂[j] = p*z₁[j] - q*z₀[j]
    M = np.array([[z1[i, 0], -z0[i, 0]], 
                  [z1[j, 0], -z0[j, 0]]])
    b = np.array([z2[i, 0], z2[j, 0]])

    details = {
        'z0': _format_vector(z0.flatten()),
        'z1': _format_vector(z1.flatten()),
        'z2': _format_vector(z2.flatten()),
        'indices_used': [int(i), int(j)],
        'matrix_M': [[_format_complex_number(c) for c in row] for row in M.tolist()],
        'vector_b': [_format_complex_number(c) for c in b.tolist()],
    }

    try:
        # Giải hệ để tìm [p, q]
        coeffs = np.linalg.solve(M, b)
        p, q = coeffs[0], coeffs[1]
    except np.linalg.LinAlgError:
        return None, None, ["Không thể giải hệ phương trình để tìm p, q. Ma trận M suy biến."], details

    details.update({
        'solved_p': _format_complex_number(p),
        'solved_q': _format_complex_number(q),
        'quadratic_equation': f"t² - ({_format_complex_number(p)})t + ({_format_complex_number(q)}) = 0"
    })

    # Giải phương trình bậc hai: t² - pt + q = 0 để tìm các giá trị riêng
    eigenvalues = np.roots([1, -p, q])
    
    # Tìm eigenvectors tương ứng bằng phương pháp lặp nghịch đảo dịch chuyển (rất hiệu quả)
    eigenvectors = []
    for eigval in eigenvalues:
        try:
            # (A - eigval*I)v_k+1 = v_k
            shifted_A = A - eigval * np.eye(n)
            v = np.random.rand(n, 1).astype(complex) # Khởi tạo vector phức
            for _ in range(max_iter): # Vài vòng lặp là đủ để hội tụ về VTR gần nhất
                v_new = np.linalg.solve(shifted_A, v)
                v = v_new / np.linalg.norm(v_new)
                if np.linalg.norm(v - v_new) < tol:
                    break
            eigenvectors.append(v)
        except np.linalg.LinAlgError:
            # Nếu ma trận suy biến, trả về vector không làm placeholder
            eigenvectors.append(np.zeros((n, 1), dtype=complex))

    return eigenvalues, eigenvectors, [], details


def power_method_single(A, tol=1e-9, max_iter=250):
    """
    Tìm giá trị riêng trội (và vector riêng tương ứng) của ma trận A.
    Hàm này tự động xử lý 3 trường hợp:
    1. Một GTR trội thực duy nhất.
    2. Hai GTR trội trái dấu (bằng cách chạy trên A²).
    3. Hai GTR trội phức liên hợp.
    """
    n = A.shape[0]
    if n != A.shape[1]:
        return {"success": False, "error": "Ma trận phải là ma trận vuông."}

    steps = []
    warnings = []
    
    # --- THỬ TRƯỜNG HỢP 1: GTR THỰC TRỘI ---
    x = np.random.rand(n, 1).astype(complex) # Sử dụng vector phức để xử lý tổng quát
    x = x / np.linalg.norm(x)
    lambda_old = 0.0

    for i in range(max_iter):
        Ax = A @ x
        
        # Ước lượng giá trị riêng bằng Tỷ lệ Rayleigh
        lambda_new = (x.T @ Ax) / (x.T @ x)
        lambda_new = complex(lambda_new[0, 0])

        # Chuẩn hóa
        norm_Ax = np.linalg.norm(Ax)
        if norm_Ax < 1e-12:
            return {"success": True, "message": "Vector lặp tiến về vector không.", "eigenvalues": [_format_complex_number(0.0)], "eigenvectors": [_format_vector(x.flatten())], "steps": steps}
        
        x_new = Ax / norm_Ax
        
        steps.append({
            'k': i + 1,
            'x_k': _format_vector(x.flatten()),
            'Ax_k': _format_vector(Ax.flatten()),
            'lambda_k': _format_complex_number(lambda_new)
        })

        # Kiểm tra hội tụ (cho GTR thực)
        if abs(lambda_new.imag) < tol and np.abs(lambda_new.real - lambda_old.real) < tol:
            return {
                "success": True,
                "message": "Tìm thấy một giá trị riêng trội thực (vòng lặp hội tụ).",
                "eigenvalues": [_format_complex_number(lambda_new)],
                "eigenvectors": [_format_vector(x_new.flatten())],
                "steps": steps
            }
        
        lambda_old = lambda_new
        x = x_new

    # --- NẾU KHÔNG HỘI TỤ, THỬ TRƯỜNG HỢP 3 (PHỨC LIÊN HỢP) ---
    warnings.append("Vòng lặp không hội tụ đơn giản, nghi ngờ có cặp GTR phức hoặc đối dấu.")
    eigenvalues, eigenvectors, errors, complex_details = _solve_for_complex_pair(A, x, tol, max_iter)

    if eigenvalues is None:
        # --- NẾU VẪN THẤT BẠI, THỬ TRƯỜNG HỢP 2 (ĐỐI DẤU) ---
        warnings.append("Thử nghiệm trường hợp GTR đối dấu bằng cách xét A*A.")
        A_squared = A @ A
        # Gọi đệ quy để tìm GTR của A^2
        lambda_sq_dict = power_method_single(A_squared, tol, max_iter)
        
        opposite_sign_details = {
            'A_squared': [[_format_complex_number(c) for c in row] for row in A_squared.tolist()],
            'A_squared_result': lambda_sq_dict, # Recursive result
        }
        
        if lambda_sq_dict['success'] and len(lambda_sq_dict['eigenvalues']) == 1:
            try:
                lambda_val_sq_str = lambda_sq_dict['eigenvalues'][0]
                lambda_val_sq = complex(lambda_val_sq_str.replace('i','j')).real
                
                if lambda_val_sq < 0:
                    return {"success": False, "error": f"Không thể tìm GTR đối dấu vì GTR của A² là số âm ({lambda_val_sq:.4f}).", "steps": steps}

                lambda1 = np.sqrt(lambda_val_sq)
                
                v_from_A2_str = lambda_sq_dict['eigenvectors'][0]
                v_from_A2 = np.array([complex(c.replace('i','j')) for c in v_from_A2_str]).reshape(-1,1)

                # Tìm v1, v2 từ v của A^2
                v1 = (A @ v_from_A2 + lambda1 * v_from_A2)
                v2 = (A @ v_from_A2 - lambda1 * v_from_A2)
                v1 /= np.linalg.norm(v1)
                v2 /= np.linalg.norm(v2)

                opposite_sign_details.update({
                    'lambda_squared_found': _format_complex_number(lambda_val_sq),
                    'v_from_A2': _format_vector(v_from_A2.flatten()),
                    'final_lambda1': _format_complex_number(lambda1),
                    'final_lambda2': _format_complex_number(-lambda1),
                    'v1_calculation': "(A · v' + λ₁ · v')",
                    'v2_calculation': "(A · v' - λ₁ · v')",
                    'v1_final': _format_vector(v1.flatten()),
                    'v2_final': _format_vector(v2.flatten()),
                })

                return {
                    "success": True,
                    "message": "Tìm thấy cặp giá trị riêng trội đối dấu.",
                    "eigenvalues": [_format_complex_number(lambda1), _format_complex_number(-lambda1)],
                    "eigenvectors": [_format_vector(v1.flatten()), _format_vector(v2.flatten())],
                    "steps": steps, 
                    "warnings": warnings,
                    "opposite_sign_details": opposite_sign_details
                }
            except (ValueError, TypeError, IndexError) as e:
                 return {"success": False, "error": f"Không thể xử lý kết quả từ A² để tìm GTR đối dấu. Lỗi: {str(e)}", "steps": steps}

    if eigenvalues is None:
        return {"success": False, "error": f"Không hội tụ sau {max_iter} lần lặp và các phương pháp khác cũng thất bại. {errors}", "steps": steps}

    return {
        "success": True,
        "message": "Tìm thấy cặp giá trị riêng trội (trường hợp phức hoặc đối dấu).",
        "eigenvalues": [_format_complex_number(e) for e in eigenvalues],
        "eigenvectors": [_format_vector(v.flatten()) for v in eigenvectors],
        "steps": steps,
        "warnings": warnings,
        "complex_pair_details": complex_details
    }

def power_iteration_deflation(A, num_values=1, tol=1e-6, max_iter=100):
    """
    Tìm các giá trị riêng và vector riêng trội của ma trận A
    bằng phương pháp Lũy thừa kết hợp Xuống thang (Hotelling's deflation).
    Hàm này được dùng cho cả việc tìm 1 và nhiều GTR.
    """
    try:
        if A.shape[0] != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}
        
        n = A.shape[0]
        if num_values > n:
            num_values = n # Giới hạn số GTR cần tìm bằng cấp của ma trận
            
        A_current = A.copy().astype(float)
        eigenvalues = []
        eigenvectors = []
        all_steps = []
        warnings = [] # Khởi tạo danh sách cảnh báo

        for s in range(num_values):
            # --- Power Iteration để tìm GTR trội của A_current ---
            x = np.random.rand(n, 1) # Vector khởi tạo ngẫu nhiên
            x = x / np.linalg.norm(x)
            
            lambda_prev = 0
            iteration_steps = []
            
            for i in range(max_iter):
                Ax = A_current @ x
                # Tính giá trị riêng bằng công thức Rayleigh
                lambda_curr = float((x.T @ Ax) / (x.T @ x))
                
                norm_Ax = np.linalg.norm(Ax)
                if norm_Ax == 0: # Tránh lỗi chia cho 0
                    break
                
                x_new = Ax / norm_Ax
                
                iteration_steps.append({
                    "k": i + 1,
                    "x_k": x.flatten().tolist(),
                    "Ax_k": Ax.flatten().tolist(),
                    "lambda_k": lambda_curr
                })
                
                if np.abs(lambda_curr - lambda_prev) < tol:
                    break
                
                lambda_prev = lambda_curr
                x = x_new
            else: # Nếu vòng lặp kết thúc mà không break (không hội tụ)
                # THÊM CẢNH BÁO KHI VƯỢT QUÁ SỐ LẦN LẶP
                warnings.append(f"Cảnh báo: Phép lặp cho giá trị riêng thứ {s + 1} không hội tụ sau {max_iter} lần lặp. Kết quả có thể không chính xác.")

            eigenvalues.append(lambda_curr)
            
            all_steps.append({
                "eigenvalue_index": s + 1,
                "matrix_before_deflation": A_current.tolist(),
                "iteration_summary": {
                    "found_eigenvalue": lambda_curr,
                    "found_eigenvector": x.flatten().tolist(),
                    "iterations": len(iteration_steps)
                },
                "iteration_details": iteration_steps
            })

            # --- Deflation (Xuống thang) bằng phương pháp Hotelling ---
            if s < num_values - 1:
                v = x
                A_current = A_current - lambda_curr * (v @ v.T)

        message = (f"Tìm thấy giá trị riêng trội bằng PP Lũy thừa." if num_values == 1 
                   else f"Tìm thấy {len(eigenvalues)} giá trị riêng bằng PP Lũy thừa & Xuống thang.")
        
        eigenvectors = []
        for eigval in eigenvalues:
            try:
                # (A - eigval*I)v_k+1 = v_k
                shifted_A = A - eigval * np.eye(n)
                v = np.random.rand(n, 1)
                for _ in range(max_iter): 
                    v_new = np.linalg.solve(shifted_A, v)
                    v = v_new / np.linalg.norm(v_new)
                    if np.linalg.norm(v_new - v) < tol:
                        break
                eigenvectors.append(_format_vector(v.flatten()))
            except np.linalg.LinAlgError:
                zeros_vec = np.zeros((n, 1), dtype=complex)
                # Nếu ma trận suy biến, trả về vector không làm placeholder
                eigenvectors.append(_format_vector(zeros_vec.flatten()))
        return {
            "success": True,
            "message": message,
            "eigenvalues": eigenvalues,
            "eigenvectors": eigenvectors,
            "steps": all_steps,
            "warnings": warnings # Trả về danh sách cảnh báo
        }

    except np.linalg.LinAlgError as e:
        return {"success": False, "error": f"Lỗi đại số tuyến tính: {e}"}
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
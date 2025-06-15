import numpy as np

def solve_simple_iteration(B, d, x0, eps=1e-5, max_iter=100, norm_choice='inf'):
    """
    Giải hệ phương trình tuyến tính bằng phương pháp lặp đơn x = Bx + d.
    Hàm này hỗ trợ:
    - Giải đồng thời nhiều hệ phương trình (khi d và x0 có nhiều cột).
    - Lựa chọn chuẩn tính toán (1 hoặc vô cùng) cho tất cả các bước.
    - Sử dụng điều kiện dừng nâng cao: error < (||I - B|| / ||B||) * tol.

    Args:
        B (np.ndarray): Ma trận lặp B, kích thước (n, n).
        d (np.ndarray): Vector/Ma trận hằng số d, kích thước (n, m), với m >= 1.
        x0 (np.ndarray): Vector/Ma trận khởi tạo x0, kích thước (n, m).
        eps (float): Sai số do người dùng nhập.
        max_iter (int): Số lần lặp tối đa.
        norm_choice (str): Lựa chọn chuẩn ('1' hoặc 'inf').

    Returns:
        dict: Một dictionary chứa kết quả chi tiết của quá trình lặp.
    """
    try:
        B = np.array(B, dtype=float)
        d = np.array(d, dtype=float)
        x0 = np.array(x0, dtype=float)

        n = B.shape[0]

        # Xác định chuẩn sẽ sử dụng dựa trên lựa chọn từ giao diện
        norm = 1 if norm_choice == '1' else np.inf

        # --- KIỂM TRA ĐIỀU KIỆN ĐẦU VÀO ---
        if B.shape[0] != B.shape[1]:
            return {"success": False, "error": f"Ma trận B phải là ma trận vuông. Kích thước hiện tại: {B.shape}"}
        
        # Đảm bảo d và x0 là ma trận 2D để xử lý nhất quán
        if d.ndim == 1:
            d = d.reshape(-1, 1)
        if x0.ndim == 1:
            x0 = x0.reshape(-1, 1)

        if B.shape[1] != d.shape[0]:
            return {"success": False, "error": f"Số cột của B ({B.shape[1]}) không khớp với số hàng của d ({d.shape[0]})"}
        if d.shape != x0.shape:
            return {"success": False, "error": f"Kích thước của d ({d.shape}) và x0 ({x0.shape}) phải giống nhau."}

        # --- TÍNH TOÁN CÁC GIÁ TRỊ PHÂN TÍCH HỘI TỤ ---
        norm_B = np.linalg.norm(B, norm)
        
        if norm_B == 0:
            # Nếu chuẩn của B là 0, điều kiện dừng không xác định. Dùng eps mặc định.
            stopping_threshold = eps
        else:
            I = np.identity(n)
            norm_I_minus_B = np.linalg.norm(I - B, norm)
            stopping_threshold = (norm_I_minus_B / norm_B) * eps
        
        warning_message = None
        if norm_B >= 1:
            norm_symbol = '₁' if norm == 1 else '∞'
            warning_message = (
                f"CẢNH BÁO: Điều kiện hội tụ có thể không được thỏa mãn. "
                f"Chuẩn ||B||{norm_symbol} = {norm_B:.4f} ≥ 1. "
                "Quá trình lặp có thể không hội tụ."
            )

        # --- QUÁ TRÌNH LẶP ---
        x_k = x0.copy()
        steps = [{'k': 0, 'x_k': x_k.tolist(), 'error': 'N/A'}]

        for k in range(1, max_iter + 1):
            x_k_plus_1 = B @ x_k + d
            error = np.linalg.norm(x_k_plus_1 - x_k, norm)
            x_k = x_k_plus_1
            steps.append({'k': k, 'x_k': x_k.tolist(), 'error': error})

            # Sử dụng ngưỡng dừng mới để so sánh
            if error < stopping_threshold:
                return {
                    "success": True,
                    "solution": x_k.tolist(),
                    "message": f"Hội tụ sau {k} lần lặp.",
                    "iterations": k,
                    "steps": steps,
                    "B": B.tolist(),
                    "d": d.tolist(),
                    "stopping_threshold": stopping_threshold,
                    "norm_B": norm_B,
                    "warning_message": warning_message,
                    "norm_used": norm_choice
                }

        return {
            "success": False,
            "solution": x_k.tolist(),
            "error": f"Không hội tụ sau {max_iter} lần lặp. Sai số cuối cùng là {error:.2e}.",
            "iterations": max_iter,
            "steps": steps,
            "B": B.tolist(),
            "d": d.tolist(),
            "stopping_threshold": stopping_threshold,
            "norm_B": norm_B,
            "warning_message": warning_message,
            "norm_used": norm_choice
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định trong quá trình tính toán: {e}\n{traceback.format_exc()}"}
import numpy as np

def solve_inverse_bordering(A, **kwargs):
    """
    Tính ma trận nghịch đảo bằng phương pháp viền quanh.
    """
    try:
        if A.shape[0] != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}
        
        n = A.shape[0]
        steps = []
        
        # Bước 1: Khởi tạo với ma trận con cấp 1
        if np.isclose(A[0, 0], 0):
            return {"success": False, "error": "Phần tử A[0,0] bằng 0, không thể bắt đầu."}
        
        inv_Ak = np.array([[1.0 / A[0, 0]]])
        steps.append({
            "message": f"Bước 1: Nghịch đảo của ma trận con cấp 1 A₁ = [[{A[0,0]:.4f}]]",
            "matrix": inv_Ak.tolist()
        })

        # Bước 2: Lặp từ cấp 2 đến n
        for k in range(1, n):
            # Tách các khối từ ma trận A cấp k+1
            Ak = A[:k, :k]
            u_k = A[:k, k].reshape(-1, 1) # cột viền
            v_k_T = A[k, :k].reshape(1, -1) # hàng viền
            a_kk = A[k, k]
            
            # Tính các thành phần của ma trận nghịch đảo cấp k+1
            inv_Ak_u_k = inv_Ak @ u_k
            v_k_T_inv_Ak = v_k_T @ inv_Ak
            
            theta_k = a_kk - (v_k_T @ inv_Ak_u_k)[0, 0]
            if np.isclose(theta_k, 0):
                return {"success": False, "error": f"Ma trận suy biến tại bước k={k+1} (theta = 0)."}

            # Các khối của ma trận nghịch đảo mới
            B11 = inv_Ak + (inv_Ak_u_k @ v_k_T_inv_Ak) / theta_k
            B12 = -inv_Ak_u_k / theta_k
            B21 = -v_k_T_inv_Ak / theta_k
            B22 = np.array([[1.0 / theta_k]])

            # Ghép các khối lại
            top_row = np.hstack((B11, B12))
            bottom_row = np.hstack((B21, B22))
            inv_Ak = np.vstack((top_row, bottom_row))

            steps.append({
                "message": f"Bước {k+1}: Tính nghịch đảo cho ma trận con cấp {k+1}",
                "theta": theta_k,
                "matrix": inv_Ak.tolist()
            })

        check_matrix = A @ inv_Ak
        return {
            "success": True,
            "message": "Tính ma trận nghịch đảo thành công bằng phương pháp viền quanh.",
            "inverse": inv_Ak.tolist(),
            "check": check_matrix.tolist(),
            "steps": steps
        }

    except np.linalg.LinAlgError as e:
        return {"success": False, "error": f"Lỗi đại số tuyến tính: {e}"}
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
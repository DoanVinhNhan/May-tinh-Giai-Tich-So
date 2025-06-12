import numpy as np
import scipy.linalg

def solve_inverse_lu(A, **kwargs):
    """
    Tính ma trận nghịch đảo A⁻¹ bằng phân rã LU.
    A⁻¹ = U⁻¹L⁻¹P.
    """
    try:
        if A.shape[0] != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}
        if np.linalg.det(A) == 0:
             return {"success": False, "error": "Ma trận suy biến (det(A)=0), không có nghịch đảo."}

        n = A.shape[0]
        steps = []

        # Bước 1: Phân rã PA = LU
        P, L, U = scipy.linalg.lu(A)
        steps.append({
            "message": "Bước 1: Phân rã PA = LU",
            "P": P.tolist(),
            "L": L.tolist(),
            "U": U.tolist()
        })
        
        # Bước 2: Tìm nghịch đảo của L và U
        inv_L = np.linalg.inv(L)
        inv_U = np.linalg.inv(U)
        steps.append({
            "message": "Bước 2: Tính L⁻¹ và U⁻¹",
            "L_inv": inv_L.tolist(),
            "U_inv": inv_U.tolist()
        })

        # Bước 3: Tính A⁻¹ = U⁻¹L⁻¹P
        inv_A = inv_U @ inv_L @ P
        steps.append({
            "message": "Bước 3: Tính A⁻¹ = U⁻¹L⁻¹P",
            "matrix": inv_A.tolist()
        })
        
        check_matrix = A @ inv_A

        return {
            "success": True,
            "message": "Tính ma trận nghịch đảo bằng phân rã LU thành công.",
            "inverse": inv_A.tolist(),
            "check": check_matrix.tolist(),
            "steps": steps
        }
        
    except np.linalg.LinAlgError as e:
        return {"success": False, "error": f"Lỗi đại số tuyến tính: {e}"}
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
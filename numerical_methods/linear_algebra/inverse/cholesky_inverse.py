import numpy as np

def solve_inverse_cholesky(A, **kwargs):
    """
    Tính ma trận nghịch đảo A^-1 bằng phương pháp Cholesky.
    Nếu A không đối xứng, tính (A^T A)^-1 A^T.
    """
    try:
        if A.shape[0] != A.shape[1]:
            return {"success": False, "error": "Ma trận phải là ma trận vuông."}
        
        n = A.shape[0]
        steps = []
        
        is_symmetric = np.allclose(A, A.T)
        
        if is_symmetric:
            M = A
            steps.append({"message": "Ma trận A đối xứng. Tiến hành phân tích Cholesky trực tiếp."})
        else:
            M = A.T @ A
            steps.append({
                "message": "Ma trận A không đối xứng. Tính M = AᵀA.",
                "matrix": M.tolist()
            })

        # Phân rã Cholesky: M = UᵀU
        try:
            U = np.linalg.cholesky(M).T # numpy.linalg.cholesky trả về L, ta cần U=L.T
        except np.linalg.LinAlgError:
            return {"success": False, "error": "Ma trận không xác định dương, không thể phân rã Cholesky."}
        
        steps.append({
            "message": "Phân rã Cholesky M = UᵀU.",
            "U": U.tolist(),
            "L": U.T.tolist() # U.T chính là L trong M = LU
        })

        # Tìm nghịch đảo của U (ma trận tam giác trên)
        inv_U = np.linalg.inv(U)
        steps.append({
            "message": "Tính U⁻¹.",
            "matrix": inv_U.tolist()
        })
        
        # Tính nghịch đảo của M: M⁻¹ = U⁻¹(U⁻¹)ᵀ
        inv_M = inv_U @ inv_U.T
        steps.append({
            "message": "Tính M⁻¹ = U⁻¹(U⁻¹)ᵀ.",
            "matrix": inv_M.tolist()
        })
        
        if is_symmetric:
            inv_A = inv_M
            message = "Tính ma trận nghịch đảo A⁻¹ = M⁻¹ thành công."
        else:
            # Tính A⁻¹ = M⁻¹Aᵀ
            inv_A = inv_M @ A.T
            steps.append({
                "message": "Tính A⁻¹ = M⁻¹Aᵀ.",
                "matrix": inv_A.tolist()
            })
            message = "Tính ma trận nghịch đảo A⁻¹ = (AᵀA)⁻¹Aᵀ thành công."
        
        check_matrix = A @ inv_A
        return {
            "success": True,
            "message": message,
            "inverse": inv_A.tolist(),
            "check": check_matrix.tolist(),
            "steps": steps
        }

    except np.linalg.LinAlgError as e:
        return {"success": False, "error": f"Lỗi đại số tuyến tính: {e}"}
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
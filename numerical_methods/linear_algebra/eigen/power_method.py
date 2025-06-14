# FILE: numerical_methods/linear_algebra/eigen/power_method.py
import numpy as np

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
                pass # Có thể thêm cảnh báo ở đây nếu muốn

            eigenvalues.append(lambda_curr)
            eigenvectors.append(x.flatten().tolist())
            
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

        return {
            "success": True,
            "message": message,
            "eigenvalues": eigenvalues,
            "eigenvectors": eigenvectors,
            "steps": all_steps
        }

    except np.linalg.LinAlgError as e:
        return {"success": False, "error": f"Lỗi đại số tuyến tính: {e}"}
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}
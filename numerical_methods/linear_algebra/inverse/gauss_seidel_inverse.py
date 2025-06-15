import numpy as np
import traceback

def _gauss_seidel_solver(A, b, eps, max_iter):
    """
    Hàm trợ giúp: Giải một hệ phương trình Ax = b bằng phương pháp Gauss-Seidel.
    """
    n = len(b)
    x = np.zeros(n)
    iteration_details = []

    for k in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            if A[i, i] == 0:
                # Tránh lỗi chia cho 0 nếu phần tử đường chéo bằng 0
                raise ValueError(f"Phần tử đường chéo a[{i},{i}] bằng 0, không thể tiếp tục.")
            
            sum1 = np.dot(A[i, :i], x[:i])
            sum2 = np.dot(A[i, i + 1:], x_old[i + 1:])
            x[i] = (b[i] - sum1 - sum2) / A[i, i]
        
        error = np.linalg.norm(x - x_old, np.inf)
        iteration_details.append({
            'k': k + 1,
            'x_k': x.tolist(),
            'error': error
        })
        if error < eps:
            break
    
    return x, iteration_details

def solve_inverse_gauss_seidel(A, eps=1e-5, max_iter=100, **kwargs):
    """
    Tính ma trận nghịch đảo của A bằng cách giải n hệ phương trình tuyến tính
    Ax_j = e_j với j=1,...,n bằng phương pháp Gauss-Seidel.
    """
    try:
        n = A.shape[0]
        if n != A.shape[1]:
            return {"success": False, "error": "Ma trận đầu vào phải là ma trận vuông."}

        # Kiểm tra điều kiện chéo trội (điều kiện đủ để hội tụ)
        diag_sum = np.sum(np.abs(A), axis=1) - np.abs(np.diag(A))
        if not np.all(np.abs(np.diag(A)) > diag_sum):
            print("Cảnh báo: Ma trận không chéo trội nghiêm ngặt. Gauss-Seidel có thể không hội tụ.")

        I = np.identity(n)
        X_inv = np.zeros((n, n))
        steps = []

        # Giải n hệ phương trình, mỗi hệ cho một cột của ma trận nghịch đảo
        for j in range(n):
            e_j = I[:, j]
            x_j, details = _gauss_seidel_solver(A, e_j, eps, max_iter)
            X_inv[:, j] = x_j
            
            steps.append({
                "message": f"<b>Giải hệ Ax = e<sub>{j+1}</sub> để tìm cột thứ {j+1} của ma trận nghịch đảo:</b>",
                "iterations_table": details
            })

        check_matrix = A @ X_inv

        return {
            "success": True,
            "inverse": X_inv.tolist(),
            "steps": steps,
            "check": check_matrix.tolist(),
            "message": "Tính toán hoàn tất bằng phương pháp Gauss-Seidel."
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Lỗi không xác định: {e}\n{traceback.format_exc()}"}
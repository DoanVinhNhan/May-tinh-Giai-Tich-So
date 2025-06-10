import numpy as np

def calculate_svd(A):
    """
    Thực hiện phân tích giá trị kỳ dị (SVD) đầy đủ cho một ma trận A.
    A = U * Sigma * V^T

    Args:
        A (np.ndarray): Ma trận đầu vào, kích thước (m, n).

    Returns:
        dict: Một từ điển chứa các ma trận U (m, m), Sigma (m, n), V^T (n, n)
              và các bước tính toán trung gian.
    """
    try:
        # Kiểm tra ma trận đầu vào không rỗng
        if A.size == 0:
            return {"success": False, "error": "Ma trận đầu vào không được rỗng."}

        m, n = A.shape

        # --- Bước 1: Tính V và các giá trị kỳ dị từ A.T @ A ---
        # AtA là ma trận (n, n)
        AtA = A.T @ A
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
        diag_len = min(m, n)
        Sigma[:diag_len, :diag_len] = np.diag(singular_values)
        
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
            "U": U.tolist(),
            "Sigma": Sigma.tolist(),
            "V_transpose": V.T.tolist(),
            "intermediate_steps": {
                "A_transpose_A": AtA.tolist(),
                "eigenvalues_of_ATA": eigenvalues_V_sorted.tolist(),
                "singular_values": singular_values.tolist(),
                "V_matrix": V.tolist()
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Lỗi trong quá trình tính toán SVD: {str(e)}"}


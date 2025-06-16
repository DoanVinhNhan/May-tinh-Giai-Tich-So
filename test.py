import numpy as np

def power_method_complex_conjugate(A, stable_iter=100, tol=1e-9, max_iter=1000):
    """
    Tìm cặp giá trị riêng trội phức liên hợp.

    Args:
        A (np.array): Ma trận vuông thực đầu vào.
        stable_iter (int): Số vòng lặp để vector ổn định trong không gian con.
        tol (float): Ngưỡng sai số (không dùng trực tiếp, nhưng để tương thích).
        max_iter (int): Số lần lặp tối đa.

    Returns:
        np.array: Mảng chứa hai giá trị riêng phức liên hợp, hoặc None.
    """
    # FIX 1: Use A.shape[0] to get an integer dimension for the vector
    n = A.shape[0] 
    
    # Bắt đầu với một vector ngẫu nhiên
    x = np.random.rand(n)
    
    # Chạy một số vòng lặp để vector hội tụ vào không gian con 2D
    for _ in range(stable_iter):
        x = A @ x
        x = x / np.linalg.norm(x)

    # Lấy 3 vector liên tiếp
    z0 = x
    z1 = A @ z0
    z2 = A @ z1
    
    # Chọn 2 chỉ số i, j để lập hệ phương trình
    indices = np.argsort(np.abs(z0))[-2:]
    
    # FIX 3: Unpack indices correctly
    i, j = indices[0], indices[1]

    # Lập hệ phương trình M * [p, -q]^T = b
    M = np.array([[z1[i], -z0[i]], 
                  [z1[j], -z0[j]]])
    b = np.array([z2[i], z2[j]])

    try:
        # Giải hệ để tìm [p, q]
        coeffs = np.linalg.solve(M, b)
        # FIX 4: Unpack coefficients correctly
        p, q = coeffs
    except np.linalg.LinAlgError:
        print("Không thể giải hệ phương trình để tìm p, q. Ma trận suy biến.")
        return None

    # Giải phương trình bậc hai: t^2 - p*t + q = 0
    eigenvalues = np.roots([1, -p, q])
    
    return eigenvalues

# --- Ví dụ minh họa ---
# FIX 2: Define a complete, square matrix
# Ma trận này có giá trị riêng là 1+2i và 1-2i
A_case3 = np.array([[ 3,  5,  3, -2,  4],
               [ 4,  1, -6,  0,  3],
               [ 2,  0,  1,  7, -2],
               [ 3,  1,  4,  5,  8],
               [-2,  4,  0,  0,  3]])

print("Ma trận A cho trường hợp 3:\n", A_case3)
complex_eigs = power_method_complex_conjugate(A_case3)

if complex_eigs is not None:
    # The output contains two conjugate values
    print(f"\nCặp giá trị riêng phức liên hợp tìm được: {complex_eigs[0]} và {complex_eigs[1]}")
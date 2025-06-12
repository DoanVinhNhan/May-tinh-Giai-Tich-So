import numpy as np

def getCharPolynomial(A):
    n = A.shape[0]
    p = np.zeros(n + 1)
    p[0] = 1.0
    p[1:] = -A[0, :]
    return p

def findSimpleA(A, k):
    n, _ = A.shape
    M = np.eye(n)
    M[k-1, :] = A[k, :]
    inverseM = np.eye(n)
    inverseM[k-1, :] = -A[k, :] / A[k, k-1]
    inverseM[k-1, k-1] = 1 / A[k, k-1]
    similarA = M.dot(A).dot(inverseM)
    return similarA, inverseM

def danilevsky_algorithm(A):
    """
    Thuật toán Danilevsky: trả về giá trị riêng, vector riêng, Frobenius, đa thức đặc trưng và các bước trung gian.
    Số đếm hàng/cột bắt đầu từ 1 (theo toán học).
    """
    n = A.shape[0]
    back = np.eye(n)
    similar = A.copy()
    steps_log = []
    steps_log.append({'desc': 'Ma trận ban đầu', 'matrix': similar.copy().tolist()})

    for k in range(n - 1, 0, -1):
        # Ghi lại ma trận trước biến đổi tại bước k (bước k tương ứng với hàng/cột thứ k+1 theo toán học)
        steps_log.append({'desc': f'Trước biến đổi tại bước k={k} ', 'matrix': similar.copy().tolist()})
        if abs(similar[k, k-1]) > 1e-9:
            # Biến đổi đồng dạng: đưa phần tử (hàng {k+1}, cột {k}) về dạng Frobenius
            similar, inverseM = findSimpleA(similar, k)
            back = back.dot(inverseM)
            steps_log.append({
                'desc': f'Sau biến đổi tại bước k={k} (đưa hàng {k+1} về dạng Frobenius: chỉ còn phần tử tại cột {k})',
                'matrix': similar.copy().tolist()
            })
        else:
            found_swap = False
            for j in range(k - 1):
                if abs(similar[k, j]) > 1e-9:
                    # Hoán vị cột/hàng để đưa phần tử khác 0 về vị trí (hàng {k+1}, cột {k})
                    similar[:, [j, k-1]] = similar[:, [k-1, j]]
                    similar[[j, k-1], :] = similar[[k-1, j], :]
                    back[:, [j, k-1]] = back[:, [k-1, j]]
                    steps_log.append({
                        'desc': f'Hoán vị cột/hàng {j+1} và {k} tại bước k={k} (đưa phần tử khác 0 về vị trí ({k+1},{k}))',
                        'matrix': similar.copy().tolist()
                    })
                    found_swap = True
                    break
            if not found_swap:
                steps_log.append({'desc': f'Không thể biến đổi tại bước k={k} (không tìm thấy phần tử khác 0 để hoán vị)', 'matrix': similar.copy().tolist()})
                continue

    steps_log.append({'desc': 'Ma trận Frobenius (dạng đồng hành)', 'matrix': similar.copy().tolist()})

    char_poly = getCharPolynomial(similar)
    eigenvalues = np.roots(char_poly)
    list_eigenvectors = []
    for val in eigenvalues:
        y = np.power(val, np.arange(n - 1, -1, -1)).reshape((n, 1))
        eigenvector_A = back.dot(y)
        if abs(eigenvector_A[-1, 0]) > 1e-9:
            eigenvector_A = eigenvector_A / eigenvector_A[-1, 0]
        list_eigenvectors.append(eigenvector_A)

    results = {
        'eigenvalues': [v.real if abs(v.imag) < 1e-10 else v for v in eigenvalues],
        'eigenvectors': [vec.tolist() for vec in list_eigenvectors],
        'frobenius_matrix': similar.tolist(),
        'char_poly': char_poly.tolist(),
        'steps': steps_log
    }
    return results
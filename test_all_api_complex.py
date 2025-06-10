import numpy as np
import requests
import json

BASE_URL = 'http://127.0.0.1:5001/matrix/'

def pretty_matrix(mat):
    if isinstance(mat, list):
        return '\n'.join(['\t'.join([str(round(x,4)) for x in row]) for row in mat])
    return str(mat)

def test_api(endpoint, payload, desc):
    print(f'==== {desc} ===')
    try:
        resp = requests.post(BASE_URL + endpoint, json=payload, timeout=15)
        print('Status:', resp.status_code)
        data = resp.json()
        print('Success:', data.get('success'))
        if not data.get('success'):
            print('Error:', data.get('error'))
        else:
            for k, v in data.items():
                if k in ['solution', 'U', 'Sigma', 'V_transpose', 'L', 'U', 'P', 'decomposition', 'general_solution', 'null_space_vectors']:
                    print(f'{k}:\n{pretty_matrix(v)}')
        print('\n')
    except Exception as e:
        print('Exception:', e)
        print('\n')

def main():
    # ==== SVD ====
    # Đề thi: Ma trận vuông, ma trận chữ nhật, ma trận hạng thấp, ma trận toàn 0, ma trận có số hàng > số cột
    test_api('svd', {'matrix_a': [[1,2,3],[4,5,6],[7,8,9]]}, 'SVD 3x3 (hạng thấp)')
    test_api('svd', {'matrix_a': [[1,2,3,4],[5,6,7,8],[9,10,11,12]]}, 'SVD 3x4 (đề thi)')
    test_api('svd', {'matrix_a': [[0,0,0],[0,0,0],[0,0,0]]}, 'SVD ma trận 0')
    test_api('svd', {'matrix_a': [[1,2],[3,4],[5,6],[7,8]]}, 'SVD 4x2 (m>n, phải báo lỗi)')
    test_api('svd', {'matrix_a': [[1,0,0],[0,1,0],[0,0,1]]}, 'SVD ma trận đơn vị')

    # ==== Gauss-Jordan ====
    # Hệ có nghiệm duy nhất, vô nghiệm, vô số nghiệm, hệ nhiều vế phải, hệ suy biến, hệ cỡ lớn
    test_api('gauss-jordan', {'matrix_a': [[2,1,-1],[-3,-1,2],[-2,1,2]], 'matrix_b': [[8],[-11],[-3]]}, 'Gauss-Jordan unique solution (đề thi)')
    test_api('gauss-jordan', {'matrix_a': [[1,1],[2,2]], 'matrix_b': [[1],[3]]}, 'Gauss-Jordan no solution (song song)')
    test_api('gauss-jordan', {'matrix_a': [[1,2],[2,4]], 'matrix_b': [[3],[6]]}, 'Gauss-Jordan infinite solutions (trùng nhau)')
    test_api('gauss-jordan', {'matrix_a': [[1,2,3],[4,5,6],[7,8,9]], 'matrix_b': [[6],[15],[24]]}, 'Gauss-Jordan hạng thấp, nhiều vế phải')
    test_api('gauss-jordan', {'matrix_a': [[1,2,3,4],[2,4,6,8],[3,6,9,12],[4,8,12,16]], 'matrix_b': [[10],[20],[30],[40]]}, 'Gauss-Jordan hệ suy biến cỡ lớn')

    # ==== Gauss-Elimination ====
    test_api('gauss-elimination', {'matrix_a': [[2,1,-1],[-3,-1,2],[-2,1,2]], 'matrix_b': [[8],[-11],[-3]]}, 'Gauss-Elimination unique solution (đề thi)')
    test_api('gauss-elimination', {'matrix_a': [[1,1],[2,2]], 'matrix_b': [[1],[3]]}, 'Gauss-Elimination no solution')
    test_api('gauss-elimination', {'matrix_a': [[1,2],[2,4]], 'matrix_b': [[3],[6]]}, 'Gauss-Elimination infinite solutions')

    # ==== LU ====
    test_api('lu-decomposition', {'matrix_a': [[2,1,1],[4,-6,0],[-2,7,2]], 'matrix_b': [[5],[-2],[9]]}, 'LU unique solution (đề thi)')
    test_api('lu-decomposition', {'matrix_a': [[1,2],[2,4]], 'matrix_b': [[3],[6]]}, 'LU infinite solutions')
    test_api('lu-decomposition', {'matrix_a': [[1,2],[2,4]], 'matrix_b': [[3],[7]]}, 'LU no solution')
    test_api('lu-decomposition', {'matrix_a': [[1,2,3,4],[2,4,6,8],[3,6,9,12],[4,8,12,16]], 'matrix_b': [[10],[20],[30],[40]]}, 'LU hệ suy biến cỡ lớn')

    # ==== Cholesky ====
    test_api('cholesky', {'matrix_a': [[25,15,-5],[15,18,0],[-5,0,11]], 'matrix_b': [[35],[33],[6]]}, 'Cholesky unique solution (đề thi)')
    test_api('cholesky', {'matrix_a': [[1,2],[3,4]], 'matrix_b': [[5],[6]]}, 'Cholesky non-symmetric (tự động chuyển)')
    test_api('cholesky', {'matrix_a': [[4,12,-16],[12,37,-43],[-16,-43,98]], 'matrix_b': [[1],[2],[3]]}, 'Cholesky hệ đối xứng dương xác định')
    test_api('cholesky', {'matrix_a': [[1,2,3],[2,4,6],[3,6,9]], 'matrix_b': [[6],[12],[18]]}, 'Cholesky hệ suy biến')

    # ==== Biên: Ma trận toàn 0, ma trận đơn vị, hệ cực lớn (giới hạn) ====
    test_api('gauss-jordan', {'matrix_a': [[0,0,0],[0,0,0],[0,0,0]], 'matrix_b': [[0],[0],[0]]}, 'Gauss-Jordan all zero')
    test_api('gauss-jordan', {'matrix_a': [[1,0,0],[0,1,0],[0,0,1]], 'matrix_b': [[1],[2],[3]]}, 'Gauss-Jordan identity')
    # Hệ lớn (giới hạn), chỉ test performance, không cần nghiệm đúng
    bigA = [[1 if i==j else 0 for j in range(20)] for i in range(20)]
    bigB = [[i+1] for i in range(20)]
    test_api('gauss-jordan', {'matrix_a': bigA, 'matrix_b': bigB}, 'Gauss-Jordan 20x20 identity')

if __name__ == '__main__':
    main()

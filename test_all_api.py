import numpy as np
import requests
import json

# Địa chỉ server backend Flask
BASE_URL = 'http://127.0.0.1:5001/matrix/'

def pretty_matrix(mat):
    if isinstance(mat, list):
        return '\n'.join(['\t'.join([str(round(x,4)) for x in row]) for row in mat])
    return str(mat)

def test_api(endpoint, payload, desc):
    print(f'==== {desc} ===')
    try:
        resp = requests.post(BASE_URL + endpoint, json=payload, timeout=10)
        print('Status:', resp.status_code)
        data = resp.json()
        print('Success:', data.get('success'))
        if not data.get('success'):
            print('Error:', data.get('error'))
        else:
            # In nghiệm hoặc decomposition nếu có
            for k, v in data.items():
                if k in ['solution', 'U', 'Sigma', 'V_transpose', 'L', 'U', 'P', 'decomposition', 'general_solution', 'null_space_vectors']:
                    print(f'{k}:\n{pretty_matrix(v)}')
        print('\n')
    except Exception as e:
        print('Exception:', e)
        print('\n')

def main():
    # Test SVD
    A = [[1,2,3],[4,5,6],[7,8,9]]
    test_api('svd', {'matrix_a': A}, 'SVD 3x3')
    # Test SVD m>n (phải báo lỗi)
    A2 = [[1,2],[3,4],[5,6]]
    test_api('svd', {'matrix_a': A2}, 'SVD m>n (should fail)')

    # Test Gauss-Jordan
    A = [[2,1,-1],[ -3,-1,2],[ -2,1,2]]
    B = [[8],[ -11],[ -3]]
    test_api('gauss-jordan', {'matrix_a': A, 'matrix_b': B}, 'Gauss-Jordan unique solution')
    # Test Gauss-Jordan vô nghiệm
    A = [[1,1],[2,2]]
    B = [[1],[3]]
    test_api('gauss-jordan', {'matrix_a': A, 'matrix_b': B}, 'Gauss-Jordan no solution')
    # Test Gauss-Jordan vô số nghiệm
    A = [[1,2],[2,4]]
    B = [[3],[6]]
    test_api('gauss-jordan', {'matrix_a': A, 'matrix_b': B}, 'Gauss-Jordan infinite solutions')

    # Test Gauss-Elimination
    A = [[2,1,-1],[ -3,-1,2],[ -2,1,2]]
    B = [[8],[ -11],[ -3]]
    test_api('gauss-elimination', {'matrix_a': A, 'matrix_b': B}, 'Gauss-Elimination unique solution')

    # Test LU
    A = [[2,1,1],[4,-6,0],[-2,7,2]]
    B = [[5],[-2],[9]]
    test_api('lu-decomposition', {'matrix_a': A, 'matrix_b': B}, 'LU unique solution')
    # Test LU vô số nghiệm
    A = [[1,2],[2,4]]
    B = [[3],[6]]
    test_api('lu-decomposition', {'matrix_a': A, 'matrix_b': B}, 'LU infinite solutions')
    # Test LU vô nghiệm
    A = [[1,2],[2,4]]
    B = [[3],[7]]
    test_api('lu-decomposition', {'matrix_a': A, 'matrix_b': B}, 'LU no solution')

    # Test Cholesky
    A = [[25,15,-5],[15,18,0],[-5,0,11]]
    B = [[35],[33],[6]]
    test_api('cholesky', {'matrix_a': A, 'matrix_b': B}, 'Cholesky unique solution')
    # Test Cholesky không đối xứng (phải tự động chuyển)
    A = [[1,2],[3,4]]
    B = [[5],[6]]
    test_api('cholesky', {'matrix_a': A, 'matrix_b': B}, 'Cholesky non-symmetric')

if __name__ == '__main__':
    main()

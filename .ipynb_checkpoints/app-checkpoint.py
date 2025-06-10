from flask import Flask, render_template, request, jsonify
import numpy as np
import json

from numerical_methods.linear_algebra.eigen.svd import calculate_svd
from numerical_methods.linear_algebra.direct_methods.gauss_elimination import solve_gauss_elimination
from numerical_methods.linear_algebra.direct_methods.gauss_jordan import solve_gauss_jordan
from numerical_methods.linear_algebra.direct_methods.lu_decomposition import solve_lu
from numerical_methods.linear_algebra.direct_methods.cholesky import solve_cholesky

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

def hpt_solver(solver_function):
    data = request.get_json()
    if not data or 'matrix_a' not in data or 'matrix_b' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A hoặc B."}), 400
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        matrix_b = np.array(data['matrix_b'], dtype=float)
        result = solver_function(matrix_a, matrix_b)
        # Đảm bảo luôn trả về JSON serializable
        return jsonify(result)
    except Exception as e:
        import traceback
        print("Lỗi khi xử lý request:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {traceback.format_exc()}"}), 500

@app.route('/matrix/svd', methods=['POST'])
def handle_svd_calculation():
    data = request.get_json()
    if not data or 'matrix_a' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A."}), 400
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        result = calculate_svd(matrix_a)
        return jsonify(result)
    except Exception as e:
        import traceback
        print("Lỗi khi xử lý SVD:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

@app.route('/matrix/gauss-jordan', methods=['POST'])
def handle_gauss_jordan_calculation():
    return hpt_solver(solve_gauss_jordan)

@app.route('/matrix/gauss-elimination', methods=['POST'])
def handle_gauss_elimination_calculation():
    return hpt_solver(solve_gauss_elimination)

@app.route('/matrix/lu-decomposition', methods=['POST'])
def handle_lu_decomposition_calculation():
    return hpt_solver(solve_lu)

@app.route('/matrix/cholesky', methods=['POST'])
def handle_cholesky_calculation():
    return hpt_solver(solve_cholesky)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
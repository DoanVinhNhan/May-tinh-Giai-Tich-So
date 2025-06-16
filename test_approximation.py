#!/usr/bin/env python3
"""
Test script để kiểm tra chức năng xấp xỉ ma trận SVD
"""

import requests
import json
import time

def test_svd_approximation():
    """Test chức năng xấp xỉ ma trận SVD"""
    
    # URL của server
    url = "http://127.0.0.1:5001/matrix/svd_approximation"
    
    # Ma trận test đơn giản
    test_matrix = [
        [4, 0, 0],
        [0, 3, 0], 
        [0, 0, 2]
    ]
    
    print("🧪 Bắt đầu test chức năng xấp xỉ ma trận SVD...")
    print(f"Ma trận test:\n{test_matrix}")
    
    # Test 1: Xấp xỉ rank-k
    print("\n📋 Test 1: Xấp xỉ rank-k (k=2)")
    payload1 = {
        "matrix_a": test_matrix,
        "approximation_method": "rank-k",
        "k": 2
    }
    
    try:
        response1 = requests.post(url, json=payload1, timeout=10)
        print(f"Status code: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get("success"):
                print("✅ Test 1 PASSED - Rank-k approximation hoạt động!")
                print(f"Approximated matrix shape: {len(result1.get('approximated_matrix', []))}x{len(result1.get('approximated_matrix', [[]])[0]) if result1.get('approximated_matrix') else 0}")
            else:
                print(f"❌ Test 1 FAILED - Backend error: {result1.get('error')}")
        else:
            print(f"❌ Test 1 FAILED - HTTP error: {response1.status_code}")
            print(f"Response: {response1.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Test 1 FAILED - Không thể kết nối đến server!")
        print("💡 Hãy chạy: python app.py")
        return False
    except Exception as e:
        print(f"❌ Test 1 FAILED - Lỗi: {e}")
        return False
    
    # Test 2: Xấp xỉ threshold
    print("\n📋 Test 2: Xấp xỉ threshold (threshold=1.5)")
    payload2 = {
        "matrix_a": test_matrix,
        "approximation_method": "threshold", 
        "threshold": 1.5
    }
    
    try:
        response2 = requests.post(url, json=payload2, timeout=10)
        print(f"Status code: {response2.status_code}")
        
        if response2.status_code == 200:
            result2 = response2.json()
            if result2.get("success"):
                print("✅ Test 2 PASSED - Threshold approximation hoạt động!")
            else:
                print(f"❌ Test 2 FAILED - Backend error: {result2.get('error')}")
        else:
            print(f"❌ Test 2 FAILED - HTTP error: {response2.status_code}")
            
    except Exception as e:
        print(f"❌ Test 2 FAILED - Lỗi: {e}")
    
    # Test 3: Xấp xỉ error-bound
    print("\n📋 Test 3: Xấp xỉ error-bound (error_bound=0.5)")
    payload3 = {
        "matrix_a": test_matrix,
        "approximation_method": "error-bound",
        "error_bound": 0.5
    }
    
    try:
        response3 = requests.post(url, json=payload3, timeout=10)
        print(f"Status code: {response3.status_code}")
        
        if response3.status_code == 200:
            result3 = response3.json()
            if result3.get("success"):
                print("✅ Test 3 PASSED - Error-bound approximation hoạt động!")
            else:
                print(f"❌ Test 3 FAILED - Backend error: {result3.get('error')}")
        else:
            print(f"❌ Test 3 FAILED - HTTP error: {response3.status_code}")
            
    except Exception as e:
        print(f"❌ Test 3 FAILED - Lỗi: {e}")
    
    print("\n🎯 Kết luận:")
    print("- Nếu tất cả test PASSED: Chức năng xấp xỉ ma trận hoạt động đúng!")
    print("- Nếu có test FAILED: Cần kiểm tra lại backend hoặc frontend")
    
    return True

def test_frontend_elements():
    """Test các element trong frontend"""
    print("\n🌐 Kiểm tra frontend elements...")
    
    # Đọc file HTML để kiểm tra các element cần thiết
    try:
        with open('/Users/doanvinhnhan/projectps/GTS/May-tinh-Giai-Tich-So/templates/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        required_elements = [
            'matrix-approximation-page',
            'matrix-a-input-approx', 
            'approx-method-select',
            'calculate-approximation-btn',
            'loading-spinner-approx',
            'error-message-approx',
            'results-area-approx'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in html_content:
                missing_elements.append(element)
        
        if not missing_elements:
            print("✅ Tất cả HTML elements cần thiết đều có!")
        else:
            print(f"❌ Thiếu HTML elements: {missing_elements}")
            
    except Exception as e:
        print(f"❌ Lỗi khi đọc file HTML: {e}")
    
    # Kiểm tra JavaScript functions
    try:
        with open('/Users/doanvinhnhan/projectps/GTS/May-tinh-Giai-Tich-So/static/js/main.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        required_functions = [
            'setupMatrixApproximationEvents',
            'displaySvdApproximationResults'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f'function {func}' not in js_content:
                missing_functions.append(func)
        
        if not missing_functions:
            print("✅ Tất cả JavaScript functions cần thiết đều có!")
        else:
            print(f"❌ Thiếu JavaScript functions: {missing_functions}")
            
    except Exception as e:
        print(f"❌ Lỗi khi đọc file JavaScript: {e}")

if __name__ == "__main__":
    print("🚀 Kiểm thử chức năng xấp xỉ ma trận SVD")
    print("=" * 50)
    
    # Test frontend elements trước
    test_frontend_elements()
    
    # Đợi một chút
    time.sleep(1)
    
    # Test backend
    test_svd_approximation()
    
    print("\n" + "=" * 50)
    print("📝 Hướng dẫn:")
    print("1. Nếu server chưa chạy, hãy chạy: python app.py")
    print("2. Mở browser và truy cập: http://127.0.0.1:5001")
    print("3. Chọn 'Ma trận xấp xỉ SVD' trong menu")
    print("4. Nhập ma trận và test các phương pháp xấp xỉ")

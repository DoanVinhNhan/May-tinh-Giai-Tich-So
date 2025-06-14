# Máy tính Giải tích số

Một ứng dụng web cung cấp bộ công cụ toàn diện để giải các bài toán trong lĩnh vực giải tích số. Giao diện được xây dựng bằng HTML, CSS, và JavaScript, trong khi phần xử lý thuật toán mạnh mẽ ở backend được cung cấp bởi Python với Flask và các thư viện tính toán khoa học.

## Tính năng nổi bật

Ứng dụng hỗ trợ một loạt các phương pháp số, mỗi phương pháp đều hiển thị các bước giải trung gian chi tiết để người dùng có thể theo dõi và hiểu rõ quy trình tính toán.

### 1. Giải phương trình `f(x) = 0`
- **Phương pháp chia đôi (Bisection)**
- **Phương pháp lặp đơn (Simple Iteration)**
- **Phương pháp Newton (Tiếp tuyến)**
- **Phương pháp dây cung (Secant)**
- Hỗ trợ nhập hàm số dưới dạng LaTeX và tùy chỉnh điều kiện dừng (sai số tuyệt đối, tương đối, số lần lặp).

### 2. Giải phương trình đa thức
- Tự động tìm khoảng chứa nghiệm, phân ly nghiệm bằng cách xác định các điểm cực trị, và giải chính xác bằng phương pháp chia đôi.

### 3. Đại số tuyến tính

#### Giải hệ phương trình tuyến tính (AX = B)
- **Phương pháp trực tiếp:**
  - Khử Gauss
  - Gauss-Jordan
  - Phân rã LU
  - Phân rã Cholesky
- **Phương pháp lặp:**
  - Lặp Jacobi
  - Lặp Gauss-Seidel

#### Tìm ma trận nghịch đảo (A⁻¹)
- **Phương pháp trực tiếp:**
  - Gauss-Jordan
  - Phân rã LU
  - Phân rã Cholesky
  - Viền ma trận
- **Phương pháp lặp:**
  - Lặp Jacobi
  - Lặp Newton

#### Trị riêng và Vector riêng
- **Phương pháp Danilevsky** để tìm đa thức đặc trưng, trị riêng và vector riêng.
- **Phân rã giá trị suy biến (SVD)**, bao gồm cả phương pháp lũy thừa để tìm các giá trị kỳ dị lớn nhất.

### 4. Giải hệ phương trình phi tuyến
- **Phương pháp lặp đơn** cho hệ nhiều biến.
- **Phương pháp Newton** và **Newton cải tiến** cho hệ nhiều biến.

## Công nghệ sử dụng

- **Backend:**
  - **Python 3**: Ngôn ngữ lập trình chính.
  - **Flask**: Micro web framework để xây dựng API.
  - **NumPy**: Thư viện nền tảng cho tính toán khoa học, xử lý ma trận và vector.
  - **SymPy**: Thư viện cho toán học biểu tượng, dùng để phân tích các hàm số do người dùng nhập.
- **Frontend:**
  - **HTML5**: Cấu trúc trang web.
  - **Tailwind CSS**: Framework CSS để xây dựng giao diện người dùng hiện đại.
  - **JavaScript (ES6+)**: Xử lý logic phía client, tương tác người dùng và gọi API.
- **Hiển thị công thức:**
  - **KaTeX**: Thư viện JavaScript siêu nhanh để hiển thị các công thức toán học từ cú pháp LaTeX.

## Cài đặt và Chạy dự án

### Yêu cầu
- Python 3.8+
- `pip` (trình quản lý gói của Python)
- Trình duyệt web hiện đại (Chrome, Firefox, Edge,...)

### Hướng dẫn cài đặt
1.  **Clone repository về máy của bạn:**
    ```bash
    git clone https://github.com/DoanVinhNhan/May-tinh-Giai-Tich-So
    cd May-tinh-Giai-Tich-So
    ```

2.  **(Khuyến khích) Tạo và kích hoạt môi trường ảo:**
    ```bash
    # Lệnh cho Windows
    python -m venv .venv
    source .venv/bin/activate

    # Lệnh cho macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết từ file `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

### Chạy ứng dụng
1.  **Khởi động server Flask (Backend):**
    Mở terminal trong thư mục gốc của dự án và chạy lệnh:
    ```bash
    python app.py
    ```
    Server sẽ khởi động, thường là ở địa chỉ `http://127.0.0.1:5001`.
    > **Lưu ý:** Giao diện người dùng đã được thiết kế để giao tiếp với server backend đang chạy. Hãy đảm bảo server Flask luôn hoạt động khi bạn sử dụng ứng dụng.

document.addEventListener('DOMContentLoaded', function () {
    // Khi vừa load trang, tự động render trang mặc định là matrix-solve-direct
    renderPage('matrix-solve-direct');
    // Gắn lại event cho sidebar menu (đảm bảo khi chuyển sang SVD sẽ gắn event đúng)
    document.querySelectorAll('[data-page]').forEach(btn => {
        btn.addEventListener('click', e => {
            renderPage(btn.getAttribute('data-page'));
        });
    });
    setupDisplaySettingsEvents();
});

// === DOM ELEMENTS ===
// KHÔNG lấy các biến DOM toàn cục ở đây nữa!

// === GLOBAL STATE ===
let displayPrecision = 4; // Số chữ số sau dấu phẩy mặc định
let zeroTolerance = 1e-15;
// === HELPER FUNCTIONS ===

function setupDisplaySettingsEvents() {
    const precisionInput = document.getElementById('setting-precision');
    const toleranceInput = document.getElementById('setting-zero-tolerance');

    if (!precisionInput || !toleranceInput) {
        console.warn("Không tìm thấy các ô input cài đặt hiển thị.");
        return;
    };

    // Xử lý thay đổi số chữ số
    precisionInput.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        if (!isNaN(val) && val >= 0 && val <= 15) {
            displayPrecision = val;
            // Nếu có kết quả cũ, render lại với định dạng mới
            if (window.lastResult && typeof window.lastDisplayFn === 'function') {
                const currentMethod = window.lastResult.method_used_for_display;
                window.lastDisplayFn(window.lastResult, currentMethod);
            }
        }
    });

    // Xử lý thay đổi ngưỡng làm tròn về 0
    toleranceInput.addEventListener('input', (e) => {
        const valStr = e.target.value;
        // Cho phép các định dạng khoa học như "1e-15"
        if (/^-?\d*(\.\d+)?(e-?d+)?$/i.test(valStr)) {
            const val = parseFloat(valStr);
            if (!isNaN(val) && val >= 0) {
                zeroTolerance = val;
                // Nếu có kết quả cũ, render lại với định dạng mới
                if (window.lastResult && typeof window.lastDisplayFn === 'function') {
                    const currentMethod = window.lastResult.method_used_for_display;
                    window.lastDisplayFn(window.lastResult, currentMethod);
                }
            }
        }
    });
}



// Hàm trợ giúp để tạo bảng
function createIterativeTable(rows, headers) {
    let table = `<div class="overflow-x-auto"><table class=" collapsible-table min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>`;
    headers.forEach(h => table += `<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">${h}</th>`);
    table += `</tr></thead><tbody class="bg-white divide-y divide-gray-200">`;
    rows.forEach(row => {
        const x_k_formatted = Array.isArray(row.x_k[0]) ? formatMatrix(row.x_k) : `[${row.x_k.map(v => formatNumber(v)).join(', ')}]`;
        const errorFormatted = (typeof row.error === 'string') ? row.error : formatNumber(row.error);
        table += `<tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${row.k}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${x_k_formatted}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${errorFormatted}</td>
                  </tr>`;
    });
    table += `</tbody></table></div>`;
    return table;
}

    // --- Hàm chuyển đổi LaTeX sang Python ---
function latexToPython(latex) {
    if (!latex) return "";
    let pyExpr = latex;

    // Xử lý các trường hợp đặc biệt trước
    // Căn bậc n: \sqrt[n]{x} -> x**(1/n)
    pyExpr = pyExpr.replace(/\\sqrt\[(.*?)\]\{(.*?)\}/g, '($2)**(1/($1))');
    // Căn bậc 2: \sqrt{x} -> sqrt(x)
    pyExpr = pyExpr.replace(/\\sqrt\{(.*?)\}/g, 'sqrt($1)');
    // Phân số: \frac{a}{b} -> (a)/(b)
    pyExpr = pyExpr.replace(/\\frac\{(.*?)\}\{(.*?)\}/g, '($1)/($2)');
    // Log cơ số a: \log_{a}{b} -> log(b, a) (Sửa lỗi logic)
    pyExpr = pyExpr.replace(/\\log_\{(.*?)\}\{(.*?)\}/g, 'log($2, $1)');
    // Biến có chỉ số: x_1, x_{23} -> x1, x23
    pyExpr = pyExpr.replace(/x_\{?(\d+)\}?/g, 'x$1');

    // Xử lý các hàm chuẩn
    pyExpr = pyExpr.replace(/\\(sin|cos|tan|asin|acos|atan|ln|exp|abs|pi)/g, '$1');

    // Xử lý các toán tử
    pyExpr = pyExpr.replace(/\^/g, '**');      // Lũy thừa
    pyExpr = pyExpr.replace(/\\cdot/g, '*');   // Nhân
    
    // Xóa các dấu ngoặc nhọn còn lại của LaTeX
    pyExpr = pyExpr.replace(/\{/g, '(');
    pyExpr = pyExpr.replace(/\}/g, ')');
    
    // Xóa các khoảng trắng thừa
    pyExpr = pyExpr.replace(/\s+/g, ' ');

    return pyExpr;
}
function formatLatexMatrix(data) {
    if (!Array.isArray(data) || !Array.isArray(data[0])) return '';
    let tableHtml = '<table class=" collapsible-table matrix-table">';
    data.forEach(row => {
        tableHtml += '<tr>';
        row.forEach(cell => {
            // Cell chứa chuỗi LaTeX thuần túy
            const escapedCell = cell.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            tableHtml += `<td>${escapedCell}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</table>';
    return `<div class="matrix-container">${tableHtml}</div>`;
}
function parseMatrix(matrixString) {
    try {
        const rows = matrixString.trim().split('\n').filter(r => r.trim() !== '');
        if (rows.length === 0) return [];
        const matrix = rows.map(row =>
            row.trim().split(/\s+/).map(numStr => {
                const number = parseFloat(numStr);
                if (isNaN(number)) throw new Error(`Giá trị không hợp lệ: "${numStr}"`);
                return number;
            })
        );
        const firstRowLength = matrix[0].length;
        if (!matrix.every(row => row.length === firstRowLength)) {
            throw new Error('Các hàng phải có cùng số lượng phần tử.');
        }
        return matrix;
    } catch (error) {
        return { error: error.message };
    }
}

function formatNumber(num, precision = displayPrecision) {
    if (num === null || num === undefined) return 'N/A';

    // Nên định nghĩa một hằng số sai số nhỏ ở đây
    const zeroTolerance = 1e-9;

    // 1. Hàm phụ trợ để định dạng một số thực
    const formatReal = (realNum) => {
        // Kiểm tra xem số có phải là số nguyên không
        if (Math.abs(realNum - Math.round(realNum)) < zeroTolerance) {
            return Math.round(realNum).toString(); // Trả về dạng số nguyên
        }
        // Nếu không thì trả về dạng có phần thập phân
        return realNum.toFixed(precision);
    };

    // Case 1: Số phức dạng object {re, im}
    if (typeof num === 'object' && num !== null && num.hasOwnProperty('re') && num.hasOwnProperty('im')) {
        let realPart = num.re;
        let imagPart = num.im;
        if (Math.abs(realPart) < zeroTolerance) realPart = 0;
        if (Math.abs(imagPart) < zeroTolerance) imagPart = 0;

        // SỬA LỖI: Dùng hàm formatReal
        if (imagPart === 0) return formatReal(realPart);
        
        const sign = imagPart < 0 ? ' - ' : ' + ';
        // SỬA LỖI: Dùng hàm formatReal cho cả hai phần
        return `${formatReal(realPart)}${sign}${formatReal(Math.abs(imagPart))}i`;
    }

    // Case 2: Số thực thông thường
    if (typeof num === 'number') {
        // SỬA LỖI QUAN TRỌNG NHẤT: Phải truyền `num`, không phải `precision`
        return formatReal(num);
    }

    // Case 3: Số phức dạng chuỗi
    if (typeof num === 'string' && num.endsWith('j')) {
        let splitPos = -1;
        for (let i = num.length - 2; i > 0; i--) {
            if (num[i] === '+' || num[i] === '-') {
                if (num[i-1].toLowerCase() !== 'e') {
                    splitPos = i;
                    break; 
                }
            }
        }

        if (splitPos !== -1) {
            const realStr = num.substring(0, splitPos);
            const imagStr = num.substring(splitPos, num.length - 1);
            
            const realPart = parseFloat(realStr);
            const imagPart = parseFloat(imagStr);

            if (!isNaN(realPart) && !isNaN(imagPart)) {
                // SỬA LỖI: Dùng hàm formatReal
                if (Math.abs(imagPart) < zeroTolerance) {
                     return formatReal(realPart);
                }
                const sign = imagPart < 0 ? ' - ' : ' + ';
                // SỬA LỖI: Dùng hàm formatReal cho cả hai phần
                return `${formatReal(realPart)}${sign}${formatReal(Math.abs(imagPart))}i`;
            }
        }
    }

    // Fallback
    return num;
}


function formatMatrix(data, precision = displayPrecision) {
    // Thêm kiểm tra để đảm bảo data là mảng 2 chiều hợp lệ
    if (!Array.isArray(data) || !Array.isArray(data[0])) return '';

    // --- Phần tạo bảng HTML cho ma trận (giữ nguyên) ---
    let tableHtml = '<table class=" collapsible-table matrix-table">';
    data.forEach(row => {
        tableHtml += '<tr>';
        row.forEach(cell => {
            tableHtml += `<td>${formatNumber(cell, precision)}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</table>';

    // --- Phần tạo nút sao chép ---
    const copyIcon = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z" />
            <path d="M5 3a2 2 0 00-2 2v6a2 2 0 002 2V5h6a2 2 0 00-2-2H5z" />
        </svg>`;
    
    const copyButtonHtml = `
        <button
            class="copy-matrix-btn absolute -top-1 -right-1 p-1.5 text-gray-500 bg-white bg-opacity-75 backdrop-blur-sm border border-gray-200 hover:bg-gray-200 hover:text-gray-800 rounded-lg transition duration-150 opacity-0 group-hover:opacity-100 focus:opacity-100"
            data-matrix='${JSON.stringify(data)}'
            title="Chép ma trận">
            ${copyIcon}
        </button>
    `;
    
    // --- Trả về HTML cuối cùng ---
    // Bọc ma trận và nút sao chép trong một div với class 'group' và 'relative'
    // 'group' để hiệu ứng group-hover hoạt động, 'relative' để định vị nút con 'absolute'
    return `<div class="group relative inline-block">${copyButtonHtml}${tableHtml}</div>`;
}

/**
 * Tự động tìm tất cả các bảng có class 'collapsible-table',
 * ẩn các hàng ở giữa và thêm nút "Xem thêm / Ẩn bớt".
 * @param {number} headRows - Số hàng đầu tiên luôn hiển thị.
 * @param {number} tailRows - Số hàng cuối cùng luôn hiển thị.
 */
function setupCollapsibleTables(headRows = 3, tailRows = 2) {
    document.querySelectorAll('.collapsible-table').forEach(table => {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        const rows = Array.from(tbody.querySelectorAll('tr'));
        const totalRows = rows.length;
        const MIN_ROWS_TO_COLLAPSE = headRows + tailRows + 2; // Chỉ thu gọn nếu có đủ hàng

        if (totalRows > MIN_ROWS_TO_COLLAPSE) {
            // Ẩn các hàng ở giữa
            for (let i = headRows; i < totalRows - tailRows; i++) {
                rows[i].classList.add('iteration-row-hidden');
            }

            // Tạo và chèn hàng chứa nút "Xem thêm"
            const toggleRow = document.createElement('tr');
            toggleRow.classList.add('toggle-row');
            const toggleCell = document.createElement('td');
            toggleCell.colSpan = rows[0] ? rows[0].cells.length : 1; // Nút sẽ chiếm toàn bộ chiều rộng bảng
            toggleCell.style.textAlign = 'center';

            const toggleBtn = document.createElement('button');
            toggleBtn.classList.add('toggle-table-btn');
            
            const hiddenRowCount = totalRows - headRows - tailRows;
            toggleBtn.textContent = `... (Xem thêm...`;
            toggleBtn.dataset.state = 'collapsed'; // Trạng thái ban đầu

            toggleCell.appendChild(toggleBtn);
            toggleRow.appendChild(toggleCell);

            // Chèn hàng có nút bấm vào sau hàng cuối cùng của phần đầu
            rows[headRows - 1].after(toggleRow);

            // Thêm sự kiện click cho nút
            toggleBtn.addEventListener('click', () => {
                const isCollapsed = toggleBtn.dataset.state === 'collapsed';
                for (let i = headRows; i < totalRows - tailRows; i++) {
                    rows[i].classList.toggle('iteration-row-hidden');
                }
                
                if (isCollapsed) {
                    toggleBtn.textContent = 'Ẩn bớt';
                    toggleBtn.dataset.state = 'expanded';
                } else {
                    toggleBtn.textContent = `... (Xem thêm ${hiddenRowCount} dòng) ...`;
                    toggleBtn.dataset.state = 'collapsed';
                }
            });
        }
    });
}

function attachCopyMatrixEvents() {
    const copyButtons = document.querySelectorAll('.copy-matrix-btn');

    copyButtons.forEach(button => {
        // Gắn sự kiện 'click' cho mỗi nút
        button.addEventListener('click', (event) => {
            const buttonEl = event.currentTarget;
            const jsonMatrix = buttonEl.dataset.matrix; // Lấy dữ liệu từ thuộc tính data-matrix
            if (!jsonMatrix) return;

            const matrix = JSON.parse(jsonMatrix);
            
            // Chuyển mảng 2D thành chuỗi, các cột cách nhau bằng tab, các hàng cách nhau bằng xuống dòng
            const matrixText = matrix.map(row => 
                row.map(cell => {
                    // Xử lý các số phức nếu có
                    if (typeof cell === 'object' && cell !== null && cell.hasOwnProperty('re')) {
                        return formatNumber(cell);
                    }
                    return cell;
                }).join('\t')
            ).join('\n');

            // Sử dụng API Clipboard của trình duyệt để sao chép
            navigator.clipboard.writeText(matrixText).then(() => {
                // Phản hồi cho người dùng: đổi icon thành dấu tick màu xanh
                const originalIcon = buttonEl.innerHTML;
                buttonEl.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>`;
                buttonEl.disabled = true;

                // Sau 2 giây, trả lại icon cũ
                setTimeout(() => {
                    buttonEl.innerHTML = originalIcon;
                    buttonEl.disabled = false;
                }, 2000);
            }).catch(err => {
                console.error('Lỗi khi sao chép ma trận:', err);
                alert('Không thể sao chép vào clipboard.');
            });
        });
    });
}

function displayError(message) {
    const errorMessageDiv = document.getElementById('error-message');
    const resultsAreaDiv = document.getElementById('results-area');
    if (resultsAreaDiv) resultsAreaDiv.innerHTML = '';
    if (errorMessageDiv) {
        errorMessageDiv.classList.remove('hidden');
        errorMessageDiv.textContent = `Lỗi: ${message}`;
    }
}

function resetDisplay() {
    const loadingSpinnerDiv = document.getElementById('loading-spinner');
    const errorMessageDiv = document.getElementById('error-message');
    const resultsAreaDiv = document.getElementById('results-area');

    if (loadingSpinnerDiv) loadingSpinnerDiv.classList.add('hidden');
    if (errorMessageDiv) errorMessageDiv.classList.add('hidden');
    if (resultsAreaDiv) resultsAreaDiv.innerHTML = '';
}

async function handleCalculation(endpoint, body) {
    resetDisplay();
    const loadingSpinnerDiv = document.getElementById('loading-spinner');
    if(loadingSpinnerDiv) loadingSpinnerDiv.classList.remove('hidden');

    try {
        const response = await fetch("http://127.0.0.1:5001" + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            let errorText = `Lỗi Server: ${response.status} ${response.statusText}`;
            try {
                const errorResult = await response.json();
                errorText = errorResult.error || errorText;
            } catch (e) {
                // Do nothing if response is not JSON
            }
            displayError(errorText);
            return;
        }

        let result;
        try {
            result = await response.json();
        } catch (jsonErr) {
            displayError('Lỗi: Server trả về dữ liệu không phải JSON.');
            console.error('Lỗi parse JSON:', jsonErr);
            return;
        }

        resetDisplay();

        if (!result.success) {
            displayError(result.error || 'Lỗi không xác định từ server.');
            console.error('Lỗi backend:', result.error);
            return;
        }
        
        const displayMap = {
            'svd': wrapDisplay(displaySvdResults),
            'gauss-jordan': wrapDisplay(displayGaussJordanResults),
            'gauss-elimination': wrapDisplay(displayGaussEliminationResults),
            'lu-decomposition': wrapDisplay(displayLuResults),
            'cholesky': wrapDisplay(displayCholeskyResults),
            'danilevsky': wrapDisplay(displayDanilevskyResults),
            'power-single': wrapDisplay(displayEigenPowerResults),
            'power-deflation': wrapDisplay(displayEigenPowerResults),
            'solve': wrapDisplay(displayNonlinearEquationResults), 
            'lu': wrapDisplay(displayInverseResults), 
            'bordering': wrapDisplay(displayInverseResults),
            'jacobi': wrapDisplay(displayInverseResults),
            'newton': wrapDisplay(displayInverseResults),
            'gauss-seidel': wrapDisplay(displayInverseResults),
            'nonlinear-system/solve': wrapDisplay(displayNonlinearSystemResults),
            'polynomial/solve': wrapDisplay(displayPolynomialResults)
        };
        
        let key = endpoint.split('/').pop();

        if (endpoint.includes('/matrix/eigen/')) {
            key = endpoint.split('/').pop();
        } else if (endpoint === '/polynomial/solve') {
            key = 'polynomial/solve';
        } else if (endpoint === '/nonlinear-system/solve') {
            key = 'nonlinear-system/solve';
        } else if (endpoint.includes('/matrix/inverse/')) {
            displayMap[key](result, key);
            return; 
        } else if (endpoint.includes('/matrix/iterative/')) {
            displayIterativeHptResults(result, key);
            if (key === 'jacobi') {
                displayJacobiAnalysis(result);
            }
            if (key === 'gauss-seidel') {
                displayGaussSeidelAnalysis(result);
            }
            return;
        }
        
        if (displayMap[key]) {
            displayMap[key](result);
        } else {
             document.getElementById('results-area').innerHTML = '<div class="text-red-600">Không có hàm hiển thị kết quả phù hợp cho endpoint này.</div>';
             console.warn('Không có hàm hiển thị cho endpoint:', endpoint);
        }

    } catch (err) {
        resetDisplay();
        displayError('Không thể kết nối đến máy chủ. Hãy chắc chắn backend Flask đang chạy.\n' + err);
        console.error('Lỗi kết nối hoặc JS:', err);
    }
}

function wrapDisplay(fn) {
    return function(result, method) {
        window.lastResult = result;
        window.lastDisplayFn = fn;
        fn(result, method);
        setupCollapsibleTables();
    };
}

// --- PAGE RENDERING LOGIC FOR SIDEBAR MENU ---
function renderPage(page) {
    const mainContent = document.getElementById('main-content');
    const pageTitle = document.getElementById('page-title');
    if (!mainContent) return;

    let pageHtml = '';
    let setupFunction = null;
    let title = 'Máy tính Giải tích số';

    if (page === 'matrix-solve-direct') {
        pageHtml = document.getElementById('matrix-solve-direct-page').innerHTML;
        setupFunction = setupMatrixSolveEvents;
        title = 'Giải Hệ Phương Trình Tuyến Tính';
    } else if (page === 'matrix-solve-iterative') { // START: THÊM LỰA CHỌN RENDER MỚI
        pageHtml = document.getElementById('matrix-solve-iterative-page').innerHTML;
        setupFunction = setupMatrixSolveIterativeEvents;
        title = 'PP Lặp - Giải Hệ Phương Trình';
    } else if (page === 'matrix-inverse-direct') {
        pageHtml = document.getElementById('matrix-inverse-direct-page').innerHTML;
        setupFunction = setupMatrixInverseDirectEvents;
        title = 'Tính Ma Trận Nghịch Đảo';
    } else if (page === 'matrix-inverse-iterative') {
        pageHtml = document.getElementById('matrix-inverse-iterative-page').innerHTML;
        setupFunction = setupMatrixInverseIterativeEvents;
        title = 'Tính Ma Trận Nghịch Đảo (Lặp)';
    } else if (page === 'matrix-svd') {
        pageHtml = document.getElementById('matrix-svd-page').innerHTML;
        setupFunction = setupMatrixSvdEvents;
        title = 'Phân Rã Giá Trị Suy Biến (SVD)';
    } else if (page === 'matrix-eigen-methods') {
        pageHtml = document.getElementById('matrix-eigen-methods-page').innerHTML;
        pageTitle.textContent = 'Tìm Giá Trị Riêng';
        setupFunction = setupMatrixEigenMethodsEvents;
    } else if (page === 'nonlinear-solve') {
        pageHtml = document.getElementById('nonlinear-solve-page').innerHTML;
        setupFunction = setupNonlinearSolveEvents;
        title = 'Giải phương trình phi tuyến f(x) = 0';
    } else if (page === 'nonlinear-system-solve') {
        pageHtml = document.getElementById('nonlinear-system-solve-page').innerHTML;
        setupFunction = setupNonlinearSystemSolveEvents;
        title = 'Giải Hệ Phương Trình Phi Tuyến';
    } else if (page === 'polynomial-solve') {
        pageHtml = document.getElementById('polynomial-solve-page').innerHTML;
        setupFunction = setupPolynomialSolveEvents;
        title = 'Giải Phương Trình Đa Thức';
    } else {
        pageHtml = '<div class="text-center text-gray-500">Chọn một chức năng ở menu bên trái.</div>';
    }
    
    mainContent.innerHTML = pageHtml;
    pageTitle.textContent = title;

    if(setupFunction) {
        setupFunction();
    }

    window.lastResult = null;
    window.lastDisplayFn = null;
}

// Gắn sự kiện cho sidebar menu
document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', e => {
        // BƯỚC 1: Xóa màu active khỏi TẤT CẢ các nút
        // Dòng code này sẽ tìm mọi phần tử có thuộc tính [data-page] và xóa hết các lớp màu của chúng.
        document.querySelectorAll('[data-page]').forEach(b => {
            b.classList.remove('bg-blue-100', 'text-blue-700');
            b.classList.remove('bg-green-100', 'text-green-700');
            b.classList.remove('bg-yellow-100', 'text-yellow-700');
            b.classList.remove('bg-purple-100', 'text-purple-700');
        });
        
        // BƯỚC 2: Thêm màu active cho nút vừa được click
        const button = e.currentTarget;
        const page = button.getAttribute('data-page');

        if (page.startsWith('matrix')) {
            button.classList.add('bg-blue-100', 'text-blue-700');
        } else if (page === 'nonlinear-solve') {
            button.classList.add('bg-green-100', 'text-green-700');
        } else if (page === 'polynomial-solve') {
            button.classList.add('bg-purple-100', 'text-purple-700');
        // END: THÊM ĐỔI MÀU
        } else if (page === 'nonlinear-system-solve') {
            button.classList.add('bg-yellow-100', 'text-yellow-700');
        }

        // BƯỚC 3: Hiển thị nội dung trang tương ứng
        renderPage(page);
    });
});
// Hàm setup lại event cho trang giải hệ phương trình
function setupHptCalculation(endpoint) {
    const matrixA_Input = document.getElementById('matrix-a-input-hpt');
    const matrixB_Input = document.getElementById('matrix-b-input-hpt');

    const matrixA = parseMatrix(matrixA_Input.value);
    if (matrixA.error || matrixA.length === 0) {
        displayError(matrixA.error || 'Ma trận A không được để trống.');
        return;
    }
    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) {
        displayError(matrixB.error || 'Ma trận B không được để trống.');
        return;
    }
    if (matrixA.length !== matrixB.length) {
         displayError(`Số hàng của ma trận A (${matrixA.length}) và B (${matrixB.length}) phải bằng nhau.`);
         return;
    }

    const body = { matrix_a: matrixA, matrix_b: matrixB };
    handleCalculation(endpoint, body);
}

function setupMatrixSolveEvents() {
    document.getElementById('calculate-gauss-btn').onclick = () => setupHptCalculation('/matrix/gauss-elimination');
    document.getElementById('calculate-gj-btn').onclick = () => setupHptCalculation('/matrix/gauss-jordan');
    document.getElementById('calculate-lu-btn').onclick = () => setupHptCalculation('/matrix/lu-decomposition');
    document.getElementById('calculate-cholesky-btn').onclick = () => setupHptCalculation('/matrix/cholesky');
}

// --- START: CÁC HÀM SETUP EVENT MỚI ---
function setupInverseCalculation(endpoint, inputId) {
    const matrixA_Input = document.getElementById(inputId);
    const matrixA = parseMatrix(matrixA_Input.value);

    if (matrixA.error || matrixA.length === 0) {
        displayError(matrixA.error || 'Ma trận A không được để trống.');
        return;
    }

    if (matrixA.length !== matrixA[0].length) {
        displayError('Ma trận nghịch đảo yêu cầu ma trận vuông.');
        return;
    }

    const body = { matrix_a: matrixA };
    
    // Thêm các tham số cho phương pháp lặp
    if (inputId === 'matrix-a-input-inv-iter') {
        const tolerance = document.getElementById('inv-iter-tolerance').value;
        const maxIter = document.getElementById('inv-iter-max-iter').value;
        const x0Method = document.getElementById('inv-iter-x0-select').value;
        if (!tolerance || !maxIter) {
            displayError("Vui lòng nhập đủ Sai số và Số lần lặp tối đa.");
            return;
        }
        body.tolerance = parseFloat(tolerance);
        body.max_iter = parseInt(maxIter);
        body.x0_method = x0Method;
    }

    handleCalculation(endpoint, body);
}

function setupMatrixInverseDirectEvents() {
    const inputId = 'matrix-a-input-inv-direct';
    document.getElementById('calculate-inv-gj-btn').onclick = () => setupInverseCalculation('/matrix/inverse/gauss-jordan', inputId);
    document.getElementById('calculate-inv-lu-btn').onclick = () => setupInverseCalculation('/matrix/inverse/lu', inputId);
    document.getElementById('calculate-inv-cholesky-btn').onclick = () => setupInverseCalculation('/matrix/inverse/cholesky', inputId);
    document.getElementById('calculate-inv-bordering-btn').onclick = () => setupInverseCalculation('/matrix/inverse/bordering', inputId);
}

function setupMatrixInverseIterativeEvents() {
    const inputId = 'matrix-a-input-inv-iter';
    document.getElementById('calculate-inv-jacobi-btn').onclick = () => setupInverseCalculation('/matrix/inverse/jacobi', inputId);
    document.getElementById('calculate-inv-newton-btn').onclick = () => setupInverseCalculation('/matrix/inverse/newton', inputId);
    document.getElementById('calculate-inv-gauss-seidel-btn').onclick = () => setupInverseCalculation('/matrix/inverse/gauss-seidel', inputId);
}

// --- END: CÁC HÀM SETUP EVENT MỚI ---

// Hàm setup lại event cho trang SVD
function setupMatrixSvdEvents() {
    const matrixA_Input = document.getElementById('matrix-a-input-svd');
    const methodSelect = document.getElementById('svd-method-select');
    const numSingularInput = document.getElementById('svd-num-singular');
    const yInitInput = document.getElementById('svd-init-matrix-input');
    const powerOptionsDiv = document.getElementById('svd-power-options');

    function updateSvdOptions() {
        if (methodSelect.value === 'power') {
            powerOptionsDiv.style.display = 'block';
        } else {
            powerOptionsDiv.style.display = 'none';
        }
    }
    if (methodSelect) {
        methodSelect.onchange = updateSvdOptions;
        updateSvdOptions();
    }

    document.getElementById('calculate-svd-btn').onclick = () => {
        const matrixA = parseMatrix(matrixA_Input.value);
        if (matrixA.error || matrixA.length === 0) {
            displayError(matrixA.error || 'Ma trận A không được để trống.');
            return;
        }
        const method = methodSelect ? methodSelect.value : 'default';
        const body = { matrix_a: matrixA, method };
        if (method === 'power') {
            if (numSingularInput && numSingularInput.value) {
                body.num_singular = parseInt(numSingularInput.value);
            }
            if (yInitInput && yInitInput.value.trim()) {
                let yInitArr = [];
                const lines = yInitInput.value.trim().split('\n');
                if (lines.length === 1) {
                    yInitArr = lines[0].trim().split(/\s+/).map(Number);
                } else {
                    yInitArr = lines.map(x => parseFloat(x.trim()));
                }
                if (yInitArr.some(isNaN)) {
                    displayError('Vector khởi đầu không hợp lệ.');
                    return;
                }
                body.init_matrix = yInitArr;
            }
        }
        handleCalculation('/matrix/svd', body);
    };
}
// Hàm setup lại event cho trang Danilevsky
function setupMatrixEigenMethodsEvents() {
    const tabs = document.querySelectorAll('.eigen-tab');
    const tabContents = document.querySelectorAll('.eigen-tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => {
                item.classList.remove('text-blue-600', 'border-blue-500');
                item.classList.add('text-gray-500', 'border-transparent', 'hover:text-gray-700', 'hover:border-gray-300');
            });
            tab.classList.add('text-blue-600', 'border-blue-500');
            tab.classList.remove('text-gray-500', 'border-transparent');

            const targetContentId = `eigen-${tab.dataset.tab}-content`;
            tabContents.forEach(content => {
                content.style.display = content.id === targetContentId ? 'block' : 'none';
            });
            document.getElementById('results-area').innerHTML = '';
        });
    });

    // --- Gắn sự kiện cho từng nút tính toán (ĐÃ SỬA) ---

    // 1. Danilevsky
    document.getElementById('calculate-danilevsky-btn').onclick = () => {
        const matrixStr = document.getElementById('matrix-a-input-danilevsky').value;
        const matrixA = parseMatrix(matrixStr);
        if (matrixA.error) {
            displayError(matrixA.error);
            return;
        }
        // Sửa ở đây: Chỉ 2 tham số
        handleCalculation('/matrix/danilevsky', { matrix_a: matrixA });
    };

    // 2. Power Method (Single)
    document.getElementById('calculate-power-method-single-btn').onclick = () => {
        const matrixStr = document.getElementById('matrix-a-input-power-single').value;
        const matrixA = parseMatrix(matrixStr);
        if (matrixA.error) {
            displayError(matrixA.error);
            return;
        }
        const tolerance = document.getElementById('power-single-tolerance').value;
        const max_iter = document.getElementById('power-single-max-iter').value;
        const body = { matrix_a: matrixA, tolerance: tolerance, max_iter: max_iter };
        // Sửa ở đây: Chỉ 2 tham số
        handleCalculation('/matrix/eigen/power-single', body);
    };

    // 3. Power Method & Deflation
    document.getElementById('calculate-power-method-deflation-btn').onclick = () => {
        const matrixStr = document.getElementById('matrix-a-input-power-deflation').value;
        const matrixA = parseMatrix(matrixStr);
        if (matrixA.error) {
            displayError(matrixA.error);
            return;
        }
        const num_eigen = document.getElementById('power-deflation-num-eigen').value;
        const tolerance = document.getElementById('power-deflation-tolerance').value;
        const max_iter = document.getElementById('power-deflation-max-iter').value;
        const body = { matrix_a: matrixA, num_eigen: num_eigen, tolerance: tolerance, max_iter: max_iter };
        // Sửa ở đây: Chỉ 2 tham số
        handleCalculation('/matrix/eigen/power-deflation', body);
    };
}

// Hàm hiển thị kết quả cho 2 phương pháp Lũy thừa
function setupNonlinearSolveEvents() {
    // --- Lấy các element trên DOM ---
    const methodSelect = document.getElementById('nonlinear-method-select');
    const calculateBtn = document.getElementById('calculate-nonlinear-btn');
    
    // THÊM MỚI: Lấy element của dropdown điều kiện dừng
    const stopModeSelect = document.getElementById('stop-mode-select');

    const fGroup = document.getElementById('f-expression-group');
    const phiGroup = document.getElementById('phi-expression-group');
    const x0Group = document.getElementById('x0-group');
    const advancedStopGroup = document.getElementById('advanced-stop-condition-group');

    const fInput = document.getElementById('f-expression-input');
    const phiInput = document.getElementById('phi-expression-input');

    const fPreview = document.getElementById('f-latex-preview');
    const phiPreview = document.getElementById('phi-latex-preview');
    
    const advLabel1 = document.getElementById('adv-stop-label-1');
    const advLabel2 = document.getElementById('adv-stop-label-2');

    // SỬA ĐỔI: Tạo cấu trúc dữ liệu mới chứa cả công thức sai số tuyệt đối và tương đối
    const errorFormulas = {
        newton: {
            absolute: {
                opt1: String.raw`\frac{|f(x_{n})|}{m_1}`,
                opt2: String.raw`\frac{M_2}{2m_1}|x_{n+1}-x_n|^2`
            },
            relative: {
                opt1: String.raw`\frac{|f(x_{n})|}{m_1 |x_n|}`,
                opt2: String.raw`\frac{M_2}{2m_1}\frac{|x_{n+1}-x_n|^2}{|x_{n+1}|}`
            }
        },
        secant: {
            absolute: {
                opt1: String.raw`\frac{|f(x_n)|}{m_1}`,
                opt2: String.raw`\frac{M_1-m_1}{m_1}|x_n-x_{n-1}|`
            },
            relative: {
                opt1: String.raw`\frac{|f(x_n)|}{m_1 |x_n|}`,
                opt2: String.raw`\frac{M_1-m_1}{m_1}\frac{|x_n-x_{n-1}|}{|x_{n+1}|}`
            }
        }
    };

    // --- Hàm render LaTeX (live preview) --- (Giữ nguyên)
    function renderLatex(inputElement, previewElement) {
        const latexString = inputElement.value;
        if (latexString.trim() === "") {
            previewElement.innerHTML = "";
            previewElement.classList.remove('text-red-500');
            return;
        }
        try {
            katex.render(latexString, previewElement, { throwOnError: true, displayMode: true });
            previewElement.classList.remove('text-red-500');
        } catch (error) {
            previewElement.textContent = "Lỗi cú pháp LaTeX";
            previewElement.classList.add('text-red-500');
        }
    }

    // --- Gắn sự kiện ---
    fInput.addEventListener('input', () => renderLatex(fInput, fPreview));
    phiInput.addEventListener('input', () => renderLatex(phiInput, phiPreview));
    
    // SỬA ĐỔI HOÀN TOÀN: Hàm cập nhật giao diện
    function updateUIVisibility() {
        const method = methodSelect.value;
        const mode = stopModeSelect.value; // Lấy cả mode (tuyệt đối, tương đối, lặp)

        // 1. Ẩn/hiện các ô nhập f(x) và φ(x)
        fGroup.style.display = (method !== 'simple_iteration') ? 'block' : 'none';
        phiGroup.style.display = (method === 'simple_iteration') ? 'block' : 'none';
        x0Group.style.display = (method === 'simple_iteration') ? 'block' : 'none';
        
        // 2. Điều kiện để hiện khung chọn công thức sai số
        const showAdvanced = (method === 'newton' || method === 'secant') && 
                             (mode === 'absolute_error' || mode === 'relative_error');
        
        advancedStopGroup.style.display = showAdvanced ? 'block' : 'none';
        
        if (showAdvanced) {
            // Lấy đúng bộ công thức dựa trên cả phương pháp và loại sai số
            const errorModeKey = mode.split('_')[0]; // 'absolute_error' -> 'absolute'
            const formulaSet = errorFormulas[method][errorModeKey];
            
            if (formulaSet) {
                try {
                    katex.render(formulaSet.opt1, advLabel1, { throwOnError: false, displayMode: false });
                    katex.render(formulaSet.opt2, advLabel2, { throwOnError: false, displayMode: false });
                } catch (e) {
                    console.error("Lỗi render KaTeX:", e);
                }
            }
        }
        
        renderLatex(fInput, fPreview);
        renderLatex(phiInput, phiPreview);
    }

    // Gắn sự kiện cho cả hai dropdown
    methodSelect.addEventListener('change', updateUIVisibility);
    stopModeSelect.addEventListener('change', updateUIVisibility); // THÊM MỚI

    // Logic nút "Giải" (giữ nguyên như trước)
    calculateBtn.addEventListener('click', () => {
        const method = methodSelect.value;
        const latexExpression = (method === 'simple_iteration') ? phiInput.value : fInput.value;
        const pythonExpression = latexToPython(latexExpression);
        const stopConditionElement = document.querySelector('input[name="advanced-stop-option"]:checked');
        const stopConditionValue = stopConditionElement ? stopConditionElement.value : null;

        const body = {
            method: method,
            expression: pythonExpression,
            interval_a: document.getElementById('interval-a-input').value,
            interval_b: document.getElementById('interval-b-input').value,
            mode: document.getElementById('stop-mode-select').value,
            value: document.getElementById('stop-value-input').value,
            stop_condition: stopConditionValue, 
        };

        if (method === 'simple_iteration') {
            body.x0 = document.getElementById('x0-input').value;
        }
        
        // Validate inputs
        if (!latexExpression) {
            displayError('Vui lòng nhập biểu thức hàm số.');
            return;
        }
        if (!body.interval_a || !body.interval_b) {
            displayError('Vui lòng nhập đủ khoảng [a, b].');
            return;
        }
        if (!body.value) {
            displayError('Vui lòng nhập giá trị cho điều kiện dừng.');
            return;
        }

        handleCalculation('/nonlinear-equation/solve', body);
    });

    // Khởi tạo UI và preview ban đầu
    updateUIVisibility();
}


function displayNonlinearEquationResults(result) {
    const resultsArea = document.getElementById('results-area');
    
    // Phần 1: Hiển thị kết quả tóm tắt
    let html = `
        <h3 class="result-heading">Kết Quả Giải Phương Trình</h3>
        <div class="text-center font-medium text-lg mb-6 p-4 bg-green-50 rounded-lg shadow-inner">
            Nghiệm x ≈ <span class="font-bold text-green-700">${formatNumber(result.solution)}</span>
        </div>
        <div class="mb-4 text-center text-gray-600">
            Số lần lặp: ${result.iterations}
        </div>
    `;

    // Phần 2: Chỉ hiển thị các hệ số có trong kết quả trả về
    let coeffsHtmlParts = [];
    if (result.hasOwnProperty('m1')) {
        coeffsHtmlParts.push(`<span class="font-mono" id="m1-container">m_1 = \\min|f'(x)| \\approx ${formatNumber(result.m1, 4)}</span>`);
    }
    if (result.hasOwnProperty('M1')) {
        coeffsHtmlParts.push(`<span class="font-mono" id="M1-container">M_1 = \\max|f'(x)| \\approx ${formatNumber(result.M1, 4)}</span>`);
    }
    if (result.hasOwnProperty('M2')) {
        coeffsHtmlParts.push(`<span class="font-mono" id="M2-container">M_2 = \\max|f''(x)| \\approx ${formatNumber(result.M2, 4)}</span>`);
    }
    if (result.hasOwnProperty('q')) {
        coeffsHtmlParts.push(`<span class="font-mono" id="q-container">q = \\max|\\phi'(x)| \\approx ${formatNumber(result.q, 4)}</span>`);
    }

    if (coeffsHtmlParts.length > 0) {
        html += `<div class="text-center text-sm text-gray-800 mb-6 p-3 bg-gray-100 rounded-md">
                    <span class="font-semibold">Các hệ số hội tụ: </span>
                    ${coeffsHtmlParts.join('; &nbsp; ')}
                 </div>`;
    }

    // Phần 3: Hiển thị bảng các bước lặp với thứ tự cột được sắp xếp
    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Bảng Các Bước Lặp</h3>`;
        
        const headers = Object.keys(result.steps[0]);

        // SỬA ĐỔI: Cập nhật lại mảng thứ tự ưu tiên cho các cột
        const preferredOrder = [
            'n', 'k',         // 1. Cột lặp
            'a', 'a_k',       // 2. Cột biên a (cho Bisection)
            'b', 'b_k',       // 3. Cột biên b (cho Bisection)
            'c', 'c_k', 'x_n', 'x_k', // 4. Cột nghiệm xấp xỉ
            'f(c)', 'f(c_k)', 'f(x_n)', 'f_xk', 'f(x_k)', // 5. Cột giá trị hàm
            'error'           // 6. Cột sai số
            // Các cột khác sẽ được sắp xếp theo alphabet sau các cột này
        ];

        headers.sort((a, b) => {
            let indexA = preferredOrder.indexOf(a);
            let indexB = preferredOrder.indexOf(b);
            if (indexA === -1) indexA = Infinity;
            if (indexB === -1) indexB = Infinity;
            if (indexA !== indexB) return indexA - indexB;
            return a.localeCompare(b);
        });
        
        html += `<div class="overflow-x-auto"><table class=" collapsible-table min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>`;
        
        headers.forEach(header => {
            const headerDisplayMap = {
                'n': 'n', 'k': 'k', 'a': 'a_n', 'b': 'b_n',
                'c': 'c_n', 'x_n': 'x_n',
                'f(c)': 'f(c_n)', 'f(x_n)': 'f(x_n)',
                'phi(x_k)': '\\phi(x_k)', "f'(x_k)": "f'(x_k)",
                'error': '\\text{Sai số}',
            };
            const displayHeader = headerDisplayMap[header] || header;
            html += `<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider"><span class="katex-header" data-header="${displayHeader}"></span></th>`;
        });
        html += `</tr></thead><tbody class="bg-white divide-y divide-gray-200">`;

        result.steps.forEach(step => {
            html += `<tr>`;
            headers.forEach(header => {
                html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${formatNumber(step[header])}</td>`;
            });
            html += `</tr>`;
        });
        html += `</tbody></table></div></div>`;
    }
    
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();

    // Phần 4: Render LaTeX cho các hệ số và tiêu đề bảng
    coeffsHtmlParts.forEach((part) => {
        const idMatch = part.match(/id="([^"]+)"/);
        if (idMatch) {
            const element = document.getElementById(idMatch[1]);
            if (element) {
                katex.render(element.textContent, element, { throwOnError: false, displayMode: false });
            }
        }
    });

    document.querySelectorAll('.katex-header').forEach(element => {
        const latexString = element.getAttribute('data-header');
        katex.render(latexString, element, { throwOnError: false });
    });
}
// ===============================================
// === END: CODE MỚI
// ===============================================
function displayEigenPowerResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Phương Pháp Luỹ Thừa</h3>`;

    if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-green-50 rounded-lg shadow-inner">${result.message}</div>`;
    }
    
    // Hiển thị cảnh báo nếu có
    if (result.warnings && result.warnings.length > 0) {
        result.warnings.forEach(warning => {
            html += `<div class="text-center font-medium text-md mb-6 p-3 bg-yellow-100 text-yellow-800 rounded-lg shadow-inner">${warning}</div>`;
        });
    }

    // Phần 1: Hiển thị bảng kết quả tóm tắt cuối cùng
    if (result.eigenvalues && result.eigenvectors) {
        html += `<div class="mb-8 p-4 border rounded-lg bg-gray-50">
                    <h4 class="font-semibold text-gray-700 text-lg mb-2 text-center">Kết quả cuối cùng</h4>
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="px-4 py-2 text-left font-medium text-gray-600">#</th>
                                <th class="px-4 py-2 text-left font-medium text-gray-600">Giá trị riêng (λ)</th>
                                <th class="px-4 py-2 text-left font-medium text-gray-600">Vector riêng tương ứng (v)</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">`;
        result.eigenvalues.forEach((val, i) => {
            // Chuyển đổi vector từ chuỗi phức thành mảng số phức để formatMatrix có thể xử lý
            const vector_data = result.eigenvectors[i].map(v_str => {
                 try {
                    // Cố gắng parse chuỗi phức, ví dụ "1-2.5j"
                    const complexVal = parseFloat(v_str.replace('j', 'j'));
                    return isNaN(complexVal) ? v_str : complexVal;
                 } catch(e) { return v_str; }
            });
            const vec_as_column = vector_data.map(v => [v]); // Chuyển thành vector cột để hiển thị
            html += `<tr>
                        <td class="px-4 py-2 font-mono">${i + 1}</td>
                        <td class="px-4 py-2 font-mono text-indigo-700 font-semibold">${formatNumber(val)}</td>
                        <td class="px-4 py-2 font-mono">${formatMatrix(vec_as_column)}</td>
                     </tr>`;
        });
        html += `   </tbody>
                    </table>
                 </div>`;
    }

    // Phần 2: Hiển thị các bước lặp chi tiết
    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Lặp & Xuống Thang Chi Tiết</h3>`;

        const isSimplePowerMethod = result.steps[0].hasOwnProperty('k') && !result.steps[0].hasOwnProperty('eigenvalue_index');

        if (isSimplePowerMethod) {
            // Trường hợp chỉ chạy PP Lũy thừa đơn giản, không xuống thang
            if (result.complex_pair_details) {
                const details = result.complex_pair_details;
                html += `<div class="mt-10 p-4 border rounded-lg bg-gray-50/50">
                            <h3 class="result-heading !text-xl !border-gray-300">Chi tiết tìm cặp GTR Phức</h3>
                            <div class="space-y-4 text-sm">
                                <p>Lấy 3 vector lặp cuối cùng (đã chuẩn hóa):</p>
                                <ul class="list-disc list-inside ml-4 font-mono bg-gray-100 p-3 rounded">
                                   <li><b>z₀:</b> [${details.z0.join(', ')}]</li>
                                   <li><b>z₁ = A·z₀:</b> [${details.z1.join(', ')}]</li>
                                   <li><b>z₂ = A·z₁:</b> [${details.z2.join(', ')}]</li>
                                </ul>
                                <p>Lập hệ phương trình tuyến tính <b>z₂ ≈ p·z₁ - q·z₀</b> để tìm p, q. Sử dụng 2 phương trình tại các chỉ số <b>${details.indices_used.map(i => i+1).join(', ')}</b>:</p>
                                <div class="flex justify-center items-center flex-wrap gap-x-4">
                                   <div class="matrix-display !inline-block" title="Ma trận M">${formatMatrix(details.matrix_M)}</div>
                                   <span class="font-mono text-lg"> · </span>
                                   <div class="matrix-display !inline-block" title="Vector [p, -q]"><table class=" collapsible-table matrix-table"><tr><td>p</td></tr><tr><td>-q</td></tr></table></div>
                                   <span class="font-mono text-lg"> = </span>
                                   <div class="matrix-display !inline-block" title="Vector b">${formatMatrix(details.vector_b.map(v => [v]))}</div>
                                </div>
                                <p>Giải hệ, tìm được <b>p ≈ ${details.solved_p}</b> và <b>q ≈ ${details.solved_q}</b>.</p>
                                <p>Nghiệm của phương trình đặc trưng <b class="font-mono bg-indigo-100 text-indigo-800 px-2 py-1 rounded">${details.quadratic_equation}</b> là các giá trị riêng cần tìm.</p>
                            </div>
                         </div>`;
            }
            if (result.opposite_sign_details) {
                const details = result.opposite_sign_details;
                html += `<div class="mt-10 p-4 border rounded-lg bg-gray-50/50">
                            <h3 class="result-heading !text-xl !border-gray-300">Chi tiết tìm cặp GTR Đối Dấu</h3>
                            <div class="space-y-4 text-sm">
                                <p>Do lặp không hội tụ, ta xét ma trận <b>A' = A²</b>:</p>
                                <div class="matrix-display">${formatMatrix(details.A_squared)}</div>
                                <details class="mt-3 bg-white p-3 rounded border">
                                    <summary class="cursor-pointer font-medium text-blue-600 hover:text-blue-800">Xem quá trình lặp cho A'</summary>
                                    <div class="overflow-x-auto mt-2">`;
                const subResult = details.A_squared_result;
                if (subResult && subResult.steps && subResult.steps.length > 0) {
                    html += `<table class=" collapsible-table min-w-full divide-y divide-gray-200 text-sm"><thead class="bg-gray-100"><tr><th class="px-4 py-2 text-left font-medium text-gray-600">k</th><th class="px-4 py-2 text-left font-medium text-gray-600">xₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">A'·xₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">λ'ₖ</th></tr></thead><tbody class="bg-white divide-y divide-gray-200">`;
                    subResult.steps.forEach(iter => { html += `<tr><td class="px-4 py-2 font-mono">${iter.k}</td><td class="px-4 py-2 font-mono">[${iter.x_k.join(', ')}]</td><td class="px-4 py-2 font-mono">[${iter.Ax_k.join(', ')}]</td><td class="px-4 py-2 font-mono text-blue-700 font-semibold">${iter.lambda_k}</td></tr>`; });
                    html += `</tbody></table>`;
                } else { html += `<p class="text-gray-500">Không có chi tiết bước lặp cho A'.</p>`; }
                html += `</div></details>
                                <p>Kết quả cho <b>A'</b>: GTR trội <b>λ' ≈ ${details.lambda_squared_found}</b> và VTR tương ứng <b>v' ≈ [${details.v_from_A2.join(', ')}]</b>.</p>
                                <p>Các giá trị riêng của A là: <b>λ₁,₂ = ±√λ' ≈ ±${details.final_lambda1}</b>.</p>
                                <p>Các vector riêng tương ứng của A được tính bằng:</p>
                                <ul class="list-disc list-inside ml-4 font-mono bg-gray-100 p-3 rounded">
                                    <li><b>v₁ = (A·v' + λ₁·v') ≈</b> [${details.v1_final.join(', ')}]</li>
                                    <li><b>v₂ = (A·v' - λ₁·v') ≈</b> [${details.v2_final.join(', ')}]</li>
                                </ul>
                            </div>
                        </div>`;
            }
             html += `<p class="text-center text-sm text-gray-500 mb-4">(Đây là các bước lặp cơ bản của phương pháp luỹ thừa, trước khi xét các trường hợp đặc biệt)</p>`;
             html += `<div class="overflow-x-auto mt-2"><table class=" collapsible-table min-w-full divide-y divide-gray-200 text-sm"><thead class="bg-gray-100"><tr><th class="px-4 py-2 text-left font-medium text-gray-600">k</th><th class="px-4 py-2 text-left font-medium text-gray-600">xₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">A·xₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">λₖ</th></tr></thead><tbody class="bg-white divide-y divide-gray-200">`;
             result.steps.forEach(iter => { html += `<tr><td class="px-4 py-2 font-mono">${iter.k}</td><td class="px-4 py-2 font-mono">[${iter.x_k.join(', ')}]</td><td class="px-4 py-2 font-mono">[${iter.Ax_k.join(', ')}]</td><td class="px-4 py-2 font-mono text-blue-700 font-semibold">${iter.lambda_k}</td></tr>`; });
             html += `</tbody></table></div>`;
        } else {
            // Trường hợp có xuống thang (logic hiển thị mới)
            html += `<div class="space-y-8">`;
            result.steps.forEach((step, stepIdx) => {
                html += `<div class="p-4 border border-blue-200 rounded-lg bg-blue-50/50">
                            <h4 class="font-semibold text-blue-800 text-xl">Bước ${step.eigenvalue_index}: Tìm giá trị riêng trội của A<sub>${step.eigenvalue_index - 1}</sub></h4>
                            <p class="text-sm text-gray-600 mt-2">Ma trận hiện tại A<sub>${step.eigenvalue_index - 1}</sub>:</p>
                            <div class="matrix-display">${formatMatrix(step.matrix_before_deflation)}</div>
                            
                            <details class="mt-3 bg-white p-3 rounded border" open>
                                <summary class="cursor-pointer font-medium text-gray-700 hover:text-gray-900">Chi tiết quá trình lặp của Bước ${step.eigenvalue_index}</summary>
                                <div class="mt-2 space-y-3">`;

                // 'iteration_details' bây giờ là một danh sách các bước lặp nhỏ
                const stepDetails = step.iteration_details; 

                if (stepDetails && Array.isArray(stepDetails) && stepDetails.length > 0) {
                    html += `<div class="overflow-x-auto"><h5 class="text-sm font-semibold text-gray-600 mb-1">Các bước lặp:</h5><table class=" collapsible-table min-w-full divide-y divide-gray-200 text-sm"><thead class="bg-gray-100"><tr><th class="px-4 py-2 text-left font-medium text-gray-600">k</th><th class="px-4 py-2 text-left font-medium text-gray-600">xₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">A·xₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">λₖ</th></tr></thead><tbody class="bg-white divide-y divide-gray-200">`;
                    stepDetails.forEach(iter => {
                        html += `<tr><td class="px-4 py-2 font-mono">${iter.k}</td><td class="px-4 py-2 font-mono">[${iter.x_k.map(v => formatNumber(v)).join(', ')}]</td><td class="px-4 py-2 font-mono">[${iter.Ax_k.map(v => formatNumber(v)).join(', ')}]</td><td class="px-4 py-2 font-mono text-blue-700 font-semibold">${formatNumber(iter.lambda_k)}</td></tr>`;
                    });
                    html += `</tbody></table></div>`;
                }

                html += `</div></details>`;
                
                // Hiển thị kết quả tìm được trong bước này
                const summary = step.iteration_summary;
                if (summary && summary.found_eigenvalue) {
                     html += `<div class="mt-4 p-3 bg-green-100 rounded-md"><p class="font-medium text-green-800">Kết quả của Bước ${step.eigenvalue_index}:</p>`;
                     html += `<p class="font-mono text-sm">→ Tìm được GTR ≈ <b>${formatNumber(summary.found_eigenvalue)}</b></p>`;
                     html += `</div>`;
                }
                
                html += `</div>`; // Đóng div của một bước xuống thang
            });
            html += `</div>`;
        }
        html += `</div>`;
    }

    resultsArea.innerHTML = html;
    attachCopyMatrixEvents();
}

function displayJacobiAnalysis(result) {
    // Chỉ hoạt động nếu có đủ dữ liệu phân tích
    if (result.contraction_coefficient === undefined || result.norm_used === undefined) {
        return;
    }

    const resultsArea = document.getElementById('results-area');
    if (!resultsArea) return;

    const analysisDiv = document.createElement('div');
    
    let html = `<div class="mt-10">
                    <h3 class="result-heading">Phân Tích Hội Tụ</h3>
                    <div class="p-4 border rounded-lg bg-gray-50">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-center">`;
    
    let dominanceText = '';
    const normSymbol = result.norm_used === '1' ? '₁' : '∞';
    if (result.dominance_type === 'row') {
        dominanceText = `Ma trận chéo trội hàng. Sử dụng Chuẩn ${normSymbol}.`;
    } else if (result.dominance_type === 'column') {
        dominanceText = `Ma trận chéo trội cột. Sử dụng Chuẩn ${normSymbol}.`;
    } else {
        dominanceText = `Ma trận không chéo trội. Sử dụng Chuẩn ${normSymbol} mặc định.`;
    }

    html += `<div class="p-3 bg-white rounded-md shadow-sm">
                <span class="font-medium text-gray-600">Điều kiện hội tụ</span>
                <p class="text-base text-gray-800 mt-1">${dominanceText}</p>
             </div>`;

    html += `<div class="p-3 bg-white rounded-md shadow-sm">
                <span class="font-medium text-gray-600">Hệ số co q = ||B||${normSymbol}</span>
                <p class="font-mono text-xl text-blue-600 mt-1">${formatNumber(result.contraction_coefficient, 6)}</p>
             </div>`;
                 
    html += `       </div>
                </div>
            </div>`;
    
    analysisDiv.innerHTML = html;
    // Thêm khối phân tích vào cuối của khu vực kết quả
    resultsArea.prepend(analysisDiv);
}

// --- START: CODE MỚI ---
function displayInverseResults(result, method) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Ma Trận Nghịch Đảo A⁻¹</h3>`;
    
    if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-blue-50 rounded-lg shadow-inner">${result.message}</div>`;
    }

    // --- BỔ SUNG: Hiển thị thông tin Jacobi Inverse ---
    if (method === 'jacobi') {
        html += `<div class="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-3 bg-gray-50 rounded shadow">
                <div><b>Hệ số co:</b> <span class="font-mono">${typeof result.contraction_coefficient !== 'undefined' ? result.contraction_coefficient.toFixed(6) : ''}</span></div>
                <div><b>Chuẩn dừng:</b> <span class="font-mono">${result.norm_used || ''}</span></div>
                <div><b>Chéo trội:</b> <span class="font-mono">${result.dominance_type || ''}</span></div>
            </div>
            <div class="p-3 bg-gray-50 rounded shadow">
                <div><b>Công thức dừng:</b> <span class="font-mono">${result.stop_formula || ''}</span></div>
                <div><b>X₀:</b> <span class="font-mono">${result.x0_label || ''}</span></div>
            </div>
        </div>`;
    }
    if (method === 'gauss-seidel' && result.contraction_coefficient_q !== undefined) {
        html += `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 shadow-sm">
                <div class="font-semibold text-blue-700 mb-2 flex items-center">
                    <span class="material-icons mr-2">info</span> Thông tin hội tụ & lặp
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1 text-sm">
                    <div><b>Hệ số co q:</b> ${formatNumber(result.contraction_coefficient_q, 6)}</div>
                    <div><b>Hệ số s:</b> ${formatNumber(result.contraction_coefficient_s, 6)}</div>
                    <div><b>Chuẩn sử dụng:</b> ${result.norm_used}</div>
                    <div><b>Kiểu chéo trội:</b> ${result.dominance_type}</div>
                    <div class="md:col-span-2"><b>Công thức dừng:</b> <span class="font-mono">${result.stop_formula}</span></div>
                    <div class="md:col-span-2"><b>X₀:</b> <span class="font-mono">${result.x0_label}</span></div>
                </div>
                </div>
        `;
    }
    // --- END BỔ SUNG ---

    if (result.inverse) {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Ma trận nghịch đảo A⁻¹:</h4><div class="matrix-display">${formatMatrix(result.inverse)}</div></div>`;
    }
    
    if (result.check) {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Kiểm tra A · A⁻¹ (gần bằng ma trận đơn vị E):</h4><div class="matrix-display">${formatMatrix(result.check)}</div></div>`;
    }

    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3><div class="space-y-8">`;
        result.steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4>`;
            
            if (step.matrix) {
                 html += `<div class="matrix-display">${formatMatrix(step.matrix)}</div>`;
            }
            
            // === THAY ĐỔI TẠI ĐÂY ===
            // 1. Xử lý các tham số thông thường
            ['L', 'U', 'P', 'M', 'inv_M', 'theta', 'L_inv', 'U_inv'].forEach(key => {
                if (step[key] !== undefined) {
                    let labelHtml = `<span class="font-semibold">${key}:</span>`;
                    html += `<div class="mt-2">${labelHtml}`;
                    if (Array.isArray(step[key])) { 
                        html += `<div class="matrix-display">${formatMatrix(step[key])}</div>`;
                    } else { 
                        html += ` <span class="font-mono"> ${formatNumber(step[key])}</span>`;
                    }
                    html += `</div>`;
                }
            });

            // 2. Xử lý riêng tham số 'q' để làm nổi bật
            if (step.q !== undefined) {
                html += `<div class="mt-4 p-4 bg-indigo-50 rounded-lg text-center border border-indigo-200 shadow-sm">
                             <p class="text-sm font-medium text-indigo-800 mb-2">Điều kiện hội tụ</p>
                             <div class="text-xl md:text-2xl" id="q-prominent-block"></div>
                         </div>`;
            }
            
            if (step.iterations) {
                html += `<div class="space-y-6 mt-4">`;
                step.iterations.forEach(iter_step => {
                    html += `<div class="p-4 border rounded-lg bg-gray-50/50">
                        <p class="font-semibold text-gray-800">Bước lặp ${iter_step.iteration_number}</p>
                        <div class="mt-2">
                            <p class="font-medium text-sm text-gray-600">Ma trận X<sub>${iter_step.iteration_number}</sub>:</p>
                            <div class="matrix-display">${formatMatrix(iter_step.matrix_Xk)}</div>
                        </div>
                        <div class="mt-2">
                            <p class="font-medium text-sm text-gray-600">Sai số chuẩn 2:</p>
                            <p class="font-mono text-center bg-gray-100 p-2 rounded-md">||Xₖ - Xₖ₋₁||₂ ≈ ${formatNumber(iter_step.error_2, 8)}</p>
                        </div>
                        <div class="mt-2">
                            <p class="font-medium text-sm text-gray-600">Sai số hậu nghiệm:</p>
                            <p class="font-mono text-center bg-gray-100 p-2 rounded-md">q/(1-q)·||Xₖ - Xₖ₋₁||₂ ≈ ${formatNumber(iter_step.estimated_error, 8)}</p>
                        </div>
                    </div>`;
                });
                html += `</div>`;
            }
            
            if (step.table) {
                // Nếu là bảng lặp Gauss-Seidel, Jacobi, Newton, hiển thị tiêu đề đúng công thức
                let errorHeader = 'Sai số';
                let aposterioriHeader = '';
                if (method === 'jacobi') {
                    errorHeader = 'q/(1-q)·||Xₖ₊₁ - Xₖ||';
                    aposterioriHeader = '||Xₖ₊₁ - Xₖ||';
                } else if (method === 'newton') {
                    errorHeader = 'q/(1-q)·||Xₖ₊₁ - Xₖ||₂';
                    aposterioriHeader = '||Xₖ₊₁ - Xₖ||₂';
                } else if (method === 'gauss-seidel') {
                    errorHeader = 'q/[(1-s)(1-q)]·||Xₖ₊₁ - Xₖ||';
                    aposterioriHeader = '||Xₖ₊₁ - Xₖ||';
                }
                html += `<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50"><tr>
                            <th class="px-4 py-2">Lần lặp</th>
                            <th class="px-4 py-2">X<sub>k</sub></th>`;
                if (aposterioriHeader) {
                    html += `<th class="px-4 py-2">${aposterioriHeader}</th>`;
                }
                html += `<th class="px-4 py-2">${errorHeader}</th>
                        </tr></thead><tbody>`;
                step.table.forEach(row => {
                    html += `<tr>
                            <td class="px-4 py-2 text-center">${row.k}</td>
                            <td class="px-4 py-2 font-mono">${formatMatrix(row.x_k)}</td>`;
                if (aposterioriHeader) {
                    html += `<td class="px-4 py-2 text-center">${row.error_norm !== undefined ? formatNumber(row.error_norm, 8) : ''}</td>`;
                }
                html += `<td class="px-4 py-2 text-center">${row.error_aposteriori !== undefined && row.error_aposteriori !== null ? formatNumber(row.error_aposteriori, 8) : formatNumber(row.error, 8)}</td>`;
                html += `</tr>`;
            });
            html += `</tbody></table></div>`;
            }

            html += `</div>`;
        });
        html += `</div>`;
    }

    resultsArea.innerHTML = html;
    attachCopyMatrixEvents();
    
    // === THAY ĐỔI TẠI ĐÂY ===
    // 3. Tìm khối nổi bật và render KaTeX vào đó
    const qProminentBlock = document.getElementById('q-prominent-block');
    // Giá trị 'q' nằm trong bước đầu tiên của kết quả
    const qValue = result.steps && result.steps[0] ? result.steps[0].q : undefined;

    if (qProminentBlock && qValue !== undefined && window.katex) {
        const qValueFormatted = formatNumber(qValue, 6);
        const latexString = String.raw`||I - AX_0||_2 \approx ${qValueFormatted}`;
        try {
            katex.render(latexString, errorFormulaEl, {
                throwOnError: false,
                displayMode: false
            });
        } catch (e) {
            console.error("Lỗi render KaTeX", e);
            errorFormulaEl.textContent = "Công thức lỗi...";
        }
    }
}
// --- END: CODE MỚI ---


// === CÁC HÀM HIỂN THỊ CŨ (GIỮ NGUYÊN) ===
function showSvdTab(tab) {
    document.querySelectorAll('.svd-tab').forEach(div => div.classList.add('hidden'));
    document.getElementById('svd-tab-' + tab).classList.remove('hidden');
}
function displaySvdResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `
        <div class="flex space-x-2 mb-6">
            <button type="button" onclick="showSvdTab('full')" class="svd-tab-btn" id="svd-btn-full">Dạng đầy đủ</button>
            <button type="button" onclick="showSvdTab('reduced')" class="svd-tab-btn" id="svd-btn-reduced">Dạng rút gọn</button>
            <button type="button" onclick="showSvdTab('sum')" class="svd-tab-btn" id="svd-btn-sum">Tổng thành phần</button>
        </div>
        <div id="svd-tab-full" class="svd-tab">
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                <div class="font-semibold text-indigo-700 mb-2">Ma trận U</div>
                <div class="matrix-display">${formatMatrix(result.U)}</div>
            </div>
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                <div class="font-semibold text-indigo-700 mb-2">Ma trận Σ</div>
                <div class="matrix-display">${formatMatrix(result.Sigma)}</div>
            </div>
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                <div class="font-semibold text-indigo-700 mb-2">Ma trận Vᵀ</div>
                <div class="matrix-display">${formatMatrix(result.V_transpose)}</div>
            </div>
        </div>
        <div id="svd-tab-reduced" class="svd-tab hidden">
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                <div class="font-semibold text-indigo-700 mb-2">U (rút gọn)</div>
                <div class="matrix-display">${formatMatrix(result.U_reduced)}</div>
            </div>
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                <div class="font-semibold text-indigo-700 mb-2">Σ (rút gọn)</div>
                <div class="matrix-display">${formatMatrix(result.Sigma_reduced)}</div>
            </div>
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                <div class="font-semibold text-indigo-700 mb-2">Vᵀ (rút gọn)</div>
                <div class="matrix-display">${formatMatrix(result.Vt_reduced)}</div>
            </div>
        </div>
        <div id="svd-tab-sum" class="svd-tab hidden">
            ${(result.svd_sum_components || []).map((comp, i) => `
                <div class="mb-2">
                    <b>Thành phần ${i+1}:</b> σ = ${formatNumber(comp.sigma)}, 
                        u = [${comp.u.map(v => formatNumber(v)).join(', ')}],
                        v = [${comp.v.map(v => formatNumber(v)).join(', ')}]
                </div>
            `).join('')}
        </div>
        `;
    if (result.intermediate_steps) {
        if (result.intermediate_steps.A_transpose_A){
            html += `<div class="mt-10"><h3 class="result-heading">Các Bước Tính Toán Trung Gian</h3><div class="space-y-6">`;
        }
        if (result.intermediate_steps.A_transpose_A) {
            html += `<div><h4 class="font-medium text-gray-700">Ma trận AᵀA</h4><div class="matrix-display">${formatMatrix(result.intermediate_steps.A_transpose_A)}</div></div>`;
        }
        if (result.intermediate_steps.eigenvalues_of_ATA) {
            html += `<div><h4 class="font-medium text-gray-700">Giá trị riêng của AᵀA (λ)</h4><div class="p-3 bg-gray-50 rounded-md text-sm font-mono">[ ${result.intermediate_steps.eigenvalues_of_ATA.map(v => formatNumber(v)).join(', ')} ]</div></div>`;
        }
        if (result.intermediate_steps.singular_values) {
            html += `<div><h4 class="font-medium text-gray-700">Giá trị kỳ dị (σ = √λ)</h4><div class="p-3 bg-gray-50 rounded-md text-sm font-mono">[ ${result.intermediate_steps.singular_values.map(v => formatNumber(v)).join(', ')} ]</div></div>`;
        }
        if (result.intermediate_steps.V_matrix) {
            html += `<div><h4 class="font-medium text-gray-700">Ma trận V</h4><div class="matrix-display">${formatMatrix(result.intermediate_steps.V_matrix)}</div></div>`;
        }
        if (result.intermediate_steps.steps) {
            html += `<div class="mt-8"><h4 class="font-medium text-gray-700">Các bước lặp Power Method + Xuống thang</h4>`;
            result.intermediate_steps.steps.forEach((step, idx) => {
                html += `<div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                    <h5 class="font-medium text-gray-700 mb-2">Giá trị kỳ dị thứ ${step.singular_index} (σ ≈ ${formatNumber(step.singular_value)})</h5>
                    <div class="mb-2 text-sm text-gray-600">Các bước lặp:</div>
                    <ol class="list-decimal ml-6 mb-2 text-sm">`;
                step.lambda_steps.forEach((lam, i) => {
                     html += `<li>λ<sub>${i+1}</sub> = ${formatNumber(lam)}, vector y: [${step.y_steps[i+1].map(v => formatNumber(v,3)).join(', ')}]</li>`;
                });
                html += `</ol>
                    <div class="mb-2 text-sm text-gray-600">Véctơ riêng cuối cùng (chuẩn hóa): [${step.right_vec.map(v => formatNumber(v,4)).join(', ')}]</div>
                </div>`;
            });
            html += `</div>`;
        }
        html += `</div>`;
    }
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
}

function displayGaussJordanResults(result) {
    const resultsArea = document.getElementById('results-area');
    // Phân biệt giữa giải HPT và tìm nghịch đảo
    if (result.inverse) {
        return displayInverseResults(result, 'gauss-jordan');
    }
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Gauss-Jordan', result);
    if (result.intermediate_steps) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Biến Đổi Ma Trận</h3><div class="space-y-8">`;
        result.intermediate_steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4><div class="matrix-display">${formatMatrix(step.matrix)}</div></div>`;
        });
        html += `</div></div>`;
    }
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
}
    
function displayGaussEliminationResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Khử Gauss', result);
    if (result.forward_steps) {
        html += `<div class="mt-10"><h3 class="result-heading">Quy Trình Thuận</h3><div class="space-y-8">`;
        result.forward_steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4><div class="matrix-display">${formatMatrix(step.matrix)}</div></div>`;
        });
        html += `</div></div>`;
    }
    if (result.backward_steps && result.backward_steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Quy Trình Nghịch</h3><div class="space-y-8">`;
        result.backward_steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4><div class="p-3 bg-gray-100 rounded-md text-sm font-mono text-center">Ma trận nghiệm X hiện tại:<br>${formatMatrix(step.solution_so_far)}</div></div>`;
        });
        html += `</div></div>`;
    }
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
}

function displayLuResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Phân Tách LU', result);
    if (result.decomposition && (result.decomposition.L || result.decomposition.U || result.decomposition.P)) {
               html += `<div class="mt-10"><h3 class="result-heading">Các Ma Trận Phân Rã</h3>`;

        // Hiển thị ma trận P nếu có (thường là ma trận hoán vị)
        if (result.decomposition.P) {
            html += `<div class="mt-6">
                        <h4 class="font-medium text-center text-gray-700">Ma trận Hoán vị P</h4>
                        <div class="matrix-display">${formatMatrix(result.decomposition.P)}</div>
                     </div>`;
        }

        // Hiển thị ma trận L
        if (result.decomposition.L) {
            html += `<div class="mt-6">
                        <h4 class="font-medium text-center text-gray-700">Ma trận L</h4>
                        <div class="matrix-display">${formatMatrix(result.decomposition.L)}</div>
                     </div>`;
        }

        // Hiển thị ma trận U
        if (result.decomposition.U) {
            html += `<div class="mt-6">
                        <h4 class="font-medium text-center text-gray-700">Ma trận U</h4>
                        <div class="matrix-display">${formatMatrix(result.decomposition.U)}</div>
                     </div>`;
        }

        html += `</div>`; // Đóng thẻ div của mục "Các Ma Trận Phân Rã"
    }
    if (result.status === 'unique_solution' && result.intermediate_y) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3>`;
        html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Giải Ly = PB, ta được Y:</h4><div class="matrix-display">${formatMatrix(result.intermediate_y)}</div></div>`;
        html += `</div>`;
    }
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
}


function displayCholeskyResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Phân Tách Cholesky', result);
    if (result.decomposition.M && result.transformation_message.includes('không đối xứng')) {
         html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Ma trận M = AᵀA</h4><div class="matrix-display">${formatMatrix(result.decomposition.M)}</div></div>`;
    }
    if (result.decomposition.U && result.decomposition.Ut) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Phân Tách (M = UᵀU)</h3>`;
        html += `<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4">`;
        html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.decomposition.U)}</div></div>`;
        html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận Uᵀ</h4><div class="matrix-display">${formatMatrix(result.decomposition.Ut)}</div></div>`;
        html += `</div>`;
    }
    if (result.intermediate_y) {
        html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Giải Uᵀy = d, ta được Y:</h4><div class="matrix-display">${formatMatrix(result.intermediate_y)}</div></div>`;
    }
    html += `</div>`;
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
}


function displayDanilevskyResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Tìm Giá Trị Riêng (Danielevsky)</h3>`;

    if (result.eigenvalues && result.eigenvectors) {
        // Định dạng và hiển thị các giá trị riêng
        const formattedEigenvalues = result.eigenvalues.map(v => formatNumber(v, displayPrecision)).join(',&nbsp;&nbsp; ');
        html += `<div class="mb-8">
                     <h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Giá trị riêng (λ):</h4>
                     <div class="matrix-display text-center">[${formattedEigenvalues}]</div>
                 </div>`;

        // --- BẮT ĐẦU LOGIC CHUYỂN ĐỔI QUAN TRỌNG ---
        // Backend trả về một danh sách các vector cột (mảng 3D).
        // Chúng ta cần chuyển nó thành một ma trận 2D chuẩn để hiển thị.
        const eigenvectorsFromBackend = result.eigenvectors;
        let matrixToDisplay = [];

        if (eigenvectorsFromBackend && eigenvectorsFromBackend.length > 0 && eigenvectorsFromBackend[0].length > 0) {
            const numRows = eigenvectorsFromBackend[0].length;
            const numCols = eigenvectorsFromBackend.length;
            
            // Tạo một ma trận 2D rỗng
            matrixToDisplay = Array(numRows).fill(null).map(() => Array(numCols).fill(null));

            // Lặp qua dữ liệu 3D và điền vào ma trận 2D
            for (let col = 0; col < numCols; col++) { // col tương ứng với mỗi vector riêng
                for (let row = 0; row < numRows; row++) { // row tương ứng với mỗi thành phần của vector
                    // Lấy giá trị từ cấu trúc lồng nhau [vector][thành phần][giá trị]
                    if (eigenvectorsFromBackend[col] && eigenvectorsFromBackend[col][row] && eigenvectorsFromBackend[col][row][0] !== undefined) {
                        matrixToDisplay[row][col] = eigenvectorsFromBackend[col][row][0];
                    }
                }
            }
        }
        // --- KẾT THÚC LOGIC CHUYỂN ĐỔI ---

        // Bây giờ, gọi formatMatrix với ma trận 2D đã được chuyển đổi
        const formattedEigenvectors = formatMatrix(matrixToDisplay, displayPrecision);
        html += `<div class="mb-8">
                     <h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Vector riêng tương ứng (các cột):</h4>
                     <div class="matrix-display">${formattedEigenvectors}</div>
                 </div>`;
        
        if (result.char_poly && result.char_poly.length > 0) {
            let polyString = 'P(λ) = ';
            const coeffs = result.char_poly;
            const n = coeffs.length - 1;

            for (let i = 0; i < coeffs.length; i++) {
                // SỬA LỖI: Lấy hệ số trực tiếp, không qua ".real"
                // Đồng thời kiểm tra xem nó có phải là object không để đảm bảo tương thích
                let coeff_val = coeffs[i];
                if (typeof coeff_val === 'object' && coeff_val !== null && coeff_val.hasOwnProperty('re')) {
                    coeff_val = coeff_val.re;
                }

                // Nếu sau khi lấy giá trị mà vẫn không phải là số thì bỏ qua
                if (isNaN(coeff_val)) continue;
                if (Math.abs(coeff_val) < zeroTolerance) continue;

                let power = n - i;

                if (i > 0) {
                    polyString += (coeff_val > 0) ? ' + ' : ' - ';
                    coeff_val = Math.abs(coeff_val);
                } else if (coeff_val < 0) {
                    polyString += '-';
                    coeff_val = Math.abs(coeff_val);
                }

                const formattedCoeff = formatNumber(coeff_val);
                if (formattedCoeff !== '1' || power === 0) {
                     polyString += formattedCoeff;
                }
                
                if (power > 0) {
                    polyString += 'λ';
                    if (power > 1) {
                        polyString += `<sup>${power}</sup>`;
                    }
                }
            }
            
            html += `
                <div class="mt-8 border-t pt-6">
                    <h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Đa thức đặc trưng:</h4>
                    <div class="matrix-display text-center text-xl font-mono !bg-indigo-100 !text-indigo-800">
                        ${polyString}
                    </div>
                </div>
            `;
        }

        if (result.steps && result.steps.length > 0) {
            html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3><div class="space-y-8">`;
            result.steps.forEach(step => {
                html += `<div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                    <div class="font-semibold text-indigo-700 mb-2">${step.desc}</div>
                    <div class="matrix-display">${formatMatrix(step.matrix)}</div>`;
                if (step.C) {
                    html += `<div class="mt-2"><b>Ma trận hoán vị C:</b><div class="matrix-display">${formatMatrix(step.C)}</div></div>`;
                }
                if (step.M) {
                    html += `<div class="mt-2"><b>Ma trận biến đổi M:</b><div class="matrix-display">${formatMatrix(step.M)}</div></div>`;
                }
                if (step.M_inv) {
                    html += `<div class="mt-2"><b>Ma trận nghịch đảo M⁻¹:</b><div class="matrix-display">${formatMatrix(step.M_inv)}</div></div>`;
                }
                html += `</div>`;
            });
            html += `</div></div>`;
        }
    } else {
        html += `<div class="text-red-500">Lỗi: Định dạng kết quả trả về không hợp lệ.</div>`;
    }
    
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
}

// Hiển thị kết quả hệ phương trình dạng tổng quát (dùng cho Gauss, Gauss-Jordan, LU, Cholesky)
function displayGenericHptResults(title, result) {
    let html = `<h3 class="result-heading">${title}</h3>`;
     if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-blue-50 rounded-lg shadow-inner">${result.message}</div>`;
    }
    if (result.transformation_message) {
        html += `<p class="text-center text-gray-600 mb-4">${result.transformation_message}</p>`;
    }

    if (result.status === 'unique_solution') {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm X:</h4><div class="matrix-display">${formatMatrix(result.solution)}</div></div>`;
    } else if (result.status === 'infinite_solutions') {
        const { particular_solution, null_space_vectors, num_free_vars } = result.general_solution;
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm tổng quát:</h4>`;
        let termHtml = '';
        for (let i = 0; i < num_free_vars; i++) {
            const v_k = null_space_vectors.map(row => [row[i]]);
            termHtml += `&nbsp; + &nbsp; t<sub>${i+1}</sub> &nbsp; <div class="matrix-display !inline-block">${formatMatrix(v_k)}</div>`;
        }
        html += `<div class="flex justify-center items-center flex-wrap"><span class="text-2xl mr-4">X = </span><div class="matrix-display !inline-block" title="Nghiệm riêng Xp">${formatMatrix(particular_solution)}</div>${termHtml}</div>`;
        html += `<p class="text-center text-sm text-gray-500 mt-2">Với t<sub>k</sub> là các tham số tự do.</p></div>`;
    } else if (result.status === 'no_solution') {
         if (result.solution_matrix || (result.forward_steps && result.forward_steps.length > 0) ) {
            const last_matrix = result.solution_matrix || result.forward_steps[result.forward_steps.length - 1].matrix;
            html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Dạng ma trận cuối cùng cho thấy sự mâu thuẫn:</h4><div class="matrix-display">${formatMatrix(last_matrix)}</div></div>`;
        }
    }
    return html;
}
function setupNonlinearSystemSolveEvents() {
    // Lấy các element trên DOM
    const methodSelect = document.getElementById('ns-method-select');
    const expressionsInput = document.getElementById('ns-expressions-input');
    const previewDiv = document.getElementById('ns-latex-preview');
    const x0Input = document.getElementById('ns-x0-input');
    const domainGroup = document.getElementById('ns-domain-group');
    const expressionsLabel = document.getElementById('ns-expressions-label');
    const calculateBtn = document.getElementById('calculate-ns-btn');
    const normGroup = document.getElementById('ns-norm-selection-group');

    const placeholders = {
        newton: "x_1^2 + x_2^2 - 1\nx_1^2 - x_2",
        newton_modified: "x_1^2 + x_2^2 - 1\nx_1^2 - x_2",
        simple_iteration: "\\sqrt{1 - x_2^2}\n\\sqrt{x_1}"
    };

    // Hàm render LaTeX cho các biểu thức nhập vào (không đổi)
    function renderSystemLatex() {
        if (!expressionsInput || !previewDiv) return;
        const latexLines = expressionsInput.value.trim().split('\n');
        previewDiv.innerHTML = '';
        if (expressionsInput.value.trim() === "") return;
        
        latexLines.forEach(line => {
            const lineDiv = document.createElement('div');
            lineDiv.className = 'w-full text-center';
            try {
                katex.render(line, lineDiv, { throwOnError: true, displayMode: false });
            } catch (error) {
                lineDiv.textContent = `Lỗi cú pháp: "${line}"`;
                lineDiv.className = 'w-full text-left text-red-500 text-sm';
            }
            previewDiv.appendChild(lineDiv);
        });
    }
    
    // Hàm cập nhật hiển thị của các thành phần UI (không đổi)
    function updateUIVisibility() {
        const method = methodSelect.value;
        expressionsInput.placeholder = placeholders[method];

        if (method === 'simple_iteration') {
            expressionsLabel.innerHTML = 'Hệ hàm lặp <span class="font-mono text-sm">X = &phi;(X)</span>';
            domainGroup.style.display = 'block';
        } else {
            expressionsLabel.innerHTML = 'Hệ phương trình <span class="font-mono text-sm">F(X) = 0</span>';
            domainGroup.style.display = 'none';
        }
        
        const showNormSelector = (method === 'newton' || method === 'newton_modified');
        normGroup.style.display = showNormSelector ? 'block' : 'none';
        
        renderSystemLatex();
    }

    // SỬA LỖI: Chỉ render công thức chuẩn một lần duy nhất khi hàm được thiết lập
    try {
        const normInfEl = document.getElementById('ns-norm-inf-katex');
        const norm1El = document.getElementById('ns-norm-1-katex');

        // Kiểm tra xem đã render chưa, nếu rồi thì không làm gì cả
        if (normInfEl && !normInfEl.hasChildNodes()) {
            katex.render('\\|v\\|_\\infty', normInfEl, { throwOnError: false, displayMode: false });
        }
        if (norm1El && !norm1El.hasChildNodes()) {
            katex.render('\\|v\\|_1', norm1El, { throwOnError: false, displayMode: false });
        }
    } catch (e) {
        console.error("Lỗi render KaTeX cho lựa chọn chuẩn:", e);
    }
    
    // Gắn các sự kiện (không đổi)
    methodSelect.addEventListener('change', updateUIVisibility);
    expressionsInput.addEventListener('input', renderSystemLatex);

    calculateBtn.addEventListener('click', () => {
        const method = methodSelect.value;
        const latexExpressions = expressionsInput.value.trim().split('\n').filter(line => line.trim() !== '');
        if (latexExpressions.length === 0) return displayError('Vui lòng nhập hệ phương trình.');
        const expressions = latexExpressions.map(latexToPython);
        const n = expressions.length;

        const x0_lines = x0Input.value.trim().split('\n').filter(line => line.trim() !== '');
        if (x0_lines.length !== n) return displayError(`Số lượng giá trị ban đầu (${x0_lines.length}) không khớp với số phương trình (${n}).`);
        const x0 = x0_lines.map(val => parseFloat(val.trim()));
        if (x0.some(isNaN)) return displayError('Giá trị ban đầu X₀ không hợp lệ.');

        const normChoiceEl = document.querySelector('input[name="ns-norm-option"]:checked');
        const normChoice = normChoiceEl ? normChoiceEl.value : 'infinity';

        const body = {
            n: n, method: method, expressions: expressions, x0: x0,
            stop_option: document.getElementById('ns-stop-option-select').value,
            stop_value: document.getElementById('ns-stop-value-input').value,
            norm_choice: normChoice
        };

        if (method === 'simple_iteration') {
            const domainInput = document.getElementById('ns-domain-input');
            const domain_lines = domainInput.value.trim().split('\n').filter(line => line.trim() !== '');
            if (domain_lines.length !== n) return displayError(`Số lượng miền D (${domain_lines.length}) không khớp với số phương trình (${n}).`);
            body.a0 = [];
            body.b0 = [];
            for (const line of domain_lines) {
                const parts = line.trim().split(/\s+/);
                if (parts.length !== 2 || isNaN(parseFloat(parts[0])) || isNaN(parseFloat(parts[1]))) {
                    return displayError(`Miền D có dòng không hợp lệ: "${line}".`);
                }
                body.a0.push(parseFloat(parts[0]));
                body.b0.push(parseFloat(parts[1]));
            }
        }
        handleCalculation('/nonlinear-system/solve', body);
    });
    
    // Gọi để cập nhật giao diện lần đầu (không đổi)
    updateUIVisibility();
}

function displayNonlinearSystemResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Giải Hệ Phi Tuyến</h3>`;

    if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-green-50 rounded-lg shadow-inner">${result.message}</div>`;
    }

    if (result.solution) {
        const solMatrix = result.solution.map(v => [v]);
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm X ≈</h4><div class="matrix-display">${formatMatrix(solMatrix)}</div></div>`;
    }

    if (result.J_max_vals) {
        html += `<div class="mt-8 p-4 border rounded-lg bg-gray-50">
                    <h4 class="font-semibold text-gray-700 text-lg mb-3 text-center">Phân Tích Hội Tụ</h4>
                     <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-center">
                         <div class="p-3 bg-gray-100 rounded-md">
                            <span class="font-medium">Chuẩn ma trận lặp ||B||${normSymbol}</span>
                            <p class="font-mono text-xl">${formatNumber(result.max_row_sum, 6)}</p>
                         </div>
                         <div class="p-3 bg-gray-100 rounded-md">
                            <span class="font-medium">Ngưỡng dừng thực tế</span>
                            <p class="font-mono text-xl">${formatNumber(result.stopping_threshold, 8)}</p>
                         </div>
                     </div>
                 </div>`;
    }

    let diagnosticHtml = '';
    if (result.jacobian_matrix_latex) {
        diagnosticHtml += `<div class="p-4 bg-gray-50 rounded-lg flex flex-col">
                        <h4 class="font-semibold text-gray-700 text-center mb-2">Ma trận Jacobi J(X)</h4>
                        <div id="jacobian-matrix-container" class="flex-grow flex items-center justify-center">${formatLatexMatrix(result.jacobian_matrix_latex)}</div>
                     </div>`;
    }
    if (result.J0_inv_matrix) {
        diagnosticHtml += `<div class="p-4 bg-gray-50 rounded-lg flex flex-col">
                    <h4 class="font-semibold text-gray-700 text-center mb-2">Ma trận J(X₀)⁻¹</h4>
                    <div class="flex-grow flex items-center justify-center">${formatMatrix(result.J0_inv_matrix, 5)}</div>
                 </div>`;
    }
    
    if (diagnosticHtml) {
        html += `<div class="flex flex-wrap justify-center gap-6 mt-8 mb-8">${diagnosticHtml}</div>`;
    }

    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Bảng Các Bước Lặp</h3>`;
        const headers = Object.keys(result.steps[0]);
        // Sửa lại tên cột error cho thân thiện hơn
        const headerDisplayMap = {
            'error': 'Sai số'
        }
        html += `<div class="overflow-x-auto"><table class=" collapsible-table min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>`;
        headers.forEach(header => {
            html += `<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider font-mono">${headerDisplayMap[header] || header}</th>`;
        });
        html += `</tr></thead><tbody class="bg-white divide-y divide-gray-200">`;
        result.steps.forEach(step => {
            html += `<tr>`;
            headers.forEach(header => {
                 html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${formatNumber(step[header], 6)}</td>`;
            });
            html += `</tr>`;
        });
        html += `</tbody></table></div></div>`;
    }
    
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();
    
    if (result.jacobian_matrix_latex) {
        const container = document.getElementById('jacobian-matrix-container');
        if (container) {
            container.querySelectorAll('td').forEach(cell => {
                try { katex.render(cell.textContent, cell, { throwOnError: false, displayMode: false }); } catch(e) { console.error('Lỗi render KaTeX:', e); }
            });
        }
    }
}

function setupMatrixSolveIterativeEvents() {
    // Logic chuyển tab
    const tabs = document.querySelectorAll('.iter-hpt-tab');
    const tabContents = document.querySelectorAll('.iter-hpt-tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => {
                item.classList.remove('text-blue-600', 'border-blue-500');
                item.classList.add('text-gray-500', 'border-transparent', 'hover:text-gray-700', 'hover:border-gray-300');
            });
            tab.classList.add('text-blue-600', 'border-blue-500');
            tab.classList.remove('text-gray-500', 'border-transparent');
            const targetContentId = `iter-hpt-${tab.dataset.tab}-content`;
            tabContents.forEach(content => {
                content.style.display = content.id === targetContentId ? 'block' : 'none';
            });
            resetDisplay();
        });
    });

    // Gắn sự kiện cho các nút
    document.getElementById('calculate-jacobi-btn').onclick = () => setupIterativeHptCalculation('/matrix/iterative/jacobi');
    document.getElementById('calculate-gs-btn').onclick = () => setupIterativeHptCalculation('/matrix/iterative/gauss-seidel');
    // Gắn sự kiện cho nút mới
    document.getElementById('calculate-simple-iteration-btn').onclick = () => setupSimpleIterationHptCalculation('/matrix/iterative/simple-iteration');
}
function setupIterativeHptCalculation(endpoint) {
    const matrixA_Input = document.getElementById('matrix-a-input-iter');
    const matrixB_Input = document.getElementById('matrix-b-input-iter');
    const x0_Input = document.getElementById('x0-input-iter');
    const tolerance_Input = document.getElementById('iter-tolerance');
    const maxIter_Input = document.getElementById('iter-max-iter');

    const matrixA = parseMatrix(matrixA_Input.value);
    if (matrixA.error || matrixA.length === 0) {
        displayError(matrixA.error || 'Ma trận A không được để trống.');
        return;
    }
    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) {
        displayError(matrixB.error || 'Ma trận B không được để trống.');
        return;
    }
    const x0 = parseMatrix(x0_Input.value);
     if (x0.error || x0.length === 0) {
        displayError(x0.error || 'Vector lặp ban đầu X₀ không được để trống.');
        return;
    }

    if (matrixA.length !== matrixB.length || matrixA.length !== x0.length) {
         displayError(`Số hàng của ma trận A (${matrixA.length}), B (${matrixB.length}) và X₀ (${x0.length}) phải bằng nhau.`);
         return;
    }
     if (matrixA.length !== matrixA[0].length) {
        displayError('Ma trận A phải là ma trận vuông.');
        return;
    }

    const body = {
        matrix_a: matrixA,
        matrix_b: matrixB,
        x0: x0,
        tolerance: parseFloat(tolerance_Input.value),
        max_iter: parseInt(maxIter_Input.value)
    };
    handleCalculation(endpoint, body);
}
function setupPolynomialSolveEvents() {
    document.getElementById('calculate-poly-btn').onclick = () => {
        const coeffs = document.getElementById('poly-coeffs-input').value.trim().split(/\s+/).map(Number).filter(n => !isNaN(n));
        if (coeffs.length < 2) return displayError('Vui lòng nhập ít nhất 2 hệ số.');

        // Lấy giá trị từ các ô nhập mới
        const tolerance = parseFloat(document.getElementById('poly-tolerance').value);
        const maxIter = parseInt(document.getElementById('poly-max-iter').value);

        if (isNaN(tolerance) || isNaN(maxIter)) {
            return displayError('Sai số và Số lần lặp phải là các số hợp lệ.');
        }

        const body = { 
            coeffs: coeffs,
            tolerance: tolerance,
            max_iter: maxIter
        };

        handleCalculation('/polynomial/solve', body);
    };
}

function displayPolynomialResults(result) {
    const resultsArea = document.getElementById('results-area');
    
    let html = `<h3 class="result-heading">Kết Quả Giải Phương Trình Đa Thức</h3>`;

    // Thay đổi ở đây: Tạo một div container để render LaTeX
    html += `<div id="polynomial-latex-container" class="text-center text-2xl mb-6 p-4 bg-purple-50 rounded-lg shadow-inner"></div>`;
    
    // Bước 1: Khoảng chứa nghiệm (giữ nguyên)
    html += `<div class="mb-8 p-4 border rounded-lg bg-gray-50">
                <h4 class="font-semibold text-gray-700 text-lg mb-2 text-center">Bước 1: Tìm khoảng chứa nghiệm</h4>
                <p class="text-gray-600">Dựa trên các hệ số, tất cả các nghiệm thực (nếu có) của đa thức sẽ nằm trong khoảng:</p>
                <p class="text-center font-bold text-xl text-purple-700 my-2">[${formatNumber(result.bounds[0])}, ${formatNumber(result.bounds[1])}]</p>
             </div>`;

    // Bước 2: Phân ly nghiệm (giữ nguyên)
    html += `<div class="mb-8 p-4 border rounded-lg bg-gray-50">
                <h4 class="font-semibold text-gray-700 text-lg mb-2 text-center">Bước 2: Phân ly nghiệm</h4>
                <p class="text-gray-600">Tìm các điểm cực trị (nghiệm của đạo hàm) để chia khoảng lớn thành các khoảng nhỏ hơn, mỗi khoảng chứa tối đa 1 nghiệm.</p>
                <p class="text-gray-800 mt-2">Các điểm cực trị thực tìm được: <span class="font-mono">${result.critical_points.length > 0 ? result.critical_points.map(p => formatNumber(p)).join(', ') : 'Không có'}</span></p>
                <p class="text-gray-800 mt-2">Các khoảng sẽ được xét nghiệm: <span class="font-mono">${result.search_intervals.map(iv => `[${formatNumber(iv[0])}, ${formatNumber(iv[1])}]`).join('; ')}</span></p>
             </div>`;
             
    // Bước 3: Tìm nghiệm (giữ nguyên)
    html += `<div class="mb-8 p-4 border rounded-lg bg-gray-50">
                <h4 class="font-semibold text-gray-700 text-lg mb-2 text-center">Bước 3: Tìm nghiệm trong từng khoảng</h4>`;

    if (result.found_roots.length === 0) {
        html += `<p class="text-center text-gray-500 font-medium mt-4">Không tìm thấy nghiệm thực nào trong các khoảng trên.</p>`;
    } else {
        html += `<p class="text-gray-600 mb-4">Sử dụng phương pháp Chia đôi (Bisection) trong các khoảng có dấu của f(x) thay đổi ở 2 biên.</p>`;
        html += `<div class="space-y-6">`;
        result.found_roots.forEach((root_info, index) => {
            html += `<div class="p-4 border border-purple-200 rounded-lg">
                        <p class="font-semibold text-purple-800 text-xl">Nghiệm ${index + 1} ≈ <span class="font-mono">${formatNumber(root_info.root_value)}</span></p>
                        <p class="text-sm text-gray-500">Tìm thấy trong khoảng [${formatNumber(root_info.interval[0])}, ${formatNumber(root_info.interval[1])}]</p>
                        
                        <details class="mt-3">
                            <summary class="cursor-pointer text-sm font-medium text-purple-600 hover:text-purple-800">Xem các bước lặp (Chia đôi)</summary>
                            <div class="overflow-x-auto mt-2">
                                <table class=" collapsible-table min-w-full divide-y divide-gray-200 text-sm">
                                    <thead class="bg-gray-100"><tr><th class="px-4 py-2 text-left font-medium text-gray-600">k</th><th class="px-4 py-2 text-left font-medium text-gray-600">aₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">bₖ</th><th class="px-4 py-2 text-left font-medium text-gray-600">cₖ = (aₖ+bₖ)/2</th><th class="px-4 py-2 text-left font-medium text-gray-600">f(cₖ)</th></tr></thead>
                                    <tbody class="bg-white divide-y divide-gray-200">`;
            root_info.bisection_steps.forEach(step => {
                html += `<tr>
                            <td class="px-4 py-2 font-mono">${step.k}</td>
                            <td class="px-4 py-2 font-mono">${formatNumber(step.a)}</td>
                            <td class="px-4 py-2 font-mono">${formatNumber(step.b)}</td>
                            <td class="px-4 py-2 font-mono text-purple-700 font-semibold">${formatNumber(step.c)}</td>
                            <td class="px-4 py-2 font-mono">${formatNumber(step['f(c)'])}</td>
                         </tr>`;
            });
            html += `</tbody></table></div></details></div>`;
        });
        html += `</div>`;
    }
    html += `</div>`;
    resultsArea.innerHTML = html;

    attachCopyMatrixEvents();

    // Thay đổi ở đây: Render chuỗi LaTeX vào container đã tạo
    const polyContainer = document.getElementById('polynomial-latex-container');
    if (polyContainer && result.polynomial_str) {
        try {
            // Thêm "= 0" vào chuỗi LaTeX và render
            katex.render(result.polynomial_str + " = 0", polyContainer, {
                throwOnError: false,
                displayMode: true
            });
        } catch (e) {
            console.error("Lỗi render KaTeX cho đa thức:", e);
            // Nếu lỗi, hiển thị dạng văn bản thường để người dùng vẫn thấy kết quả
            polyContainer.textContent = result.polynomial_str + " = 0";
        }
    }
}

function setupSimpleIterationHptCalculation(endpoint) {
    const matrixB_Input = document.getElementById('matrix-b-input-simple-iter');
    const matrixD_Input = document.getElementById('matrix-d-input-simple-iter');
    const x0_Input = document.getElementById('x0-input-simple-iter');
    const tolerance_Input = document.getElementById('simple-iter-tolerance');
    const maxIter_Input = document.getElementById('simple-iter-max-iter');
    const normChoice_Input = document.getElementById('simple-iter-norm-choice');

    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) return displayError(matrixB.error || 'Ma trận B không được để trống.');

    const matrixD = parseMatrix(matrixD_Input.value);
    if (matrixD.error || matrixD.length === 0) return displayError(matrixD.error || 'Ma trận d không được để trống.');
    
    const x0 = parseMatrix(x0_Input.value);
    if (x0.error || x0.length === 0) return displayError(x0.error || 'Vector lặp ban đầu X₀ không được để trống.');

    if (matrixB.length !== matrixB[0].length) return displayError('Ma trận B phải là ma trận vuông.');
    if (matrixB.length !== matrixD.length || matrixB.length !== x0.length) return displayError(`Số hàng của ma trận B (${matrixB.length}), d (${matrixD.length}) và X₀ (${x0.length}) phải bằng nhau.`);
     
    const body = {
        matrix_b: matrixB,
        matrix_d: matrixD,
        x0: x0,
        tolerance: parseFloat(tolerance_Input.value),
        max_iter: parseInt(maxIter_Input.value),
        norm_choice: normChoice_Input.value
    };
    handleCalculation(endpoint, body);
}

function displayIterativeHptResults(result, method) {
    const resultsArea = document.getElementById('results-area');
    const methodMap = {
        'jacobi': 'Jacobi',
        'gauss-seidel': 'Gauss-Seidel',
        'simple-iteration': 'Lặp Đơn'
    };
    let html = `<h3 class="result-heading">Kết Quả Giải Hệ Bằng ${methodMap[method] || method}</h3>`;

    if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-blue-50 rounded-lg shadow-inner">${result.message}</div>`;
    }
    if (result.warning_message || result.warning) { // Hỗ trợ cả hai tên key
        html += `<div class="text-center font-medium text-md mb-6 p-3 bg-yellow-100 text-yellow-800 rounded-lg shadow-inner">${result.warning_message || result.warning}</div>`;
    }

    if (result.solution) {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm X:</h4><div class="matrix-display">${formatMatrix(result.solution)}</div></div>`;
    }
    
    // Phần hiển thị thông tin hội tụ cho PP Lặp Đơn
    if (method === 'simple-iteration') {
        const normSymbol = result.norm_used === '1' ? '₁' : '∞';
        html += `<div class="mt-8 p-4 border rounded-lg bg-gray-50">
                    <h4 class="font-semibold text-gray-700 text-lg mb-3 text-center">Phân Tích Hội Tụ</h4>
                     <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-center">
                         <div class="p-3 bg-gray-100 rounded-md">
                            <span class="font-medium">Chuẩn ma trận lặp ||B||${normSymbol}</span>
                            <p class="font-mono text-xl">${formatNumber(result.norm_B, 6)}</p>
                         </div>
                         <div class="p-3 bg-gray-100 rounded-md">
                            <span class="font-medium">Ngưỡng dừng thực tế</span>
                            <p class="font-mono text-xl">${formatNumber(result.stopping_threshold, 8)}</p>
                         </div>
                     </div>
                 </div>`;
    }

    if (result.steps && result.steps.length > 0) {
        const firstStep = result.steps[0];
        let tableHtml = '';

        if (firstStep.table) { // Dành cho Jacobi, Gauss-Seidel
            // THAY ĐỔI TẠI ĐÂY
            
            let errorHeader = 'Sai số';
            let aposterioriHeader = '';
            if (method === 'jacobi') {
                errorHeader = 'q/(1-q)·||Xₖ₊₁ - Xₖ||';
                aposterioriHeader = '||Xₖ₊₁ - Xₖ||';
            } else if (method === 'newton') {
                errorHeader = 'q/(1-q)·||Xₖ₊₁ - Xₖ||₂';
                aposterioriHeader = '||Xₖ₊₁ - Xₖ||₂';
            } else if (method === 'gauss-seidel') {
                errorHeader = 'q/[(1-s)(1-q)]·||Xₖ₊₁ - Xₖ||';
                aposterioriHeader = '||Xₖ₊₁ - Xₖ||';
            }
            tableHtml = `<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50"><tr>
                            <th class="px-4 py-2">Lần lặp</th>
                            <th class="px-4 py-2">X<sub>k</sub></th>`;
            if (aposterioriHeader) {
                tableHtml += `<th class="px-4 py-2">${aposterioriHeader}</th>`;
            }
            tableHtml += `<th class="px-4 py-2">${errorHeader}</th>
                        </tr></thead><tbody>`;
            firstStep.table.forEach(row => {
                tableHtml += `<tr>
                            <td class="px-4 py-2 text-center">${row.k}</td>
                            <td class="px-4 py-2 font-mono">${formatMatrix(row.x_k)}</td>`;
                if (aposterioriHeader) {
                    tableHtml += `<td class="px-4 py-2 text-center">${row.error_norm !== undefined ? formatNumber(row.error_norm, 8) : ''}</td>`;
                }
                tableHtml += `<td class="px-4 py-2 text-center">${row.error_aposteriori !== undefined && row.error_aposteriori !== null ? formatNumber(row.error_aposteriori, 8) : formatNumber(row.error, 8)}</td>`;
                tableHtml += `</tr>`;
            });
            tableHtml += `</tbody></table></div>`;

        } else { // Dành cho Lặp đơn
            tableHtml = createIterativeTable(result.steps, ['Lần lặp k', 'Nghiệm X_k', 'Sai số ||Xₖ - Xₖ₋₁||']);
        }

        if (tableHtml) {
             html += `<div class="mt-10"><h3 class="result-heading">Bảng Quá Trình Lặp</h3>${tableHtml}</div>`;
        }
    }
    
    resultsArea.innerHTML = html;
    attachCopyMatrixEvents();
}

function displayGaussSeidelAnalysis(result) {
        if (result.contraction_coefficient_q === undefined) {
            return;
        }

        const resultsArea = document.getElementById('results-area');
        if (!resultsArea) return;

        const analysisDiv = document.createElement('div');
        const normSymbol = result.norm_used === '1' ? '₁' : '∞';
        let dominanceText = `Ma trận ${result.dominance_type}. Sử dụng Chuẩn ${result.norm_used}.`;

        let html = `<div class="mt-10">
                        <h3 class="result-heading">Phân Tích Hội Tụ</h3>
                        <div class="p-4 border rounded-lg bg-gray-50">
                            <div class="p-3 mb-4 bg-white rounded-md shadow-sm text-center">
                                <span class="font-medium text-gray-600">Điều kiện hội tụ</span>
                                <p class="text-base text-gray-800 mt-1">${dominanceText}</p>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-center">
                                <div class="p-3 bg-white rounded-md shadow-sm">
                                    <span class="font-medium text-gray-600">Hệ số co q</span>
                                    <p class="font-mono text-xl text-blue-600 mt-1">${formatNumber(result.contraction_coefficient_q, 6)}</p>
                                </div>
                                <div class="p-3 bg-white rounded-md shadow-sm">
                                    <span class="font-medium text-gray-600">Hệ số s</span>
                                    <p class="font-mono text-xl text-blue-600 mt-1">${formatNumber(result.contraction_coefficient_s, 6)}</p>
                                </div>
                            </div>
                            <div class="text-center mt-4 text-sm text-gray-500">
                               Điều kiện dừng: <span id="error-formula-katex-gs"></span>
                            </div>
                        </div>
                    </div>`;

        analysisDiv.innerHTML = html;
        resultsArea.prepend(analysisDiv); // Đưa lên đầu khu vực kết quả

        const errorFormulaEl = document.getElementById('error-formula-katex-gs');
        if (errorFormulaEl && window.katex) {
            const latexString = String.raw`\frac{q}{(1-s)(1-q)}\|X_k - X_{k-1}\| < \epsilon`;
            try {
                katex.render(latexString, errorFormulaEl, {
                    throwOnError: false,
                    displayMode: false
                });
            } catch (e) {
                console.error("Lỗi render KaTeX", e);
                errorFormulaEl.textContent = "Công thức lỗi...";
            }
        }
    }
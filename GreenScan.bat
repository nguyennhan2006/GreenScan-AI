@echo off
rem GreenScan - nhap dup de chay. Lan dau tu cai dat (can Python 3.11+ va Node.js 20+).
rem Sau do mo http://localhost:8000 trong trinh duyet. Dong cua so nay de dung.
setlocal
rem Bang ma UTF-8 cho Python: cua so cmd tieng Viet (cp1258) khong in duoc chu co dau.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Tao moi truong Python va cai GreenScan - chi lam lan dau, mat vai phut...
  python -m venv .venv
  if errorlevel 1 goto nopython
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -e .
  if errorlevel 1 goto fail
)

if not exist "frontend\dist\index.html" (
  where npm >nul 2>nul
  if errorlevel 1 goto nonode
  echo [2/3] Dung giao dien web - chi lam lan dau...
  pushd frontend
  call npm ci
  if errorlevel 1 (popd & goto fail)
  call npm run build
  if errorlevel 1 (popd & goto fail)
  popd
)

if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul

echo [3/3] Khoi dong GreenScan tai http://localhost:8000 ...
".venv\Scripts\python.exe" -m quantum_gw.cli app
if errorlevel 1 (
  echo.
  echo GreenScan da dung. Neu co loi o tren, chup man hinh cua so nay gui nguoi ho tro.
  pause
)
goto end

:nopython
echo Khong tim thay Python. Cai Python 3.11 tro len tu https://www.python.org/downloads/
echo (tick "Add python.exe to PATH") roi nhap dup lai tep nay.
pause
exit /b 1

:nonode
echo Khong tim thay Node.js - can mot lan de dung giao dien. Cai tu https://nodejs.org/
echo roi nhap dup lai tep nay.
pause
exit /b 1

:fail
echo Cai dat that bai - xem thong bao loi o tren.
pause
exit /b 1

:end
endlocal

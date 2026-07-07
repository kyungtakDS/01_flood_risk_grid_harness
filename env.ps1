# flood_risk311 실행 환경 고정 스크립트
# 사용: 파이프라인/스크립트 실행 전에 dot-source 한다 →  . .\env.ps1
#
# 왜 필요한가: 이 시스템에는 PostgreSQL/PostGIS의 PROJ가 설치되어 있고
# 시스템 PROJ_LIB 이 그쪽(proj.db 구버전)을 가리켜, conda 환경의 재투영이
# 깨진다. 재투영은 표준격자 표준화의 핵심이므로 반드시 conda PROJ로 고정한다.

$envRoot = "C:\miniconda3\envs\flood_risk311"

$env:PROJ_LIB   = "$envRoot\Library\share\proj"
$env:PROJ_DATA  = "$envRoot\Library\share\proj"
$env:GDAL_DATA  = "$envRoot\Library\share\gdal"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$py = "$envRoot\python.exe"
Write-Host "[env] flood_risk311 고정 완료"
Write-Host "[env] PROJ_LIB = $env:PROJ_LIB"
Write-Host "[env] python   = $py"
Write-Host "[env] 실행 예:  & `"$py`" src\standardize\raster_align.py ..."

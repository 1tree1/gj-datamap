# PowerPoint(설치된 것)로 pptx 를 PNG 로 내보내 레이아웃을 눈으로 확인한다. 사용: render_check.ps1 <pptx> <출력폴더>
param([string]$Pptx, [string]$OutDir)
New-Item -ItemType Directory -Force $OutDir | Out-Null
Get-ChildItem $OutDir -Filter *.PNG -ErrorAction SilentlyContinue | Remove-Item -Force
$ps = New-Object -ComObject PowerPoint.Application
try {
  $pres = $ps.Presentations.Open($Pptx, -1, 0, 0)
  $pres.Export($OutDir, "PNG", 1600, 900)
  "exported: " + $pres.Slides.Count + " slides"
  $pres.Close()
} catch { "ERR: " + $_.Exception.Message } finally { $ps.Quit() }

# PowerPoint(설치된 것)로 pptx 를 PNG(또는 PDF)로 내보낸다. 사용: render_pptx.ps1 -Pptx <경로> -OutDir <폴더> [-W 1600] [-H 1131] [-Slides 1,5,9] [-Pdf <pdf경로>]
param([string]$Pptx, [string]$OutDir, [int]$W = 1600, [int]$H = 1131, [string]$Slides = "", [string]$Pdf = "")
New-Item -ItemType Directory -Force $OutDir | Out-Null
$ps = New-Object -ComObject PowerPoint.Application
try {
  $pres = $ps.Presentations.Open($Pptx, -1, 0, 0)
  if ($Pdf -ne "") { $pres.SaveAs($Pdf, 32); "pdf: " + $Pdf }
  if ($Slides -eq "") {
    Get-ChildItem $OutDir -Filter *.PNG -ErrorAction SilentlyContinue | Remove-Item -Force
    $pres.Export($OutDir, "PNG", $W, $H); "exported all: " + $pres.Slides.Count + " slides"
  } else {
    foreach ($n in $Slides.Split(",")) { $i = [int]$n; $pres.Slides($i).Export((Join-Path $OutDir ("슬라이드" + $i + ".PNG")), "PNG", $W, $H) }
    "exported: " + $Slides
  }
  $pres.Close()
} catch { "ERR: " + $_.Exception.Message } finally { $ps.Quit() }

$ErrorActionPreference='Stop'
$taskRoot=Join-Path (Get-Location) 'work/20261011_analysis_redesign'
$taskPpt=Join-Path $taskRoot 'output/구경주역_중간마감_v3_현황분석.pptx'
$taskPdf=Join-Path $taskRoot 'output/구경주역_중간마감_v3_현황분석.pdf'
$taskRender=Join-Path $taskRoot 'build/powerpoint_render'
New-Item -ItemType Directory -Path $taskRender -Force | Out-Null
$taskApp=New-Object -ComObject PowerPoint.Application
$taskDeck=$null
try {
 $taskDeck=$taskApp.Presentations.Open($taskPpt,-1,0,0)
 if($taskDeck.Slides.Count -ne 60){throw 'Unexpected slide count'}
 $taskDeck.SaveAs($taskPdf,32)
 for($taskPage=1;$taskPage -le $taskDeck.Slides.Count;$taskPage++){
  $taskSlide=$taskDeck.Slides.Item($taskPage)
  $taskSlide.Export((Join-Path $taskRender ($taskPage.ToString('00')+'.png')),'PNG',1280,720)
 }
 $taskResults=[ordered]@{slides=$taskDeck.Slides.Count;powerpointVersion=$taskApp.Version;pdf=$taskPdf;renderDirectory=$taskRender;openedSuccessfully=$true}
 $taskResults | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'build/powerpoint_validation.json') -Encoding utf8
 Write-Output ($taskResults | ConvertTo-Json -Compress)
} finally {if($null -ne $taskDeck){$taskDeck.Close()}}

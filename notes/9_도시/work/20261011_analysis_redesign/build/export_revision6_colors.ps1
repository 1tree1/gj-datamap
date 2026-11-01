$ErrorActionPreference='Stop'
$taskBase='C:/Users/OFFICE/Desktop/9_도시/work/20261011_analysis_redesign/build'
$taskRender=Join-Path $taskBase 'revision6_color_render'
New-Item -ItemType Directory -Path $taskRender -Force | Out-Null
$taskApp=New-Object -ComObject PowerPoint.Application
$taskDeck=$null
try {
 $taskDeck=$taskApp.Presentations.Open((Join-Path $taskBase 'revision6_full_candidate.pptx'),-1,0,0)
 foreach($taskPage in @(18,19,20,21)) {
  $taskDeck.Slides.Item($taskPage).Export((Join-Path $taskRender ($taskPage.ToString('00')+'.png')),'PNG',1280,720)
 }
 Write-Output 'Rendered slides 18-21.'
} finally {if($null -ne $taskDeck){$taskDeck.Close()}}

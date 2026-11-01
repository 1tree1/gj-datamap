param([string]$Pptx, [string]$OutDir, [string]$Selected='')
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$taskApp=New-Object -ComObject PowerPoint.Application
$taskDeck=$null
try {
  $taskDeck=$taskApp.Presentations.Open($Pptx,-1,0,0)
  $taskPages=if($Selected){$Selected.Split(',') | ForEach-Object{[int]$_}}else{1..$taskDeck.Slides.Count}
  foreach($taskPage in $taskPages){
    $taskDeck.Slides.Item($taskPage).Export((Join-Path $OutDir ($taskPage.ToString('00')+'.png')),'PNG',1280,720)
  }
  Write-Output ('Rendered '+$taskDeck.Slides.Count+' slide deck, '+$taskPages.Count+' pages, PowerPoint '+$taskApp.Version)
} finally {if($null -ne $taskDeck){$taskDeck.Close()}}

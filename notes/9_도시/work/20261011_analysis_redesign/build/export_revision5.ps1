param([string]$Ppt,[string]$Render,[string]$Pdf='',[int]$Expected=0,[int]$Width=1600)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path $Render -Force | Out-Null
$taskApp=New-Object -ComObject PowerPoint.Application
$taskDeck=$null
try {
 $taskDeck=$taskApp.Presentations.Open($Ppt,-1,0,0)
 if($Expected -gt 0 -and $taskDeck.Slides.Count -ne $Expected){throw 'Unexpected slide count'}
 if($Pdf){$taskDeck.SaveAs($Pdf,32)}
 for($taskPage=1;$taskPage -le $taskDeck.Slides.Count;$taskPage++){
  $taskDeck.Slides.Item($taskPage).Export((Join-Path $Render ($taskPage.ToString('00')+'.png')),'PNG',$Width,([int]($Width*9/16)))
 }
 [ordered]@{slides=$taskDeck.Slides.Count;pdf=$Pdf;renderDirectory=$Render;openedSuccessfully=$true} | ConvertTo-Json -Compress
} finally {if($null -ne $taskDeck){$taskDeck.Close()}}

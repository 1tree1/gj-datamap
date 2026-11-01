$ErrorActionPreference='Stop'
$taskApp=New-Object -ComObject PowerPoint.Application
$taskBase=Join-Path (Get-Location) 'work/20261011_analysis_redesign/build'
$taskDeck=$null
try{
 $taskDeck=$taskApp.Presentations.Open2007((Join-Path $taskBase 'merged_raw.pptx'),-1,0,0,-1)
 Write-Output ('repair opened '+$taskDeck.Slides.Count)
 $taskDeck.SaveAs((Join-Path $taskBase 'repaired_diagnostic.pptx'),24)
}finally{if($null -ne $taskDeck){$taskDeck.Close()}}

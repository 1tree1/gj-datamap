$ErrorActionPreference='Stop'
$taskApp=New-Object -ComObject PowerPoint.Application
$taskBase=Join-Path (Get-Location) 'work/20261011_analysis_redesign/build'
$taskPaths=@((Get-ChildItem -LiteralPath 'work/20261011_midterm_deck/output' -Filter '*_v2.pptx' | Select-Object -First 1).FullName,(Join-Path $taskBase 'merged_raw.pptx'),(Join-Path $taskBase 'merged_candidate.pptx'))
foreach($taskPath in $taskPaths){
 $taskP=$null
 try{$taskP=$taskApp.Presentations.Open($taskPath,-1,0,0);Write-Output ((Split-Path $taskPath -Leaf)+': OK '+$taskP.Slides.Count)}
 catch{Write-Output ((Split-Path $taskPath -Leaf)+': FAILED '+$_.Exception.Message)}
 finally {if($null -ne $taskP){$taskP.Close()}}
}

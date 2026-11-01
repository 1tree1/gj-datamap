$ErrorActionPreference='Stop'
$taskSource='C:\Users\OFFICE\Desktop\9_도시\work\20261011_analysis_redesign\output\구경주역_중간마감_v11_계획인구와규모.pptx'
$taskTest='C:\Users\OFFICE\Desktop\9_도시\work\20261011_analysis_redesign\build\revision11_editability_test.pptx'
Copy-Item -LiteralPath $taskSource -Destination $taskTest -Force
$taskApp=New-Object -ComObject PowerPoint.Application
$taskDeck=$null
try {
 $taskDeck=$taskApp.Presentations.Open($taskTest,0,0,0)
 $taskChartShape=$null
 foreach($shape in $taskDeck.Slides.Item(50).Shapes){if($shape.HasChart -eq -1){$taskChartShape=$shape;break}}
 if($null -eq $taskChartShape){throw 'No editable chart'}
 $taskChartShape.Width=$taskChartShape.Width*0.98
 $taskChartShape.Chart.SeriesCollection(1).Name='Editability check'
 $taskTableShape=$null
 foreach($shape in $taskDeck.Slides.Item(52).Shapes){if($shape.HasTable -eq -1){$taskTableShape=$shape;break}}
 if($null -eq $taskTableShape){throw 'No editable table'}
 $taskTableShape.Table.Cell(2,1).Shape.TextFrame.TextRange.Text='Editability check'
 $taskDeck.Save()
 $taskDeck.Close();$taskDeck=$null
 $taskDeck=$taskApp.Presentations.Open($taskTest,-1,0,0)
 $taskChartOK=$false;$taskTableOK=$false
 foreach($shape in $taskDeck.Slides.Item(50).Shapes){if($shape.HasChart -eq -1){$taskChartOK=($shape.Chart.SeriesCollection(1).Name -eq 'Editability check')}}
 foreach($shape in $taskDeck.Slides.Item(52).Shapes){if($shape.HasTable -eq -1){$taskTableOK=($shape.Table.Cell(2,1).Shape.TextFrame.TextRange.Text -eq 'Editability check')}}
 if(-not ($taskChartOK -and $taskTableOK)){throw 'Edit did not persist after reopen'}
 [ordered]@{application='PowerPoint';chartEditResizeSaveReopen=$taskChartOK;tableEditSaveReopen=$taskTableOK;finalFileUnchanged=$true}|ConvertTo-Json|Set-Content -LiteralPath 'C:\Users\OFFICE\Desktop\9_도시\work\20261011_analysis_redesign\build\revision11_editability_verification.json' -Encoding UTF8
 Write-Output 'PowerPoint native chart and table edit/save/reopen passed in a private copy.'
} finally {if($taskDeck){$taskDeck.Close()}}

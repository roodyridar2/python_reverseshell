[int]$fileCount = 0
[int]$folderCount = 0
[int]$totalSize = 0

$path = "C:\Users\roody\Desktop\Flutter"

$fileInfo = Get-ChildItem $path -Recurse

foreach ($item in $fileInfo) {
  if ($item.PSIsContainer) {
    # PSIsContainer check is this a folder
    $folderCount++
  }
  else {
    # then is this a file
    $fileCount++
    $totalSize += $item.Length
  }
}

Write-Host "Path $($path) "
Write-Host "Total Directories: $folderCount"
Write-Host "Total File: $fileCount"
Write-Host "Total Size of files: $($totalSize / 1MB)MB"








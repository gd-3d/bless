$parent_directory = Split-Path -Path (Get-Location) -Leaf -Resolve
$target_subfolder = Split-Path -Path ".\$parent_directory" -Leaf -Resolve
$addon_name = "bless"


if ( get-childitem -Include __pycache__ -Recurse -force )
{
    get-childitem -Include __pycache__ -Recurse -force | Remove-Item -Force -Recurse
}
if ( Test-Path ".\$target_subfolder\$name" )
{
    Remove-Item  -Recurse -Path ".\$target_subfolder\$name"
}
if ( Test-Path ".\$target_subfolder")
{
    Compress-Archive -Force -Path .\$target_subfolder -Destination ".\$addon_name.zip"
} 

# write-host "Press any key to continue..."
# [void][System.Console]::ReadKey($true)
# Find out if the current user identity is elevated (has admin rights)
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal $identity
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Proxy Config
$proxy='<proxy adress here>'
[system.net.webrequest]::defaultwebproxy = new-object system.net.webproxy($proxy)
[system.net.webrequest]::defaultwebproxy.credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
[system.net.webrequest]::defaultwebproxy.BypassProxyOnLocal = $true
# $ENV:HTTP_PROXY=$proxy
# $ENV:HTTPS_PROXY=$proxy

# Bash-like Readline behavior
Import-Module PSReadLine
Set-PSReadLineOption -EditMode Emacs
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadLineKeyHandler -Key "Ctrl+RightArrow" -Function ForwardWord
Set-PSReadLineKeyHandler -Key "Ctrl+LeftArrow" -Function BackwardWord

# Git Integration (Status, Branch, etc) via Posh
Import-Module posh-git

# Clipboard interaction is bound by default in Windows mode, but not Emacs mode.
Set-PSReadLineKeyHandler -Key Ctrl+C -Function Copy
Set-PSReadLineKeyHandler -Key Ctrl+v -Function Paste

$APPS_DIR="C:\Apps\"
$DEV_DIR="C:\Dev\"

# Some useful aliases
function ..{ cd .. }
function ...{ cd ..\.. }
function wget ($url) {(new-object Net.WebClient).DownloadString("$url")}
function open { "explorer.exe $(pwd)" | iex }
function pwd { Get-Location }
function home { cd $env:USERPROFILE }
function ent { cd $DEV_DIR }
function wt {
    $wt_path = where.exe wt
    & "$wt_path"
}

function gitconfig {
    subl("C:\Users\$env:USERPROFILE\.gitconfig")
}

function fix_firefox {
    Copy-Item -Path "C:\Users\$env:USERPROFILE\AppData\Local\FirefoxProfiles\profiles.ini" -Destination "C:\Users\$env:USERPROFILE\AppData\Roaming\Mozilla\Firefox\profiles.ini"
}

function subl($file) { & "$APPS_DIR\Sublime Text\subl.exe" $file }
function subm() { & "$APPS_DIR\Sublime Merge\smerge.exe" $(pwd) }
set-alias which where.exe
set-alias l ls # muscle memory

# PowerShell prompt
function prompt 
{ 
    $prompt_cd = "$(Get-Location)"
    if ($isAdmin) 
    {
        $prompt_icon = " #" 
        $host.ui.rawui.WindowTitle = "[ADMIN] $prompt_cd"
    }
    else 
    {
        $prompt_icon = " $"
        $host.ui.rawui.WindowTitle = $prompt_cd
    }

    $GitPromptSettings.DefaultPromptPrefix = ""
    $GitPromptSettings.DefaultPromptSuffix = "$prompt_icon"
    $GitPromptSettings.DefaultPromptPath = "$prompt_cd"
    # $prompt = Write-Prompt "$prompt_cd"
    $prompt = & $GitPromptScriptBlock
    if ($prompt) { 
        "$prompt " 
    } else { 
        " " 
    }

    # Your non-prompt logic here
    # Write-Prompt "$prompt $GitPromptScriptBlock"
}


# Simple function to start a new elevated process. If arguments are supplied then 
# a single command is started with admin rights; if not then a new admin instance
# of PowerShell is started.
function sudo
{
    if ($args.Count -gt 0)
    {   
       $argList = "& '" + $args + "'"
       Start-Process "$psHome\powershell.exe" -Verb runAs -ArgumentList $argList
    }
    else
    {
       Start-Process "$psHome\powershell.exe" -Verb runAs
    }
}


function df {
    $colItems = Get-wmiObject -class "Win32_LogicalDisk" -namespace "root\CIMV2" -computername localhost

    $items = ""
    foreach ($objItem in $colItems) {
        #$items += Write-Output $objItem.DeviceID $objItem.Description $objItem.FileSystem "Free:" ($objItem.FreeSpace / 1GB).toString("f2")"GB" "Total:" ($objItem.Size / 1GB).ToString("f2")"GB" ($objItem.Size / 1GB - $objItem.FreeSpace / 1GB).toString("f2")GB
        $items += Write-Output "Drive:" $objItem.DeviceID "# Filesystem:" $objItem.FileSystem "# Free:" ($objItem.FreeSpace / 1GB).toString("f2")"GB # Total:" ($objItem.Size / 1GB).ToString("f2")"GB # Used:" ($objItem.Size / 1GB - $objItem.FreeSpace / 1GB).toString("f2")GB
    }
    $items

}


function setjava() {
    $env:JAVA_HOME = '$APPS_DIR\java\OpenJDK_17.0.2\'
    $env:Path += $env:JAVA_HOME
    java -version
}


# We don't need these any more; they were just temporary variables to get to $isAdmin. 
Remove-Variable identity
Remove-Variable principal

$pshost = get-host
$pswindow = $pshost.ui.rawui
cls

# Print time
$timeStr = (Get-Date).ToLongTimeString()
Write-Host "$timeStr  $stackStr" -fore "darkgray"
(& uv generate-shell-completion powershell) | Out-String | Invoke-Expression

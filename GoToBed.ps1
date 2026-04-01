# Go-to-Bed - Bedtime Reminder
# PowerShell version

param(
    [switch]$Hidden
)

# Hide console window
if ($Hidden) {
    Add-Type -Name Window -Namespace Console -MemberDefinition '
    [DllImport("Kernel32.dll")]
    public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
    '
    $consolePtr = [Console.Window]::GetConsoleWindow()
    [Console.Window]::ShowWindow($consolePtr, 0) # 0 = Hide
}

# Configuration
$ConfigFile = Join-Path $env:USERPROFILE ".go-to-bed.conf"
$CheckInterval = 30 # seconds
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Default configuration
$DefaultConfig = @{
    bedtime = "22:00"
    weekdays = @("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
}

# Load configuration
function Get-Config {
    if (Test-Path $ConfigFile) {
        try {
            $config = Get-Content $ConfigFile -Raw | ConvertFrom-Json
            Write-Host "Loaded configuration from $ConfigFile"
            return $config
        }
        catch {
            Write-Host "Error loading config, using defaults: $_"
            return $DefaultConfig
        }
    }
    else {
        Write-Host "No config file found, using defaults"
        return $DefaultConfig
    }
}

# Check if today is an active weekday
function Test-ActiveWeekday {
    param($Weekdays)
    
    $dayMap = @{
        "Monday" = "Mon"
        "Tuesday" = "Tue"
        "Wednesday" = "Wed"
        "Thursday" = "Thu"
        "Friday" = "Fri"
        "Saturday" = "Sat"
        "Sunday" = "Sun"
    }
    
    $today = (Get-Date).DayOfWeek.ToString()
    $todayShort = $dayMap[$today]
    
    return $Weekdays -contains $todayShort
}

# Show notification
function Show-Notification {
    param($Username)
    
    Add-Type -AssemblyName System.Windows.Forms
    
    $notification = New-Object System.Windows.Forms.NotifyIcon
    $notification.Icon = [System.Drawing.SystemIcons]::Information
    $notification.BalloonTipTitle = "Go to Bed!"
    $notification.BalloonTipText = "$Username, it's time to go to bed!"
    $notification.Visible = $true
    $notification.ShowBalloonTip(5000)
    
    Start-Sleep -Seconds 2
    $notification.Dispose()
}

# Show fullscreen banner
function Show-Banner {
    param($Username)
    
    $bannerScript = Join-Path $ScriptDir "Show-Banner.ps1"
    if (Test-Path $bannerScript) {
        & $bannerScript -Username $Username
    }
    else {
        Write-Host "Banner script not found: $bannerScript"
    }
}

# Main loop
Write-Host "==================================="
Write-Host "   Go-to-Bed Service Started"
Write-Host "==================================="
Write-Host ""

$config = Get-Config
Write-Host "Bedtime: $($config.bedtime)"
Write-Host "Active days: $($config.weekdays -join ', ')"
Write-Host ""
Write-Host "Checking every $CheckInterval seconds..."
Write-Host "Press Ctrl+C to stop"
Write-Host ""

$username = $env:USERNAME

while ($true) {
    try {
        # Reload config on each check (allows live updates)
        $config = Get-Config
        
        # Check if today is active
        if (-not (Test-ActiveWeekday -Weekdays $config.weekdays)) {
            Start-Sleep -Seconds $CheckInterval
            continue
        }
        
        # Parse bedtime
        $now = Get-Date
        try {
            $bedtimeTime = [DateTime]::ParseExact($config.bedtime, "HH:mm", $null)
            $bedtime = Get-Date -Hour $bedtimeTime.Hour -Minute $bedtimeTime.Minute -Second 0
        }
        catch {
            Write-Host "Error parsing bedtime: $($config.bedtime)"
            Start-Sleep -Seconds $CheckInterval
            continue
        }
        
        # Check if it's bedtime (within interval window)
        $diff = ($now - $bedtime).TotalSeconds
        
        if ($diff -ge 0 -and $diff -lt $CheckInterval) {
            $dayOfWeek = $now.DayOfWeek
            Write-Host "[$now] Bedtime reached! Showing reminder for $username on $dayOfWeek"
            
            # Show notification
            Show-Notification -Username $username
            
            # Show fullscreen banner
            Show-Banner -Username $username
            
            # Wait to avoid showing multiple times
            Start-Sleep -Seconds 60
        }
    }
    catch {
        Write-Host "Error in main loop: $_"
    }
    
    Start-Sleep -Seconds $CheckInterval
}

# Go-to-Bed Configuration GUI
# WPF-based configuration tool

# Hide PowerShell window
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'
$consolePtr = [Console.Window]::GetConsoleWindow()
[Console.Window]::ShowWindow($consolePtr, 0) | Out-Null

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

$CONFIG_FILE = "$env:USERPROFILE\.go-to-bed.conf"

# Load existing config
$currentConfig = $null
if (Test-Path $CONFIG_FILE) {
    try {
        $currentConfig = Get-Content $CONFIG_FILE -Raw | ConvertFrom-Json
    } catch {
        Write-Host "Error loading config: $_"
    }
}

# Default values
$defaultBedtime = if ($currentConfig) { $currentConfig.bedtime } else { "22:00" }
$defaultWeekdays = if ($currentConfig) { $currentConfig.weekdays } else { @("Mon","Tue","Wed","Thu","Fri","Sat","Sun") }

[xml]$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Go-to-Bed Settings" 
        Width="550" Height="700" 
        WindowStartupLocation="CenterScreen"
        ResizeMode="NoResize"
        Background="#F5F5F5">
    <Window.Resources>
        <Style TargetType="TextBlock">
            <Setter Property="FontFamily" Value="Segoe UI"/>
            <Setter Property="FontSize" Value="14"/>
        </Style>
        <Style TargetType="CheckBox">
            <Setter Property="FontFamily" Value="Segoe UI"/>
            <Setter Property="FontSize" Value="13"/>
            <Setter Property="Margin" Value="5,5,5,5"/>
        </Style>
        <Style TargetType="Button">
            <Setter Property="FontFamily" Value="Segoe UI"/>
            <Setter Property="FontSize" Value="14"/>
            <Setter Property="Padding" Value="20,10"/>
            <Setter Property="Cursor" Value="Hand"/>
        </Style>
        <Style TargetType="TextBox">
            <Setter Property="FontFamily" Value="Segoe UI"/>
            <Setter Property="FontSize" Value="14"/>
            <Setter Property="Padding" Value="5"/>
        </Style>
    </Window.Resources>
    
    <Grid Margin="20">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>
        
        <!-- Header -->
        <Grid Grid.Row="0" Background="#2C3E50" Margin="-20,-20,-20,0">
            <StackPanel Margin="20,15">
                <TextBlock Text="Go-to-Bed Settings" FontSize="24" FontWeight="Bold" Foreground="White"/>
                <TextBlock Text="Configure your bedtime reminder" FontSize="12" Foreground="#BDC3C7" Margin="0,5,0,0"/>
            </StackPanel>
        </Grid>
        
        <!-- Bedtime Section -->
        <StackPanel Grid.Row="1" Margin="0,25,0,0">
            <TextBlock Text="Bedtime" FontSize="16" FontWeight="SemiBold" Foreground="#2C3E50" Margin="0,0,0,10"/>
            <Border Background="White" CornerRadius="5" Padding="15" BorderBrush="#BDC3C7" BorderThickness="1">
                <StackPanel>
                    <TextBlock Text="What time do you want to go to bed?" Foreground="#7F8C8D" Margin="0,0,0,10"/>
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="Hour:" VerticalAlignment="Center" Margin="0,0,10,0" Width="50"/>
                        <TextBox x:Name="HourTextBox" Width="60" MaxLength="2" Text="22"/>
                        <TextBlock Text=":" VerticalAlignment="Center" Margin="10,0" FontSize="18" FontWeight="Bold"/>
                        <TextBlock Text="Minute:" VerticalAlignment="Center" Margin="0,0,10,0" Width="50"/>
                        <TextBox x:Name="MinuteTextBox" Width="60" MaxLength="2" Text="00"/>
                    </StackPanel>
                </StackPanel>
            </Border>
        </StackPanel>
        
        <!-- Weekdays Section -->
        <StackPanel Grid.Row="2" Margin="0,20,0,0">
            <TextBlock Text="Active Days" FontSize="16" FontWeight="SemiBold" Foreground="#2C3E50" Margin="0,0,0,10"/>
            <Border Background="White" CornerRadius="5" Padding="15" BorderBrush="#BDC3C7" BorderThickness="1">
                <StackPanel>
                    <TextBlock Text="On which days should the reminder appear?" Foreground="#7F8C8D" Margin="0,0,0,15"/>
                    
                    <!-- Quick Select Buttons -->
                    <StackPanel Orientation="Horizontal" Margin="0,0,0,15">
                        <Button x:Name="AllDaysBtn" Content="Every Day" Background="#3498DB" Foreground="White" Padding="15,8" Margin="0,0,10,0"/>
                        <Button x:Name="WeekdaysBtn" Content="Weekdays" Background="#95A5A6" Foreground="White" Padding="15,8" Margin="0,0,10,0"/>
                        <Button x:Name="WeekendBtn" Content="Weekend" Background="#95A5A6" Foreground="White" Padding="15,8"/>
                    </StackPanel>
                    
                    <Separator Margin="0,5,0,15"/>
                    
                    <!-- Individual Day Checkboxes -->
                    <Grid>
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition/>
                            <ColumnDefinition/>
                        </Grid.ColumnDefinitions>
                        <StackPanel Grid.Column="0">
                            <CheckBox x:Name="MonCheckBox" Content="Monday" IsChecked="True"/>
                            <CheckBox x:Name="TueCheckBox" Content="Tuesday" IsChecked="True"/>
                            <CheckBox x:Name="WedCheckBox" Content="Wednesday" IsChecked="True"/>
                            <CheckBox x:Name="ThuCheckBox" Content="Thursday" IsChecked="True"/>
                        </StackPanel>
                        <StackPanel Grid.Column="1">
                            <CheckBox x:Name="FriCheckBox" Content="Friday" IsChecked="True"/>
                            <CheckBox x:Name="SatCheckBox" Content="Saturday" IsChecked="True"/>
                            <CheckBox x:Name="SunCheckBox" Content="Sunday" IsChecked="True"/>
                        </StackPanel>
                    </Grid>
                </StackPanel>
            </Border>
        </StackPanel>
        
        <!-- Status Message -->
        <TextBlock x:Name="StatusText" Grid.Row="4" 
                   Text="" 
                   Foreground="#27AE60" 
                   FontWeight="SemiBold" 
                   HorizontalAlignment="Center" 
                   VerticalAlignment="Center"
                   Visibility="Collapsed"/>
        
        <!-- Action Buttons -->
        <StackPanel Grid.Row="5" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,20,0,0">
            <Button x:Name="SaveButton" Content="Save Settings" Background="#27AE60" Foreground="White" Padding="25,12" Margin="0,0,10,0"/>
            <Button x:Name="CancelButton" Content="Cancel" Background="#95A5A6" Foreground="White" Padding="25,12"/>
        </StackPanel>
    </Grid>
</Window>
"@

# Load XAML
$reader = New-Object System.Xml.XmlNodeReader $xaml
$window = [Windows.Markup.XamlReader]::Load($reader)

# Get controls
$hourTextBox = $window.FindName("HourTextBox")
$minuteTextBox = $window.FindName("MinuteTextBox")
$monCheckBox = $window.FindName("MonCheckBox")
$tueCheckBox = $window.FindName("TueCheckBox")
$wedCheckBox = $window.FindName("WedCheckBox")
$thuCheckBox = $window.FindName("ThuCheckBox")
$friCheckBox = $window.FindName("FriCheckBox")
$satCheckBox = $window.FindName("SatCheckBox")
$sunCheckBox = $window.FindName("SunCheckBox")
$allDaysBtn = $window.FindName("AllDaysBtn")
$weekdaysBtn = $window.FindName("WeekdaysBtn")
$weekendBtn = $window.FindName("WeekendBtn")
$saveButton = $window.FindName("SaveButton")
$cancelButton = $window.FindName("CancelButton")
$statusText = $window.FindName("StatusText")

# Set current values
if ($defaultBedtime -match "^(\d{1,2}):(\d{2})$") {
    $hourTextBox.Text = $matches[1]
    $minuteTextBox.Text = $matches[2]
}

# Set weekdays checkboxes
$monCheckBox.IsChecked = $defaultWeekdays -contains "Mon"
$tueCheckBox.IsChecked = $defaultWeekdays -contains "Tue"
$wedCheckBox.IsChecked = $defaultWeekdays -contains "Wed"
$thuCheckBox.IsChecked = $defaultWeekdays -contains "Thu"
$friCheckBox.IsChecked = $defaultWeekdays -contains "Fri"
$satCheckBox.IsChecked = $defaultWeekdays -contains "Sat"
$sunCheckBox.IsChecked = $defaultWeekdays -contains "Sun"

# Quick select button handlers
$allDaysBtn.Add_Click({
    $monCheckBox.IsChecked = $true
    $tueCheckBox.IsChecked = $true
    $wedCheckBox.IsChecked = $true
    $thuCheckBox.IsChecked = $true
    $friCheckBox.IsChecked = $true
    $satCheckBox.IsChecked = $true
    $sunCheckBox.IsChecked = $true
})

$weekdaysBtn.Add_Click({
    $monCheckBox.IsChecked = $true
    $tueCheckBox.IsChecked = $true
    $wedCheckBox.IsChecked = $true
    $thuCheckBox.IsChecked = $true
    $friCheckBox.IsChecked = $true
    $satCheckBox.IsChecked = $false
    $sunCheckBox.IsChecked = $false
})

$weekendBtn.Add_Click({
    $monCheckBox.IsChecked = $false
    $tueCheckBox.IsChecked = $false
    $wedCheckBox.IsChecked = $false
    $thuCheckBox.IsChecked = $false
    $friCheckBox.IsChecked = $false
    $satCheckBox.IsChecked = $true
    $sunCheckBox.IsChecked = $true
})

# Save button handler
$saveButton.Add_Click({
    # Validate time
    $hour = $hourTextBox.Text
    $minute = $minuteTextBox.Text
    
    if ([string]::IsNullOrWhiteSpace($hour) -or [string]::IsNullOrWhiteSpace($minute)) {
        [System.Windows.MessageBox]::Show("Please enter both hour and minute!", "Validation Error", "OK", "Error")
        return
    }
    
    $hourNum = 0
    $minuteNum = 0
    if (-not [int]::TryParse($hour, [ref]$hourNum) -or -not [int]::TryParse($minute, [ref]$minuteNum)) {
        [System.Windows.MessageBox]::Show("Please enter valid numbers for time!", "Validation Error", "OK", "Error")
        return
    }
    
    if ($hourNum -lt 0 -or $hourNum -gt 23) {
        [System.Windows.MessageBox]::Show("Hour must be between 0 and 23!", "Validation Error", "OK", "Error")
        return
    }
    
    if ($minuteNum -lt 0 -or $minuteNum -gt 59) {
        [System.Windows.MessageBox]::Show("Minute must be between 0 and 59!", "Validation Error", "OK", "Error")
        return
    }
    
    # Check at least one day selected
    $anyDaySelected = $monCheckBox.IsChecked -or $tueCheckBox.IsChecked -or $wedCheckBox.IsChecked -or 
                      $thuCheckBox.IsChecked -or $friCheckBox.IsChecked -or $satCheckBox.IsChecked -or $sunCheckBox.IsChecked
    
    if (-not $anyDaySelected) {
        [System.Windows.MessageBox]::Show("Please select at least one day!", "Validation Error", "OK", "Error")
        return
    }
    
    # Build weekdays array
    $weekdays = @()
    if ($monCheckBox.IsChecked) { $weekdays += "Mon" }
    if ($tueCheckBox.IsChecked) { $weekdays += "Tue" }
    if ($wedCheckBox.IsChecked) { $weekdays += "Wed" }
    if ($thuCheckBox.IsChecked) { $weekdays += "Thu" }
    if ($friCheckBox.IsChecked) { $weekdays += "Fri" }
    if ($satCheckBox.IsChecked) { $weekdays += "Sat" }
    if ($sunCheckBox.IsChecked) { $weekdays += "Sun" }
    
    # Format time with leading zeros
    $formattedHour = $hourNum.ToString("00")
    $formattedMinute = $minuteNum.ToString("00")
    $bedtime = "${formattedHour}:${formattedMinute}"
    
    # Create config object
    $config = @{
        bedtime = $bedtime
        weekdays = $weekdays
    }
    
    try {
        # Save to file
        $config | ConvertTo-Json | Out-File -FilePath $CONFIG_FILE -Encoding UTF8 -Force
        
        # Show success message
        $result = [System.Windows.MessageBox]::Show("Settings saved successfully!`n`nBedtime: $bedtime`nActive days: $($weekdays -join ', ')`n`nThe service will reload the configuration automatically.", "Success", "OK", "Information")
        
        $window.Close()
    }
    catch {
        [System.Windows.MessageBox]::Show("Error saving configuration: $_", "Error", "OK", "Error")
    }
})

# Cancel button handler
$cancelButton.Add_Click({
    $window.Close()
})

# Show window
$window.ShowDialog() | Out-Null

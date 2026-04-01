# Show-Banner.ps1 - WPF Fullscreen Banner

param(
    [string]$Username = $env:USERNAME
)

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

[xml]$xaml = @"
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="Go to Bed!"
    WindowStyle="None"
    WindowState="Maximized"
    ResizeMode="NoResize"
    Topmost="True"
    Background="#CC000000"
    ShowInTaskbar="False">
    
    <Grid>
        <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center">
            
            <!-- Moon Emoji -->
            <TextBlock 
                Text="🌙" 
                FontSize="120" 
                HorizontalAlignment="Center"
                Margin="0,0,0,40"/>
            
            <!-- Main Message -->
            <TextBlock 
                Name="MainMessage"
                Text="$Username, it's time to go to bed!"
                FontSize="48"
                FontWeight="Bold"
                Foreground="White"
                HorizontalAlignment="Center"
                TextAlignment="Center"
                Margin="40,0,40,40"/>
            
            <!-- Subtitle -->
            <TextBlock 
                Text="Good night! 😴"
                FontSize="36"
                Foreground="White"
                HorizontalAlignment="Center"
                Margin="0,0,0,60"/>
            
            <!-- OK Button -->
            <Button 
                Name="OkButton"
                Content="OK, I'm going to bed now"
                FontSize="24"
                Padding="40,20,40,20"
                HorizontalAlignment="Center"
                Cursor="Hand">
                <Button.Style>
                    <Style TargetType="Button">
                        <Setter Property="Background" Value="#2196F3"/>
                        <Setter Property="Foreground" Value="White"/>
                        <Setter Property="BorderThickness" Value="0"/>
                        <Setter Property="Template">
                            <Setter.Value>
                                <ControlTemplate TargetType="Button">
                                    <Border 
                                        Background="{TemplateBinding Background}" 
                                        CornerRadius="8"
                                        Padding="{TemplateBinding Padding}">
                                        <ContentPresenter 
                                            HorizontalAlignment="Center" 
                                            VerticalAlignment="Center"/>
                                    </Border>
                                </ControlTemplate>
                            </Setter.Value>
                        </Setter>
                        <Style.Triggers>
                            <Trigger Property="IsMouseOver" Value="True">
                                <Setter Property="Background" Value="#1976D2"/>
                            </Trigger>
                        </Style.Triggers>
                    </Style>
                </Button.Style>
            </Button>
            
        </StackPanel>
    </Grid>
</Window>
"@

# Load XAML
$reader = New-Object System.Xml.XmlNodeReader $xaml
$window = [Windows.Markup.XamlReader]::Load($reader)

# Get controls
$okButton = $window.FindName("OkButton")
$mainMessage = $window.FindName("MainMessage")

# Update username in message
$mainMessage.Text = "🌙 $Username, it's time to go to bed! 🌙"

# Button click event
$okButton.Add_Click({
    $window.Close()
})

# Auto-close after 2 minutes
$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMinutes(2)
$timer.Add_Tick({
    $timer.Stop()
    $window.Close()
})
$timer.Start()

# Show window
$window.ShowDialog() | Out-Null

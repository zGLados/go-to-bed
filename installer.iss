; Go-to-Bed Installer Script for Inno Setup
; https://jrsoftware.org/isinfo.php

#define MyAppName "Go-to-Bed"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Go-to-Bed Contributors"
#define MyAppURL "https://github.com/zGLados/go-to-bed"
#define MyAppExeName "GoToBed.ps1"
#define MyAppLauncher "Start-GoToBed.vbs"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{8B3D4A5C-9E2F-4B1A-A8C3-D6E7F8A9B0C1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=GoToBed-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={sys}\WindowsPowerShell\v1.0\powershell.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "autostart"; Description: "Start automatically when Windows starts"; GroupDescription: "Additional options:"; Flags: checkedonce
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "GoToBed.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "Show-Banner.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "Start-GoToBed.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "configure.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppLauncher}"
Name: "{group}\Configuration"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\configure.ps1"""; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppLauncher}"; Tasks: desktopicon

[Registry]
; Autostart registry entry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppLauncher}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
; Start application after installation
Filename: "{app}\{#MyAppLauncher}"; Description: "Start {#MyAppName} now"; Flags: postinstall skipifsilent nowait

[Code]
var
  ConfigPage: TWizardPage;
  HourEdit: TEdit;
  MinuteEdit: TEdit;
  MonCheckBox, TueCheckBox, WedCheckBox, ThuCheckBox: TCheckBox;
  FriCheckBox, SatCheckBox, SunCheckBox: TCheckBox;
  EveryDayCheckBox, WeekdaysCheckBox, WeekendCheckBox: TCheckBox;

procedure CreateConfigPage;
var
  Y: Integer;
  Label1, Label2, Label3, Label4: TLabel;
begin
  ConfigPage := CreateCustomPage(wpSelectTasks, 'Bedtime Configuration', 'Choose when you want to be reminded to go to bed');
  
  Y := 10;
  
  { Bedtime selection }
  Label1 := TLabel.Create(ConfigPage);
  Label1.Parent := ConfigPage.Surface;
  Label1.Caption := 'Bedtime (24-hour format):';
  Label1.Left := 0;
  Label1.Top := Y;
  Label1.Font.Style := [fsBold];
  
  Y := Y + 25;
  
  Label2 := TLabel.Create(ConfigPage);
  Label2.Parent := ConfigPage.Surface;
  Label2.Caption := 'Hour:';
  Label2.Left := 0;
  Label2.Top := Y + 3;
  
  HourEdit := TEdit.Create(ConfigPage);
  HourEdit.Parent := ConfigPage.Surface;
  HourEdit.Left := 50;
  HourEdit.Top := Y;
  HourEdit.Width := 40;
  HourEdit.Text := '22';
  
  Label3 := TLabel.Create(ConfigPage);
  Label3.Parent := ConfigPage.Surface;
  Label3.Caption := 'Minute:';
  Label3.Left := 110;
  Label3.Top := Y + 3;
  
  MinuteEdit := TEdit.Create(ConfigPage);
  MinuteEdit.Parent := ConfigPage.Surface;
  MinuteEdit.Left := 160;
  MinuteEdit.Top := Y;
  MinuteEdit.Width := 40;
  MinuteEdit.Text := '00';
  
  Y := Y + 40;
  
  { Quick selection options }
  Label4 := TLabel.Create(ConfigPage);
  Label4.Parent := ConfigPage.Surface;
  Label4.Caption := 'Active days:';
  Label4.Left := 0;
  Label4.Top := Y;
  Label4.Font.Style := [fsBold];
  
  Y := Y + 25;
  
  EveryDayCheckBox := TCheckBox.Create(ConfigPage);
  EveryDayCheckBox.Parent := ConfigPage.Surface;
  EveryDayCheckBox.Caption := 'Every day (Mon-Sun)';
  EveryDayCheckBox.Left := 0;
  EveryDayCheckBox.Top := Y;
  EveryDayCheckBox.Width := 200;
  EveryDayCheckBox.Checked := True;
  
  Y := Y + 25;
  
  WeekdaysCheckBox := TCheckBox.Create(ConfigPage);
  WeekdaysCheckBox.Parent := ConfigPage.Surface;
  WeekdaysCheckBox.Caption := 'Weekdays only (Mon-Fri)';
  WeekdaysCheckBox.Left := 0;
  WeekdaysCheckBox.Top := Y;
  WeekdaysCheckBox.Width := 200;
  
  Y := Y + 25;
  
  WeekendCheckBox := TCheckBox.Create(ConfigPage);
  WeekendCheckBox.Parent := ConfigPage.Surface;
  WeekendCheckBox.Caption := 'Weekend only (Sat-Sun)';
  WeekendCheckBox.Left := 0;
  WeekendCheckBox.Top := Y;
  WeekendCheckBox.Width := 200;
  
  Y := Y + 35;
  
  { Individual day selection }
  TLabel.Create(ConfigPage).Parent := ConfigPage.Surface;
  with TLabel(ConfigPage.FindComponent('TLabel')) do begin
    Caption := 'Or select individual days:';
    Left := 0;
    Top := Y;
  end;
  
  Y := Y + 20;
  
  MonCheckBox := TCheckBox.Create(ConfigPage);
  MonCheckBox.Parent := ConfigPage.Surface;
  MonCheckBox.Caption := 'Monday';
  MonCheckBox.Left := 0;
  MonCheckBox.Top := Y;
  MonCheckBox.Width := 100;
  MonCheckBox.Checked := True;
  
  TueCheckBox := TCheckBox.Create(ConfigPage);
  TueCheckBox.Parent := ConfigPage.Surface;
  TueCheckBox.Caption := 'Tuesday';
  TueCheckBox.Left := 110;
  TueCheckBox.Top := Y;
  TueCheckBox.Width := 100;
  TueCheckBox.Checked := True;
  
  WedCheckBox := TCheckBox.Create(ConfigPage);
  WedCheckBox.Parent := ConfigPage.Surface;
  WedCheckBox.Caption := 'Wednesday';
  WedCheckBox.Left := 220;
  WedCheckBox.Top := Y;
  WedCheckBox.Width := 100;
  WedCheckBox.Checked := True;
  
  Y := Y + 25;
  
  ThuCheckBox := TCheckBox.Create(ConfigPage);
  ThuCheckBox.Parent := ConfigPage.Surface;
  ThuCheckBox.Caption := 'Thursday';
  ThuCheckBox.Left := 0;
  ThuCheckBox.Top := Y;
  ThuCheckBox.Width := 100;
  ThuCheckBox.Checked := True;
  
  FriCheckBox := TCheckBox.Create(ConfigPage);
  FriCheckBox.Parent := ConfigPage.Surface;
  FriCheckBox.Caption := 'Friday';
  FriCheckBox.Left := 110;
  FriCheckBox.Top := Y;
  FriCheckBox.Width := 100;
  FriCheckBox.Checked := True;
  
  Y := Y + 25;
  
  SatCheckBox := TCheckBox.Create(ConfigPage);
  SatCheckBox.Parent := ConfigPage.Surface;
  SatCheckBox.Caption := 'Saturday';
  SatCheckBox.Left := 0;
  SatCheckBox.Top := Y;
  SatCheckBox.Width := 100;
  SatCheckBox.Checked := True;
  
  SunCheckBox := TCheckBox.Create(ConfigPage);
  SunCheckBox.Parent := ConfigPage.Surface;
  SunCheckBox.Caption := 'Sunday';
  SunCheckBox.Left := 110;
  SunCheckBox.Top := Y;
  SunCheckBox.Width := 100;
  SunCheckBox.Checked := True;
end;

procedure QuickSelectClick(Sender: TObject);
begin
  if Sender = EveryDayCheckBox then begin
    if EveryDayCheckBox.Checked then begin
      WeekdaysCheckBox.Checked := False;
      WeekendCheckBox.Checked := False;
      MonCheckBox.Checked := True;
      TueCheckBox.Checked := True;
      WedCheckBox.Checked := True;
      ThuCheckBox.Checked := True;
      FriCheckBox.Checked := True;
      SatCheckBox.Checked := True;
      SunCheckBox.Checked := True;
    end;
  end
  else if Sender = WeekdaysCheckBox then begin
    if WeekdaysCheckBox.Checked then begin
      EveryDayCheckBox.Checked := False;
      WeekendCheckBox.Checked := False;
      MonCheckBox.Checked := True;
      TueCheckBox.Checked := True;
      WedCheckBox.Checked := True;
      ThuCheckBox.Checked := True;
      FriCheckBox.Checked := True;
      SatCheckBox.Checked := False;
      SunCheckBox.Checked := False;
    end;
  end
  else if Sender = WeekendCheckBox then begin
    if WeekendCheckBox.Checked then begin
      EveryDayCheckBox.Checked := False;
      WeekdaysCheckBox.Checked := False;
      MonCheckBox.Checked := False;
      TueCheckBox.Checked := False;
      WedCheckBox.Checked := False;
      ThuCheckBox.Checked := False;
      FriCheckBox.Checked := False;
      SatCheckBox.Checked := True;
      SunCheckBox.Checked := True;
    end;
  end;
end;

procedure InitializeWizard;
begin
  CreateConfigPage;
  EveryDayCheckBox.OnClick := @QuickSelectClick;
  WeekdaysCheckBox.OnClick := @QuickSelectClick;
  WeekendCheckBox.OnClick := @QuickSelectClick;
end;

function ValidateConfigPage: Boolean;
var
  Hour, Minute: Integer;
  ErrorMsg: String;
begin
  Result := False;
  ErrorMsg := '';
  
  { Validate hour }
  Hour := StrToIntDef(HourEdit.Text, -1);
  if (Hour < 0) or (Hour > 23) then
    ErrorMsg := 'Hour must be between 0 and 23';
  
  { Validate minute }
  Minute := StrToIntDef(MinuteEdit.Text, -1);
  if (ErrorMsg = '') and ((Minute < 0) or (Minute > 59)) then
    ErrorMsg := 'Minute must be between 0 and 59';
  
  { Check at least one day selected }
  if (ErrorMsg = '') and not (MonCheckBox.Checked or TueCheckBox.Checked or WedCheckBox.Checked or 
      ThuCheckBox.Checked or FriCheckBox.Checked or SatCheckBox.Checked or SunCheckBox.Checked) then
    ErrorMsg := 'Please select at least one day';
  
  if ErrorMsg <> '' then begin
    MsgBox(ErrorMsg, mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = ConfigPage.ID then
    Result := ValidateConfigPage;
end;

procedure SaveConfig;
var
  ConfigFile: String;
  ConfigContent: String;
  Weekdays: String;
  Hour, Minute: String;
begin
  ConfigFile := ExpandConstant('{%USERPROFILE}') + '\.go-to-bed.conf';
  
  { Pad hour and minute with zeros }
  Hour := HourEdit.Text;
  if Length(Hour) = 1 then
    Hour := '0' + Hour;
  Minute := MinuteEdit.Text;
  if Length(Minute) = 1 then
    Minute := '0' + Minute;
  
  { Build weekdays array }
  Weekdays := '';
  if MonCheckBox.Checked then Weekdays := Weekdays + '"Mon",';
  if TueCheckBox.Checked then Weekdays := Weekdays + '"Tue",';
  if WedCheckBox.Checked then Weekdays := Weekdays + '"Wed",';
  if ThuCheckBox.Checked then Weekdays := Weekdays + '"Thu",';
  if FriCheckBox.Checked then Weekdays := Weekdays + '"Fri",';
  if SatCheckBox.Checked then Weekdays := Weekdays + '"Sat",';
  if SunCheckBox.Checked then Weekdays := Weekdays + '"Sun",';
  
  { Remove trailing comma }
  if Length(Weekdays) > 0 then
    Delete(Weekdays, Length(Weekdays), 1);
  
  { Create JSON config }
  ConfigContent := '{' + #13#10;
  ConfigContent := ConfigContent + '  "bedtime": "' + Hour + ':' + Minute + '",' + #13#10;
  ConfigContent := ConfigContent + '  "weekdays": [' + Weekdays + ']' + #13#10;
  ConfigContent := ConfigContent + '}';
  
  { Save to file }
  SaveStringToFile(ConfigFile, ConfigContent, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    SaveConfig;
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  { Check if already running - check for PowerShell process }
  { We'll just proceed, taskkill will handle it during install if needed }
end;

[UninstallRun]
; Stop the application before uninstall  
Filename: "taskkill"; Parameters: "/F /IM powershell.exe /FI ""WINDOWTITLE eq Go-to-Bed*"""; Flags: runhidden; RunOnceId: "StopGoToBed"
Filename: "taskkill"; Parameters: "/F /IM wscript.exe /FI ""WINDOWTITLE eq Start-GoToBed.vbs*"""; Flags: runhidden; RunOnceId: "StopLauncher"

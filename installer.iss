; Go-to-Bed Installer Script for Inno Setup
; https://jrsoftware.org/isinfo.php

#define MyAppName "Go-to-Bed"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Go-to-Bed Contributors"
#define MyAppURL "https://github.com/zGLados/go-to-bed"
#define MyAppExeName "go-to-bed.exe"

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
; Icon and graphics
SetupIconFile=
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "autostart"; Description: "Automatisch beim Windows-Start ausführen"; GroupDescription: "Zusätzliche Optionen:"; Flags: checkedonce
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "go-to-bed.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "configure.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Konfiguration"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\configure.ps1"""; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Autostart registry entry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
; Run configuration after installation
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\configure.ps1"""; Description: "Schlafenszeit jetzt konfigurieren"; Flags: postinstall shellexec skipifsilent nowait
; Start application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} jetzt starten"; Flags: postinstall skipifsilent nowait

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  // Check if already running
  if CheckForMutexes('Global\GoToBedMutex') then
  begin
    if MsgBox('Go-to-Bed läuft bereits. Soll die Anwendung beendet werden?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec('taskkill', '/F /IM go-to-bed.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      Result := False;
    end;
  end;
end;

[UninstallRun]
; Stop the application before uninstall
Filename: "taskkill"; Parameters: "/F /IM go-to-bed.exe"; Flags: runhidden; RunOnceId: "StopGoToBed"

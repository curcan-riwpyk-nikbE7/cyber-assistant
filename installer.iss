[Setup]
AppName=Cyber Assistant
AppVersion=2.1.0
AppPublisher=KINGSAID
DefaultDirName={autopf}\Cyber Assistant
DefaultGroupName=Cyber Assistant
OutputBaseFilename=Cyber_Assistant_Setup_v2.1
OutputDir=C:\Users\KINGSAID\cyber-assistant\dist
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "Запускать Кибер вместе с Windows"; GroupDescription: "Автозагрузка:"

[Files]
Source: "C:\Users\KINGSAID\cyber-assistant\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".git\*,.venv\*,dist\*,*.iss"

[Icons]
Name: "{autoprograms}\Cyber Assistant"; Filename: "pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"
Name: "{autodesktop}\Cyber Assistant"; Filename: "pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{commonstartup}\Cyber Assistant"; Filename: "pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; Tasks: autostart

[Run]
Filename: "pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,Cyber Assistant}"; Flags: nowait postinstall skipifsilent

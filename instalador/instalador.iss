; Script de instalación Inno Setup para "Lee y Juega"
; Diseñado para Windows 10 y Windows 11

#define MyAppName "Lee y Juega"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Educación ICFES Colombia"
#define MyAppExeName "LeeYJuega.exe"

[Setup]
AppId={{C6D2B784-9A4E-4089-A5F8-7F4B749E69A1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Instalador_Lee_y_Juega_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Iniciar automáticamente con Windows"; GroupDescription: "Opciones de inicio:"

[Files]
; Archivos generados por PyInstaller en dist\LeeYJuega
Source: "..\dist\LeeYJuega\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\LeeYJuega\graficas_generadas"
Type: files; Name: "{userappdata}\LeeYJuega\logs\*.log"

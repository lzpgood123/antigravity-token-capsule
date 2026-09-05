; Inno Setup Script for Antigravity Token Capsule
; Produces professional Windows installer (.exe) unpacking the high-performance onedir bundle

#define MyAppName "Antigravity Token Capsule"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "lzpgood123"
#define MyAppURL "https://github.com/lzpgood123/antigravity-token-capsule"
#define MyAppExeName "token-capsule.exe"

[Setup]
AppId={{5E973B90-E57A-4546-95D9-2D86FE4A9362}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\AntigravityTokenCapsule
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Run with standard user privileges - no UAC administrator elevation required!
PrivilegesRequired=lowest
OutputDir=dist\installer
OutputBaseFilename=token-capsule-Setup-v{#MyAppVersion}
SetupIconFile=capsule.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\onedir\token-capsule\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; Script generated for SPHENKS
#define MyAppName "Sphenks"
#define MyAppVersion "0.5"
#define MyAppPublisher "Team Husk"
#define MyAppExeName "Sphenks_Demo.exe"

[Setup]
AppId={{1F5285DD-66D5-442B-BB47-4F199DC74E81}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; Setup dosyasının adı ve çıkacağı yer (Masaüstü)
OutputBaseFilename=Sphenks_Setup_v0.5
OutputDir=C:\Users\hp\Desktop
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; BURASI DÜZELTİLDİ: Senin masaüstündeki klasör yolunu tam olarak yazdık.
; "recursesubdirs" komutu sayesinde _internal klasörünü OTOMATİK olarak alır.
Source: "C:\Users\hp\Desktop\Sphenks_Demo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; WorkingDir parametresi eklendi.
; Bu, kısayola "Oyunu açarken Program Files klasöründen güç al" der.

Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
; SPHENKS FINAL SETUP SCRIPT
; Sesleri ve Kısayol sorununu çözen versiyon.

#define MyAppName "Sphenks"
#define MyAppVersion "1.0"
#define MyAppPublisher "Team Husk"
#define MyAppExeName "Sphenks.exe"

[Setup]
; --- KİMLİK AYARLARI ---
; AppId benzersiz olmalı, bunu değiştirme.
AppId={{8B4567A1-C234-4D5E-9F01-23456789ABCD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; --- KURULUM YERİ ---
; {autopf} -> Otomatik olarak Program Files (x86) veya Program Files seçer.
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; --- ÇIKTI AYARLARI ---
; Setup dosyasını Masaüstüne atar
OutputDir={userdesktop}
OutputBaseFilename=Sphenks_Setup_v1
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; --- DOSYALAR ---
; dist\Sphenks klasöründeki her şeyi alıyoruz.

; 1. Ana EXE
Source: "dist\Sphenks\Sphenks.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. Tüm Klasörler (_internal, assets, sounds hepsi buradadır)
; recursesubdirs: Alt klasörleri de al
; createallsubdirs: Klasör yapısını koru
Source: "dist\Sphenks\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; --- KISAYOL AYARLARI (KRİTİK BÖLÜM) ---
; WorkingDir: "{app}" eklemesi, kısayolun assets klasörünü bulmasını sağlar.

; Başlat Menüsü Kısayolu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

; Masaüstü Kısayolu
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
; Kurulum bitince çalıştır
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
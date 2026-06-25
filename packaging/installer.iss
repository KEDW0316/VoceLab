; Inno Setup 스크립트 — PyInstaller onefile(dist/VoceLab.exe)을 설치 마법사로 감싼다.
; CI(windows)에서 ISCC.exe packaging/installer.iss 로 컴파일 → dist/VoceLab-Setup.exe

#define AppVersion "0.1.0"

[Setup]
AppName=VoceLab
AppVersion={#AppVersion}
AppPublisher=VoceLab
DefaultDirName={autopf}\VoceLab
DefaultGroupName=VoceLab
DisableProgramGroupPage=yes
; 관리자 권한 없이 사용자 영역에 설치(서명 없는 앱의 마찰 최소화)
PrivilegesRequired=lowest
SourceDir=..
OutputDir=dist
OutputBaseFilename=VoceLab-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 작업:"

[Files]
Source: "dist\VoceLab.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VoceLab"; Filename: "{app}\VoceLab.exe"
Name: "{group}\VoceLab 제거"; Filename: "{uninstallexe}"
Name: "{autodesktop}\VoceLab"; Filename: "{app}\VoceLab.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VoceLab.exe"; Description: "VoceLab 실행"; Flags: nowait postinstall skipifsilent

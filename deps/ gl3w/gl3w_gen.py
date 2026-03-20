name: Build Thalixte ReShade 32-bit Only (No OpenGL)

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - name: Checkout with submodules
      uses: actions/checkout@v4
      with:
        submodules: recursive

    - name: Setup MSBuild
      uses: microsoft/setup-msbuild@v2

    - name: Disable gl3w generation (bypass 403 error)
      shell: powershell
      run: |
        $dummyScript = @'
#!/usr/bin/env python
import sys
print("gl3w_gen.py skipped - using pre-generated files")
sys.exit(0)
'@
        Set-Content -Path "deps/gl3w/gl3w_gen.py" -Value $dummyScript -Encoding UTF8
        Write-Host "gl3w_gen.py disabled"

    - name: Build ReShade 32-bit
      shell: cmd
      run: |
        msbuild ReShade.sln ^
          /p:Configuration=Release ^
          /p:Platform="32-bit" ^
          /p:WindowsTargetPlatformVersion=10.0.22000.0 ^
          /p:PlatformToolset=v143 ^
          /t:"ReShade";"ReShade FX";"ImGui";"MinHook";"stb";"FXC";"Injector" ^
          /m ^
          /verbosity:minimal

    - name: Collect 32-bit DLLs
      shell: powershell
      run: |
        New-Item -ItemType Directory -Force -Path "output_32bit"
        
        $paths = @(
          "bin\32-bit\Release\ReShade32.dll",
          "bin\Win32\Release\ReShade32.dll",
          "bin\Release\Win32\ReShade32.dll"
        )
        
        foreach ($p in $paths) {
          if (Test-Path $p) {
            Copy-Item $p "output_32bit\"
            Write-Host "Found: $p"
          }
        }
        
        if (-not (Test-Path "output_32bit\ReShade32.dll")) {
          Get-ChildItem -Path "bin" -Recurse | Select-Object FullName
          exit 1
        }

    - name: Upload Artifact
      uses: actions/upload-artifact@v4
      with:
        name: Thalixte-ReShade-32bit
        path: output_32bit/
        retention-days: 30

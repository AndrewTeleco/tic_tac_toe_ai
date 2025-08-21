import os
from uncompyle6.main import decompile_file

# Carpeta donde están los .pyc
source_dir = "tic_tac_toe"
# Carpeta donde se guardarán los archivos recuperados
output_dir = "recuperado"

os.makedirs(output_dir, exist_ok=True)

for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith(".pyc"):
            pyc_path = os.path.join(root, file)
            # Mantener la estructura de carpetas
            relative_path = os.path.relpath(root, source_dir)
            target_dir = os.path.join(output_dir, relative_path)
            os.makedirs(target_dir, exist_ok=True)
            py_file = os.path.join(target_dir, file.replace(".cpython-313.pyc", ".py"))
            
            try:
                with open(py_file, "w", encoding="utf-8") as out_f:
                    decompile_file(pyc_path, out_f)
                print(f"Recuperado: {py_file}")
            except Exception as e:
                print(f"No se pudo recuperar {pyc_path}: {e}")

print("\n✅ Recuperación completada. Revisa la carpeta 'recuperado/'")

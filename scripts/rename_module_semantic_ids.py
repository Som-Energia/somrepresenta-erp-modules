import sys
import erppeek
import configdb
from yamlns import namespace as ns
from pathlib2 import Path


script_directory = Path(__file__).absolute().parent


erp = erppeek.Client(**configdb.erppeek)
imd = erp.model('ir.model.data')

modules = ns.load(str(script_directory/'renamed_modules.yaml'))


for old_module, new_module in modules.items():
    if "-r" in sys.argv:
        old_module, new_module = new_module, old_module

    current_module_ids = imd.search([
        ('module', '=', old_module),
        ('model', '!=', 'ir.module.module'),
    ])

    if not current_module_ids:
        continue

    imd.write(current_module_ids, dict(
        module=new_module
    ))
    current_modules = imd.read(current_module_ids)

    for module in current_modules:
        print("{module} . {name}: {model} . {id}".format(**module))

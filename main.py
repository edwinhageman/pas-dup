import getopt
import os
import shutil
import sys
from pathlib import Path

from lxml import etree


def main(argv):
    name = ''
    source = ''
    dest = ''

    try:
        opts, args = getopt.getopt(argv, 'hn:s:d:', ['name=', 'source=', 'dest='])
    except getopt.GetoptError:
        print(__file__ + '-n <name> -s <source path> -d <dest path>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(__file__ + ' -n <name> -s <source path> -d <dest path>')
            sys.exit()
        elif opt in ('-n', '--name'):
            name = arg
        elif opt in ('-s', '--source'):
            source = arg
        elif opt in ('-d', '--dest'):
            dest = arg

    if name == '' or source == '' or dest == '':
        print(__file__ + '-n <name> -s <source path> -d <dest path>')
        sys.exit(0)

    copy_solution(source, dest)

    update_solution_file(dest, name)
    conn_refs = update_customizations_file(dest, name)
    env_vars = update_env_var_definition_files(dest, name)

    update_workflow_files(dest, conn_refs, env_vars)

    print('successfully dupped solution')

def copy_solution(source_path, dest_path):
    path = Path(dest_path)
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)


def update_solution_file(path, name):
    file = os.path.join(path, 'solution.xml')
    with open(file) as f:
        contents = f.read()
    with open(file, 'w') as f:
        contents = change_solution_name(contents, name)
        f.write(contents)


def change_solution_name(xml, name):
    root = etree.fromstring(xml)
    manifest = root.find('SolutionManifest')

    manifest.find('UniqueName').text = name

    localized_names = manifest.find('LocalizedNames')
    for localized_name in localized_names.findall('LocalizedName'):
        localized_name.set('description', name)

    return etree.tostring(root).decode('utf-8')


def update_customizations_file(path, name):
    file = os.path.join(path, 'customizations.xml')
    with open(file) as f:
        contents = f.read()
    with open(file, 'w') as d:
        references = find_connection_references(contents)
        table = rename_connection_references(references, name)
        contents = change_customizations_connection_references(contents, table)
        d.write(contents)
        return table


def find_connection_references(xml):
    root = etree.fromstring(xml)
    conn_references = root.find('connectionreferences')

    result = []
    for conn_ref in conn_references.findall('connectionreference'):
        result.append(conn_ref.get('connectionreferencelogicalname'))

    return result


def rename_connection_references(references, prefix):
    table = {}
    for idx, ref in enumerate(references):
        table[ref] = 'conn_ref_{0}_{1}'.format(prefix, idx)
    return table


def change_customizations_connection_references(xml, table):
    root = etree.fromstring(xml)
    conn_references = root.find('connectionreferences')

    for ref in conn_references.findall('connectionreference'):
        new_name = table[ref.get('connectionreferencelogicalname')]
        ref.set('connectionreferencelogicalname', new_name)

    return etree.tostring(root).decode('utf-8')


def update_env_var_definition_files(path, name):
    definitions = {}
    folder_path = os.path.join(path, 'environmentvariabledefinitions')
    for folder in os.listdir(folder_path):
        file_path = os.path.join(folder_path, folder, 'environmentvariabledefinition.xml')
        with open(file_path) as r:
            contents = r.read()
            old_name = load_environment_variable_name(contents)
            new_name = rename_environment_variable_definitions(name, len(definitions))
            definitions[old_name] = new_name
            contents = change_environment_variable_name(contents, new_name)
        with open(file_path, 'w') as w:
            w.write(contents)
    return definitions


def load_environment_variable_name(xml):
    root = etree.fromstring(xml)
    return root.get('schemaname')


def rename_environment_variable_definitions(prefix, idx):
    return 'env_var_{0}_{1}'.format(prefix, idx)


def change_environment_variable_name(xml, newname):
    root = etree.fromstring(xml)
    root.set('schemaname', newname)

    return etree.tostring(root).decode('utf-8')


def update_workflow_files(path, conn_references, env_variables):
    folder_path = os.path.join(path, 'Workflows')
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        with open(file_path) as r:
            contents = replace_workflow_references(r.read(), conn_references, env_variables)
        with open(file_path, 'w') as w:
            w.write(contents)


def replace_workflow_references(txt, conn_references, env_variables):
    for old, new in conn_references.items():
        txt = txt.replace(old, new)

    for old, new in env_variables.items():
        txt = txt.replace(old, new)

    return txt


if __name__ == "__main__":
    main(sys.argv[1:])

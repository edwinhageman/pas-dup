import os
import shutil
import unittest
from pathlib import Path

from lxml import etree

from main import change_solution_name, update_customizations_file, find_connection_references, \
    rename_connection_references, change_customizations_connection_references, load_environment_variable_name, \
    change_environment_variable_name, rename_environment_variable_definitions, update_env_var_definition_files, \
    replace_workflow_references, copy_solution, update_solution_file

solution_XML = '''
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="9.2.24112.214" SolutionPackageVersion="9.2" languagecode="1043" generatedBy="CrmLive" OrganizationVersion="9.2.24112.214" OrganizationSchemaType="Standard" CRMServerServiceabilityVersion="9.2.24112.00214">
  <SolutionManifest>
    <UniqueName>Solution</UniqueName>
    <LocalizedNames>
      <LocalizedName description="Solution" languagecode="1043" />
    </LocalizedNames>
    <Descriptions>
      <Description description="" languagecode="1043" />
    </Descriptions>
    <Version>1.1.0.0</Version>
    <Managed>0</Managed>
  </SolutionManifest>
</ImportExportXml>
'''

customizations_XML = '''\
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="9.2.24112.214" SolutionPackageVersion="9.2" languagecode="1043" generatedBy="CrmLive" OrganizationVersion="9.2.24112.214" OrganizationSchemaType="Standard" CRMServerServiceabilityVersion="9.2.24112.00214">
  <CustomControls />
  <EntityDataProviders />
  <connectionreferences>
    <connectionreference connectionreferencelogicalname="eh_sharedsharepointonline_db1031">
      <connectionreferencedisplayname>SharePoint Solution-db103</connectionreferencedisplayname>
      <connectorid>/providers/Microsoft.PowerApps/apis/shared_sharepointonline</connectorid>
      <iscustomizable>1</iscustomizable>
      <statecode>0</statecode>
      <statuscode>1</statuscode>
    </connectionreference>
    <connectionreference connectionreferencelogicalname="eh_sharedtodo_f0a68">
      <connectionreferencedisplayname>Microsoft To-Do (Business) Solution-f0a68</connectionreferencedisplayname>
      <connectorid>/providers/Microsoft.PowerApps/apis/shared_todo</connectorid>
      <iscustomizable>1</iscustomizable>
      <statecode>0</statecode>
      <statuscode>1</statuscode>
    </connectionreference>
  </connectionreferences>
  <Languages>
    <Language>1043</Language>
  </Languages>
</ImportExportXml>'''

workflow_JSON = '''{
    "properties": {
    "connectionReferences": {
      "shared_excelonlinebusiness": {
        "api": {
          "name": "shared_excelonlinebusiness"
        },
        "connection": {
          "connectionReferenceLogicalName": "eh_sharedexcelonlinebusiness_6c321"
        },
        "runtimeSource": "invoker"
      },
      "shared_todo": {
        "api": {
          "name": "shared_todo"
        },
        "connection": {
          "connectionReferenceLogicalName": "new_sharedtodo_d1789"
        },
        "runtimeSource": "invoker"
      },
      "shared_sharepointonline-1": {
        "api": {
          "name": "shared_sharepointonline"
        },
        "connection": {
          "connectionReferenceLogicalName": "eh_sharedsharepointonline_db103"
        },
        "runtimeSource": "invoker"
      }
    },
    "definition": {
      "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "$authentication": {
          "defaultValue": {},
          "type": "SecureObject"
        },
        "$connections": {
          "defaultValue": {},
          "type": "Object"
        },
        "Sharepoint site (eh_Sharepointsite)": {
          "defaultValue": "",
          "type": "String",
          "metadata": {
            "schemaName": "eh_Sharepointsite"
          }
        },
      },
    },
    },'''

environmentvariabledefinition_XML = '''<environmentvariabledefinition schemaname="eh_configfile">
  <displayname default="config file">
    <label description="config file" languagecode="1043" />
  </displayname>
  <introducedversion>1.0.0.0</introducedversion>
  <iscustomizable>1</iscustomizable>
  <isrequired>0</isrequired>
  <secretstore>0</secretstore>
  <type>100000000</type>
</environmentvariabledefinition>'''


class TestSolution(unittest.TestCase):
    path = 'resources/test_solution'

    def setUp(self):
        path = Path(self.path)
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)
        shutil.copytree('resources/solution', path, dirs_exist_ok=True)

    def tearDown(self):
        path = Path('resources/test_solution')
        shutil.rmtree(path, ignore_errors=True)

    def loadXMLFromFile(self, path):
        return etree.parse(path)

    def test_copy_solution(self):
        source_path = 'resources/solution'
        dest_path = 'resources/solution_copy'
        shutil.rmtree(dest_path, ignore_errors=True)

        copy_solution(source_path, dest_path)

        self.assertTrue(os.path.exists(dest_path))
        shutil.rmtree(dest_path, ignore_errors=True)

    def test_update_solution_file(self):
        update_solution_file(self.path, 'TEST_SOLUTION')

        xml = self.loadXMLFromFile(os.path.join(self.path, 'solution.xml'))
        name = xml.find('SolutionManifest').find('UniqueName').text

        self.assertEqual(name, 'TEST_SOLUTION')

    def test_change_solution_name(self):
        expected = '''\
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="9.2.24112.214" SolutionPackageVersion="9.2" languagecode="1043" generatedBy="CrmLive" OrganizationVersion="9.2.24112.214" OrganizationSchemaType="Standard" CRMServerServiceabilityVersion="9.2.24112.00214">
  <SolutionManifest>
    <UniqueName>new name</UniqueName>
    <LocalizedNames>
      <LocalizedName description="new name" languagecode="1043"/>
    </LocalizedNames>
    <Descriptions>
      <Description description="" languagecode="1043"/>
    </Descriptions>
    <Version>1.1.0.0</Version>
    <Managed>0</Managed>
  </SolutionManifest>
</ImportExportXml>'''
        output = change_solution_name(solution_XML, "new name")
        self.assertEqual(expected, output)

    def test_update_customizations_file(self):
        update_customizations_file(self.path, 'TEST_SOLUTION')

        xml = self.loadXMLFromFile(os.path.join(self.path, 'customizations.xml'))
        for ref in xml.find('connectionreferences').findall('connectionreference'):
            self.assertTrue(ref.get('connectionreferencelogicalname').startswith('conn_ref_TEST_SOLUTION'))

    def test_find_connection_references(self):
        expected = ['eh_sharedsharepointonline_db1031', 'eh_sharedtodo_f0a68']

        result = find_connection_references(customizations_XML)

        self.assertEqual(expected, result)

    def test_rename_connection_references(self):
        expected = {
            'eh_sharedsharepointonline_db1031': 'conn_ref_newprefix_0',
            'eh_sharedtodo_f0a68': 'conn_ref_newprefix_1'
        }

        result = rename_connection_references(['eh_sharedsharepointonline_db1031', 'eh_sharedtodo_f0a68'], 'newprefix')

        self.assertEqual(expected, result)

    def test_update_connection_references(self):
        expected = '''\
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="9.2.24112.214" SolutionPackageVersion="9.2" languagecode="1043" generatedBy="CrmLive" OrganizationVersion="9.2.24112.214" OrganizationSchemaType="Standard" CRMServerServiceabilityVersion="9.2.24112.00214">
  <CustomControls/>
  <EntityDataProviders/>
  <connectionreferences>
    <connectionreference connectionreferencelogicalname="newprefix_0">
      <connectionreferencedisplayname>SharePoint Solution-db103</connectionreferencedisplayname>
      <connectorid>/providers/Microsoft.PowerApps/apis/shared_sharepointonline</connectorid>
      <iscustomizable>1</iscustomizable>
      <statecode>0</statecode>
      <statuscode>1</statuscode>
    </connectionreference>
    <connectionreference connectionreferencelogicalname="newprefix_1">
      <connectionreferencedisplayname>Microsoft To-Do (Business) Solution-f0a68</connectionreferencedisplayname>
      <connectorid>/providers/Microsoft.PowerApps/apis/shared_todo</connectorid>
      <iscustomizable>1</iscustomizable>
      <statecode>0</statecode>
      <statuscode>1</statuscode>
    </connectionreference>
  </connectionreferences>
  <Languages>
    <Language>1043</Language>
  </Languages>
</ImportExportXml>'''
        table = {
            'eh_sharedsharepointonline_db1031': 'newprefix_0',
            'eh_sharedtodo_f0a68': 'newprefix_1'
        }

        output = change_customizations_connection_references(customizations_XML, table)

        self.assertEqual(expected, output)

    def test_load_environment_variable_name(self):
        expected = 'eh_configfile'

        output = load_environment_variable_name(environmentvariabledefinition_XML)

        self.assertEqual(expected, output)

    def test_change_environment_variable_name(self):
        expected = '''<environmentvariabledefinition schemaname="newname">
  <displayname default="config file">
    <label description="config file" languagecode="1043"/>
  </displayname>
  <introducedversion>1.0.0.0</introducedversion>
  <iscustomizable>1</iscustomizable>
  <isrequired>0</isrequired>
  <secretstore>0</secretstore>
  <type>100000000</type>
</environmentvariabledefinition>'''

        output = change_environment_variable_name(environmentvariabledefinition_XML, 'newname')

        self.assertEqual(expected, output)

    def test_rename_environment_variable(self):
        expected = 'env_var_prefix_1'

        output = rename_environment_variable_definitions('prefix', 1)

        self.assertEqual(expected, output)

    def test_update_env_var_definition_files(self):
        update_env_var_definition_files(self.path, 'TEST_SOLUTION')

        xml = self.loadXMLFromFile(os.path.join(self.path,
                                                'environmentvariabledefinitions/eh_Sharepointsite/environmentvariabledefinition.xml'))
        schemaname = xml.getroot().get('schemaname')
        self.assertTrue(schemaname.startswith('env_var_TEST_SOLUTION'))

    def test_replace_workflow_references(self):
        expected = '''{
    "properties": {
    "connectionReferences": {
      "shared_excelonlinebusiness": {
        "api": {
          "name": "shared_excelonlinebusiness"
        },
        "connection": {
          "connectionReferenceLogicalName": "conn_ref_newprefix_0"
        },
        "runtimeSource": "invoker"
      },
      "shared_todo": {
        "api": {
          "name": "shared_todo"
        },
        "connection": {
          "connectionReferenceLogicalName": "conn_ref_newprefix_1"
        },
        "runtimeSource": "invoker"
      },
      "shared_sharepointonline-1": {
        "api": {
          "name": "shared_sharepointonline"
        },
        "connection": {
          "connectionReferenceLogicalName": "conn_ref_newprefix_2"
        },
        "runtimeSource": "invoker"
      }
    },
    "definition": {
      "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "$authentication": {
          "defaultValue": {},
          "type": "SecureObject"
        },
        "$connections": {
          "defaultValue": {},
          "type": "Object"
        },
        "Sharepoint site (env_var_newprefix_0)": {
          "defaultValue": "",
          "type": "String",
          "metadata": {
            "schemaName": "env_var_newprefix_0"
          }
        },
      },
    },
    },'''
        conn_references = {
            'eh_sharedexcelonlinebusiness_6c321': 'conn_ref_newprefix_0',
            'new_sharedtodo_d1789': 'conn_ref_newprefix_1',
            'eh_sharedsharepointonline_db103': 'conn_ref_newprefix_2',
        }
        env_variables = {
            'eh_Sharepointsite': 'env_var_newprefix_0',
        }
        output = replace_workflow_references(workflow_JSON, conn_references, env_variables)
        self.assertEqual(expected, output)


if __name__ == "__main__":
    unittest.main()

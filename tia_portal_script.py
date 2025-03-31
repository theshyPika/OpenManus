import tia_portal.config as tia_config
import time
import os
import logging
from tia_portal import Client
from tia_portal.version import TiaVersion

# Logging configuration
logging.basicConfig(
    filename="F:\\llm_log\\script_execution.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def initialize_tia_client():
    tia_config.load()
    return Client()

def create_or_open_project(tia_client, project_workspace, template_project_name, new_project_name):
    new_project_file = os.path.join(project_workspace, new_project_name)
    if not os.path.exists(new_project_file):
        tia_client.open_project(project_workspace, template_project_name)
        tia_client.project.save_as(new_project_name)
    else:
        tia_client.open_project(project_workspace, new_project_name)

def modify_plc_settings(plc, new_project_name, PLC_DEVICE_NO, PLC_SN):
    plc.set_name("P." + new_project_name + "_OP" + PLC_DEVICE_NO + "=PLC-KF" + PLC_SN)

def generate_code_groups(plc, SOFTWARE_MODULES):
    software_list = plc.get_software()
    software_group_list = software_list.get_user_block_groups()
    external_source_groups = software_list.get_external_source_groups()

    for software_module in SOFTWARE_MODULES:
        temp_group = software_group_list.find(software_module)
        if temp_group.value is None:
            temp_group = software_group_list.create(software_module)
        else:
            temp_group.value.Delete()
            temp_group.value = None
            temp_group = software_group_list.create(software_module)

        external_group = external_source_groups.find(software_module)
        if external_group.value is None:
            external_group = external_source_groups.create(software_module)
        else:
            external_group.value.Delete()
            external_group.value = None
            external_group = external_source_groups.create(software_module)

        if temp_group.get_blocks().find(f"{os.path.split(software_module)[1]}_DIY_HMI").value is None:
            tmp_dict = {}
            tmp_dict["M10"] = os.path.split(software_module)[1]
            logging.info(os.path.split(software_module)[1])
            temp_group.get_blocks().create(tmp_dict)

def main():
    start_time = time.time()
    logging.info(f"----create plc project start time [{start_time}]-------")

    tia_client = initialize_tia_client()

    project_workspace = "F:\\tmp\\02_Projects\\02_Projects"
    template_project_name = "Preh_Template_V2_0_V18"
    new_project_name = "project_3"
    create_or_open_project(tia_client, project_workspace, template_project_name, new_project_name)

    plcs = tia_client.project.get_plcs()
    if len(plcs) == 0:
        logging.info(f"No PLCs found in project")
    elif len(plcs) > 1:
        logging.info(f"Multiple PLCs found in project")
    else:
        plc = plcs[0]
        modify_plc_settings(plc, new_project_name, "01", "1")
        generate_code_groups(plc, ["Module 10", "Module 20"])

    logging.info(f"----create plc project end time [{time.time()}]-------")

if __name__ == "__main__":
    main()
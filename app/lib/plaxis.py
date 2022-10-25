"""
Copyright (c) 2022 VIKTOR B.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

VIKTOR B.V. PROVIDES THIS SOFTWARE ON AN "AS IS" BASIS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import numpy as np
from plxscripting.easy import new_server

# Define the paths where the json files are created. This is with respect to the current working directory of the VIKTOR
# worker
path_input_json = Path(__file__).parent / "input.json"
path_materials_json = Path(__file__).parent / "materials.json"
path_output_json = Path(__file__).parent / "output.json"
# Open the files and store the obtained dictionaries
with open(path_input_json, "r", encoding="utf-8") as f:
    params_embankment = json.load(f)
with open(path_materials_json, "r", encoding="utf-8") as f:
    params_materials = json.load(f)


# Define a function that is needed to convert input parameters to a suitable PLAXIS-material-input
def get_deepest_dict(dict_list: Union[List[Dict], Dict]) -> Dict:
    """Parameters are nested in the input. Flatten it out to a single dict using this function.

    This function works by taking a dictionary or a list as input. If it is a dict, recursively enter that dict to
    obtain the deepest items. Do the same for a list. In the end, update the dict with the deepest items, and return
    that dict"""
    deepest_dict = {}  # Instantiate an empty dict where we store the deepest items
    if isinstance(dict_list, dict):  # Apparently it's a dict
        for key, value in dict_list.items():
            if isinstance(value, dict):
                # The item in the dict is a dict again! Let's go one level deeper...
                deepest_dict.update(get_deepest_dict(value))
            elif not isinstance(value, type(None)):
                # Convert values if necessary
                if value == "True":
                    value = True
                if value == "False":
                    value = False
                deepest_dict.update({key: value})  # Great! This was the deepest item, so update the main dict
    elif isinstance(dict_list, list):
        for item in dict_list:
            deepest_dict.update(get_deepest_dict(item))  # Go a lever deeper...
    return deepest_dict


# The material keys have to be inserted in a specific order. This order is as follows:
ORDERED_MATERIAL_KEYS = [
    "Object",
    "Comments",
    "MaterialName",
    "Colour",
    "SoilModel",
    "UserDefinedIndex",
    "DrainageType",
    "DilatancyCutOff",
    "UndrainedBehaviour",
    "InterfaceStrength",
    "ConsiderGapClosure",
    "K0PrimaryIsK0Secondary",
    "K0Determination",
    "CrossPermeability",
    "Gref",
    "cref",
    "phi",
    "psi",
    "verticalref",
    "cinc",
    "K0",
    "gammaUnsat",
    "gammaSat",
    "perm_primary_horizontal_axis",
    "perm_vertical_axis",
    "Rinter",
    "TensileStrength",
    "UDPower",
    "verticalinc",
    "Ginc",
    "ninit",
    "nmin",
    "nmax",
    "gammaPore",
    "ck",
    "nuu",
    "UDPRef",
    "RinterResidualStrength",
    "einit",
    "emin",
    "emax",
    "Dinter",
    "SkemptonB",
    "KwRefN",
    "VolumetricSpecificStorage",
    "K0Primary",
    "K0Secondary",
    "OCR",
    "POP",
    "SoilRatioSmall",
    "SoilRatioMedium",
    "SoilRatioLarge",
    "PsiUnsat",
    "HydraulicModel",
    "FlowDataModel",
    "DrainageConductivity",
    "DefaultValuesAdvanced",
    "nu",
    "DataSetFlow",
    "SoilTypeFlow",
    "UsdaSoilType",
    "M50",
    "UseDefaultsFlow",
    "TablePsiPermSat",
    "SplinePsiPerm",
    "SplinePsiSat",
    "UseAlternatives",
    "lambdaModified",
    "kappaModified",
    "LambdaKappa",
    "powerm",
    "Pref",
    "M",
    "K0nc",
    "Cc",
    "Cs",
    "TensionCutOff",
    "MuModified",
    "Ca",
    "E50ref",
    "EoedRef",
    "EurRef",
    "ErefOed50",
    "ErefUr50",
    "powerm",
    "Pref",
    "Rf",
    "M",
    "Kfac",
    "Gi0ref",
    "K0nc",
    "Cc",
    "Cs",
    "FailureCriterion",
    "G0ref",
    "gamma07",
    "Einc",
    "CVRef",
]

# Open PLAXIS and start server. Specify PLAXIS path on server.
PLAXIS_PATH = r"C:\Program Files\Bentley\Geotechnical\PLAXIS 2D CONNECT Edition V21\\Plaxis2DXInput.exe"
PORT_I = 10000  # Define a port number.
PORT_O = 10001
PASSWORD = "s1<BvF8rMM?ZRRR%"
with subprocess.Popen(
    [PLAXIS_PATH, f"--AppServerPassword={PASSWORD}", f"--AppServerPort={PORT_I}"],
    shell=False,
):  # Use a context wrapper such that the process will be closed after the job finishes
    time.sleep(5)  # Wait for PLAXIS to boot before sending commands to the scripting service.
    # Start the scripting server.
    s_i, g_i = new_server("localhost", PORT_I, password=PASSWORD)
    s_o, g_o = new_server("localhost", PORT_O, password=PASSWORD)
    s_i.new()  # Start a new project

    # Add soil materials. This must be done in a specific order to ensure the materials are set correctly
    materials = {}  # Make a dict to be able to refer to the materials by name
    for i, params_material in enumerate(params_materials):
        material_zip_list = []
        material_flattened_dict = get_deepest_dict(
            params_material
        )  # Get the deepest items from the material parameters dict
        for (
            material_key
        ) in ORDERED_MATERIAL_KEYS:  # Use a specific material key order such that the settings are set correctly
            if material_key in material_flattened_dict:
                material_zip_list.append((material_key, material_flattened_dict[material_key]))
        material = g_i.soilmat(material_zip_list[0])
        for material_zip in material_zip_list[1:]:
            material.setproperties(*material_zip)  # Set all the properties of the material in an iterative fashion
        materials.update({material_flattened_dict["MaterialName"]: material})

    embankment_parameters = params_embankment["geometry_tab"]["embankment"]
    soil_parameters = params_embankment["geometry_tab"]["soil"]
    drain_parameters = params_embankment["geometry_tab"]["drain"]
    layer_thicknesses = [layer["thickness"] for layer in soil_parameters["layers"]]
    soil_depth = -1 * sum(layer_thicknesses)
    g_i.SoilContour.initializerectangular(0, soil_depth, soil_parameters["width"], embankment_parameters["height"])
    borehole = g_i.borehole(0)
    layers = [g_i.soillayer(layer["thickness"]) for layer in soil_parameters["layers"]]
    borehole.Head = -1  # Water level is at -1 m
    _ = [
        g_i.setmaterial(soil, materials[layer["material"]["name"]])
        for soil, layer in zip(g_i.Soils, soil_parameters["layers"])
    ]
    g_i.gotostructures()
    # Define the points of the embankment structure
    point_list = [
        g_i.point(x, y)
        for x, y in [
            (0, embankment_parameters["height"]),
            (embankment_parameters["width"] / 2.0, embankment_parameters["height"]),
            (
                (embankment_parameters["width"] + embankment_parameters["slope_width"]) / 2.0,
                embankment_parameters["height"] / 2.0,
            ),
            (0, embankment_parameters["height"] / 2.0),
            (0, 0),
            (embankment_parameters["width"] / 2.0 + embankment_parameters["slope_width"], 0),
        ]
    ]
    # Always draw the bottom layer first, as it otherwise does not connect
    embankment_bottom_layer = g_i.polygon(*point_list[2:])[0]  # Last four points are the bottom layer
    embankment_top_layer = g_i.polygon(*point_list[:4])[0]  # First four points are the top layer
    # Set the proper materials on the embankment layers
    g_i.setmaterial(embankment_top_layer.Soil, materials[embankment_parameters["material.name"]])
    g_i.setmaterial(embankment_bottom_layer.Soil, materials[embankment_parameters["material.name"]])
    if drain_parameters["selector"]:  # If drains are enabled
        _ = [  # Set the drain depth to just above the end of the selected layer
            g_i.drain((x, 0), (x, (-1 + 1e-7) * sum(layer_thicknesses[: drain_parameters["depth"]])))
            for x in np.arange(
                drain_parameters["spacing"] / 2.0,
                embankment_parameters["width"] / 2.0 + embankment_parameters["slope_width"],
                drain_parameters["spacing"],
            )
        ]
    g_i.gotomesh()
    g_i.mesh(0.06)
    g_i.gotostages()
    # Set the phases
    phase_0 = g_i.Phases[0]
    g_i.GroundwaterFlow.BoundaryXMin.set(phase_0, "Closed")
    g_i.GroundwaterFlow.BoundaryYMin.set(phase_0, "Open")
    phase_names = [  # Define the names of the phases
        "First embankment construction",
        "First consolidation",
        "Second embankment construction",
        "End of consolidation",
    ]
    phase_1 = g_i.phase(phase_0)
    phase_1.Identification = phase_names[0]
    phase_1.DeformCalcType = "Consolidation"
    phase_1.TimeInterval = 2  # Phase takes two days
    g_i.activate(embankment_bottom_layer, phase_1)
    if drain_parameters["selector"]:  # If drains are enabled
        g_i.activate(g_i.Drains, phase_1)
    phase_2 = g_i.phase(phase_1)
    phase_2.Identification = phase_names[1]
    phase_2.DeformCalcType = "Consolidation"
    # Use P_Excess as exit condition for automatic phase length determination. This is not the same as in tutorial 08!
    phase_2.Deform.LoadingType = "Minimum excess pore pressure"
    phase_3 = g_i.phase(phase_2)
    phase_3.Identification = phase_names[2]
    phase_3.DeformCalcType = "Consolidation"
    phase_3.TimeInterval = 1
    g_i.activate(embankment_top_layer, phase_3)
    phase_4 = g_i.phase(phase_3)
    phase_4.Identification = phase_names[3]
    phase_4.DeformCalcType = "Consolidation"
    phase_4.Deform.LoadingType = "Minimum excess pore pressure"
    g_i.selectmeshpoints()
    g_o.addcurvepoint("Node", g_o.Soils[0][0], (0, -1 * layer_thicknesses[0]))
    g_o.update()
    g_i.calculate()

    # Read the output
    steps_time = []
    steps_p_excess = []
    g_i.view(g_i.Phases[-1])  # Starts output window
    for step in g_o.Steps:
        steps_p_excess.append(g_o.getcurveresults(g_o.CurvePoints[0], step, g_o.ResultTypes.Soil.PExcess))
        steps_time.append(step.Reached.Time.value)
    g_o.close()  # Close the output window
    g_i.kill()  # Close the input window

with open(path_output_json, "w", encoding="utf-8") as f:  # Save the output in a json file to be returned by the worker
    json.dump({"time": steps_time, "p_excess": steps_p_excess}, f)

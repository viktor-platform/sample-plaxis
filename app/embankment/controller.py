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
from copy import deepcopy
from io import BytesIO
from pathlib import Path

import plotly.graph_objects as go
from munch import Munch
from munch import unmunchify
from viktor import File
from viktor.core import ViktorController
from viktor.external.generic import GenericAnalysis
from viktor.views import GeometryResult
from viktor.views import GeometryView
from viktor.views import PlotlyResult
from viktor.views import PlotlyView

from app.embankment.parametrization import EmbankmentParametrization
from app.embankment.visualisation import get_embankment_geometry_group


class EmbankmentController(ViktorController):
    """
    Controller to show embankment designs
    """

    label = "Embankment"
    parametrization = EmbankmentParametrization

    @GeometryView("Embankment 2D", view_mode="2D", duration_guess=1)
    def visualize_embankment_model(self, params: Munch, entity_id: int, **kwargs: dict) -> GeometryResult:
        """Show the embankment model using a 2D geometry view"""
        geometry_group = get_embankment_geometry_group(params)
        return GeometryResult(geometry_group)

    @PlotlyView("PLAXIS analysis", duration_guess=300)
    def run_plaxis(self, params, **kwargs) -> PlotlyResult:
        """Evaluate the PLAXIS embankment model and visualise the result"""
        params_ = deepcopy(params)
        params_materials_list = [params_.geometry_tab.embankment.material.last_saved_params]
        # Preprocess params: replace all material IDs with the name of the material
        params_.geometry_tab.embankment.material = {
            "name": params_.geometry_tab.embankment.material.last_saved_params.general.MaterialName
        }
        for layer in params_.geometry_tab.soil.layers:
            params_materials_list.append(unmunchify(layer.material.last_saved_params))
            layer.material = {"name": layer.material.last_saved_params.general.MaterialName}
        # Make the files that should be sent to the worker
        json_input = json.dumps(unmunchify(params_))
        json_materials = json.dumps(params_materials_list)
        plaxis_script_path = Path(__file__).parents[1] / "lib" / "plaxis.py"
        plaxis_script_bytes = File.from_path(plaxis_script_path).getvalue_binary()
        files = [
            ("input.json", BytesIO(json_input.encode())),
            ("materials.json", BytesIO(json_materials.encode())),
            ("plaxis.py", BytesIO(plaxis_script_bytes)),
        ]
        # Run the worker
        generic_analysis = GenericAnalysis(files=files, output_filenames=["output.json"], executable_key="plaxis")
        generic_analysis.execute(timeout=600)
        output_file = generic_analysis.get_output_file("output.json")
        # Load the output from the worker
        output = json.load(output_file)
        # Visualise the output
        fig = go.Figure(data=go.Scatter(x=output["time"], y=output["p_excess"]))
        fig.update_layout(xaxis_title="Time [days]", yaxis_title="P_Excess [kN / m^2]")
        return PlotlyResult(fig.to_json())

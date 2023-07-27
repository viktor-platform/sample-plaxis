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
import numpy as np
from munch import Munch
from viktor import Color
from viktor import UserError
from viktor.geometry import Group
from viktor.geometry import Material
from viktor.geometry import Point
from viktor.geometry import Polygon


def _check_params(params: Munch) -> None:
    err_list = []
    if (
        params.geometry_tab.embankment.width + params.geometry_tab.embankment.slope_width * 2
        > params.geometry_tab.soil.width / 1.5
    ):
        err_list.append("The soil width needs to be at least 1.5 as large as the total embankment width")
    if not all(
        [params.geometry_tab.embankment.material, *[layer.material for layer in params.geometry_tab.soil.layers]]
    ):
        err_list.append("Please make sure materials are defined for the embankment and soil layers")
    if err_list:
        raise UserError(". ".join(err_list))


def _get_rgb(value: int):
    blue = (value & 0xFF0000) >> 16
    green = (value & 0xFF00) >> 8
    red = value & 0xFF
    return Color(red, green, blue)


def get_embankment_geometry_group(params: Munch) -> Group:
    """Converts the embankment params to a Group.
    This can be used as input for a visualisation using a GeometryResult"""
    _check_params(params)  # Check that the parameters make sense
    # Draw embankment polygon
    embankment = Polygon(
        points=[
            Point(params.geometry_tab.embankment.width / -2.0 - params.geometry_tab.embankment.slope_width, 0),
            Point(params.geometry_tab.embankment.width / -2.0, params.geometry_tab.embankment.height),
            Point(params.geometry_tab.embankment.width / 2.0, params.geometry_tab.embankment.height),
            Point(params.geometry_tab.embankment.width / 2.0 + params.geometry_tab.embankment.slope_width, 0),
        ],
        material=Material(
            name=params.geometry_tab.embankment.material.last_saved_params.general.MaterialName,
            color=_get_rgb(params.geometry_tab.embankment.material.last_saved_params.general.Colour),
        ),
    )
    # Create the soil layers
    soil_x_min = params.geometry_tab.soil.width / -2.0
    soil_x_max = params.geometry_tab.soil.width / 2.0
    layers = []
    depth = 0
    for layer in params.geometry_tab.soil.layers:
        layers.append(
            Polygon(
                points=[
                    Point(soil_x_min, depth),
                    Point(soil_x_max, depth),
                    Point(soil_x_max, depth - layer.thickness),
                    Point(soil_x_min, depth - layer.thickness),
                ],
                material=Material(
                    name=layer.material.name, color=_get_rgb(layer.material.last_saved_params.general.Colour)
                ),
            )
        )
        depth -= layer.thickness
    # Draw the drains
    drains = []
    if params.geometry_tab.drain.selector:
        spacing = params.geometry_tab.drain.spacing
        drain_x_locations = np.arange(
            spacing / 2.0,
            params.geometry_tab.embankment.width / 2.0 + params.geometry_tab.embankment.slope_width,
            spacing,
        )
        drain_x_locations = np.concatenate((-1.0 * drain_x_locations, drain_x_locations))
        drain_width = 0.1
        try:
            drain_depth = layers[params.geometry_tab.drain.depth - 1].points[-1].y
        except IndexError as err:
            raise UserError("This drain depth is deeper than the amount of layers available") from err
        drains = [
            Polygon(
                points=[
                    Point(x_loc + drain_width, 0),
                    Point(x_loc + drain_width, drain_depth),
                    Point(x_loc - drain_width, drain_depth),
                    Point(x_loc - drain_width, 0),
                ],
                material=Material(name="Drain", color=Color.viktor_blue()),
            )
            for x_loc in drain_x_locations
        ]
    return Group([embankment, *layers, *drains])

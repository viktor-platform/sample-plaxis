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
from munch import Munch
from viktor.parametrization import BooleanField
from viktor.parametrization import DynamicArray
from viktor.parametrization import EntityOptionField
from viktor.parametrization import IntegerField
from viktor.parametrization import Lookup
from viktor.parametrization import NumberField
from viktor.parametrization import Parametrization
from viktor.parametrization import Section
from viktor.parametrization import Tab


def _max_drain_depth(params: Munch, **kwargs) -> int:
    """
    Return the maximum amount of layers of how deep the drains can be
    :param kwargs: passed keyword arguments
    :return: maximum amount of layers as int
    """
    return len(params.geometry_tab.soil.layers)


class EmbankmentParametrization(Parametrization):
    """
    Define the parametrization of an embankment
    """

    geometry_tab = Tab("Geometry")
    geometry_tab.embankment = Section("Embankment")
    geometry_tab.embankment.width = NumberField(
        "Embankment width",
        default=16.0,
        step=0.1,
        min=1.0,
        max=50.0,
        num_decimals=2,
        variant="standard",
        suffix="m")
    geometry_tab.embankment.height = NumberField(
        "Height",
        default=4.0,
        step=0.1,
        min=1.0,
        max=10.0,
        num_decimals=2,
        variant="standard",
        suffix="m")
    geometry_tab.embankment.slope_width = NumberField(
        "Slope width",
        default=12.0,
        step=0.1,
        min=1.0,
        max=50.0,
        num_decimals=2,
        variant="standard",
        suffix="m")
    geometry_tab.embankment.material = EntityOptionField(ui_name="Material", entity_type_names=["Material"])
    geometry_tab.soil = Section("Soil")
    geometry_tab.soil.width = NumberField(
        "Soil semi-width",
        default=60.0,
        step=0.1,
        min=30.0,
        max=120.0,
        num_decimals=2,
        variant="standard",
        suffix="m")
    geometry_tab.soil.layers = DynamicArray("Layers")
    geometry_tab.soil.layers.thickness = NumberField(
        "Thickness",
        default=3.0,
        step=0.1,
        min=1.0,
        max=5.0,
        num_decimals=2,
        variant="standard",
        suffix="m")
    geometry_tab.soil.layers.material = EntityOptionField(
        ui_name="Material",
        entity_type_names=["Material"],
    )

    geometry_tab.drain = Section("Drains")
    geometry_tab.drain.selector = BooleanField("Use drains", default=False)
    geometry_tab.drain.spacing = NumberField(
        "Drain spacing",
        default=2.0,
        step=0.1,
        min=0.1,
        max=None,
        num_decimals=2,
        variant="standard",
        suffix="m",
        visible=Lookup("geometry_tab.drain.selector"))
    geometry_tab.drain.depth = IntegerField(
        "Drain depth",
        default=2,
        min=1,
        max=_max_drain_depth,
        suffix="layers deep",
        visible=Lookup("geometry_tab.drain.selector"))

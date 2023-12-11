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
from viktor import Color
from viktor.parametrization import LineBreak
from viktor.parametrization import NumberField
from viktor.parametrization import OptionField
from viktor.parametrization import OptionListElement
from viktor.parametrization import Parametrization
from viktor.parametrization import Tab
from viktor.parametrization import TextField

from app.embankment.constants import COLORS


def _get_rgb_number(red: int, green: int, blue: int) -> int:
    """get colour number from RGB value using bit left shift"""
    i_b = blue << 16  # left shift 16 bits for blue
    i_g = green << 8  # left shift  8 bits for green
    i_r = red  # left shift  0 bits for red
    return i_b + i_g + i_r


def _get_color_options(**kwargs) -> [OptionListElement, ...]:
    """Get the options for the colour dropdown"""
    value: Color
    return [
        OptionListElement(_get_rgb_number(*value.rgb), key) for key, value in sorted(COLORS.items(), key=lambda i: i[0])
    ]


class MaterialParametrization(Parametrization):
    """
    Define the parametrization of a material. Follow the logic as in PLAXIS

    All the names are equal to the keys in the plaxis input object SoilMat
    # Todo include logic of hiding/showing applicable fields
    """

    general = Tab("General")
    general.MaterialName = TextField("Name")
    general.Colour = OptionField(
        ui_name="Colour",
        options=_get_color_options,
        default="yellow",
        variant="standard")
    # Define the inputs for material properties, as defined in the tutorial PDF (PLAXIS_2D_2018-Tutorial-Lesson05.pdf)
    general.new_line = LineBreak()
    general.SoilModel = OptionField(
        ui_name="Material Model",
        options=["Hardening Soil", "Soft Soil"])
    general.DrainageType = OptionField(
        ui_name="Type",
        description="Type of material behaviour",
        options=["Drained", "Undrained (A)"])
    general.gammaUnsat = NumberField(
        ui_name="$γ_{unsat}$",
        description="Soil unit weight above phreatic level",
        suffix="kN / m^3")
    general.gammaSat = NumberField(
        ui_name="$γ_{sat}$",
        description="Soil unit weight below phreatic level",
        suffix="kN / m^3")
    general.einit = NumberField(
        ui_name="$e_{init}$",
        description="Initial void ratio",
        suffix="-")
    param = Tab("Parameters")
    param.E50ref = NumberField(
        ui_name="$E^{ref}_{50}$",
        description="Secant stiffness in standard drained triaxial test",
        suffix="kN / m^2")
    param.EoedRef = NumberField(
        ui_name="$E^{ref}_{oed}$",
        description="Tangent stiffness for primary oedometer loading",
        suffix="kN / m^2")
    param.EurRef = NumberField(
        ui_name="$E^{ref}_{ur}$",
        description="Unloading / reloading stiffness",
        suffix="kN / m^2")
    param.powerm = NumberField(
        ui_name="m",
        description="Power for stress-level dependency of stiffness",
        suffix="-")
    param.lambdaModified = NumberField(
        ui_name="$λ^{*}$",
        description="Modified compression index",
        suffix="-")
    param.kappaModified = NumberField(
        ui_name="$κ^{*}$",
        description="Modified swelling index",
        suffix="-")
    param.cref = NumberField(
        ui_name="$c_{ref}'$",
        description="Cohesion",
        suffix="kN / m^2")
    param.phi = NumberField(
        ui_name="$φ'$",
        description="Friction angle",
        suffix="deg")
    param.psi = NumberField(
        ui_name="$ψ$",
        description="Dilatancy angle",
        suffix="deg")
    param.DefaultValuesAdvanced = OptionField(ui_name="Advanced: set to default", options=["True", "False"])
    groundwater = Tab("Groundwater")
    groundwater.DataSetFlow = OptionField(
        ui_name="data set",
        options=["USDA"])
    groundwater.UsdaSoilType = OptionField(
        ui_name="soil type",
        options=["Loamy sand", "Sand", "Clay"])
    groundwater.SoilRatioSmall = NumberField(
        ui_name="larger than 2μm",
        suffix="%")
    groundwater.SoilRatioMedium = NumberField(
        ui_name="2μm - 50μm",
        suffix="%")
    groundwater.SoilRatioLarge = NumberField(
        ui_name="50μm - 2mm",
        suffix="%")
    groundwater.UseDefaultsFlow = OptionField(
        ui_name="Use defaults",
        options=[OptionListElement("fromdataset", "From data set"), OptionListElement("none", "None")])
    groundwater.perm_primary_horizontal_axis = NumberField(
        ui_name="$k_{x}$",
        description="Horizontal permeability",
        suffix="m/day")
    groundwater.perm_vertical_axis = NumberField(
        ui_name="$k_{y}$",
        description="Vertical permeability",
        suffix="m/day")
    groundwater.ck = NumberField(
        ui_name="$c_{k}$",
        description="Change in permeability",
        suffix="-")
    interfaces = Tab("Interfaces")
    interfaces.new_line_4 = LineBreak()
    interfaces.InterfaceStrength = OptionField(
        ui_name="Interface strength",
        options=["Rigid"])
    interfaces.Rinter = NumberField(
        ui_name="$R_{inter}$",
        description="Strength reduction factor",
        suffix="-")
    interfaces.new_line_5 = LineBreak()
    interfaces.K0Determination = OptionField(
        ui_name="$K_{0}$ determination",
        options=["Automatic"])
    interfaces.OCR = NumberField(
        ui_name="OCR",
        description="Over-consolidation ratio",
        suffix="-")
    interfaces.POP = NumberField(
        ui_name="POP",
        description="Pre-overburden pressure",
        suffix="kN / m^2")

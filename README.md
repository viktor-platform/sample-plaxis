![](https://img.shields.io/badge/SDK-v13.0.0-blue) <Please check version is the same as specified in requirements.txt>

# PLAXIS embankment evaluator
This sample app shows how to integrate PLAXIS into a VIKTOR application. In this application the following tutorial is
used as an example: [PLAXIS 2D Tutorial 08: Construction of a road embankment](https://communities.bentley.com/products/geotech-analysis/w/plaxis-soilvision-wiki/45559/plaxis-2d-tutorial-08-construction-of-a-road-embankment).
This sample app is built on PLAXIS v21.

An example interaction with the sample app is shown below.

![Inside the application you can define materials, make an embankment and evaluate this in the "PLAXIS analysis" tab](source/images/sample-app-overview.gif "Sample app overview")

# Installing the application
Since a worker is needed for this application, some work is required to install the application properly.

1. A worker should be installed according to the VIKTOR docs: [PLAXIS generic worker docs](https://docs.viktor.ai/docs/guides/integrations/plaxis)
This worker should be on the same machine as where PLAXIS is installed.
2. PLAXIS uses some Python interpreter, which can be the default one PLAXIS provides, or another one which you can
define yourself in PLAXIS itself by navigating through the menu:  
`Expert -> Python -> Configure Python Interpreter -> Use the follwing Python interpreter`  
Here you can navigate to your preferred Python environment, and then click `Install required components...`. As the
PLAXIS-Python script provided by this sample application works with munch and numpy, install these packages on the 
selected Python environment.
3. Once this is configured, install the sample application. In the file `app/lib/plaxis.py`, the following two variables
should be edited:
    - `PLAXIS_PATH`: Set the correct path to your `Plaxis2DXInput.exe`
    - `PASSWORD`: Set the password that is defined `Expert -> Configure remote scripting server`
4. Finally, check the worker status in the integration status menu. The Generic worker should state that all instances are available. 

# Using the application
The application has two main objects: Material and Embankment. You can set up various materials in the Material editor.
The Embankment is setup in the Embankment editor.

### Material editor
An example of the material editor is shown below. To keep things as simple as possible, only the options are implemented
that are shown in the tutorial. This can easily be extended to fit your own needs!

### Embankment editor
The embankment is parametrized in three sections:
- Embankment itself: a width of the top part of the embankment (16 metres in the tutorial), the width of 
the slope (12 metres in the tutorial) and height (4 metres in the tutorial). Furthermore a material for the embankment 
needs to be specified
- Soil below the embankment: the semi-width of the soil (60 m in the tutorial), and the soil layers. One can add a 
row for each layer, and specify a thickness and a material for each layer
- Drains: Enable/disable the drains, and if they are enabled, specify the spacing and depth of the drains

On the right-hand-side you can view what the embankment looks like in the `Embankment 2D` view, and analyse the model in
the `PLAXIS analysis` view.

# Specific script use
PLAXIS-specific code can be found in `app/functions/plaxis.py`. This is the file that is sent to the generic VIKTOR 
worker. You can use this file without VIKTOR, yet then you need to specify your own `input.json` and `material.json` 
files. Furthermore, you have to specify your own output visualisation if wished.

# App structure
embankment_folder: has embankments as its children
  └─ embankment: defines the input for PLAXIS and retrieves the output from PLAXIS
material_folder: has materials as its children
  └─ material: can be used as a data-set for PLAXIS material inputs

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

from app.embankment.controller import EmbankmentController as Embankment
from app.embankment_folder.controller import EmbankmentFolderController as EmbankmentFolder
from app.material.controller import MaterialController as Material
from app.material_folder.controller import MaterialFolderController as MaterialFolder

from viktor import InitialEntity

initial_entities = [
    InitialEntity('EmbankmentFolder', name='Embankments', children=[
        InitialEntity('Embankment', name='sample embankment', params='../manifest/Embankment/sample-embankment.json')
    ]),
    InitialEntity('MaterialFolder', name='Materials', children=[
        InitialEntity('Material', name='Embankment', params='../manifest/Material/embankment.json'),
        InitialEntity('Material', name='Peat', params='../manifest/Material/peat.json'),
        InitialEntity('Material', name='Clay', params='../manifest/Material/clay.json'),
        InitialEntity('Material', name='Sand', params='../manifest/Material/sand.json')
    ])
]

<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="Symbology">
  <renderer-v2 type="graduatedSymbol" attr="priority_score" graduatedMethod="GraduatedColor" symbollevels="0">
    <ranges>
      <range symbol="0" render="true" lower="0" upper="25" label="Low"/>
      <range symbol="1" render="true" lower="25" upper="50" label="Moderate"/>
      <range symbol="2" render="true" lower="50" upper="75" label="High"/>
      <range symbol="3" render="true" lower="75" upper="100" label="Critical"/>
    </ranges>
    <symbols>
      <symbol type="fill" name="0"><layer class="SimpleFill"><Option type="Map"><Option name="color" value="42,157,143,130" type="QString"/></Option></layer></symbol>
      <symbol type="fill" name="1"><layer class="SimpleFill"><Option type="Map"><Option name="color" value="233,196,106,140" type="QString"/></Option></layer></symbol>
      <symbol type="fill" name="2"><layer class="SimpleFill"><Option type="Map"><Option name="color" value="244,162,97,150" type="QString"/></Option></layer></symbol>
      <symbol type="fill" name="3"><layer class="SimpleFill"><Option type="Map"><Option name="color" value="230,57,70,160" type="QString"/></Option></layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>

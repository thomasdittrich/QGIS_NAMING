import processing
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import QgsCoordinateReferenceSystem, QgsProject

layer = iface.activeLayer()

# Layer reprojectieren (kopieren und in EPSG:4326 umwandeln)
params = {
    'INPUT': layer,
    'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
    'OUTPUT': 'memory:'  # kann auch als Datei gespeichert werden
}
result = processing.run("native:reprojectlayer", params)

layername= f"{combined_value}{'_reprojeziert'}"

reprojected_layer = result['OUTPUT']

# Neue Layer in Projekt hinzufügen
QgsProject.instance().addMapLayer(reprojected_layer)

# In diesem Fall arbeiten wir mit der neuen Layer (reprojected_layer)
# Die weiteren Schritte sind gleich, nur auf `reprojected_layer` statt auf `layer`

# Sicherstellen, dass die Felder vorhanden sind
def ensure_field_exists(layer, field_name):
    fields = [field.name() for field in layer.fields()]
    if field_name not in fields:
        layer.dataProvider().addAttributes([QgsField(field_name, QVariant.String)])
        layer.updateFields()

# Jetzt mit der reprojizierten Layer weiterarbeiten
layer = reprojected_layer

# Sicherstellen, dass die Felder existieren
ensure_field_exists(layer, 'CLIENT_NAM')
ensure_field_exists(layer, 'FARM_NAME')
ensure_field_exists(layer, 'FIELD_NAME')

# Start des Edit-Modus
layer.startEditing()

# Abfragen
choice, ok = QInputDialog.getItem(None, 'Wahl', 'Was soll in FIELD_NAME eingetragen werden?', ['Nur Name', 'Nummer + Name'], 0, False)
client_name, ok2 = QInputDialog.getText(None, 'Eingabe', 'CLIENT_NAM')
farm_name, ok3 = QInputDialog.getText(None, 'Eingabe', 'FARM_NAME')

if ok and ok2 and ok3:
    adjusted = False
    for feature in layer.getFeatures():
        # Werte setzen
        layer.changeAttributeValue(feature.id(), layer.fields().indexOf('FARM_NAME'), farm_name)
        layer.changeAttributeValue(feature.id(), layer.fields().indexOf('CLIENT_NAM'), client_name)

        # Attribute auslesen
        nummer = feature['NUMMER']
        teilNummer = feature['TEILNUM']
        name = feature['NAME']

        if choice == "Nur Name":
            combined_value = name
        else:
            combined_value = f"{nummer}-{teilNummer}{' '}{name}"

        # Feld 'FIELD_NAME' setzen
        layer.changeAttributeValue(feature.id(), layer.fields().indexOf('FIELD_NAME'), combined_value)

# Änderungen speichern
layer.commitChanges()

# Meldung
if layer == reprojected_layer:
    print("Layer wurde neu reprojiziert (EPSG:4326). Die Bearbeitung erfolgt auf der reprojizierten Kopie.")
else:
    print("Layer ist bereits im EPSG:4326, keine Reprojektion notwendig.")

from rest_framework import serializers

class OmnivaSavedShimpentSerializer(serializers.Serializer):
    clientItemId = serializers.CharField()
    barcode = serializers.CharField()

class OmnivaResponseSerializer(serializers.Serializer):
    resultCode = serializers.ChoiceField(choices=["OK"])
    savedShipments = OmnivaSavedShimpentSerializer(many=True)
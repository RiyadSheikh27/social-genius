from rest_framework import serializers
from support.models import Support

class SupportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Support
        fields = ['id', 'user', 'support_email', 'type', 'problem', 'report', 'feedback', 'url', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        problem = data.get('problem')
        report = data.get('report')
        feedback = data.get('feedback')

        if not (problem or report or feedback):
            raise serializers.ValidationError(
                "Please fill at least one of the following fields: problem, report, or feedback."
            )
        return data

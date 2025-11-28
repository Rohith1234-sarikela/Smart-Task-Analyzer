from rest_framework import serializers

STRATEGY_CHOICES = (
    ("smart_balance", "Smart Balance"),
    ("fastest_wins", "Fastest Wins"),
    ("high_impact", "High Impact"),
    ("deadline_driven", "Deadline Driven"),
)

class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(min_value=0.1)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

class AnalyzeRequestSerializer(serializers.Serializer):
    strategy = serializers.ChoiceField(choices=[c[0] for c in STRATEGY_CHOICES], default="smart_balance")
    tasks = TaskSerializer(many=True)

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import AnalyzeRequestSerializer
from . import scoring

# Simple in-memory storage just for the last analyzed set of tasks.
LAST_RAW_TASKS = []


@method_decorator(csrf_exempt, name="dispatch")
class AnalyzeTasksView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        # Allow payload to be either:
        # - list of tasks
        # - { "strategy": "...", "tasks": [...] }
        if isinstance(data, list):
            wrapper = {"strategy": "smart_balance", "tasks": data}
        else:
            wrapper = data

        serializer = AnalyzeRequestSerializer(data=wrapper)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        strategy = serializer.validated_data["strategy"]
        tasks = serializer.validated_data["tasks"]

        global LAST_RAW_TASKS
        LAST_RAW_TASKS = tasks

        scored = scoring.analyze_tasks(tasks, strategy=strategy)
        return Response(scored, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class SuggestTasksView(APIView):
    def get(self, request, *args, **kwargs):
        global LAST_RAW_TASKS
        if not LAST_RAW_TASKS:
            return Response(
                {"detail": "No tasks analyzed yet. Call /api/tasks/analyze/ first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scored = scoring.analyze_tasks(LAST_RAW_TASKS, strategy="smart_balance")
        top3 = scored[:3]
        return Response(top3, status=status.HTTP_200_OK)

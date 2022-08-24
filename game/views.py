import uuid
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ConnectorSerializer


class GenericWebhook(GenericAPIView):
    serializer_class = ConnectorSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id = serializer.data.get('id')
        unique_id = str(uuid.uuid4().hex)

        return Response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "inputFields": [{
                        "key": "webhook_url",
                        "label": "Webhook URL",
                        "type": "string",
                        "default": "https://orchestrator.grindery.org/webhook/genericWebhook/inboundWebhook/" + unique_id,
                        "readonly": True,
                        "helpText": "Send POST requests to this URL to trigger your workflow execution.",
                        "required": True
                    }],
                    "outputFields": []
                }
            },
            status=status.HTTP_201_CREATED
        )

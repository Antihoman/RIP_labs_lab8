from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests

from concurrent import futures

CALLBACK_URL = "http://localhost:8080/api/turns/"

executor = futures.ThreadPoolExecutor(max_workers=1)
TOKEN = 'secret_token'


def get_random_status(turn_id):
    time.sleep(5)
    return {
        "turn_id": turn_id,
        "status":bool(random.randint(0, 3)),
    }


def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return

    url = str(CALLBACK_URL+str(result["turn_id"])+'/sending/')
    requests.put(url, data={"sending_status": result['status'], "token": TOKEN}, timeout=3)


@api_view(['POST'])
def set_status(request):
    if "turn_id" in request.data.keys():
        turn_id = request.data["turn_id"]

        task = executor.submit(get_random_status, turn_id)
        task.add_done_callback(status_callback)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
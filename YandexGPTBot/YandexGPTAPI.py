import json
import logging
import threading
import requests


class YaGPTApi(threading.Thread):
    def __init__(self, message, yatoken, model="yandexgpt", temp=0.5, context=""):
        self.__model = model
        self.__temp = temp
        self.__context = context
        self.__message = message
        self.__token = yatoken
        self.__lock = threading.Lock()
        self.__result = None
        self.__error = None
        threading.Thread.__init__(self)

    def run(self):
        self._send_msg_to_model()

    def retrieve_error(self):
        self.__lock.acquire()
        error = self.__error
        self.__lock.release()
        return error

    def retrieve_result(self):
        self.__lock.acquire()
        result = self.__result
        self.__lock.release()
        return result

    def _send_msg_to_model(self):
        try:
            logging.info("Request to model " + self.__model + " with temp " + str(self.__temp) +
                         " and context \"" + self.__context + "\"")
            body = {
                "modelUri": "gpt://b1g9kpp66vb9ok1dajsk/" + self.__model + "/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": self.__temp,
                    "maxTokens": "2000"
                },
                "messages": [
                    {
                        "role": "user",
                        "text": self.__message
                    }
                ]
            }
            if self.__context != "":
                body["messages"].append({
                    "role": "system",
                    "text": self.__context
                })
            request = requests.post(url="https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer ' + self.__token,
                                             'x-folder-id': 'b1g9kpp66vb9ok1dajsk'},
                                    data=json.dumps(body))
            result = request.json()["result"]["alternatives"][0]["message"]["text"]
            logging.info("Model answer: " + result)
            self.__lock.acquire()
            self.__result = result
        except Exception as err:
            logging.warning(err)
            self.__lock.acquire()
            self.__error = err
        finally:
            self.__lock.release()

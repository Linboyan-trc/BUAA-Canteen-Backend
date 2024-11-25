# 作者: toryn
# 时间: 2024/11/25
import warnings
from enum import Enum, unique
from django.http import JsonResponse

@unique
class ErrorCode(Enum):
    """
    api error code
    """
    # success family
    SUCCESS_CODE = 200_00

    # bad request family
    BAD_REQUEST_ERROR = 400_00
    INVALID_REQUEST_ARGUMENT_ERROR = 400_01
    REQUIRED_ARG_IS_NULL_ERROR = 400_02
    CANNOT_LOGIN_ERROR = 400_03

    # unauthorized family
    UNAUTHORIZED_ERROR = 401_00
    INVALID_TOKEN_ERROR = 401_01
    INVALID_REFRESH_TOKEN_ERROR = 401_02

    # refuse family
    REFUSE_ACCESS_ERROR = 403_00

    # not found family
    NOT_FOUND_ERROR = 404_00

    # duplicated family
    DUPLICATED_ERROR = 409_00


def _api_response(success, data) -> dict:
    """
    wrap an api response dict obj
    :param success: whether the request is handled successfully
    :param data: requested data
    :return: a dictionary object, like {'success': success, 'data': data}
    """
    return {'success': success, 'data': data}


def success_api_response(data) -> dict:
    """
    wrap a success api response dict obj
    :param data: requested data
    :return: a dictionary object, like {'success': True, 'data': data}
    """
    return _api_response(True, data)


def failed_api_response(code, error_msg=None) -> dict:
    """
       wrap a failed response dict obj
       :param code: error code, refers to ErrorCode, can be an integer or a str (error name)
       :param error_msg: external error information
       :return: an api response dict obj
    """
    if isinstance(code, str):
        code = ErrorCode[code]
    if isinstance(code, int):
        code = ErrorCode(code)
    assert isinstance(code, ErrorCode)
    assert isinstance(code.value, int)

    if code.value < 1000:
        warnings.warn("using simple http code {} is deprecated".format(code.name))
        code = ErrorCode(code.value * 100)
    assert code.value >= 10000

    if error_msg is None:
        error_msg = code.name
    else:
        error_msg = error_msg

    status_code = code.value // 100
    detailed_code = code.value

    return _api_response(
        success=False,
        data={
            'code': status_code,
            'detailed_error_code': detailed_code,
            'error_msg': error_msg
        })


def response_wrapper(func):
    """
    decorate a function to return from a dict to a JsonResponse object
    :param func: an api-function
    :return: wrapped function
    """
    def _inner(*args, **kwargs):
        _response = func(*args, **kwargs)
        if isinstance(_response, dict):
            if _response['success']:
                return JsonResponse(_response)
            else:
                status_code = _response.get("data").get("code")
                return JsonResponse(_response, status=status_code)
    return _inner







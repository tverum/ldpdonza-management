from guardian.shortcuts import get_objects_for_user

from management.models import Seizoen
from management.utils import get_current_seizoen


def authorized_ploegen(request):
    user = request.user
    if request.user.is_authenticated:
        ploegen = get_objects_for_user(user, 'management.view_ploeg')
        kwargs = {
            'authorized_ploegen': ploegen
        }
    else:
        kwargs = {}
    return kwargs


def current_seizoen(request):
    """
    Retrieve the current seizoen to display in the frontend
    :param request: the request that is performed
    :return: the arguments
    """
    kwargs = {}
    if request.user.is_authenticated:
        seizoen = get_current_seizoen(request)
        kwargs['current_seizoen'] = seizoen
    kwargs['seizoenen'] = list(Seizoen.objects.all())
    return kwargs

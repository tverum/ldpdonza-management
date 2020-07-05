from guardian.shortcuts import get_objects_for_user


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

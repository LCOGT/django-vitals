from django.views.generic import View
from django.http import JsonResponse

from .conf import conf


def run_checks(request):
    failed = {}
    ok = []
    if request.GET.get('check'):
        checks_to_run = [request.GET['check']]
    else:
        checks_to_run = conf.enabled_checks.keys()

    for c in checks_to_run:
        check = conf.enabled_checks[c]
        inst = check['class'](name=c, **check['args'])
        inst.run_check()
        if inst.errors:
            failed[inst.name] = inst.errors
        else:
            ok.append(inst.name)

    return {'ok': ok, 'failed': failed}


class VitalsJSONView(View):
    def get(self, request):
        results = run_checks(request)
        if results['failed']:
            status = 500
        else:
            status = 200

        return JsonResponse(results, status=status)
